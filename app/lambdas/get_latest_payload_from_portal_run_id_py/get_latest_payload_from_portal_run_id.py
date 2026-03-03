#!/usr/bin/env python3

"""
Get the dragen wgts dna succeeded event object
"""

# Layer imports
from orcabus_api_tools.workflow import get_latest_payload_from_portal_run_id


def handler(event, context):
    """
    Get the workflow run object
    :param event:
    :param context:
    :return:
    """
    # Get the portal run id from the event object
    portal_run_id = event['portalRunId']

    # Get the workflow run object
    workflow_payload = get_latest_payload_from_portal_run_id(portal_run_id)

    # Return the workflow payload object
    return {
        "payload": workflow_payload
    }
