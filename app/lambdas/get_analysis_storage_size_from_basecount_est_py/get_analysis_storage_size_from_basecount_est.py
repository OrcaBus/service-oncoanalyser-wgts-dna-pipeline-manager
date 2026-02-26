#!/usr/bin/env python3

"""
Given a basecount estimate, determine the analysis storage size

We bin as follows:

Under 250 million bases: SMALL

Under 500 million bases: MEDIUM

Over 500 million bases: LARGE
"""

# Standard imports
import typing
from typing import List


# Layer imports
from orcabus_api_tools.fastq import get_fastq

# Model imports
if typing.TYPE_CHECKING:
    from orcabus_api_tools.icav2_wes.models import AnalysisStorageSize
    from orcabus_api_tools.fastq.models import Fastq


def get_analysis_storage_size_from_basecount_est(basecount_est: int) -> 'AnalysisStorageSize':
    """
    Get the analysis storage size from the basecount estimate
    :param basecount_est:
    :return:
    """
    if basecount_est < 250_000_000:
        return "SMALL"
    elif basecount_est < 500_000_000:
        return "MEDIUM"
    else:
        return "LARGE"


def handler(event, context):
    """
    Given a list of fastq ids, get the basecount estimate for each fastq and determine the analysis storage size
    :param event:
    :param context:
    :return:
    """
    # Get the fastq id list from the event
    fastq_id_list = event["fastqIdList"]

    # Get the fastq objects
    fastq_objs: List['Fastq'] = list(map(
        lambda fastq_id_iter_: get_fastq(fastq_id_iter_),
        fastq_id_list
    ))

    # Get the read count
    read_count = sum(map(
        lambda fastq_obj_iter_: fastq_obj_iter_.get('baseCountEst', 0),
        fastq_objs
    ))

    # Return the storage size
    return {
        "analysisStorageSize": get_analysis_storage_size_from_basecount_est(read_count)
    }
