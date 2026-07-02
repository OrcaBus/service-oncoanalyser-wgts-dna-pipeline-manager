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
  | 'getMissingSchemaFields'
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
  // Commentary lambdas
  | 'addPopulateDraftComment'
  | 'addReadyComment'
  | 'addWesFailureComment'
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
  'getMissingSchemaFields',
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
  // Commentary lambdas
  'addPopulateDraftComment',
  'addReadyComment',
  // Ready to ICAv2 WES lambdas
  'convertReadyEventInputsToIcav2WesEventInputs',
  'determineFastqCompressionType',
  'generateFastqUriByFastqIdMap',
  'collectOraOutputs',
  // ICAv2 WES to WRSC Event lambdas
  'convertIcav2WesEventToWrscEvent',
  'addWesFailureComment',
];

// Requirements interface for Lambda functions
export interface LambdaRequirements {
  needsOrcabusApiTools?: boolean;
  needsIcav2Tools?: boolean;
  needsHigherMemory?: boolean;
  needsSsmParametersAccess?: boolean;
  needsSchemaRegistryAccess?: boolean;
  needsExternalBucketInfo?: boolean;
  needsWorkflowInfo?: boolean;
  needsRepoUrl?: boolean;
}

// Lambda requirements mapping
export const lambdaRequirementsMap: Record<LambdaName, LambdaRequirements> = {
  // Shared pre-ready lambdas
  comparePayload: {},
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
  getMissingSchemaFields: {
    needsSchemaRegistryAccess: true,
    needsSsmParametersAccess: true,
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
  },
  getFastqListRowsFromFastqRgidList: {
    needsOrcabusApiTools: true,
    needsExternalBucketInfo: true,
  },
  // Validate Draft Complete schema
  postSchemaValidation: {
    needsOrcabusApiTools: true,
    needsWorkflowInfo: true,
    needsExternalBucketInfo: true,
    needsIcav2Tools: true,
  },
  validateDraftDataCompleteSchema: {
    needsOrcabusApiTools: true,
    needsSchemaRegistryAccess: true,
    needsSsmParametersAccess: true,
    needsWorkflowInfo: true,
  },
  // Commentary lambdas
  addPopulateDraftComment: {
    needsOrcabusApiTools: true,
    needsWorkflowInfo: true,
    needsRepoUrl: true,
  },
  addReadyComment: {
    needsOrcabusApiTools: true,
    needsWorkflowInfo: true,
  },
  // Convert ready to ICAv2 WES Event - no requirements
  convertReadyEventInputsToIcav2WesEventInputs: {
    needsOrcabusApiTools: true,
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
    needsWorkflowInfo: true,
  },
  addWesFailureComment: {
    needsOrcabusApiTools: true,
    needsWorkflowInfo: true,
  },
};

export interface LambdaInput {
  lambdaName: LambdaName;
}

export interface LambdaObject extends LambdaInput {
  lambdaFunction: PythonUvFunction;
}
