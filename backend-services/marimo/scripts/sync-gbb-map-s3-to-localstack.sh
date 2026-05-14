#!/usr/bin/env -S bash -euo pipefail
# Mirrors GBB map silver/gas_model table prefixes into LocalStack.

usage() {
	cat <<'USAGE'
Usage:
  scripts/sync-gbb-map-s3-to-localstack.sh --from cache
  scripts/sync-gbb-map-s3-to-localstack.sh --from live

Options:
  --from cache|live       cache uploads existing local cache; live refreshes cache first
  --cache-dir DIR         local cache root for mirrored AEMO bucket contents
  --source-bucket BUCKET  live S3 bucket used when --from live is selected
  --local-bucket BUCKET   LocalStack AEMO bucket to upload into
  --endpoint-url URL      LocalStack endpoint URL
  -h, --help              show this help

Environment:
  GBB_MAP_S3_CACHE_DIR    default cache root
  GBB_MAP_SOURCE_BUCKET   default live source bucket
  AEMO_BUCKET             default LocalStack target bucket
  AWS_ENDPOINT_URL        default LocalStack endpoint
  AWS_DEFAULT_REGION      AWS region for LocalStack bucket creation

The script mirrors only the Delta or parquet table prefixes needed by
notebooks/gbb_interactive_map.py.
USAGE
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
backend_services_dir="$(cd "$script_dir/../.." && pwd)"

from_mode="cache"
cache_dir="${GBB_MAP_S3_CACHE_DIR:-$backend_services_dir/.e2e/marimo-gbb-map/aemo}"
source_bucket="${GBB_MAP_SOURCE_BUCKET:-dev-energy-market-aemo}"
local_bucket="${AEMO_BUCKET:-dev-energy-market-aemo}"
localstack_endpoint="${AWS_ENDPOINT_URL:-http://localhost:4566}"
aws_region="${AWS_DEFAULT_REGION:-ap-southeast-2}"

readonly table_prefixes=(
	"silver/gas_model/silver_gas_dim_facility"
	"silver/gas_model/silver_gas_dim_location"
	"silver/gas_model/silver_gas_dim_connection_point"
	"silver/gas_model/silver_gas_fact_facility_flow_storage"
	"silver/gas_model/silver_gas_fact_nomination_forecast"
	"silver/gas_model/silver_gas_fact_capacity_outlook"
)

info() {
	printf 'INFO:%s: %s\n' "$(basename "$0")" "$*"
}

error() {
	printf 'ERROR:%s: %s\n' "$(basename "$0")" "$*" >&2
}

require_command() {
	local command_name=$1
	if ! command -v "$command_name" >/dev/null 2>&1; then
		error "required command not found: $command_name"
		exit 1
	fi
}

local_aws() {
	env \
		AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:-test}" \
		AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-test}" \
		AWS_SECURITY_TOKEN="${AWS_SECURITY_TOKEN:-test}" \
		AWS_SESSION_TOKEN="${AWS_SESSION_TOKEN:-test}" \
		AWS_DEFAULT_REGION="$aws_region" \
		aws --endpoint-url "$localstack_endpoint" "$@"
}

live_aws() {
	env -u AWS_ENDPOINT_URL aws "$@"
}

check_localstack() {
	if ! curl --silent --fail "$localstack_endpoint/_localstack/health" >/dev/null; then
		error "LocalStack is not reachable at $localstack_endpoint"
		exit 1
	fi
}

ensure_local_bucket() {
	if local_aws s3api head-bucket --bucket "$local_bucket" >/dev/null 2>&1; then
		return
	fi

	info "creating LocalStack bucket s3://$local_bucket"
	local_aws s3 mb "s3://$local_bucket" --region "$aws_region" >/dev/null
}

refresh_cache_from_live_s3() {
	info "refreshing local cache from s3://$source_bucket"
	for prefix in "${table_prefixes[@]}"; do
		info "downloading s3://$source_bucket/$prefix"
		mkdir -p "$cache_dir/$prefix"
		live_aws s3 sync \
			"s3://$source_bucket/$prefix" \
			"$cache_dir/$prefix" \
			--delete
	done
}

validate_cache() {
	local missing_count=0
	for prefix in "${table_prefixes[@]}"; do
		if ! cached_table_has_data "$cache_dir/$prefix"; then
			error "cached table prefix is missing _delta_log and parquet files: $cache_dir/$prefix"
			missing_count=$((missing_count + 1))
		fi
	done

	if ((missing_count > 0)); then
		error "cache is incomplete; run with --from live or point --cache-dir at a complete cache"
		exit 1
	fi
}

cached_table_has_data() {
	local table_dir=$1
	[[ -d "$table_dir" ]] || return 1
	[[ -d "$table_dir/_delta_log" ]] && return 0
	find "$table_dir" -maxdepth 1 -type f -name '*.parquet' -print -quit | grep -q .
}

upload_cache_to_localstack() {
	info "uploading cache to LocalStack bucket s3://$local_bucket"
	for prefix in "${table_prefixes[@]}"; do
		info "uploading $prefix"
		local_aws s3 sync \
			"$cache_dir/$prefix" \
			"s3://$local_bucket/$prefix" \
			--delete
	done
}

parse_args() {
	while (($# > 0)); do
		case "$1" in
		--from)
			if (($# < 2)); then
				error "--from requires cache or live"
				exit 2
			fi
			from_mode=$2
			shift 2
			;;
		--from-cache)
			from_mode="cache"
			shift
			;;
		--from-live)
			from_mode="live"
			shift
			;;
		--cache-dir)
			if (($# < 2)); then
				error "--cache-dir requires a path"
				exit 2
			fi
			cache_dir=$2
			shift 2
			;;
		--source-bucket)
			if (($# < 2)); then
				error "--source-bucket requires a bucket name"
				exit 2
			fi
			source_bucket=$2
			shift 2
			;;
		--local-bucket)
			if (($# < 2)); then
				error "--local-bucket requires a bucket name"
				exit 2
			fi
			local_bucket=$2
			shift 2
			;;
		--endpoint-url)
			if (($# < 2)); then
				error "--endpoint-url requires a URL"
				exit 2
			fi
			localstack_endpoint=$2
			shift 2
			;;
		-h | --help)
			usage
			exit 0
			;;
		*)
			error "unknown argument: $1"
			usage >&2
			exit 2
			;;
		esac
	done

	if [[ "$from_mode" != "cache" && "$from_mode" != "live" ]]; then
		error "--from must be cache or live"
		exit 2
	fi
}

main() {
	parse_args "$@"
	require_command aws
	require_command curl

	info "mode:       $from_mode"
	info "cache:      $cache_dir"
	info "source:     s3://$source_bucket"
	info "target:     s3://$local_bucket"
	info "endpoint:   $localstack_endpoint"

	check_localstack
	ensure_local_bucket

	if [[ "$from_mode" == "live" ]]; then
		refresh_cache_from_live_s3
	fi

	validate_cache
	upload_cache_to_localstack
	info "GBB map LocalStack sync complete."
}

main "$@"
