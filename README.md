Oncoanalyser WGTS DNA Pipeline Orchestration Service
================================================================================

- [Description](#description)
  - [Summary](#summary)
  - [Events Overview](#events-overview)
  - [Consumed Events](#consumed-events)
  - [Published Events](#published-events)
  - [DRAFT Event Example (complete)](#draft-event-example-complete)
    - [Manually Validating Schemas](#manually-validating-schemas)
    - [Making your own DRAFT WRU events with BASH / JQ (new system)](#making-your-own-draft-wru-events-with-bash--jq-new-system)
    - [Making your own DRAFT WRSC events with BASH / JQ (legacy system)](#making-your-own-draft-wrsc-events-with-bash--jq-legacy-system)
    - [Release management :construction:](#release-management-construction)
- [Infrastructure \& Deployment :construction:](#infrastructure--deployment-construction)
  - [Stateful](#stateful)
  - [Stateless](#stateless)
  - [CDK Commands](#cdk-commands)
  - [Stacks :construction:](#stacks-construction)
- [Development](#development)
  - [Project Structure](#project-structure)
  - [Setup](#setup)
    - [Requirements](#requirements)
    - [Install Dependencies](#install-dependencies)
    - [First Steps](#first-steps)
  - [Conventions](#conventions)
  - [Linting \& Formatting](#linting--formatting)
  - [Testing](#testing)
- [Glossary \& References](#glossary--references)

Description
--------------------------------------------------------------------------------

### Summary

This is the Oncoanalyser WGTS DNA Pipeline Management service,
responsible for orchestrating the Oncoanalyser WGTS DNA analyses.

This service has 3 parts:
- **DRAFT Event Populator**: responsible for providing execution parameters
- **DRAFT Event Validator**: responsible for validating execution requirements
- **Execution Manager**: responsible for executing and monitoring pipeline runs
  - **ICAv2 WES to WRU Converter**: (sub-component) responsible for converting external WES events to internal WRU events

The pipeline runs on ICAv2 through Nextflow (version 24.10)

### Events Overview

![events-overview](docs/draw-io-exports/oncoanalyser-wgts-dna-pipeline.drawio.svg)

**DRAFT Event Population**
This is handled by the DRAFT Event Populator.
We listen to DRAFT WRSC events where the workflow name is equal to `oncoanalyser-wgts-dna`.
We then try to populate the inputs for the workflow run, and generate a complete DRAFT WRU event.

**DRAFT Event Validation**
This is handled by the DRAFT Event Validator.
We listen to DRAFT WRSC events where the workflow name is equal to `oncoanalyser-wgts-dna`.
We then validate the DRAFT event against the schema and check its execution requirements. If valid, we generate a READY WRU event.

**READY Event Handler**
This is handled by the Execution Manager.
We listen to READY WRSC events where the workflow name is equal to `oncoanalyser-wgts-dna`.
We parse this to the ICAv2 WES Service to generate a ICAv2 WES workflow request.

**ICAv2 WES Analysis State Change**
This is handled by the Execution Manager.
We then parse `Icav2WesAnalysisStateChange` events from the ICAv2 WES Service to update the state of the workflow in our service and forward any changes as WRU events.


### Consumed Events

| Name / DetailType             | Source             | Schema Link   | Description                           |
|-------------------------------|--------------------|---------------|---------------------------------------|
| `WorkflowRunStateChange`      | `orcabus.workflowmanager` | [WorkflowRunStateChange](https://github.com/OrcaBus/wiki/tree/main/orcabus-platform#workflowrunstatechange) | Source of updates on WorkflowRuns (expected pipeline executions) |
| `Icav2WesAnalysisStateChange` | `orcabus.icav2wes` | TODO | ICAv2 WES Analysis State Change event |

### Published Events

| Name / DetailType        | Source                        | Schema Link   | Description           |
|--------------------------|-------------------------------|---------------|-----------------------|
| `WorkflowRunUpdate` | `orcabus.oncoanalyserwgtsdna` | [WorkflowRunUpdate](https://github.com/OrcaBus/wiki/tree/main/orcabus-platform#workflowrunupdate) | Reporting any updates to the pipeline state |

### DRAFT Event Example (complete)

DRAFT event minimal complete example that would pass the DRAFT Event Validation and result in a READY event and subsequent pipeline execution.

<details>

<summary>Click to expand</summary>

```json5
{
  "EventBusName": "OrcaBusMain",
  "Source": "orcabus.manual",
  "DetailType": "WorkflowRunUpdate",
  "Detail": {
    "status": "DRAFT",
    "timestamp": "2025-08-29T03:23:04Z",
    "workflow": {
      "name": "oncoanalyser-wgts-dna",
      "version": "2.1.0"
    },
    "workflowRunName": "umccr--automated--oncoanalyser-wgts-dna--2-1-0--20250829d165aaa2",
    "portalRunId": "20250829d165aaa2",
    "libraries": [
      {
        "orcabusId": "lib.01JBMVH3QN2PNC949C5TS9REQV",
        "libraryId": "L2300943"
      },
      {
        "orcabusId": "lib.01JBMVH3Z9K05CJAZ8FQ4V2ZZH",
        "libraryId": "L2300950"
      }
    ],
    "payload": {
      "version": "2025.08.05",
      "data": {
        "tags": {
          "libraryId": "L2300950",
          "subjectId": "HCC1395",
          "individualId": "SBJ00480",
          "fastqRgidList": [
            "GGCATTCT+CAAGCTAG.2.230629_A01052_0154_BH7WF5DSX7"
          ],
          "tumorLibraryId": "L2300943",
          "tumorFastqRgidList": [
            "ACTAAGAT+CCGCGGTT.4.230602_A00130_0258_BH55TMDSX7",
            "ACTAAGAT+CCGCGGTT.3.230602_A00130_0258_BH55TMDSX7"
          ]
        },
        "inputs": {
          "mode": "wgts",
          "groupId": "L2300943__L2300950",
          "subjectId": "L2300943__L2300950",
          "tumorDnaBamUri": "s3://test-data-503977275616-ap-southeast-2/testdata/analysis/production/dragen-wgts-dna/4.4.4/SEQC-II/01k3n0kn3nvsdtne265p0800qp/20250822e11a8540/L2300943__L2300950__hg38__linear__dragen_wgts_dna_somatic_variant_calling/L2300943_tumor.bam",
          "normalDnaBamUri": "s3://test-data-503977275616-ap-southeast-2/testdata/analysis/production/dragen-wgts-dna/4.4.4/SEQC-II/01k3n0kn3nvsdtne265p0800qp/20250822e11a8540/L2300950__hg38__graph__dragen_wgts_dna_germline_variant_calling/L2300950.bam",
          "tumorDnaSampleId": "L2300943",
          "normalDnaSampleId": "L2300950",
          "genome": "GRCh38_umccr",
          "genomeVersion": "38",
          "genomeType": "alt",
          "forceGenome": true,
          "refDataHmfDataPath": "s3://reference-data-503977275616-ap-southeast-2/refdata/hartwig/hmf-reference-data/hmftools/hmf_pipeline_resources.38_v2.1.0--1/",
          "genomes": {
            "GRCh38_umccr": {
              "fasta": "s3://reference-data-503977275616-ap-southeast-2/refdata/genomes/GRCh38_umccr/GRCh38_full_analysis_set_plus_decoy_hla.fa",
              "fai": "s3://reference-data-503977275616-ap-southeast-2/refdata/genomes/GRCh38_umccr/samtools_index/1.16/GRCh38_full_analysis_set_plus_decoy_hla.fa.fai",
              "dict": "s3://reference-data-503977275616-ap-southeast-2/refdata/genomes/GRCh38_umccr/samtools_index/1.16/GRCh38_full_analysis_set_plus_decoy_hla.fa.dict",
              "img": "s3://reference-data-503977275616-ap-southeast-2/refdata/genomes/GRCh38_umccr/bwa_index_image/0.7.17-r1188/GRCh38_full_analysis_set_plus_decoy_hla.fa.img",
              "bwamem2Index": "s3://reference-data-503977275616-ap-southeast-2/refdata/genomes/GRCh38_umccr/bwa-mem2_index/2.2.1/",
              "gridssIndex": "s3://reference-data-503977275616-ap-southeast-2/refdata/genomes/GRCh38_umccr/gridss_index/2.13.2/",
              "starIndex": "s3://reference-data-503977275616-ap-southeast-2/refdata/genomes/GRCh38_umccr/star_index/gencode_38/2.7.3a/"
            }
          }
        },
        "engineParameters": {
          "projectId": "ea19a3f5-ec7c-4940-a474-c31cd91dbad4",
          "pipelineId": "ab6e1d62-1b5a-4b24-86b8-81ccf4bdc7a2",
          "outputUri": "s3://pipeline-dev-cache-503977275616-ap-southeast-2/byob-icav2/development/analysis/oncoanalyser-wgts-dna/20250829d165aaa2/",
          "logsUri": "s3://pipeline-dev-cache-503977275616-ap-southeast-2/byob-icav2/development/logs/oncoanalyser-wgts-dna/20250829d165aaa2/",
          "cacheUri": "s3://pipeline-dev-cache-503977275616-ap-southeast-2/byob-icav2/development/cache/oncoanalyser-wgts-dna/20250829d165aaa2/"
        }
      }
    }
  }
}
```

</details>

#### Manually Validating Schemas

We have generated JSON Schemas for the complete DRAFT event **data** which you can find in the [
`./app/event-schemas`](app/event-schemas) directory.

You can interactively check if your DRAFT or READY event matches the schema using the following links:

- [Complete DRAFT Data Event Schema Page](https://www.jsonschemavalidator.net/s/ufMlzGzy)


#### Making your own DRAFT WRU events with BASH / JQ (new system)

There may be circumstances where you wish to generate DRAFT events manually, e.g. to explicitly trigger a workflow execution where automation failed or is not available. The below is a quick solution for generating a DRAFT event for a somatic Oncoanalyser WGTS DNA workflow. Omit setting the `TUMOR_LIBRARY_ID` variable for running a germline
only workflow.

> [!NOTE]
> This is a minimal example. It assumes that the rest of the required information can be retrieved and filled by the DRAFT Event Populator.

The DRAFT Event Populator will also pull necessary fastq files out of archive.

For details, see [PM.OWD.1 - Manual Pipeline Execution](./docs/operation/SOP/PM.OWD.1/PM.OWD.1-ManualPipelineExecution.md)


#### Making your own DRAFT WRSC events with BASH / JQ (legacy system)

There may be circumstances where you wish to generate WRSC events manually, the below is a quick solution for
generating a DRAFT for a oncoanalyser somatic wgts dna workflow. Omit setting the TUMOR_LIBRARY_ID variable for running a germline
only workflow.

The DRAFT populator step function will also pull necessary fastq files out of archive.

For a detailed procedure, see [Manual Pipeline Execution (legacy)](./docs/operation/examples/WRSC-DRAFT/ManualPipelineExecution.md)


#### Release management :construction:

The service employs a fully automated CI/CD pipeline that automatically builds and releases all changes to the `main`
code branch.


Infrastructure & Deployment :construction:
--------------------------------------------------------------------------------

Short description with diagrams where appropriate.
Deployment settings / configuration (e.g. CodePipeline(s) / automated builds).

Infrastructure and deployment are managed via CDK. This template provides two types of CDK entry points: `cdk-stateless`
and `cdk-stateful`.

### Stateful

- Queues
- Buckets
- Database
- ...

### Stateless

- Lambdas
- StepFunctions

### CDK Commands

You can access CDK commands using the `pnpm` wrapper script.

- **`cdk-stateless`**: Used to deploy stacks containing stateless resources (e.g., AWS Lambda), which can be easily
  redeployed without side effects.
- **`cdk-stateful`**: Used to deploy stacks containing stateful resources (e.g., AWS DynamoDB, AWS RDS), where
  redeployment may not be ideal due to potential side effects.

The type of stack to deploy is determined by the context set in the `./bin/deploy.ts` file. This ensures the correct
stack is executed based on the provided context.

For example:

```sh
# Deploy a stateless stack
pnpm cdk-stateless <command>

# Deploy a stateful stack
pnpm cdk-stateful <command>
```

### Stacks :construction:

This CDK project manages multiple stacks. The root stack (the only one that does not include `DeploymentPipeline` in its
stack ID) is deployed in the toolchain account and sets up a CodePipeline for cross-environment deployments to `beta`,
`gamma`, and `prod`.

To list all available stacks, run:

```sh
pnpm cdk-stateless ls
```

Example output:

```sh
OrcaBusStatelessServiceStack
OrcaBusStatelessServiceStack/DeploymentPipeline/OrcaBusBeta/DeployStack (OrcaBusBeta-DeployStack)
OrcaBusStatelessServiceStack/DeploymentPipeline/OrcaBusGamma/DeployStack (OrcaBusGamma-DeployStack)
OrcaBusStatelessServiceStack/DeploymentPipeline/OrcaBusProd/DeployStack (OrcaBusProd-DeployStack)
```

Development
--------------------------------------------------------------------------------

### Project Structure

The root of the project is an AWS CDK project where the main application logic lives inside the `./app` folder.

The project is organized into the following key directories:

- **`./app`**: Contains the main application logic. You can open the code editor directly in this folder, and the
  application should run independently.

- **`./bin/deploy.ts`**: Serves as the entry point of the application. It initializes two root stacks: `stateless` and
  `stateful`. You can remove one of these if your service does not require it.

- **`./infrastructure`**: Contains the infrastructure code for the project:
    - **`./infrastructure/toolchain`**: Includes stacks for the stateless and stateful resources deployed in the
      toolchain account. These stacks primarily set up the CodePipeline for cross-environment deployments.
    - **`./infrastructure/stage`**: Defines the stage stacks for different environments:
        - **`./infrastructure/stage/config.ts`**: Contains environment-specific configuration files (e.g., `beta`,
          `gamma`, `prod`).
        - **`./infrastructure/stage/stack.ts`**: The CDK stack entry point for provisioning resources required by the
          application in `./app`.

- **`.github/workflows/pr-tests.yml`**: Configures GitHub Actions to run tests for `make check` (linting and code
  style), tests defined in `./test`, and `make test` for the `./app` directory. Modify this file as needed to ensure the
  tests are properly configured for your environment.

- **`./test`**: Contains tests for CDK code compliance against `cdk-nag`. You should modify these test files to match
  the resources defined in the `./infrastructure` folder.

### Setup

#### Requirements

```sh
node --version
v22.9.0

# Update Corepack (if necessary, as per pnpm documentation)
npm install --global corepack@latest

# Enable Corepack to use pnpm
corepack enable pnpm

```

#### Install Dependencies

To install all required dependencies, run:

```sh
make install
```

#### First Steps

Before using this template, search for all instances of `TODO:` comments in the codebase and update them as appropriate
for your service. This includes replacing placeholder values (such as stack names).

### Conventions

### Linting & Formatting

Automated checks are enforces via pre-commit hooks, ensuring only checked code is committed. For details consult the
`.pre-commit-config.yaml` file.

Manual, on-demand checking is also available via `make` targets (see below). For details consult the `Makefile` in the
root of the project.

To run linting and formatting checks on the root project, use:

```sh
make check
```

To automatically fix issues with ESLint and Prettier, run:

```sh
make fix
```

### Testing

Unit tests are available for most of the business logic. Test code is hosted alongside business in `/tests/`
directories.

```sh
make test
```

Glossary & References
--------------------------------------------------------------------------------

For general terms and expressions used across OrcaBus services, please see the
platform [documentation](https://github.com/OrcaBus/wiki/blob/main/orcabus-platform/README.md#glossary--references).

Service specific terms:

| Term | Description |
|------|-------------|
| Foo  | ...         |
| Bar  | ...         |
