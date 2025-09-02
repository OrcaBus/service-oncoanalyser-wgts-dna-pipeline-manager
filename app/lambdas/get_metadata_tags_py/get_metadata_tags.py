#!/usr/bin/env python3

"""
Get the metadata tags from a library id

Given a library id, collect and return the library object
"""


from orcabus_api_tools.metadata import get_library_from_library_id


def handler(event, context):
    """
    Get the library object from a library id
    :param event:
    :param context:
    :return:
    """
    return {
        "libraryObj": get_library_from_library_id(event['libraryId']),
    }
