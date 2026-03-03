#!/usr/bin/env python3

"""
Get the fastq ids from the rgid list

Given the rgid list, return the fastq ids that are associated with these rgids.
"""

from orcabus_api_tools.fastq import get_fastq_by_rgid


def handler(event, context):
    """
    Given a list of fastq RGIDs, return the corresponding fastq IDs.
    :param event: A dictionary containing the key "fastqRgidList", which is a list of fastq RGIDs.
    :param context: AWS Lambda context object (not used in this function).
    :return: A dictionary with the key "fastqIdList", which is a list of fastq IDs corresponding to the input RGIDs.
    """
    fastq_rgid_list = event.get("fastqRgidList", [])

    all_fastq_ids = sorted(list(map(
        lambda fastq_rgid_iter_: get_fastq_by_rgid(fastq_rgid_iter_)['id'],
        fastq_rgid_list
    )))

    return {
        "fastqIdList": all_fastq_ids
    }
