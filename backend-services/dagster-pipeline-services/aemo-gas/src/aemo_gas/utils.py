from types_boto3_s3.client import S3Client


def join_by_newlines(*args: str) -> str:
    return "\n".join(args)
