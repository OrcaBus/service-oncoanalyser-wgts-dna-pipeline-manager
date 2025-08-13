/* Directory constants */
import path from 'path';
import { StageName } from '@orcabus/platform-cdk-constructs/shared-config/accounts';
import { Genome, NotInBuiltInHmfReferenceGenomesType, VersionType } from './interfaces';

export const APP_ROOT = path.join(__dirname, '../../app');
export const LAMBDA_DIR = path.join(APP_ROOT, 'lambdas');
export const STEP_FUNCTIONS_DIR = path.join(APP_ROOT, 'step-functions-templates');
export const EVENT_SCHEMAS_DIR = path.join(APP_ROOT, 'event-schemas');

/* Workflow constants */
export const WORKFLOW_NAME = 'oncoanalyser-wgts-dna';

// Yet to implement draft events into this service
// However, because this workflow has the same workflow name as the
// existing production workflow, we need to filter on the payload version
// to prevent the wrong service from being triggered
export const DEFAULT_WORKFLOW_VERSION: VersionType = '2.1.0';
export const DEFAULT_PAYLOAD_VERSION = '2025.08.05';

// Yet to implement draft events into this service
export const WORKFLOW_LOGS_PREFIX = `s3://{__CACHE_BUCKET__}/{__CACHE_PREFIX__}logs/${WORKFLOW_NAME}/`;
export const WORKFLOW_OUTPUT_PREFIX = `s3://{__CACHE_BUCKET__}/{__CACHE_PREFIX__}analysis/${WORKFLOW_NAME}/`;
export const WORKFLOW_CACHE_PREFIX = `s3://{__CACHE_BUCKET__}/{__CACHE_PREFIX__}cache/${WORKFLOW_NAME}/`;

/* We extend this every time we release a new version of the workflow */
/* This is added into our SSM Parameter Store to allow us to map workflow versions to pipeline IDs */
export const WORKFLOW_VERSION_TO_DEFAULT_ICAV2_PIPELINE_ID_MAP: Record<VersionType, string> = {
  // At the moment we are running manual deployments of the workflow
  '2.0.0': 'a64126df-d8b2-4ec0-99df-1154f44a74ef',
  '2.1.0': 'ab6e1d62-1b5a-4b24-86b8-81ccf4bdc7a2',
};

export const WORKFLOW_VERSION_TO_DEFAULT_HMF_REFERENCE_PATHS_MAP: Record<VersionType, string> = {
  '2.0.0':
    's3://pipeline-prod-cache-503977275616-ap-southeast-2/byob-icav2/reference-data/hartwig/hmf-reference-data/hmftools/hmf_pipeline_resources.38_v2.0--3/',
  '2.1.0':
    's3://pipeline-prod-cache-503977275616-ap-southeast-2/byob-icav2/reference-data/hartwig/hmf-reference-data/hmftools/hmf_pipeline_resources.38_v2.1.0--1/',
};

export const GENOMES_MAP: Record<NotInBuiltInHmfReferenceGenomesType, Genome> = {
  GRCh38_umccr: {
    fasta:
      's3://pipeline-prod-cache-503977275616-ap-southeast-2/byob-icav2/reference-data/genomes/GRCh38_umccr/GRCh38_full_analysis_set_plus_decoy_hla.fa',
    fai: 's3://pipeline-prod-cache-503977275616-ap-southeast-2/byob-icav2/reference-data/genomes/GRCh38_umccr/samtools_index/1.16/GRCh38_full_analysis_set_plus_decoy_hla.fa.fai',
    dict: 's3://pipeline-prod-cache-503977275616-ap-southeast-2/byob-icav2/reference-data/genomes/GRCh38_umccr/samtools_index/1.16/GRCh38_full_analysis_set_plus_decoy_hla.fa.dict',
    img: 's3://pipeline-prod-cache-503977275616-ap-southeast-2/byob-icav2/reference-data/genomes/GRCh38_umccr/samtools_index/1.16/GRCh38_full_analysis_set_plus_decoy_hla.fa.img',
    bwamem2_index:
      's3://pipeline-prod-cache-503977275616-ap-southeast-2/byob-icav2/reference-data/genomes/GRCh38_umccr/bwa-mem2_index/2.2.1/',
    gridss_index:
      's3://pipeline-prod-cache-503977275616-ap-southeast-2/byob-icav2/reference-data/genomes/GRCh38_umccr/gridss_index/2.13.2/',
    star_index:
      's3://pipeline-prod-cache-503977275616-ap-southeast-2/byob-icav2/reference-data/genomes/GRCh38_umccr/star_index/gencode_38/2.7.3a/',
  },
};

export const DEFAULT_WORKFLOW_INPUTS_BY_VERSION_MAP: Record<VersionType, object> = {
  '2.0.0': {
    mode: 'wgts',
    genome: 'GRCh38_umccr',
    genome_version: '38',
    genome_type: 'alt',
    force_genome: true,
  },
  '2.1.0': {
    mode: 'wgts',
    genome: 'GRCh38_umccr',
    genome_version: '38',
    genome_type: 'alt',
    force_genome: true,
  },
};

/* SSM Parameter Paths */
export const SSM_PARAMETER_PATH_PREFIX = path.join(`/orcabus/workflows/${WORKFLOW_NAME}/`);
// Workflow Parameters
export const SSM_PARAMETER_PATH_WORKFLOW_NAME = path.join(
  SSM_PARAMETER_PATH_PREFIX,
  'workflow-name'
);
export const SSM_PARAMETER_PATH_DEFAULT_WORKFLOW_VERSION = path.join(
  SSM_PARAMETER_PATH_PREFIX,
  'default-workflow-version'
);
// Input parameters
export const SSM_PARAMETER_PATH_PREFIX_INPUTS_BY_WORKFLOW_VERSION = path.join(
  SSM_PARAMETER_PATH_PREFIX,
  'inputs-by-workflow-version'
);
// Engine Parameters
export const SSM_PARAMETER_PATH_PREFIX_PIPELINE_IDS_BY_WORKFLOW_VERSION = path.join(
  SSM_PARAMETER_PATH_PREFIX,
  'pipeline-ids-by-workflow-version'
);
export const SSM_PARAMETER_PATH_ICAV2_PROJECT_ID = path.join(
  SSM_PARAMETER_PATH_PREFIX,
  'icav2-project-id'
);
export const SSM_PARAMETER_PATH_PAYLOAD_VERSION = path.join(
  SSM_PARAMETER_PATH_PREFIX,
  'payload-version'
);
export const SSM_PARAMETER_PATH_LOGS_PREFIX = path.join(SSM_PARAMETER_PATH_PREFIX, 'logs-prefix');
export const SSM_PARAMETER_PATH_OUTPUT_PREFIX = path.join(
  SSM_PARAMETER_PATH_PREFIX,
  'output-prefix'
);
export const SSM_PARAMETER_PATH_CACHE_PREFIX = path.join(SSM_PARAMETER_PATH_PREFIX, 'cache-prefix');
// Reference Parameters
export const SSM_PARAMETER_PATH_PREFIX_HMF_REFERENCE_PATHS_BY_WORKFLOW_VERSION = path.join(
  SSM_PARAMETER_PATH_PREFIX,
  'default-hmf-reference-paths-by-workflow-version'
);
export const SSM_PARAMETER_PATH_PREFIX_GENOMES = path.join(SSM_PARAMETER_PATH_PREFIX, 'genomes');

/* Event Constants */
export const EVENT_BUS_NAME = 'OrcaBusMain';
export const EVENT_SOURCE = 'orcabus.oncoanalyserwgtsdna';
export const WORKFLOW_RUN_STATE_CHANGE_DETAIL_TYPE = 'WorkflowRunStateChange';
export const ICAV2_WES_REQUEST_DETAIL_TYPE = 'Icav2WesRequest';
export const ICAV2_WES_STATE_CHANGE_DETAIL_TYPE = 'Icav2WesAnalysisStateChange';

export const WORKFLOW_MANAGER_EVENT_SOURCE = 'orcabus.workflowmanager';
export const ICAV2_WES_EVENT_SOURCE = 'orcabus.icav2wesmanager';

// Yet to implement draft events into this service
// export const FASTQ_SYNC_DETAIL_TYPE = 'FastqSync';

/* Event rule constants */
// Yet to implement draft events into this service
// export const DRAFT_STATUS = 'DRAFT';
export const READY_STATUS = 'READY';

/* Schema constants */
// Yet to implement draft events into this service
export const SCHEMA_REGISTRY_NAME = EVENT_SOURCE;
export const SSM_SCHEMA_ROOT = path.join(SSM_PARAMETER_PATH_PREFIX, 'schemas');

/* Future proofing */
export const NEW_WORKFLOW_MANAGER_IS_DEPLOYED: Record<StageName, boolean> = {
  BETA: true,
  GAMMA: false,
  PROD: false,
};

// Used to group event rules and step functions
export const STACK_PREFIX = 'orca-onco-wgts-dna';
