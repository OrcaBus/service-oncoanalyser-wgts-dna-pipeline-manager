#!/usr/bin/env python3

# Standard imports
from os import environ
from pathlib import Path
from urllib.parse import urlparse

from requests import HTTPError

# Layer imports
from orcabus_api_tools.fastq import to_fastq_list_row, get_fastq_by_rgid

# Globals
TEST_DATA_BUCKET_NAME_ENV_VAR = "TEST_DATA_BUCKET_NAME"


def handler(event, context):
    """
    Lambda handler to convert a list of FASTQ files into a list of rows.
    :param event:
    :param context:
    :return:
    """

    # Get the fastqList from the event
    fastq_rgid_list = event.get("fastqRgidList", [])
    s3_uri_prefix = event.get("s3UriPrefix", None)

    # Convert the uri prefix to a parsed object
    s3_uri_obj = (
        urlparse(s3_uri_prefix)
        if s3_uri_prefix is not None
        else None
    )

    # Collect all fastq ids from the rgid list
    all_fastq_ids = sorted(list(map(
        lambda fastq_rgid_iter_: get_fastq_by_rgid(fastq_rgid_iter_)['id'],
        fastq_rgid_list
    )))

    # Keep the test-data fastq list rows
    # (which are exempt from the requirement of being in a particular project prefix)
    non_test_data_fastq_list_ids = []
    test_data_fastq_list_rows = []

    # Try collect each fastq list row in the test-data section first
    for fastq_id_iter in all_fastq_ids:
        try:
            test_data_fqlr_iter = to_fastq_list_row(fastq_id_iter, bucket=environ[TEST_DATA_BUCKET_NAME_ENV_VAR])
            test_data_fastq_list_rows.append(test_data_fqlr_iter)
        except HTTPError:
            non_test_data_fastq_list_ids.append(fastq_id_iter)

    # Re-collect the test-data fastq list rows with the s3 uri prefix if provided
    non_test_data_fastq_list_rows = list(map(
        lambda fastq_id_iter_: to_fastq_list_row(
            fastq_id_iter_,
            **(
                {
                    "bucket": s3_uri_obj.netloc,
                    "key_prefix": (str(Path(s3_uri_obj.path)) + "/").lstrip('/')
                }
                if s3_uri_obj is not None
                else {}
            )
        ),
        non_test_data_fastq_list_ids
    ))

    # Return the list of fastq list row dicts
    return {
        "fastqListRows": test_data_fastq_list_rows + non_test_data_fastq_list_rows
    }
