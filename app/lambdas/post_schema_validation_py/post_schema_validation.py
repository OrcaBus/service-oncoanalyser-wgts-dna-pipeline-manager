#!/usr/bin/env python3

"""
Post schema validation for oncoanalyser wgts dna workflows

Performs the following steps:
* Validate engine parameters:
  - Confirm projectId resolves to a valid ICAv2 project
  - Confirm outputUri starts with the project's S3 key prefix
  - Confirm logsUri starts with the project's S3 key prefix
  - Confirm cacheUri starts with the project's S3 key prefix
  - Confirm outputUri ends with /<analysis-midfix>/<workflow-name>/<portal-run-id>/
  - Confirm logsUri ends with /logs/<workflow-name>/<portal-run-id>/
  - Confirm pipelineId is accessible in the specified projectId
* Validate inputs:
  - Confirm ALL input URIs exist via Filemanager (files and folders)
  - For URIs not in reference/test/project-prefix: validate linked to project via ICA API
* On failure: write descriptive comments to workflow run record, return {"isValid": false}
* On success: return {"isValid": true}
"""
# Imports
from pathlib import Path
from typing import Dict, Tuple, cast, List
import logging
from os import environ
from time import sleep
from urllib.parse import urlparse

# Wrapica imports
from libica.openapi.v3 import ApiException
from wrapica.project_data import coerce_data_id_or_uri_to_project_data_obj, get_project_data_obj_by_id
from wrapica.storage_configuration import get_s3_key_prefix_by_project_id
from wrapica.project_pipelines import get_project_pipeline_obj
from wrapica.project import get_project_obj_from_project_id

# Layer imports
from orcabus_api_tools.workflow import add_comment_to_workflow_run, get_workflow_run
from orcabus_api_tools.filemanager import get_s3_object_id_from_s3_uri, list_files_recursively
from orcabus_api_tools.filemanager.errors import S3FileNotFoundError
from icav2_tools import set_icav2_env_vars

# Globals
WORKFLOW_NAME_ENV_VAR = "WORKFLOW_NAME"
TEST_BUCKET_ENV_VAR = "TEST_DATA_BUCKET_NAME"
REF_DATA_BUCKET_ENV_VAR = "REF_DATA_BUCKET_NAME"
# Get test / ref env var values
TEST_BUCKET = environ[TEST_BUCKET_ENV_VAR]
REF_DATA_BUCKET = environ[REF_DATA_BUCKET_ENV_VAR]
# Get workflow env vars as values
WORKFLOW_NAME = environ[WORKFLOW_NAME_ENV_VAR]
COMMENT_AUTHOR = f"{WORKFLOW_NAME}-workflow-validation-service"
# Midfixes
ANALYSIS_MIDFIXES = ["analysis", "output", "outputs"]
LOGS_MIDFIX = "logs"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Comment formatting constants
MAX_COMMENT_LENGTH = 1024
TRUNCATION_SUFFIX = "\n... [truncated, see execution ARN for full detail]"


def _format_comment_with_arn(body: str, execution_arn: str) -> str:
    """
    Append the execution ARN footer to a comment and enforce the 1024 char limit.
    """
    footer = f"---\nStep Functions Execution: {execution_arn}"
    full_comment = f"{body}\n{footer}"

    if len(full_comment) > MAX_COMMENT_LENGTH:
        available = MAX_COMMENT_LENGTH - len(footer) - len(TRUNCATION_SUFFIX) - 1
        full_comment = f"{body[:available]}{TRUNCATION_SUFFIX}\n{footer}"

    return full_comment


def validate_engine_parameters(
        engine_parameters: Dict,
        workflow_run_id: str,
        project_prefix: str
) -> Tuple[bool, List[str]]:
    """
    Validate the engine parameters.
    :param engine_parameters: The engine parameters to validate.
    :param workflow_run_id: The workflow run ID
    :param project_prefix: The project prefix
    :return: A tuple of (is_valid, list of failure comments)
    """
    failures: List[str] = []

    # Get the project id
    project_id = engine_parameters.get("projectId")

    # Assert project id is set and resolves to a valid ICAv2 project
    if project_id is None:
        failures.append("projectId is not set")
        return False, failures
    try:
        get_project_obj_from_project_id(project_id)
    except ApiException:
        failures.append(f"Cannot find project id {project_id}")
        return False, failures

    # Get URIs
    output_uri = engine_parameters.get("outputUri", "")
    logs_uri = engine_parameters.get("logsUri", "")
    cache_uri = engine_parameters.get("cacheUri", "")
    pipeline_id = engine_parameters.get("pipelineId", "")

    # Validate the URIs start with the project prefix
    if not output_uri.startswith(project_prefix):
        failures.append(f"outputUri '{output_uri}' is not in the project context '{project_prefix}'")
    if not logs_uri.startswith(project_prefix):
        failures.append(f"logsUri '{logs_uri}' is not in the project context '{project_prefix}'")
    if cache_uri and not cache_uri.startswith(project_prefix):
        failures.append(f"cacheUri '{cache_uri}' is not in the project context '{project_prefix}'")

    # Get the portal run id from the workflow run id
    portal_run_id = get_workflow_run(workflow_run_id)['portalRunId']

    # Validate outputUri ends with /<analysis-midfix>/<workflow-name>/<portal-run-id>/
    output_uri_valid = any(
        output_uri.endswith(f"/{midfix}/{WORKFLOW_NAME}/{portal_run_id}/")
        for midfix in ANALYSIS_MIDFIXES
    )
    if not output_uri_valid:
        valid_suffixes = ", ".join(
            f"/{midfix}/{WORKFLOW_NAME}/{portal_run_id}/" for midfix in ANALYSIS_MIDFIXES
        )
        failures.append(
            f"outputUri '{output_uri}' does not end with a valid suffix. "
            f"Expected one of: {valid_suffixes}"
        )

    # Validate logsUri ends with /logs/<workflow-name>/<portal-run-id>/
    if not logs_uri.endswith(f"/{LOGS_MIDFIX}/{WORKFLOW_NAME}/{portal_run_id}/"):
        failures.append(
            f"logsUri '{logs_uri}' does not end with '/{LOGS_MIDFIX}/{WORKFLOW_NAME}/{portal_run_id}/'"
        )

    # Confirm the pipeline is accessible in the project
    try:
        _ = get_project_pipeline_obj(
            project_id=project_id,
            pipeline_id=pipeline_id,
        )
    except ValueError:
        failures.append(f"The pipeline {pipeline_id} cannot be found in the project {project_id}")

    if failures:
        return False, failures
    return True, []


def validate_inputs(
        inputs: Dict,
        project_id: str,
        project_prefix: str,
) -> Tuple[bool, List[str]]:
    """
    Validate the inputs.

    Performs two-phase validation:
    1. Filemanager existence check — confirms file/folder URIs exist at the S3 level
       (excludes reference data bucket URIs since they are not indexed by the Filemanager)
    2. ICA project context check — confirms URIs outside of ref/test/project-prefix
       are linked to the project

    :param inputs: The inputs to validate.
    :param project_id: The ICAv2 project id to validate against.
    :param project_prefix: The ICAv2 project prefix
    :return: A tuple of (is_valid, list of failure comments)
    """
    failures: List[str] = []

    # Get all data URIs from the inputs
    data_uris: List[str] = []

    # BAM inputs (from alignment data path)
    for key in ["tumorDnaBamUri", "normalDnaBamUri"]:
        uri = inputs.get(key)
        if uri:
            data_uris.append(uri)

    # FASTQ inputs (from fastq data path)
    for fastq_key in ["normalFastqListRows", "tumorFastqListRows"]:
        for fastq_obj in inputs.get(fastq_key, []):
            read1 = fastq_obj.get("read1FileUri")
            read2 = fastq_obj.get("read2FileUri")
            if read1:
                data_uris.append(read1)
            if read2:
                data_uris.append(read2)

    # Reference data inputs
    # refDataHmfDataPath is a directory URI
    ref_data_hmf = inputs.get("refDataHmfDataPath")
    if ref_data_hmf:
        data_uris.append(ref_data_hmf)

    # Genome references
    genomes = inputs.get("genomes", {})
    for genome_name, genome_data in genomes.items():
        if isinstance(genome_data, dict):
            for ref_key, ref_val in genome_data.items():
                if isinstance(ref_val, str) and ref_val.startswith("s3://"):
                    data_uris.append(ref_val)

    # Remove duplicates while preserving order
    seen = set()
    unique_uris = []
    for uri in data_uris:
        if uri not in seen:
            seen.add(uri)
            unique_uris.append(uri)
    data_uris = unique_uris

    # Phase 1: Filemanager existence check — ALL URIs except refdata bucket
    non_reference_data_uris = list(filter(
        lambda uri: not uri.startswith(f"s3://{REF_DATA_BUCKET}/"),
        data_uris
    ))
    for data_uri in non_reference_data_uris:
        # Check if it's a folder URI (ends with /)
        if data_uri.endswith("/"):
            # For folder URIs, verify at least 1 file exists under that prefix
            parsed = urlparse(data_uri)
            bucket = parsed.netloc
            prefix = str(Path(parsed.path)) + "/"
            files = list_files_recursively(bucket, prefix)
            if not (len(files) > 0):
                failures.append(
                    f"Folder URI '{data_uri}' has no files found under that prefix in the Filemanager"
                )
        else:
            # For file URIs, confirm the file exists
            try:
                get_s3_object_id_from_s3_uri(data_uri)
            except S3FileNotFoundError:
                failures.append(
                    f"Data URI '{data_uri}' cannot be found by the Filemanager, are you sure it exists?"
                )

    # If Filemanager checks failed, return early
    if failures:
        return False, failures

    # Phase 2: ICA project context validation
    # Only URIs outside ref/test/project-prefix need ICA project linking confirmed
    uris_to_validate = [
        uri for uri in data_uris
        if not (
                uri.startswith(f"s3://{REF_DATA_BUCKET}/") or
                uri.startswith(f"s3://{TEST_BUCKET}/") or
                uri.startswith(project_prefix)
        )
    ]

    # Validate each URI is accessible in the project context
    for data_uri in uris_to_validate:
        # Try get the icav2 object by uri
        try:
            project_data_obj = coerce_data_id_or_uri_to_project_data_obj(
                data_id_or_uri=data_uri,
            )
        except ValueError:
            failures.append(f"Data URI '{data_uri}' cannot be found in the project context '{project_id}'")
            continue

        # Then try get it in this context
        try:
            get_project_data_obj_by_id(
                project_id=project_id,
                data_id=project_data_obj.data.id
            )
        except ApiException:
            failures.append(f"Data URI '{data_uri}' cannot be found in the project context '{project_id}'")

    if failures:
        return False, failures
    return True, []


def handler(event, context) -> Dict[str, bool]:
    """
    Given a draft schema, validate it against the current schema and print the results.

    Input:
      {
        "workflowRunId": "wfr.xxx",
        "executionArn": "arn:aws:states:...",
        "data": {
          "engineParameters": {
            "projectId": "...",
            "pipelineId": "...",
            "outputUri": "s3://...",
            "logsUri": "s3://...",
            "cacheUri": "s3://..."
          },
          "inputs": { ... },
          "tags": { ... }
        }
      }

    Output:
      {"isValid": true}   — all checks pass
      {"isValid": false}  — at least one check failed (comment written)
    """
    # Set env vars for ICAv2 access
    set_icav2_env_vars()

    # Get the event data
    payload_data = event.get('data')
    workflow_run_id = event.get("workflowRunId", "")
    execution_arn = event.get("executionArn", "")

    # Get the ICAv2 project id from the event
    engine_parameters = payload_data.get("engineParameters", {})

    # Get the project prefix
    project_id = engine_parameters.get("projectId")
    if project_id is None:
        # Write failure comment
        add_comment_to_workflow_run(
            workflow_run_orcabus_id=workflow_run_id,
            comment=_format_comment_with_arn(
                "Post schema validation failed: projectId is not set",
                execution_arn
            ),
            author=COMMENT_AUTHOR
        )
        return {"isValid": False}

    project_prefix = cast(str, get_s3_key_prefix_by_project_id(project_id))

    # Collect all failures
    all_failures: List[str] = []

    # Validate the engine parameters
    is_valid, failures = validate_engine_parameters(
        engine_parameters,
        workflow_run_id=workflow_run_id,
        project_prefix=project_prefix,
    )
    all_failures.extend(failures)

    # Validate the inputs (only if engine params are valid — we need project context)
    if is_valid:
        inputs = payload_data.get("inputs", {})
        is_valid, failures = validate_inputs(
            inputs,
            project_id=project_id,
            project_prefix=project_prefix,
        )
        all_failures.extend(failures)

    # Write failure comments
    if all_failures:
        if len(all_failures) == 1:
            add_comment_to_workflow_run(
                workflow_run_orcabus_id=workflow_run_id,
                comment=_format_comment_with_arn(
                    f"Post schema validation failed: {all_failures[0]}",
                    execution_arn
                ),
                author=COMMENT_AUTHOR
            )
        else:
            # Write a summary comment
            add_comment_to_workflow_run(
                workflow_run_orcabus_id=workflow_run_id,
                comment=_format_comment_with_arn(
                    f"Post schema validation failed for {len(all_failures)} reasons",
                    execution_arn
                ),
                author=COMMENT_AUTHOR
            )
            # Write each failure as a separate numbered comment
            for idx, failure in enumerate(all_failures, start=1):
                add_comment_to_workflow_run(
                    workflow_run_orcabus_id=workflow_run_id,
                    comment=_format_comment_with_arn(
                        f"Reason {idx} of {len(all_failures)}: {failure}",
                        execution_arn
                    ),
                    author=COMMENT_AUTHOR
                )
                sleep(1)

        return {"isValid": False}

    return {"isValid": True}
