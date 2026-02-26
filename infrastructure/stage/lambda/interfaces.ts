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
  // Validation lambda
  | 'validateDraftDataCompleteSchema'
  // Ready to ICAv2 WES lambdas
  | 'convertReadyEventInputsToIcav2WesEventInputs'
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
  // Validate Draft Complete Schema
  'validateDraftDataCompleteSchema',
  // Ready to ICAv2 WES lambdas
  'convertReadyEventInputsToIcav2WesEventInputs',
  // ICAv2 WES to WRSC Event lambdas
  'convertIcav2WesEventToWrscEvent',
];

// Requirements interface for Lambda functions
export interface LambdaRequirements {
  needsOrcabusApiTools?: boolean;
  needsSsmParametersAccess?: boolean;
  needsSchemaRegistryAccess?: boolean;
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
  // Validate Draft Complete schema
  validateDraftDataCompleteSchema: {
    needsSchemaRegistryAccess: true,
    needsSsmParametersAccess: true,
  },
  // Convert ready to ICAv2 WES Event - no requirements
  convertReadyEventInputsToIcav2WesEventInputs: {},
  // Needs OrcaBus toolkit to get the wrsc event
  convertIcav2WesEventToWrscEvent: {
    needsOrcabusApiTools: true,
  },
};

export interface LambdaInput {
  lambdaName: LambdaName;
}

export interface LambdaObject extends LambdaInput {
  lambdaFunction: PythonUvFunction;
}
