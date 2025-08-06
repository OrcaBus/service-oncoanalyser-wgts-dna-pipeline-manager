import { IEventBus } from 'aws-cdk-lib/aws-events';
import { StateMachine } from 'aws-cdk-lib/aws-stepfunctions';

import { LambdaName, LambdaObject } from '../lambda/interfaces';

/**
 * Step Function Interfaces
 */
export type StateMachineName =
  // Ready-to-Submitted
  | 'readyEventToIcav2WesRequestEvent'
  // Post-submission event conversion
  | 'icav2WesAscEventToWorkflowRscEvent';

export const stateMachineNameList: StateMachineName[] = [
  // Ready-to-Submitted
  'readyEventToIcav2WesRequestEvent',
  // Post-submission event conversion
  'icav2WesAscEventToWorkflowRscEvent',
];

// Requirements interface for Step Functions
export interface StepFunctionRequirements {
  // Event stuff
  needsEventPutPermission?: boolean;
}

export interface StepFunctionInput {
  stateMachineName: StateMachineName;
}

export interface BuildStepFunctionProps extends StepFunctionInput {
  lambdaObjects: LambdaObject[];
  eventBus: IEventBus;
  isNewWorkflowManagerDeployed: boolean;
}

export interface StepFunctionObject extends StepFunctionInput {
  sfnObject: StateMachine;
}

export type WireUpPermissionsProps = BuildStepFunctionProps & StepFunctionObject;

export type BuildStepFunctionsProps = Omit<BuildStepFunctionProps, 'stateMachineName'>;

export const stepFunctionsRequirementsMap: Record<StateMachineName, StepFunctionRequirements> = {
  readyEventToIcav2WesRequestEvent: {
    needsEventPutPermission: true,
  },
  icav2WesAscEventToWorkflowRscEvent: {
    needsEventPutPermission: true,
  },
};

export const stepFunctionToLambdasMap: Record<StateMachineName, LambdaName[]> = {
  readyEventToIcav2WesRequestEvent: ['convertReadyEventInputsToIcav2WesEventInputs'],
  icav2WesAscEventToWorkflowRscEvent: ['convertIcav2WesEventToWrscEvent'],
};
