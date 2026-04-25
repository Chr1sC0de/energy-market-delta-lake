import gc
import os
import tempfile
from abc import ABC, abstractmethod
from typing import IO
from zipfile import ZipFile

from dagster import AssetExecutionContext
from dagster_aws.s3 import S3Resource
from polars import scan_csv
from types_boto3_s3 import S3Client

CHUNK_SIZE = 8 * 1024 * 1024  # 8MB
# Parquet row group size: limits peak memory during sink_parquet writes.
PARQUET_ROW_GROUP_SIZE = 100_000


class FileUnzipper(ABC):
    @abstractmethod
    def unzip(
        self,
        context: AssetExecutionContext,
        s3: S3Resource,
        s3_source_keys: list[str],
        s3_landing_bucket: str,
        s3_landing_prefix: str,
        s3_archive_bucket: str,
    ) -> list[dict[str, str]]: ...


class S3FileUnzipper(FileUnzipper):
    def unzip(
        self,
        context: AssetExecutionContext,
        s3: S3Resource,
        s3_source_keys: list[str],
        s3_landing_bucket: str,
        s3_landing_prefix: str,
        s3_archive_bucket: str,
    ) -> list[dict[str, str]]:
        # Return value is used only as a completion signal by downstream ops
        # (In(Nothing)). We do not accumulate results to avoid holding a
        # potentially large list in memory across all zip files in the batch.
        s3_client: S3Client = s3.get_client()

        for s3_source_key in s3_source_keys:
            context.log.info(
                f"Processing zip file s3://{s3_landing_bucket}/{s3_source_key}"
            )

            try:
                # --- 1. STREAM ZIP FROM S3 TO DISK ---
                tmp_zip_path = None
                try:
                    with tempfile.NamedTemporaryFile(
                        suffix=".zip", delete=False
                    ) as tmp_zip:
                        tmp_zip_path = tmp_zip.name
                        s3_client.download_fileobj(
                            s3_landing_bucket, s3_source_key, tmp_zip
                        )

                    member_successes: list[str] = []
                    member_failures: list[str] = []

                    # --- 2. OPEN ZIP FROM DISK ---
                    with ZipFile(tmp_zip_path) as zf:
                        for member in zf.infolist():
                            if member.is_dir():
                                continue

                            original_filename = member.filename
                            # Normalise path separators and casing only on the filename
                            # component, preserving directory structure intentionally.
                            base_dir = os.path.dirname(original_filename)
                            base_name = os.path.basename(original_filename)
                            extension = (
                                base_name.lower().rsplit(".", 1)[-1]
                                if "." in base_name
                                else ""
                            )

                            context.log.info(
                                f"Processing member: {original_filename} "
                                f"(compressed={member.compress_size:,} B, "
                                f"uncompressed={member.file_size:,} B)"
                            )

                            write_key: str | None = None

                            try:
                                # --- 3. EXTRACT MEMBER ---
                                with zf.open(member) as zipped_file:
                                    if extension == "csv":
                                        write_key = self._convert_csv_to_parquet(
                                            context=context,
                                            s3_client=s3_client,
                                            zipped_file=zipped_file,
                                            original_filename=original_filename,
                                            base_dir=base_dir,
                                            base_name=base_name,
                                            s3_target_bucket=s3_landing_bucket,
                                            s3_target_prefix=s3_landing_prefix,
                                        )
                                    else:
                                        write_key = (
                                            f"{s3_landing_prefix}/{original_filename}"
                                        )
                                        s3_client.upload_fileobj(
                                            zipped_file, s3_landing_bucket, write_key
                                        )

                                member_successes.append(original_filename)

                            except Exception as member_exc:
                                context.log.error(
                                    f"Failed to process member {original_filename}: {member_exc}",
                                    exc_info=True,
                                )
                                member_failures.append(original_filename)

                    # --- 4. DELETE ORIGINAL ZIP (only if all members succeeded) ---
                    if member_failures:
                        context.log.warning(
                            f"Skipping deletion of source zip {s3_source_key} "
                            f"because {len(member_failures)} member(s) failed: "
                            f"{member_failures}"
                        )
                    else:
                        s3_client.copy_object(
                            CopySource={
                                "Bucket": s3_landing_bucket,
                                "Key": s3_source_key,
                            },
                            Bucket=s3_archive_bucket,
                            Key=s3_source_key,
                        )
                        s3_client.delete_object(
                            Bucket=s3_landing_bucket, Key=s3_source_key
                        )
                        context.log.info(
                            f"Deleted source zip: s3://{s3_landing_bucket}/{s3_source_key}"
                        )

                    context.log.info(
                        f"Finished {s3_source_key} → {s3_landing_prefix} "
                        f"({len(member_successes)} ok, {len(member_failures)} failed)"
                    )

                finally:
                    if tmp_zip_path and os.path.exists(tmp_zip_path):
                        os.unlink(tmp_zip_path)
                    # Release any memory held by Polars/Arrow from this zip
                    # before moving on to the next one in the batch.
                    gc.collect()

            except s3_client.exceptions.NoSuchKey:
                context.log.warning(
                    f"No key found: s3://{s3_landing_bucket}/{s3_source_key}"
                )

            except Exception as e:
                context.log.error(
                    f"Failed processing {s3_source_key}: {e}", exc_info=True
                )
                raise

        return []

    def _convert_csv_to_parquet(
        self,
        context: AssetExecutionContext,
        s3_client: S3Client,
        zipped_file: IO[bytes],
        original_filename: str,
        base_dir: str,
        base_name: str,
        s3_target_bucket: str,
        s3_target_prefix: str,
    ) -> str:
        """
        Extracts a CSV from a zip member, converts it to parquet via a lazy
        scan (no full in-memory load), and uploads to S3.

        Falls back to uploading the raw CSV if conversion fails.
        Returns the S3 write key.
        """
        parquet_name = base_name.lower().rsplit(".csv", 1)[0] + ".parquet"
        output_rel = os.path.join(base_dir, parquet_name) if base_dir else parquet_name
        write_key = f"{s3_target_prefix}/{output_rel}"

        tmp_csv_path = tmp_parquet_path = None

        try:
            with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp_csv:
                tmp_csv_path = tmp_csv.name
                while chunk := zipped_file.read(CHUNK_SIZE):
                    tmp_csv.write(chunk)

            with tempfile.NamedTemporaryFile(
                suffix=".parquet", delete=False
            ) as tmp_parquet:
                tmp_parquet_path = tmp_parquet.name

            # Lazy scan — does not load entire CSV into memory.
            # low_memory=True reduces peak memory at the cost of speed.
            # row_group_size caps how many rows are buffered per Parquet row
            # group, preventing large spikes during sink_parquet writes.
            scan_csv(
                tmp_csv_path, low_memory=True, infer_schema_length=None
            ).sink_parquet(tmp_parquet_path, row_group_size=PARQUET_ROW_GROUP_SIZE)

            with open(tmp_parquet_path, "rb") as parquet_fh:
                s3_client.upload_fileobj(parquet_fh, s3_target_bucket, write_key)

            context.log.info(f"Converted {original_filename} → parquet at {write_key}")

        except Exception as e:
            context.log.warning(
                f"CSV → parquet failed for {original_filename}, "
                f"falling back to raw CSV upload. Error: {e}"
            )
            # Fallback: re-read from the temp CSV we already wrote to disk
            # (avoids the unseekable ZipExtFile problem entirely)
            write_key = f"{s3_target_prefix}/{original_filename}"
            if tmp_csv_path and os.path.exists(tmp_csv_path):
                with open(tmp_csv_path, "rb") as csv_fh:
                    s3_client.upload_fileobj(csv_fh, s3_target_bucket, write_key)
            else:
                raise RuntimeError(
                    f"CSV fallback failed: temp file unavailable for {original_filename}"
                ) from e

        finally:
            for path in (tmp_csv_path, tmp_parquet_path):
                if path and os.path.exists(path):
                    os.unlink(path)

        return write_key
