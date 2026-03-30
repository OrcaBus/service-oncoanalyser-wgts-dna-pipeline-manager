#!/usr/bin/env bash

# Set to fail
set -euo pipefail

# Globals
LAMBDA_FUNCTION_NAME="WruDraftValidator"
HOSTNAME=""

# CLI Defaults
FORCE=false  # Use --force to set to true
OUTPUT_URI_PREFIX=""
LOGS_URI_PREFIX=""
CACHE_URI_PREFIX=""
PROJECT_ID=""
COMMENT=""  # Use -c or --comment to set a comment to be added to the payload
SAVE_DRAFT_PAYLOAD=""

# Workflow constants
WORKFLOW_NAME="oncoanalyser-wgts-dna"
WORKFLOW_VERSION="2.2.0"
EXECUTION_ENGINE="ICA"
CODE_VERSION="b94cbc7"
PAYLOAD_VERSION="2025.08.05"
ANALYSIS_STORAGE_SIZE=""

# SOP constants
SOP_VERSION="2026.03.05"
SOP_ID="PM.OWD.1"
GITHUB_REPO="OrcaBus/service-oncoanalyser-wgts-dna-pipeline-manager"
THIS_SCRIPT_PATH="docs/operation/SOP/${SOP_ID}/generate-WRU-draft.sh"

# Library id array
LIBRARY_ID_ARRAY=()

# Functions
echo_stderr(){
  echo "$(date -Iseconds)" "$@" >&2
}

print_usage(){
  local hostname
  if ! hostname="$(get_hostname_from_ssm)"; then
    echo_stderr "ERROR: Couldn't get hostname var from AWS, ensure you're logged into AWS"
  fi
  if [[ -z "${hostname}" ]]; then
    hostname="<aws_account_prefix>.umccr.org"
  fi

  echo "
generate-WRU-draft.sh [-h | --help]
generate-WRU-draft.sh (library_id)...
                      (-c | --comment <comment>)
                      [-f | --force]
                      [-o | --output-uri-prefix <s3_uri>]
                      [-l | --logs-uri-prefix <s3_uri>]
                      [-t | --cache-uri-prefix <s3_uri>]
                      [-p | --project-id <project_id>]
                      [-s | --analysis-storage-size <analysis_storage_size>]
                      [--save-draft-payload <output_file>]
                      [--workflow-version <workflow_version>]
                      [--code-version <code_version>]

Description:
Run this script to generate a draft WorkflowRunUpdate event for the specified library IDs.

Research Projects Note:
If you intend to run this workflow outside of the main ICA projects (development, staging, production),
ensure you have --output-uri-prefix, --cache-uri-prefix, --logs-uri-prefix, and --project-id set appropriately.

You will also need to ensure that the ICA pipeline ID attributed to the workflow-name/version/codeVersion is
available in the ICA project id specified.

The output uri prefix, cache uri and logs uri prefixes must be set to a location inside the s3 prefix that the ICA project is mounted on.

Analysis storage size note:
If not set, the populate-draft-data step function will first look through the fastq sizes for these libraries
to gauge what analysis storage size should be used. Therefore it is recommend to set this parameter as blank

Positional arguments:
  library_id:   One or more library IDs to link to the WorkflowRunUpdate event.

Keyword arguments:
  -h | --help                                   Print this help message and exit.
  -c | --comment                                (Required) A comment to add to the payload, which will be visible in the workflow run details in OrcaUI.
  -f | --force                                  (Optional) Don't confirm before pushing the event to EventBridge.
  -o | --output-uri-prefix=<output_uri_prefix>  (Optional) S3 URI prefix, Outputs written to <output_uri_prefix><portal_run_id> (prefix value must end with a slash).
  -l | --logs-uri-prefix=<logs_uri_prefix>      (Optional) S3 URI prefix, Logs written to <logs_uri_prefix><portal_run_id> (prefix value must end with a slash).
  -t | --cache-uri-prefix=<cache_uri_prefix>    (Optional) S3 URI prefix, Cache data staged at <cache_uri_prefix><portal_run_id> (prefix value must end with a slash).
  -p | --project-id=<project_id>                (Optional) ICAv2 Project ID to associate with the workflow run
  -s | --analysis-storage-size=<size>           (Optional) Set the analysis storage size, one of:
                                                  - SMALL / MEDIUM / LARGE / XLARGE / 2XLARGE / 3XLARGE
  --save-draft-payload=<output_file>            (Optional) (Optional) Save the generated draft event to local file <output_file> after pushing to event bridge for record purposes.
  --workflow-version=<workflow_version>         (Optional) Override the default workflow version.
  --code-version=<code_version>                 (Optional) Override the default code version.

Environment:
  PORTAL_TOKEN: (Required) Your personal portal token from https://portal.${hostname}/
  AWS_PROFILE:  (Optional) The AWS CLI profile to use for authentication.
  AWS_REGION:   (Optional) The AWS region to use for AWS CLI commands.

Binaries:
  - aws CLI should be installed and configured with appropriate credentials and region.
    - install from https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
  - jq should be installed for JSON parsing
    - from https://github.com/jqlang/jq
  - semver for comparing versions
    - from https://github.com/fsaintjacques/semver-tool
  - curl should be installed for making API requests.
    - from https://curl.se/download.html
  - openssl should be available for generating random portal run ids.
    - this should be installed by default on most systems, but if not it can be installed from https://www.openssl.org/source/
  - awk should be available for parsing command output.
    - this should be installed by default on most systems. If not, it can be installed from https://www.gnu.org/software/gawk/

Example usage:
bash generate-WRU-draft.sh tumor_library_id normal_library_id \\
  --comment 'Redriving analysis after failure'

bash generate-WRU-draft.sh tumor_library_id normal_library_id \\
  --comment 'Redriving analysis after failure' \\
  --output-uri-prefix s3://project-bucket/analysis/oncoanalyser-wgts-dna/ \\
  --logs-uri-prefix s3://project-bucket/logs/oncoanalyser-wgts-dna/ \\
  --cache-uri-prefix s3://project-bucket/cache/oncoanalyser-wgts-dna/ \\
  --project-id project-uuid-1234-abcd

"
}

compare_script_version_to_repo(){
  : '
  Compare the version of this script to the version in the repo, and print a warning if they are different
  If anywhere along the way fails, return unknown
  '
  repo_script_version="$( \
    (
      # Read the document from the main branch
      curl --silent --fail --location --show-error \
        --header "Accept: text/html" \
        --url "https://raw.githubusercontent.com/${GITHUB_REPO}/refs/heads/main/${THIS_SCRIPT_PATH}" | \
      ( \
        # Read through the whole document to prevent curl erroring out
        tac | tac \
      ) | \
      (
        # Get the first occurrence with grep -m1 (SOP_VERSION="YYYY.MM.DD")
        # Remove the SOP_VERSION= prefix ("YYYY.MM.DD")
        # Remove quotes (YYYY.MM.DD)
        grep -m1 "SOP_VERSION" | \
        sed 's/^SOP_VERSION=//' | \
        jq --raw-output
      ) \
    ) || echo "unknown"
  )"

  if [[ "${SOP_VERSION}" != "${repo_script_version}" ]]; then
    echo_stderr "Warning: This script version (${SOP_VERSION}) is different from the version in the repo (${repo_script_version})."
    echo_stderr "         Consider refetching this script from https://github.com/${GITHUB_REPO}/blob/main/${THIS_SCRIPT_PATH}"
  fi
}

check_binaries(){
  : '
  Check that required binaries are installed
  '
  for binary in aws semver jq curl openssl awk; do
    if ! command -v "${binary}" > /dev/null 2>&1; then
      echo_stderr "Error: ${binary} is not installed. Please install ${binary} and try again. Exiting."
      return 1
    fi
  done

  # Check that jq is version 1.7 or higher, as we use the fromjson function which was added in 1.7
  jq_version="$(jq --version | cut -d'-' -f2)"
  if [[ "${jq_version}" =~ ^1.\d$ && ! "${jq_version}" == "1.7" ]]; then
    echo_stderr "Error: jq version 1.7 or higher is required. Please update jq and try again. Exiting."
    return 1
  fi
  # After version 1.7, jq changed their versioning to semver, so we can use semver to compare versions
  if [[ ! "$(semver compare "${jq_version}" "${MIN_REQUIREMENTS["jq"]}")" -ge 0 ]]; then
    echo_stderr "Error: jq version ${MIN_REQUIREMENTS["jq"]} or higher is required. Please update jq and try again. Exiting."
    return 1
  fi

  # Check aws cli version is 2.0.0 or higher, as we use the --cli-binary-format option which was added in 2.0.0
  aws_version="$(aws --version 2>&1 | awk '{print $1}' | cut -d'/' -f2)"
  if [[ ! "$(semver compare "${aws_version}" "${MIN_REQUIREMENTS["aws"]}")" -ge 0 ]]; then
    echo_stderr "Error: AWS CLI version ${MIN_REQUIREMENTS["aws"]} or higher is required. Please update AWS CLI and try again. Exiting."
    return 1
  fi

  # Check curl version is 7.76.0 or higher, as we use the --fail-with-body option which was added in 7.76.0
  curl_version="$(curl --version | head -n1 | awk '{print $2}')"
  if [[ ! "$(semver compare "${curl_version}" "${MIN_REQUIREMENTS["curl"]}")" -ge 0 ]]; then
    echo_stderr "Error: curl version ${MIN_REQUIREMENTS["curl"]} or higher is required. Please update curl and try again. Exiting."
    return 1
  fi
}

get_email_from_portal_token(){
  : '
  Get the email to use from the portal JWT
  We use this to make a comment on the workflow run in the OrcaUI
  once the event is pushed to EventBridge and the workflow run is created,
  to indicate who created the workflow run
  '
  jq --raw-output \
    --null-input \
    --arg portalToken "${PORTAL_TOKEN}" \
    '
      (
        # Get the middle chunk of the portal jwt token
        $portalToken | split(".")[1] |
        # Decode base64
        @base64d |
        # Load json
        fromjson
      ) |
      .email
    '
}

get_hostname_from_ssm(){
  # Cache the hostname in a global variable to
  # avoid multiple calls to SSM Parameter Store
  if [[ -n "${HOSTNAME}" ]]; then
    echo "${HOSTNAME}"
    return
  fi

  aws ssm get-parameter \
    --name "/hosted_zone/umccr/name" \
    --output json | \
  jq --raw-output \
    '.Parameter.Value'
}

get_aws_account_prefix(){
  local aws_account_id
  aws_account_id="$( \
    aws sts get-caller-identity --output json --query "Account" | \
    jq --raw-output \
  )"
  echo "${PREFIX_BY_AWS_ACCOUNT_ID[${aws_account_id}]:-"unknown_aws_account_prefix"}"
}

get_cognito_user_pool_id_prefix(){
  local cognito_user_pool_id
  cognito_user_pool_id="$( \
    jq --raw-output \
      --null-input \
      --arg portalToken "${PORTAL_TOKEN}" \
      '
        (
          # Get the middle chunk of the portal jwt token
          $portalToken | split(".")[1] |
          # Decode base64
          @base64d |
          # Load json
          fromjson
        ) |
        .iss |
        split("/")[-1]
      ' \
  )"
  echo "${COGNITO_USER_POOL_ID_BY_PREFIX[${cognito_user_pool_id}]:-"unknown_cognito_user_pool_id"}"
}

get_library_obj_from_library_id(){
  local library_id="$1"
  curl --silent --fail --show-error --location \
    --header "Authorization: Bearer ${PORTAL_TOKEN}" \
    --url "https://metadata.$(get_hostname_from_ssm)/api/v1/library?libraryId=${library_id}" | \
  jq --raw-output \
    '
      .results[0] |
      {
        "libraryId": .libraryId,
        "orcabusId": .orcabusId
      }
    '
}

generate_portal_run_id(){
  echo "$(date -u +'%Y%m%d')$(openssl rand -hex 4)"
}

get_linked_libraries(){
  for library_id in "${LIBRARY_ID_ARRAY[@]}"; do
    get_library_obj_from_library_id "${library_id}"
  done | \
  jq --slurp --raw-output --compact-output
}

get_lambda_function_name(){
  aws lambda list-functions \
    --output json \
    --query "Functions" | \
  jq --raw-output --compact-output \
    --arg functionName "${LAMBDA_FUNCTION_NAME}" \
    '
      map(select(.FunctionName | contains($functionName))) |
      .[0].FunctionName
    '
}

get_workflow(){
  local workflow_name="$1"
  local workflow_version="$2"
  local execution_engine="$3"
  local code_version="$4"
  curl --silent --fail --show-error --location \
    --request GET \
    --get \
    --header "Authorization: Bearer ${PORTAL_TOKEN}" \
    --url "https://workflow.$(get_hostname_from_ssm)/api/v1/workflow" \
    --data "$( \
      jq \
       --null-input --compact-output --raw-output \
       --arg workflowName "$workflow_name" \
       --arg workflowVersion "$workflow_version" \
       --arg executionEngine "$execution_engine" \
       --arg codeVersion "$code_version" \
       '
         {
            "name": $workflowName,
            "version": $workflowVersion,
            "executionEngine": $executionEngine,
            "codeVersion": $codeVersion
         } |
         to_entries |
         map(
           "\(.key)=\(.value)"
         ) |
         join("&")
       ' \
    )" | \
  jq --compact-output --raw-output \
    '
      .results[0]
    '
}

get_workflow_run(){
  local portal_run_id="$1"

  curl --silent --fail --show-error --location \
    --request GET \
    --get \
    --header "Authorization: Bearer ${PORTAL_TOKEN}" \
    --url "https://workflow.$(get_hostname_from_ssm)/api/v1/workflowrun?portalRunId=${portal_run_id}" | \
  jq --compact-output --raw-output \
    '
      if (.results | length) > 0 then
        .results[0]
      else
        empty
      end
    '
}

generate_workflow_comment(){
  : '
  Generate a comment on the workflow run
  '
  local workflow_run_orcabus_id="$1"
  local email_address="$2"
  curl --silent --fail-with-body --location --show-error \
    --request "POST" \
    --header "Accept: application/json" \
    --header "Authorization: Bearer ${PORTAL_TOKEN}" \
    --header "Content-Type: application/json" \
    --data "$(
      jq --null-input --raw-output \
        --arg emailAddress "${email_address}" \
        --arg sopId "${SOP_ID}" \
        --arg sopVersion "${SOP_VERSION}" \
        --arg comment "${COMMENT}" \
        '
          {
            "text": "Pipeline executed manually via SOP \($sopId)/\($sopVersion) -- \($comment)",
            "createdBy": $emailAddress
          }
        '
    )" \
    --url "https://workflow.$(get_hostname_from_ssm)/api/v1/workflowrun/${workflow_run_orcabus_id}/comment/"
}

# Get args
while [[ $# -gt 0 ]]; do
  case "$1" in
    # Help
    -h|--help)
      print_usage
      exit 0
      ;;
    # Comment
    -c|--comment)
      COMMENT="$2"
      shift 2
      ;;
    -c=*|--comment=*)
      COMMENT="${1#*=}"
      shift
      ;;
    # Force boolean
    -f|--force)
      FORCE=true
      shift
      ;;
    # Output URI prefix
    -o|--output-uri-prefix)
      OUTPUT_URI_PREFIX="$2"
      shift 2
      ;;
    -o=*|--output-uri-prefix=*)
      OUTPUT_URI_PREFIX="${1#*=}"
      shift
      ;;
    # Log URI prefix
    -l|--logs-uri-prefix)
      LOGS_URI_PREFIX="$2"
      shift 2
      ;;
    -l=*|--logs-uri-prefix=*)
      LOGS_URI_PREFIX="${1#*=}"
      shift
      ;;
    # Cache URI prefix
    -t|--cache-uri-prefix)
      CACHE_URI_PREFIX="$2"
      shift 2
      ;;
    -t=*|--cache-uri-prefix=*)
      CACHE_URI_PREFIX="${1#*=}"
      shift
      ;;
    # Project ID
    -p|--project-id)
      PROJECT_ID="$2"
      shift 2
      ;;
    -p=*|--project-id=*)
      PROJECT_ID="${1#*=}"
      shift
      ;;
    # Analysis Storage Size
    -s|--analysis-storage-size)
      ANALYSIS_STORAGE_SIZE="$2"
      shift 2
      ;;
    -s=*|--analysis-storage-size=*)
      ANALYSIS_STORAGE_SIZE="${1#*=}"
      shift
      ;;
    # Save draft payload to file
    --save-draft-payload)
      SAVE_DRAFT_PAYLOAD="$2"
      shift 2
      ;;
    --save-draft-payload=*)
      SAVE_DRAFT_PAYLOAD="${1#*=}"
      shift
      ;;
    # Workflow version
    --workflow-version)
      WORKFLOW_VERSION="$2"
      shift 2
      ;;
    --workflow-version=*)
      WORKFLOW_VERSION="${1#*=}"
      shift
      ;;
    # Code version
    --code-version)
      CODE_VERSION="$2"
      shift 2
      ;;
    --code-version=*)
      CODE_VERSION="${1#*=}"
      shift
      ;;
    # Positional arguments (library IDs)
    *)
      LIBRARY_ID_ARRAY+=("$1")
      shift
      ;;
  esac
done

# Check required environment variables
if [[ -z "${PORTAL_TOKEN:-}" ]]; then
  echo_stderr "Error: PORTAL_TOKEN environment variable is not set. Exiting."
  print_usage
  exit 1
fi

# Check comment is provided
if [[ -z "${COMMENT}" ]]; then
  echo_stderr "Error: Comment is required. Please provide a comment using the -c or --comment flag. Exiting."
  print_usage
  exit 1
fi

# Check save draft file path is valid if provided
if [[ -n "${SAVE_DRAFT_PAYLOAD}" ]]; then
  # Check parent directory exists
  if [[ ! -d "$(dirname "${SAVE_DRAFT_PAYLOAD}")" ]]; then
    echo_stderr "Error: The parent directory for the file path provided for --save-draft-payload '${SAVE_DRAFT_PAYLOAD}' does not exist."
    echo_stderr "       Please provide a valid file path with an existing parent directory. Exiting."
    exit 1
  fi
  if [[ -e "${SAVE_DRAFT_PAYLOAD}" ]]; then
    echo_stderr "Error: The file path provided for --save-draft-payload already exists. "
    echo_stderr "       Please provide a file path that does not already exist to avoid overwriting. Exiting."
    exit 1
  fi
fi

# Check AWS CLI configuration
if ! aws sts get-caller-identity --output json > /dev/null 2>&1; then
  echo_stderr "Error: AWS CLI is not configured properly. Please configure your AWS CLI with appropriate credentials and region. Exiting."
  exit 1
fi

# Set hostname
HOSTNAME="$(get_hostname_from_ssm)"

# Check script version
compare_script_version_to_repo

# Check that we're running bash and it's version 4 or higher before declaring associative arrays
if [[ ! -v BASH_VERSION || "${BASH_VERSINFO[0]}" -lt 4 ]]; then
  echo_stderr "Error! This script is not being run with bash, or bash version is less than 4.0. Exiting"
  print_usage
  exit 1
fi

# SCRIPT BINARY VERSION MIN REQUIREMENTS
declare -A MIN_REQUIREMENTS=(
  ["jq"]="1.7.0"     # For if without else options
  ["aws"]="2.0.0"    # Because what are you doing still on V1?
  ["curl"]="7.76.0"  # For --fail-with-body option
)
if ! check_binaries; then
  echo_stderr "Error: One or more required binaries are not installed. Please install the required binaries and try again. Exiting."
  print_usage
  exit 1
fi

# AWS Account ID by prefix
declare -A PREFIX_BY_AWS_ACCOUNT_ID=(
  ["843407916570"]="dev"
  ["455634345446"]="stg"
  ["472057503814"]="prod"
)
declare -A COGNITO_USER_POOL_ID_BY_PREFIX=(
  ["ap-southeast-2_iWOHnsurL"]="dev"
  ["ap-southeast-2_wWDrdTyzP"]="stg"
  ["ap-southeast-2_HFrQ3aWm8"]="prod"
)

# Confirm that the aws account id associated with the credentials
# Matches the cognito user pool id associated with the portal token,
# to help catch users who have multiple AWS profiles configured and are using the wrong one
if [[ "$(get_aws_account_prefix)" != "$(get_cognito_user_pool_id_prefix)" ]]; then
  echo_stderr "Warning: The AWS account prefix associated with your AWS credentials ($(get_aws_account_prefix)) "
  echo_stderr "         does not match the expected prefix for the portal token you provided ($(get_cognito_user_pool_id_prefix))."
  echo_stderr "         This may cause API calls to fail due to authentication issues."
  echo_stderr "         Please check that you are using the correct AWS profile and that your portal token is valid."
fi

# Get email address upfront
if ! email_address="$(get_email_from_portal_token)"; then
  echo_stderr "Error: Failed to extract email address from portal token."
  echo_stderr "       The comment will not be created. Please check that your PORTAL_TOKEN is valid."
  exit 1
fi

# Generate the portal run id
portal_run_id="$(generate_portal_run_id)"
echo_stderr "Generated Portal Run ID: ${portal_run_id}"

# Get the workflow object
workflow="$( \
  get_workflow \
    "${WORKFLOW_NAME}" "${WORKFLOW_VERSION}" \
    "${EXECUTION_ENGINE}" "${CODE_VERSION}"
)"
echo_stderr "Using workflow: $(jq --raw-output '.orcabusId' <<< "${workflow}")"

# Collecting relevant libraries
echo_stderr "Collecting libraries from metadata manager"
libraries="$(get_linked_libraries)"
# libraries are a list of objects with libraryId and orcabusId fields
# Ensure no object in the list is empty
if [[ -z "${libraries}" || "$(jq 'length' <<< "${libraries}")" == 0 ]]; then
  echo_stderr "Error: No valid libraries found for the provided library IDs. Exiting."
  exit 1
# Check length of libraries matches length of library id array, to catch cases where some library ids were invalid
elif [[ "$(jq 'length' <<< "${libraries}")" -ne "${#LIBRARY_ID_ARRAY[@]}" ]]; then
  echo_stderr "Error: One or more library IDs provided are invalid and did not return a library object."
  echo_stderr "       Please check the provided library IDs. Exiting."
  exit 1
# Check that none of the library objects have null libraryId or orcabusId,
# which would indicate an invalid library object was returned for a valid library id
elif [[ "$(jq 'map(select(.libraryId == null or .orcabusId == null)) | length' <<< "${libraries}")" -gt 0 ]]; then
  echo_stderr "Error: One or more library objects are null. Please check the provided library IDs. Exiting."
  exit 1
# Check that there's at least two linked libraries as we only take tumor/normal inputs
elif [[ "$(jq 'length' <<< "${libraries}")" -lt 2 ]]; then
  echo_stderr "Error: Less than 2 linked libraries found for the provided library IDs. At least a tumor and normal library are required. Exiting."
  exit 1
else
  echo_stderr "Found $(jq 'length' <<< "${libraries}") linked libraries"
fi

# Get the engine parameters
echo_stderr "Generating engine parameters"
engine_parameters=$( \
  jq --null-input --raw-output --compact-output \
    --arg outputUriPrefix "${OUTPUT_URI_PREFIX}" \
    --arg logsUriPrefix "${LOGS_URI_PREFIX}" \
    --arg cacheUriPrefix "${CACHE_URI_PREFIX}" \
    --arg projectId "${PROJECT_ID}" \
    --arg portalRunId "${portal_run_id}" \
    --arg analysisStorageSize "${ANALYSIS_STORAGE_SIZE}" \
    '
      # Get the engine parameters
      {
        "outputUri": ( if $outputUriPrefix != "" then ($outputUriPrefix + $portalRunId + "/") else "" end ),
        "logsUri": ( if $logsUriPrefix != "" then ($logsUriPrefix + $portalRunId + "/") else "" end ),
        "cacheUri": ( if $cacheUriPrefix != "" then ($cacheUriPrefix + $portalRunId + "/") else "" end ),
        "projectId": $projectId,
        "analysisStorageSize": $analysisStorageSize
      } |
      # Remove empty values
      with_entries(select(.value != ""))
    ' \
)

# Generate the event
lambda_payload="$( \
  jq --null-input --raw-output \
    --argjson workflow "${workflow}" \
    --arg payloadVersion "${PAYLOAD_VERSION}" \
    --arg portalRunId "${portal_run_id}" \
    --argjson libraries "${libraries}" \
    --argjson engineParameters "${engine_parameters}" \
    '
    {
      "status": "DRAFT",
      "timestamp": (now | todateiso8601),
      "workflow": $workflow,
      "workflowRunName": ("umccr--manual--" + $workflow["name"] + "--" + ($workflow["version"] | gsub("\\."; "-")) + "--" + $portalRunId),
      "portalRunId": $portalRunId,
      "libraries": $libraries,
      } |
      if ( ($engineParameters | length) > 0 ) then
        .["payload"] = {
          "version": $payloadVersion,
          "data": {
            "engineParameters": $engineParameters
          }
        }
      end
    ' \
)"

# Confirm before pushing the event
echo_stderr "Send the following payload to the lambda object:"
jq --raw-output <<< "${lambda_payload}" 1>&2
if [[ "${FORCE}" == "false" ]]; then
    read -r -p 'Confirm to push this event to EventBridge? (y/n): ' confirm_push
    if [[ ! "${confirm_push}" =~ ^[Yy]$ ]]; then
      echo_stderr "Aborting event push."
      exit 1
    fi
fi

# Saving the draft event to a local file if the --save-draft-payload flag is provided, for record purposes
if [[ -n "${SAVE_DRAFT_PAYLOAD}" ]]; then
  echo_stderr "Saving the generated draft event to ${SAVE_DRAFT_PAYLOAD}"
  jq --raw-output <<< "${lambda_payload}" > "${SAVE_DRAFT_PAYLOAD}"
fi

# Set the trap
trap 'rm -rf "${LAMBDA_TMP_DIR:-}"' EXIT

# Push the event to EventBridge
LAMBDA_TMP_DIR="$(mktemp -d "LAMBDA_TMP_DIR_XXXXXX")"
LAMBDA_DATA_PIPE="${LAMBDA_TMP_DIR}/lambda_data_pipe"
mkfifo "${LAMBDA_DATA_PIPE}"
errors_json="$(mktemp -p "${LAMBDA_TMP_DIR}" "errors.XXXXXX.json")"
echo_stderr "Pushing the draft event for portalRunId ${portal_run_id} via WRU Validation Lambda Function"
aws lambda invoke \
  --function-name "$(get_lambda_function_name)" \
  --payload "$(jq --compact-output <<< "${lambda_payload}")" \
  --cli-binary-format raw-in-base64-out \
  --no-cli-pager \
  --invocation-type 'RequestResponse' \
  "${LAMBDA_DATA_PIPE}" 1>/dev/null & \
jq --raw-output \
  '
  if .statusCode != 200 then
    .body | fromjson
  else
    empty
  end
  ' \
  < "${LAMBDA_DATA_PIPE}" \
  > "${errors_json}" & \
wait

# Check for errors from the Lambda invocation
if [[ -s "${errors_json}" ]]; then
  echo_stderr "Error pushing event to Lambda Function:"
  jq --raw-output '.' < "${errors_json}" 1>&2
  rm -rf "${LAMBDA_TMP_DIR}"
  exit 1
else
  rm -rf "${LAMBDA_TMP_DIR}"
fi

# Remove trap
trap - EXIT

# Now wait for the workflow run to be registered by the workflow manager,
# which should be done within a minute or two after pushing the event to EventBridge,
# and get the workflow run object, which contains the Orcabus ID that we will use to link the
# workflow run to the comment we will create in the next step
echo_stderr "Waiting for the workflow run to be registered by the workflow manager"

max_attempts=6  # 1 minute with 10-second intervals
attempts=0
while :; do
  # Check if we've exceeded max attempts
  if [[ "${attempts}" -ge "${max_attempts}" ]]; then
    echo_stderr "Exceeded maximum attempts (${max_attempts}) to check for workflow run registration"
    exit 1
  fi

  workflow_run_object="$( \
    get_workflow_run "${portal_run_id}"
  )"

  # Check with the workflow manager for the workflow run object
  if [[ -n "${workflow_run_object}" ]]; then
    workflow_run_orcabus_id="$(jq --raw-output '.orcabusId' <<< "${workflow_run_object}")"
    echo_stderr "Workflow run registered with ID: ${workflow_run_orcabus_id}"
    break
  else
    echo_stderr "Workflow run not yet registered, waiting 10 seconds..."
    sleep 10
    attempts="$((attempts + 1))"
  fi
done

echo_stderr "Generating workflow comment"
if ! comment_response="$(generate_workflow_comment "${workflow_run_orcabus_id}" "${email_address}")"; then
  echo_stderr "Warning: Failed to generate comment on workflow run."
  echo_stderr "         Please check that your PORTAL_TOKEN is valid and has permission to comment on the workflow run. "
  echo_stderr "         And contact the script author if the issue persists. The workflow run has been created successfully "
  echo_stderr "         but the comment indicating who created the workflow run and why will be missing."
  if parsed_error="$(jq -rc 2>/dev/null <<< "${comment_response}")"; then
    echo_stderr "         Error details: ${parsed_error}"
  else
    echo_stderr "         Error details (unparsed): ${comment_response}"
  fi
fi

echo_stderr "Workflow Run Creation Event complete!"
echo_stderr "Please head to 'https://orcaui.$(get_hostname_from_ssm)/runs/workflow/${workflow_run_orcabus_id}' to track the status of the workflow run"
