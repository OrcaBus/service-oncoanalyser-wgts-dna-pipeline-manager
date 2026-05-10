import { PythonUvFunction } from '@orcabus/platform-cdk-constructs/lambda';

export type LambdaName =
  // Shared pre-ready lambdas
  | 'comparePayload'
  | 'getDraftPayload'
  | 'findLatestWorkflow'
  | 'getDragenOutputsFromPortalRunId'
  | 'getWorkflowRunObject'
  | 'generateWruEventObjectWithMergedData'
  | 'getLatestPayloadFromPortalRunId'
  | 'getAnalysisStorageSizeFromBasecountEst'
  // Glue lambdas
  // Draft Builder lambdas
  | 'getFastqIdListFromRgidList'
  | 'getFastqRgidsFromLibraryId'
  | 'getLibraries'
  | 'getMetadataTags'
  | 'getPrefixFromProjectId'
  | 'getFastqListRowsFromFastqRgidList'
  // Validation lambda
  | 'postSchemaValidation'
  | 'validateDraftDataCompleteSchema'
  // Ready to ICAv2 WES lambdas
  | 'convertReadyEventInputsToIcav2WesEventInputs'
  | 'determineFastqCompressionType'
  | 'generateFastqUriByFastqIdMap'
  | 'collectOraOutputs'
  // ICAv2 WES to WRSC Event lambdas
  | 'convertIcav2WesEventToWrscEvent';

export const lambdaNameList: LambdaName[] = [
  // Shared pre-ready lambdas
  'comparePayload',
  'getDraftPayload',
  'findLatestWorkflow',
  'getDragenOutputsFromPortalRunId',
  'getWorkflowRunObject',
  'generateWruEventObjectWithMergedData',
  'getLatestPayloadFromPortalRunId',
  'getAnalysisStorageSizeFromBasecountEst',
  // Glue lambdas
  // Draft Builder lambdas
  'getFastqIdListFromRgidList',
  'getFastqRgidsFromLibraryId',
  'getLibraries',
  'getMetadataTags',
  'getPrefixFromProjectId',
  'getFastqListRowsFromFastqRgidList',
  // Validate Draft Complete Schema
  'postSchemaValidation',
  'validateDraftDataCompleteSchema',
  // Ready to ICAv2 WES lambdas
  'convertReadyEventInputsToIcav2WesEventInputs',
  'determineFastqCompressionType',
  'generateFastqUriByFastqIdMap',
  'collectOraOutputs',
  // ICAv2 WES to WRSC Event lambdas
  'convertIcav2WesEventToWrscEvent',
];

// Requirements interface for Lambda functions
export interface LambdaRequirements {
  needsOrcabusApiTools?: boolean;
  needsIcav2Tools?: boolean;
  needsSsmParametersAccess?: boolean;
  needsSchemaRegistryAccess?: boolean;
  needsWorkflowEnvVars?: boolean;
  needsBucketEnvVars?: boolean;
  needsHigherMemory?: boolean;
}

// Lambda requirements mapping
export const lambdaRequirementsMap: Record<LambdaName, LambdaRequirements> = {
  // Shared pre-ready lambdas
  comparePayload: {
    needsOrcabusApiTools: true,
  },
  getDraftPayload: {
    needsOrcabusApiTools: true,
  },
  findLatestWorkflow: {
    needsOrcabusApiTools: true,
  },
  getDragenOutputsFromPortalRunId: {
    needsOrcabusApiTools: true,
  },
  getWorkflowRunObject: {
    needsOrcabusApiTools: true,
  },
  generateWruEventObjectWithMergedData: {
    needsOrcabusApiTools: true,
  },
  getLatestPayloadFromPortalRunId: {
    needsOrcabusApiTools: true,
  },
  getAnalysisStorageSizeFromBasecountEst: {
    needsOrcabusApiTools: true,
  },
  // Glue lambdas
  // Draft Builder lambdas
  getFastqIdListFromRgidList: {
    needsOrcabusApiTools: true,
  },
  getFastqRgidsFromLibraryId: {
    needsOrcabusApiTools: true,
  },
  getLibraries: {
    needsOrcabusApiTools: true,
  },
  getMetadataTags: {
    needsOrcabusApiTools: true,
  },
  getPrefixFromProjectId: {
    needsOrcabusApiTools: true,
    needsIcav2Tools: true,
    needsHigherMemory: true,
  },
  getFastqListRowsFromFastqRgidList: {
    needsOrcabusApiTools: true,
    needsBucketEnvVars: true,
  },
  // Validate Draft Complete schema
  postSchemaValidation: {
    needsOrcabusApiTools: true,
    needsWorkflowEnvVars: true,
    needsBucketEnvVars: true,
    needsIcav2Tools: true,
    needsHigherMemory: true,
  },
  validateDraftDataCompleteSchema: {
    needsOrcabusApiTools: true,
    needsSchemaRegistryAccess: true,
    needsSsmParametersAccess: true,
    needsWorkflowEnvVars: true,
  },
  // Convert ready to ICAv2 WES Event - no requirements
  convertReadyEventInputsToIcav2WesEventInputs: {
    needsHigherMemory: true,
  },
  determineFastqCompressionType: {},
  generateFastqUriByFastqIdMap: {
    needsOrcabusApiTools: true,
  },
  collectOraOutputs: {
    needsOrcabusApiTools: true,
  },
  // Needs OrcaBus toolkit to get the wrsc event
  convertIcav2WesEventToWrscEvent: {
    needsOrcabusApiTools: true,
    needsWorkflowEnvVars: true,
  },
};

export interface BuildAllLambdasProps {
  refDataBucketName: string;
  testDataBucketName: string;
}

export interface BuildLambdaProps extends BuildAllLambdasProps {
  lambdaName: LambdaName;
}

export interface LambdaObject {
  lambdaName: LambdaName;
  lambdaFunction: PythonUvFunction;
}
