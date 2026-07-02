#!/usr/bin/env python3

"""
Given workflow search criteria (libraries, analysisRunId, workflow name/version/status),
find matching workflow runs from the Workflow Manager API.

Used by:
- glueSucceededEventsToDraftUpdate: finding existing DRAFT runs for this service to update
- populateDraftData: finding upstream SUCCEEDED workflows to collect outputs as inputs

"""
# Standard imports
from typing import List

# Local imports
from orcabus_api_tools.workflow import (
    get_workflow_runs_from_metadata
)
from orcabus_api_tools.workflow.models import WorkflowRunDetail

# Globals
# Terminal states that indicate a run has been superseded or is no longer relevant
NON_SUCCEEDED_TERMINATED_STATUS_LIST = [
    'FAILED',
    'ABORTED',
    'RESOLVED'
]


def handler(event, context):
    """
    Query the Workflow Manager API for workflow runs matching the given criteria.

    Input:
      {
        "workflowName": "oncoanalyser-wgts-dna",   # Required
        "workflowVersion": "1.0.0",                # Optional
        "status": "DRAFT" | "SUCCEEDED" | ...,     # Optional
        "libraries": [{"libraryId": "L1234"}],     # Conditional (required if no analysisRunId)
        "analysisRunId": "anr.xxx",                # Conditional (required if no libraries)
        "rgidList": ["RGID1", "RGID2"]             # Optional
      }

    Output:
      {"workflowRunList": [...]}  — sorted by orcabusId descending (most recent first)
      {"workflowRunList": []}     — if no match or newer run supersedes

    DRAFT Deduplication Logic:
      When status=SUCCEEDED and multiple runs are found, check if the most recent run
      (by currentState.orcabusId) is still in-progress (not SUCCEEDED and not in a
      terminal state like FAILED/ABORTED/RESOLVED). If so, return empty list — the
      newer run supersedes the succeeded one.

    :param event: Input event with search criteria
    :param context: Lambda context (unused)
    :return: Dictionary with workflowRunList
    """

    # Get the workflow type, name is mandatory
    workflow_name = event['workflowName']
    workflow_version = event.get('workflowVersion', None)

    # Workflow state
    workflow_status = event.get('status', None)

    # Get the libraries / and/or the analysis run id
    # The analysis run id takes preference when making queries
    analysis_run_id = event.get('analysisRunId', None)
    libraries = event.get('libraries', [])
    rgid_list = event.get('rgidList', None)

    # Check not both analysis run id and libraries are empty/None
    if analysis_run_id is None and not libraries:
        raise ValueError("Either analysisRunId or libraries must be provided")

    # Build library_id_list from libraries input
    library_id_list = list(map(
        lambda library_iter_: library_iter_['libraryId'],
        libraries
    )) if libraries else []

    # Query the Workflow Manager API for matching workflow runs
    workflows_list: List[WorkflowRunDetail]
    workflows_list = get_workflow_runs_from_metadata(
        analysis_run_id=analysis_run_id,
        workflow_name=workflow_name,
        workflow_version=workflow_version,
        library_id_list=library_id_list,
        rgid_list=rgid_list
    )

    # Filter to workflow state if provided
    if workflow_status is not None:
        # DRAFT deduplication: when looking for SUCCEEDED runs,
        # check if a newer non-terminated run supersedes them
        if (
            workflow_status == 'SUCCEEDED' and
            len(workflows_list) > 1
        ):
            # First remove DEPRECATED / RESOLVED runs from the dedup consideration
            # since these are no longer relevant
            active_workflows = list(filter(
                lambda workflow_run_iter: workflow_run_iter['currentState']['status'] not in NON_SUCCEEDED_TERMINATED_STATUS_LIST,
                workflows_list
            ))

            if active_workflows:
                # Get the most recent run (by currentState.orcabusId which reflects the latest state change)
                recent_run_status = sorted(
                    active_workflows,
                    key=lambda workflow_iter_: workflow_iter_['currentState']['orcabusId'],
                    reverse=True
                )[0]['currentState']['status']

                if (
                    # Not the status we're looking for (SUCCEEDED) AND
                    recent_run_status != workflow_status and
                    # Not in a terminal state — meaning it's still in-progress
                    recent_run_status not in NON_SUCCEEDED_TERMINATED_STATUS_LIST
                ):
                    # A newer run is still in-progress, superseding the succeeded one
                    return {
                        "workflowRunList": []
                    }

        # Filter by the requested status
        workflows_list = list(filter(
            lambda workflow_iter_: workflow_iter_['currentState']['status'] == workflow_status,
            workflows_list
        ))

    if len(workflows_list) == 0:
        return {
            "workflowRunList": []
        }

    # Return results sorted by orcabusId descending (most recent first)
    return {
        "workflowRunList": sorted(
            workflows_list,
            key=lambda workflow_iter_: workflow_iter_['orcabusId'],
            reverse=True
        )
    }


# if __name__ == "__main__":
#     import json
#     from os import environ
#     environ['AWS_PROFILE'] = 'umccr-development'
#     environ['HOSTNAME_SSM_PARAMETER_NAME'] = '/hosted_zone/umccr/name'
#     environ['ORCABUS_TOKEN_SECRET_ID'] = 'orcabus/token-service-jwt'
#     print(json.dumps(
#         handler(
#             {
#                 "workflowName": "dragen-wgts-dna",
#                 "libraries": [
#                     {
#                         "libraryId": "L2300950",
#                         "orcabusId": "lib.01J9T6AV2XJWBDJ42VAK6RB1XK",
#                         "readsets": [
#                             {
#                                 "orcabusId": "fqr.01JN25MRV2622KBD073XGKVYQP",
#                                 "rgid": "GGCATTCT+CAAGCTAG.2.230629_A01052_0154_BH7WF5DSX7"
#                             }
#                         ]
#                     },
#                     {
#                         "libraryId": "L2300943",
#                         "orcabusId": "lib.01J9T6ATSB40216793T4DJ7AWD",
#                         "readsets": [
#                             {
#                                 "orcabusId": "fqr.01JN25MKYXVYJD30VZVJCP6407",
#                                 "rgid": "ACTAAGAT+CCGCGGTT.4.230602_A00130_0258_BH55TMDSX7"
#                             },
#                             {
#                                 "orcabusId": "fqr.01JN25MM0R858AXWJKT5E1W270",
#                                 "rgid": "ACTAAGAT+CCGCGGTT.3.230602_A00130_0258_BH55TMDSX7"
#                             }
#                         ]
#                     }
#                 ],
#                 "status": "SUCCEEDED"
#             },
#             None
#         ),
#         indent=4
#     ))


# if __name__ == "__main__":
#     import json
#     from os import environ
#     environ['AWS_PROFILE'] = 'umccr-development'
#     environ['HOSTNAME_SSM_PARAMETER_NAME'] = '/hosted_zone/umccr/name'
#     environ['ORCABUS_TOKEN_SECRET_ID'] = 'orcabus/token-service-jwt'
#     print(json.dumps(
#         handler(
#             {
#                 "workflowName": "oncoanalyser-wgts-dna",
#                 "libraries": [
#                     {
#                         "libraryId": "L2300950",
#                         "orcabusId": "lib.01J9T6AV2XJWBDJ42VAK6RB1XK",
#                         "readsets": [
#                             {
#                                 "orcabusId": "fqr.01JN25MRV2622KBD073XGKVYQP",
#                                 "rgid": "GGCATTCT+CAAGCTAG.2.230629_A01052_0154_BH7WF5DSX7"
#                             }
#                         ]
#                     },
#                     {
#                         "libraryId": "L2300943",
#                         "orcabusId": "lib.01J9T6ATSB40216793T4DJ7AWD",
#                         "readsets": [
#                             {
#                                 "orcabusId": "fqr.01JN25MKYXVYJD30VZVJCP6407",
#                                 "rgid": "ACTAAGAT+CCGCGGTT.4.230602_A00130_0258_BH55TMDSX7"
#                             },
#                             {
#                                 "orcabusId": "fqr.01JN25MM0R858AXWJKT5E1W270",
#                                 "rgid": "ACTAAGAT+CCGCGGTT.3.230602_A00130_0258_BH55TMDSX7"
#                             }
#                         ]
#                     }
#                 ],
#                 "analysisRunId": None,
#                 "status": "DRAFT"
#             },
#             None
#         ),
#         indent=4
#     ))
