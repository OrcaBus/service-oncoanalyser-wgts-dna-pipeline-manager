import { StageName } from '@orcabus/platform-cdk-constructs/shared-config/accounts';
import { ICAV2_PROJECT_ID } from '@orcabus/platform-cdk-constructs/shared-config/icav2';
import { StatefulApplicationStackConfig, StatelessApplicationStackConfig } from './interfaces';
import {
  DEFAULT_PAYLOAD_VERSION,
  DEFAULT_WORKFLOW_INPUTS_BY_VERSION_MAP,
  DEFAULT_WORKFLOW_VERSION,
  EVENT_BUS_NAME,
  GENOMES_MAP,
  NEW_WORKFLOW_MANAGER_IS_DEPLOYED,
  SSM_PARAMETER_PATH_CACHE_PREFIX,
  SSM_PARAMETER_PATH_DEFAULT_WORKFLOW_VERSION,
  SSM_PARAMETER_PATH_ICAV2_PROJECT_ID,
  SSM_PARAMETER_PATH_LOGS_PREFIX,
  SSM_PARAMETER_PATH_OUTPUT_PREFIX,
  SSM_PARAMETER_PATH_PAYLOAD_VERSION,
  SSM_PARAMETER_PATH_PREFIX,
  SSM_PARAMETER_PATH_PREFIX_GENOMES,
  SSM_PARAMETER_PATH_PREFIX_HMF_REFERENCE_PATHS_BY_WORKFLOW_VERSION,
  SSM_PARAMETER_PATH_PREFIX_INPUTS_BY_WORKFLOW_VERSION,
  SSM_PARAMETER_PATH_PREFIX_PIPELINE_IDS_BY_WORKFLOW_VERSION,
  SSM_PARAMETER_PATH_WORKFLOW_NAME,
  WORKFLOW_CACHE_PREFIX,
  WORKFLOW_LOGS_PREFIX,
  WORKFLOW_NAME,
  WORKFLOW_OUTPUT_PREFIX,
  WORKFLOW_VERSION_TO_DEFAULT_HMF_REFERENCE_PATHS_MAP,
  WORKFLOW_VERSION_TO_DEFAULT_ICAV2_PIPELINE_ID_MAP,
} from './constants';
import { substituteBucketConstants } from './utils';
import { SsmParameterPaths, SsmParameterValues } from './ssm/interfaces';

export const getSsmParameterValues = (stage: StageName): SsmParameterValues => {
  return {
    // Values
    // Detail
    workflowName: WORKFLOW_NAME,
    workflowVersion: DEFAULT_WORKFLOW_VERSION,

    // Payload
    payloadVersion: DEFAULT_PAYLOAD_VERSION,

    // Inputs
    inputsByWorkflowVersionMap: DEFAULT_WORKFLOW_INPUTS_BY_VERSION_MAP,

    // Engine Parameters
    pipelineIdsByWorkflowVersionMap: WORKFLOW_VERSION_TO_DEFAULT_ICAV2_PIPELINE_ID_MAP,
    icav2ProjectId: ICAV2_PROJECT_ID[stage],
    logsPrefix: substituteBucketConstants(WORKFLOW_LOGS_PREFIX, stage),
    outputPrefix: substituteBucketConstants(WORKFLOW_OUTPUT_PREFIX, stage),
    cachePrefix: substituteBucketConstants(WORKFLOW_CACHE_PREFIX, stage),

    // Genomes
    genomes: GENOMES_MAP,

    // Reference SSM Paths
    hmfReferenceDataByWorkflowVersionMap: WORKFLOW_VERSION_TO_DEFAULT_HMF_REFERENCE_PATHS_MAP,
  };
};

export const getSsmParameterPaths = (): SsmParameterPaths => {
  return {
    // Top level prefix
    ssmRootPrefix: SSM_PARAMETER_PATH_PREFIX,

    // Detail
    workflowName: SSM_PARAMETER_PATH_WORKFLOW_NAME,
    workflowVersion: SSM_PARAMETER_PATH_DEFAULT_WORKFLOW_VERSION,

    // Inputs
    prefixDefaultInputsByWorkflowVersion: SSM_PARAMETER_PATH_PREFIX_INPUTS_BY_WORKFLOW_VERSION,

    // Payload
    payloadVersion: SSM_PARAMETER_PATH_PAYLOAD_VERSION,

    // Engine Parameters
    prefixPipelineIdsByWorkflowVersion: SSM_PARAMETER_PATH_PREFIX_PIPELINE_IDS_BY_WORKFLOW_VERSION,
    icav2ProjectId: SSM_PARAMETER_PATH_ICAV2_PROJECT_ID,
    logsPrefix: SSM_PARAMETER_PATH_LOGS_PREFIX,
    outputPrefix: SSM_PARAMETER_PATH_OUTPUT_PREFIX,
    cachePrefix: SSM_PARAMETER_PATH_CACHE_PREFIX,

    // Reference SSM Paths
    hmfReferenceDataSsmRootPrefix:
      SSM_PARAMETER_PATH_PREFIX_HMF_REFERENCE_PATHS_BY_WORKFLOW_VERSION,
    genomesSsmRootPrefix: SSM_PARAMETER_PATH_PREFIX_GENOMES,
  };
};

export const getStatefulStackProps = (stage: StageName): StatefulApplicationStackConfig => {
  return {
    ssmParameterValues: getSsmParameterValues(stage),
    ssmParameterPaths: getSsmParameterPaths(),
  };
};

export const getStatelessStackProps = (stage: StageName): StatelessApplicationStackConfig => {
  // Get stateless application stack props
  return {
    // Event bus object
    eventBusName: EVENT_BUS_NAME,
    isNewWorkflowManagerDeployed: NEW_WORKFLOW_MANAGER_IS_DEPLOYED[stage],
  };
};
