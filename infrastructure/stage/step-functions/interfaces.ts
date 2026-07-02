import { IEventBus } from 'aws-cdk-lib/aws-events';
import { StateMachine } from 'aws-cdk-lib/aws-stepfunctions';

import { LambdaName, LambdaObject } from '../lambda/interfaces';
import { SsmParameterPaths } from '../ssm/interfaces';

/**
 * Step Function Interfaces
 */
export type StateMachineName =
  // Glue code
  | 'glueSucceededEventsToDraftUpdate'
  // Draft populator
  | 'populateDraftData'
  // Validate draft data and put ready event
  | 'validateDraftDataAndPutReadyEvent'
  // Ready-to-Submitted
  | 'readyEventToIcav2WesRequestEvent'
  // Post-submission event conversion
  | 'icav2WesEventToWrscEvent';

export const stateMachineNameList: StateMachineName[] = [
  // Glue code
  'glueSucceededEventsToDraftUpdate',
  // Draft populator
  'populateDraftData',
  // Validate draft data and put ready event
  'validateDraftDataAndPutReadyEvent',
  // Ready-to-Submitted
  'readyEventToIcav2WesRequestEvent',
  // Post-submission event conversion
  'icav2WesEventToWrscEvent',
];

// Requirements interface for Step Functions
export interface StepFunctionRequirements {
  // Event stuff
  needsEventPutPermission?: boolean;
  // SSM Stuff
  needsSsmParameterStoreAccess?: boolean;
}

export interface StepFunctionInput {
  stateMachineName: StateMachineName;
}

export interface BuildStepFunctionProps extends StepFunctionInput {
  lambdaObjects: LambdaObject[];
  eventBus: IEventBus;
  ssmParameterPaths: SsmParameterPaths;
}

export interface StepFunctionObject extends StepFunctionInput {
  sfnObject: StateMachine;
}

export type WireUpPermissionsProps = BuildStepFunctionProps & StepFunctionObject;

export type BuildStepFunctionsProps = Omit<BuildStepFunctionProps, 'stateMachineName'>;

export const stepFunctionsRequirementsMap: Record<StateMachineName, StepFunctionRequirements> = {
  // Glue code
  glueSucceededEventsToDraftUpdate: {
    needsEventPutPermission: true,
  },
  // Draft populator
  populateDraftData: {
    needsEventPutPermission: true,
    needsSsmParameterStoreAccess: true,
  },
  // Validate draft data and put ready event
  validateDraftDataAndPutReadyEvent: {
    needsEventPutPermission: true,
  },
  // Ready-to-Submitted
  readyEventToIcav2WesRequestEvent: {
    needsEventPutPermission: true,
  },
  // Post-submission event conversion
  icav2WesEventToWrscEvent: {
    needsEventPutPermission: true,
  },
};

export const stepFunctionToLambdasMap: Record<StateMachineName, LambdaName[]> = {
  glueSucceededEventsToDraftUpdate: [
    // Shared lambdas
    'comparePayload',
    'getDraftPayload',
    'findLatestWorkflow',
    'getDragenOutputsFromPortalRunId',
    'getWorkflowRunObject',
    'generateWruEventObjectWithMergedData',
    'getLatestPayloadFromPortalRunId',
  ],
  populateDraftData: [
    // Shared lambdas
    'comparePayload',
    'getDraftPayload',
    'findLatestWorkflow',
    'getDragenOutputsFromPortalRunId',
    'getWorkflowRunObject',
    'generateWruEventObjectWithMergedData',
    'getLatestPayloadFromPortalRunId',
    'getAnalysisStorageSizeFromBasecountEst',
    'getMissingSchemaFields',
    // Draft Builder lambdas
    'getFastqIdListFromRgidList',
    'getFastqRgidsFromLibraryId',
    'getLibraries',
    'getMetadataTags',
    'getPrefixFromProjectId',
    'getFastqListRowsFromFastqRgidList',
    // Validation lambda
    'validateDraftDataCompleteSchema',
    // Commentary lambdas
    'addPopulateDraftComment',
  ],
  validateDraftDataAndPutReadyEvent: ['postSchemaValidation', 'validateDraftDataCompleteSchema'],
  readyEventToIcav2WesRequestEvent: [
    'addReadyComment',
    'convertReadyEventInputsToIcav2WesEventInputs',
    'determineFastqCompressionType',
    'getFastqIdListFromRgidList',
    'generateFastqUriByFastqIdMap',
    'collectOraOutputs',
  ],
  icav2WesEventToWrscEvent: ['convertIcav2WesEventToWrscEvent', 'addWesFailureComment'],
};
