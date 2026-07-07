#!/usr/bin/env python3

"""
Compare the payload of the original portal run id and that of the new object

We dont want to accidentally end up in an infinite loop, so we only want to push a WRU / WRSC event if
the payload has changed
"""

# Standard library imports
from deepdiff import DeepDiff

def handler(event, context):
    """
    Get the latest payload from the portal run id and compare it to the new object payload
    :param event:
    :param context:
    :return:
    """
    old_payload = event['oldPayload']
    new_payload = event['newPayload']

    if not DeepDiff(old_payload, new_payload):
        return {
            "hasChanged": False
        }
    return {
        "hasChanged": True
    }
