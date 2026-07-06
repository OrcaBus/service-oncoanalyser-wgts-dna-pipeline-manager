# Updating Pipeline Parameters

- Version: 2026.07.03
- Contact: Alexis Lucattini, [alexisl@unimelb.edu.au](mailto:alexisl@unimelb.edu.au)

This SOP describes how to update SSM parameters for the Oncoanalyser WGTS DNA pipeline.

- [Introduction](#introduction)
- [Requirements](#requirements)
- [Parameter Types](#parameter-types)
- [Procedure](#procedure)
- [Verification](#verification)


## Introduction

The Oncoanalyser WGTS DNA Pipeline Manager uses AWS SSM Parameter Store to manage configuration values
such as default project IDs, pipeline IDs, output prefixes, and reference data paths.
All parameters live under the path `/orcabus/workflows/oncoanalyser-wgts-dna/`.

## Requirements

- AWS credentials with permissions to update SSM parameters in the target account
- Knowledge of the parameter you wish to update and its expected format
- Access to the relevant AWS account (dev/stg/prod)

## Parameter Types

| Parameter Path | Description | Example Value |
|---|---|---|
| `workflow-name` | The workflow name | `oncoanalyser-wgts-dna` |
| `default-workflow-version` | Current default workflow version | `2.1.0` |
| `payload-version` | Payload schema version | `2025.08.05` |
| `icav2-project-id` | Default ICAv2 project ID | `ea19a3f5-ec7c-...` |
| `output-prefix` | S3 prefix for analysis outputs | `s3://bucket/path/analysis/oncoanalyser-wgts-dna/` |
| `logs-prefix` | S3 prefix for logs | `s3://bucket/path/logs/oncoanalyser-wgts-dna/` |
| `pipeline-ids-by-workflow-version/<version>` | ICAv2 pipeline ID | `ab6e1d62-...` |
| `inputs-by-workflow-version/<version>` | Default inputs JSON | `{"genome": "GRCh38_umccr", ...}` |

## Procedure

1. Identify which parameter needs updating and in which environment(s).
2. Update the parameter value using the AWS CLI:
   ```shell
   aws ssm put-parameter \
     --name "/orcabus/workflows/oncoanalyser-wgts-dna/<parameter-name>" \
     --value "<new-value>" \
     --type String \
     --overwrite
   ```
3. If the parameter is also defined in `infrastructure/stage/constants.ts` as a default,
   update the code and create a PR to keep infrastructure and runtime in sync.

## Verification

1. Confirm the parameter was updated:
   ```shell
   aws ssm get-parameter \
     --name "/orcabus/workflows/oncoanalyser-wgts-dna/<parameter-name>"
   ```
2. Trigger a test DRAFT event to verify the pipeline picks up the new parameter value.
   See [PM.OWD.1][sop_1_rel_path] for instructions.


[sop_1_rel_path]: ../PM.OWD.1/PM.OWD.1-ManualPipelineExecution.md
