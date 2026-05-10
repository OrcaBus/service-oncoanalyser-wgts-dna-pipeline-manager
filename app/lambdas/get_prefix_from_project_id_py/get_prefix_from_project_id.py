#!/usr/bin/env python3

"""
Given an ICAv2 project id, get the base uri for that project
"""
# Standard imports
from typing import Dict, cast

# Wrapica imports
from wrapica.storage_configuration import get_s3_key_prefix_by_project_id

# Layer imports
from icav2_tools import set_icav2_env_vars


def handler(event, context) -> Dict[str, str]:
    """
    Given an ICAv2 project id, get the base uri for that project
    """
    # Set env vars
    set_icav2_env_vars()

    # Inputs
    project_id = event.get("projectId", None)

    # Check project id is not None:
    if project_id is None:
        raise ValueError("projectId is a required input")

    return {
        "s3Uri": cast(str, get_s3_key_prefix_by_project_id(project_id))
    }
