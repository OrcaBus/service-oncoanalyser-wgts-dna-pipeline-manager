#!/usr/bin/env python3

"""
Get the libraries from the input, check their metadata,
"""
from typing import List

from orcabus_api_tools.metadata import get_library_from_library_orcabus_id
from orcabus_api_tools.metadata.models import LibraryBase


def handler(event, context):
    """
    Get the libraries from the input, check their metadata,
    :param event:
    :param context:
    :return:
    """
    libraries: List[LibraryBase] = event.get("libraries", [])
    if not libraries:
        raise ValueError("No libraries provided in the input")

    if len(libraries) > 2:
        raise ValueError("We expect at most two libraries in the input")


    if len(libraries) == 1:
        # If only one library is provided, then we have a germline library
        return {
            "libraryId": libraries[0]['libraryId']
        }

    # Get library metadata for both libraries
    library_obj_list = list(map(
        lambda library_iter_: get_library_from_library_orcabus_id(library_iter_['orcabusId']),
        libraries
    ))

    # Check if both libraries are provided
    try:
        tumor_library_obj = next(filter(
            lambda library_iter_: library_iter_['phenotype'] == 'tumor',
            library_obj_list
        ))
    except StopIteration:
        raise ValueError("No tumor library found in the input")

    try:
        library_obj = next(filter(
            lambda library_iter_: library_iter_['phenotype'] == 'normal',
            library_obj_list
        ))
    except StopIteration:
        raise ValueError("No normal library found in the input")

    # If both libraries are provided, return their IDs
    return {
        "libraryId": library_obj['libraryId'],
        "tumorLibraryId": tumor_library_obj['libraryId']
    }
