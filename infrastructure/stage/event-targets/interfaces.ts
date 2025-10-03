import { StateMachine } from 'aws-cdk-lib/aws-stepfunctions';
import { Rule } from 'aws-cdk-lib/aws-events';
import { EventBridgeRuleObject } from '../event-rules/interfaces';
import { StepFunctionObject } from '../step-functions/interfaces';

/**
 * EventBridge Target Interfaces
 */
export type EventBridgeTargetName =
  // Dragen WGTS Succeeded
  | 'upstreamSucceededEventLegacyToGlueSucceededEvents'
  | 'upstreamSucceededEventToGlueSucceededEvents'
  // Populate draft data event targets
  | 'draftLegacyToPopulateDraftDataSfnTarget'
  | 'draftToPopulateDraftDataSfnTarget'
  // Validate draft to ready
  | 'draftLegacyToValidateDraftSfnTarget'
  | 'draftToValidateDraftSfnTarget'
  // Ready to ICAv2 WES Submitted
  | 'readyLegacyToIcav2WesSubmittedSfnTarget'
  | 'readyToIcav2WesSubmittedSfnTarget'
  // Post submission
  | 'icav2WesAnalysisStateChangeEventToWrscSfnTarget';

export const eventBridgeTargetsNameList: EventBridgeTargetName[] = [
  // Dragen WGTS Succeeded
  'upstreamSucceededEventLegacyToGlueSucceededEvents',
  'upstreamSucceededEventToGlueSucceededEvents',
  // Populate draft data event targets
  'draftLegacyToPopulateDraftDataSfnTarget',
  'draftToPopulateDraftDataSfnTarget',
  // Validate draft to ready
  'draftLegacyToValidateDraftSfnTarget',
  'draftToValidateDraftSfnTarget',
  // Ready to ICAv2 WES Submitted
  'readyLegacyToIcav2WesSubmittedSfnTarget',
  'readyToIcav2WesSubmittedSfnTarget',
  // Post submission
  'icav2WesAnalysisStateChangeEventToWrscSfnTarget',
];

export interface AddSfnAsEventBridgeTargetProps {
  stateMachineObj: StateMachine;
  eventBridgeRuleObj: Rule;
}

export interface EventBridgeTargetsProps {
  eventBridgeRuleObjects: EventBridgeRuleObject[];
  stepFunctionObjects: StepFunctionObject[];
}
