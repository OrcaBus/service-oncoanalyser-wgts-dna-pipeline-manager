#!/usr/bin/env python3

"""
Given the outputs of an icav2 wes event, convert to a wrsc event

If the workflow has succeeded, we need to generate the dnaOncoanalyserAnalysisRelPath
which is just the groupId from the event inputs.
"""

# Standard imports
from copy import deepcopy
from datetime import datetime, timezone

# Layer helpers
from orcabus_api_tools.workflow import (
    get_latest_payload_from_workflow_run,
    get_workflow_run_from_portal_run_id
)


def handler(event, context):
    """
    Perform the following steps:
    1. Get portal run ID from ICAv2 WES Event Tags
    2. Look up workflow run / payload using the portal run ID
    3. Generate the WRSC Event payload based on the existing WRSC Event payload
    :param event:
    :param context:
    :return:
    """

    # ICAV2 WES State Change Event payload
    icav2_wes_event = event['icav2WesStateChangeEvent']

    # Get the portal run ID from the event tags
    portal_run_id = icav2_wes_event['tags']['portalRunId']

    # Get the workflow run using the portal run ID
    workflow_run = get_workflow_run_from_portal_run_id(portal_run_id)

    # Get the latest payload from the workflow run
    latest_payload = get_latest_payload_from_workflow_run(workflow_run['orcabusId'])

    # Check if the status was SUCCEEDED, if so we populate the 'outputs' data payload
    if icav2_wes_event['status'] == 'SUCCEEDED':
        # Get the workflow run inputs
        workflow_run_inputs = latest_payload['data']['inputs']
        # We want to generate the following output dict
        outputs = {
          "dnaOncoanalyserAnalysisRelPath": f"{workflow_run_inputs['groupId']}/",
        }
    else:
        outputs = None

    # Update the latest payload with the outputs if available
    if outputs:
        latest_payload['data']['outputs'] = outputs

    # Update the workflow object to contain 'name' and 'version'
    workflow = dict(deepcopy(workflow_run['workflow']))

    # Prepare the WRSC Event payload
    return {
        "workflowRunStateChangeEvent": {
            # New status
            "status": icav2_wes_event['status'],
            # Current time
            "timestamp": datetime.now(timezone.utc).isoformat(timespec='seconds').replace("+00:00", "Z"),
            # Portal Run ID
            "portalRunId": portal_run_id,
            # Workflow details
            "workflow": workflow,
            "workflowRunName": workflow_run['workflowRunName'],
            # Linked libraries in workflow run
            "libraries": workflow_run['libraries'],
            # Payload containing the original inputs and engine parameters
            # But with the updated outputs if available
            "payload": {
                "version": latest_payload['version'],
                "data": latest_payload['data']
            }
        }
    }
