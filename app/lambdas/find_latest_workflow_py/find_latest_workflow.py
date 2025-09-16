#!/usr/bin/env python3

"""
Given an upstream portal run id,
find the draft workflow object for sash

"""
# Standard imports
from typing import List

# Local imports
from orcabus_api_tools.workflow import (
    get_workflow_run,
    get_workflows_from_library_id_list
)
from orcabus_api_tools.workflow.models import WorkflowRunDetail
from orcabus_api_tools.workflow import get_workflows_from_analysis_run_id


def handler(event, context):
    """
    Get the latest payload from the portal run id
    :param event:
    :param context:
    :return:
    """
    # Get the upstream events

    # Get the workflow type, name is mandatory
    workflow_name = event['workflowName']
    workflow_version = event.get('workflowVersion', None)

    # Workflow state
    workflow_status = event.get('status', None)

    # Get the libraries / and/or the analysis run id
    # The analysis run id takes preference when making queries
    analysis_run_id = event.get('analysisRunId', None)
    libraries = event.get('libraries', None)

    # Check not both analysis run id and libraries are None
    if analysis_run_id is None and libraries is None:
        raise ValueError("Either analysisRunId or libraries must be provided")

    workflows_list: List[WorkflowRunDetail]
    if analysis_run_id is not None:
        workflows_list = get_workflows_from_analysis_run_id(
            analysis_run_id=analysis_run_id
        )
    else:
        # Get workflow intersection list
        workflows_list = get_workflows_from_library_id_list(
            library_id_list=list(map(
                lambda library_iter_: library_iter_['libraryId'],
                libraries
            )
        ))

    # Now we have our workflows, filter to the correct workflow name (and version if provided)
    workflows_list = list(filter(
        lambda workflow_iter_: get_workflow_run(workflow_iter_['orcabusId'])['workflow']['name'] == workflow_name,
        workflows_list
    ))

    # Filter to workflow version if provided
    if workflow_version is not None:
        workflows_list = list(filter(
            lambda workflow_iter_: get_workflow_run(workflow_iter_['orcabusId'])['workflow']['version'] == workflow_version,
            workflows_list
        ))

    # Filter to workflow state if provided
    if workflow_status is not None:
        workflows_list = list(filter(
            lambda workflow_iter_: workflow_iter_['currentState']['status'] == workflow_status,
            workflows_list
        ))

    if len(workflows_list) == 0:
        return {
            "workflowRunObject": None
        }

    # Get the latest draft workflow for the given workflow name
    return {
        "workflowRunObject": sorted(
            workflows_list,
            key=lambda workflow_iter_: workflow_iter_['orcabusId'],
            reverse=True
        )[0]
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
#                 "status": "SUCCEEDED"
#             },
#             None
#         ),
#         indent=4
#     ))
