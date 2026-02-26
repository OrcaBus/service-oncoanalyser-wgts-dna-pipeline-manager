import {
  AddSfnAsEventBridgeTargetProps,
  eventBridgeTargetsNameList,
  EventBridgeTargetsProps,
} from './interfaces';
import * as eventsTargets from 'aws-cdk-lib/aws-events-targets';
import * as events from 'aws-cdk-lib/aws-events';

export function buildWrscToSfnTarget(props: AddSfnAsEventBridgeTargetProps) {
  // We take in the event detail from the oncoanalyser wgts dna ready event
  // And return the entire detail to the state machine
  props.eventBridgeRuleObj.addTarget(
    new eventsTargets.SfnStateMachine(props.stateMachineObj, {
      input: events.RuleTargetInput.fromEventPath('$.detail'),
    })
  );
}

export function buildIcav2WesEventStateChangeToWrscSfnTarget(
  props: AddSfnAsEventBridgeTargetProps
) {
  // We take in the event detail from the icav2 wes state change event
  props.eventBridgeRuleObj.addTarget(
    new eventsTargets.SfnStateMachine(props.stateMachineObj, {
      input: events.RuleTargetInput.fromEventPath('$.detail'),
    })
  );
}

export function buildAllEventBridgeTargets(props: EventBridgeTargetsProps) {
  for (const eventBridgeTargetsName of eventBridgeTargetsNameList) {
    switch (eventBridgeTargetsName) {
      // Dragen Succeeded to Glue
      case 'upstreamSucceededEventToGlueSucceededEvents': {
        buildWrscToSfnTarget(<AddSfnAsEventBridgeTargetProps>{
          eventBridgeRuleObj: props.eventBridgeRuleObjects.find(
            (eventBridgeObject) => eventBridgeObject.ruleName === 'upstreamSucceededEvent'
          )?.ruleObject,
          stateMachineObj: props.stepFunctionObjects.find(
            (sfnObject) => sfnObject.stateMachineName === 'glueSucceededEventsToDraftUpdate'
          )?.sfnObject,
        });
        break;
      }

      // Draft to Populate Draft Data
      case 'draftToPopulateDraftDataSfnTarget': {
        buildWrscToSfnTarget(<AddSfnAsEventBridgeTargetProps>{
          eventBridgeRuleObj: props.eventBridgeRuleObjects.find(
            (eventBridgeObject) => eventBridgeObject.ruleName === 'wrscDraft'
          )?.ruleObject,
          stateMachineObj: props.stepFunctionObjects.find(
            (sfnObject) => sfnObject.stateMachineName === 'populateDraftData'
          )?.sfnObject,
        });
        break;
      }

      // Validate draft data
      case 'draftToValidateDraftSfnTarget': {
        buildWrscToSfnTarget(<AddSfnAsEventBridgeTargetProps>{
          eventBridgeRuleObj: props.eventBridgeRuleObjects.find(
            (eventBridgeObject) => eventBridgeObject.ruleName === 'wrscDraft'
          )?.ruleObject,
          stateMachineObj: props.stepFunctionObjects.find(
            (sfnObject) => sfnObject.stateMachineName === 'validateDraftToReady'
          )?.sfnObject,
        });
        break;
      }

      // Ready to Icav2 Wes Submitted
      case 'readyToIcav2WesSubmittedSfnTarget': {
        buildWrscToSfnTarget(<AddSfnAsEventBridgeTargetProps>{
          eventBridgeRuleObj: props.eventBridgeRuleObjects.find(
            (eventBridgeObject) => eventBridgeObject.ruleName === 'wrscReady'
          )?.ruleObject,
          stateMachineObj: props.stepFunctionObjects.find(
            (sfnObject) => sfnObject.stateMachineName === 'readyEventToIcav2WesRequestEvent'
          )?.sfnObject,
        });
        break;
      }

      // Post submitted
      case 'icav2WesAnalysisStateChangeEventToWrscSfnTarget': {
        buildIcav2WesEventStateChangeToWrscSfnTarget(<AddSfnAsEventBridgeTargetProps>{
          eventBridgeRuleObj: props.eventBridgeRuleObjects.find(
            (eventBridgeObject) => eventBridgeObject.ruleName === 'icav2WesAnalysisStateChange'
          )?.ruleObject,
          stateMachineObj: props.stepFunctionObjects.find(
            (sfnObject) => sfnObject.stateMachineName === 'icav2WesAscEventToWorkflowRscEvent'
          )?.sfnObject,
        });
        break;
      }
    }
  }
}
