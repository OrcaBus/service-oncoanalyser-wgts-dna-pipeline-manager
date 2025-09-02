#!/usr/bin/env python3

"""
Get the fastq rgids from the library id

Given a library id, use the fastq set endpoint to collect all rgids associated with the library.

Rgids are returned in the format '<index>+<index2>.<lane>.<instrument_run_id>'
"""

# Layer imports
from orcabus_api_tools.fastq import get_fastq_sets, get_fastq_list_rows_in_fastq_set
from orcabus_api_tools.fastq.models import Fastq


def get_rgid_from_fastq_obj(fastq_obj: Fastq):
    return ".".join([
        fastq_obj['index'],
        str(fastq_obj['lane']),
        fastq_obj['instrumentRunId']
    ])

def handler(event, context):
    """
    Given a library id, get the fastq rgids associated with the library.
    :param event:
    :param context:
    :return:
    """

    library_id = event.get("libraryId")

    fastq_sets = get_fastq_sets(
        library=library_id,
        currentFastqSet=True
        # FIXME - why does this ask for __hash__
    )

    if len(fastq_sets) != 1:
        raise ValueError(f"Expected exactly one current fastq set for library {library_id}, found {len(fastq_sets)}")

    # Get the fastqs from the fastq set
    fastqs_list = get_fastq_list_rows_in_fastq_set(fastq_sets[0]['id'])

    return {
        "fastqRgidList": list(map(
            lambda fastq_iter_: get_rgid_from_fastq_obj(fastq_iter_),
            fastqs_list
        ))
    }


# Single lane
# if __name__ == "__main__":
#     from os import environ
#     environ['AWS_PROFILE'] = 'umccr-development'
#     environ['HOSTNAME_SSM_PARAMETER_NAME'] = '/hosted_zone/umccr/name'
#     environ['ORCABUS_TOKEN_SECRET_ID'] = 'orcabus/token-service-jwt'
#     print(json.dumps(
#         handler(
#             {
#                 "libraryId": "L2401541"
#             },
#             None
#         ),
#         indent=4
#     ))
#
#     # {
#     #     "fastqRgidList": [
#     #         "AAGTCCAA+TACTCATA.2.241024_A00130_0336_BHW7MVDSXC"
#     #     ]
#     # }

# Dual lanes
# if __name__ == "__main__":
#     from os import environ
#     environ['AWS_PROFILE'] = 'umccr-development'
#     environ['HOSTNAME_SSM_PARAMETER_NAME'] = '/hosted_zone/umccr/name'
#     environ['ORCABUS_TOKEN_SECRET_ID'] = 'orcabus/token-service-jwt'
#     print(json.dumps(
#         handler(
#             {
#                 "libraryId": "L2401544"
#             },
#             None
#         ),
#         indent=4
#     ))
#
#     # {
#     #     "fastqRgidList": [
#     #         "CAAGCTAG+CGCTATGT.2.241024_A00130_0336_BHW7MVDSXC",
#     #         "CAAGCTAG+CGCTATGT.3.241024_A00130_0336_BHW7MVDSXC"
#     #     ]
#     # }
