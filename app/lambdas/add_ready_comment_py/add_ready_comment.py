#!/usr/bin/env python3

"""
Generate a workflow run comment when the readyEventToIcav2WesRequestEvent state machine starts.

Informs the user that the workflow run is transitioning from READY to SUBMITTED,
providing the Step Functions execution ARN for traceability.

For oncoanalyser-wgts-dna, when inputs come from FASTQ (tags.fromFastq is true),
the comment includes a decompression delay warning because ORA-to-FASTQ
decompression may introduce a delay between READY and SUBMITTED states.
"""

# Standard imports
from os import environ
from typing import Dict, Any

# Layer imports
from orcabus_api_tools.workflow import add_comment_to_workflow_run

# Globals
WORKFLOW_NAME_ENV_VAR = "WORKFLOW_NAME"
COMMENT_AUTHOR = "{workflow_name}-ready-to-icav2-wes-service"
MAX_COMMENT_LENGTH = 1024
TRUNCATION_SUFFIX = "\n... [truncated, see execution ARN for full detail]"


def handler(event: Dict[str, Any], context) -> Dict[str, bool]:
    """
    Add a comment to the workflow run indicating the READY-to-SUBMITTED transition has started.

    Event shape:
    {
        "workflowRunId": "<orcabus-id>",
        "executionArn": "<step-functions-execution-arn>",
        "includeOraDecompressionWarning": true | false  // optional
    }

    Returns:
    {
        "commentAdded": true
    }
    """
    workflow_run_id = event["workflowRunId"]
    execution_arn = event.get("executionArn", "")
    include_ora_warning = event.get("includeOraDecompressionWarning", False)

    workflow_name = environ.get(WORKFLOW_NAME_ENV_VAR, "unknown")
    author = COMMENT_AUTHOR.format(workflow_name=workflow_name)

    # Build comment body
    body = (
        "Submitting workflow run to ICAv2 — transitioning from READY to SUBMITTED."
    )

    if include_ora_warning:
        body += (
            "\nNote: There may be a delay between READY and SUBMITTED "
            "due to ORA-to-FASTQ decompression time."
        )

    footer = f"---\nStep Functions Execution: {execution_arn}"

    full_comment = f"{body}\n{footer}"

    # Enforce 1024 char limit
    if len(full_comment) > MAX_COMMENT_LENGTH:
        available = MAX_COMMENT_LENGTH - len(footer) - len(TRUNCATION_SUFFIX) - 1
        full_comment = f"{body[:available]}{TRUNCATION_SUFFIX}\n{footer}"

    add_comment_to_workflow_run(
        workflow_run_orcabus_id=workflow_run_id,
        comment=full_comment,
        author=author,
    )

    return {"commentAdded": True}
