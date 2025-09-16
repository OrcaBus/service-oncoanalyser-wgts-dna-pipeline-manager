#!/usr/bin/env python3

"""
Get the workflow run object
"""

# Standard library imports
from typing import Dict

# Layer imports
from orcabus_api_tools.workflow import get_workflow_run_from_portal_run_id
from orcabus_api_tools.workflow.models import WorkflowRunDetail


def handler(event, context) -> Dict[str, WorkflowRunDetail]:
    """
    Given a portal run id, return the workflow run object
    :param event:
    :param context:
    :return:
    """
    # Get the portal run id object
    portal_run_id = event['portalRunId']

    return {
        "workflowRunObject": get_workflow_run_from_portal_run_id(portal_run_id)
    }
