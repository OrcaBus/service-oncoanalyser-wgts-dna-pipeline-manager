/* Event Bridge Rules */
import {
  BuildDraftRuleProps,
  BuildReadyRuleProps,
  BuildIcav2AnalysisStateChangeRuleProps,
  eventBridgeRuleNameList,
  EventBridgeRuleObject,
  EventBridgeRuleProps,
  EventBridgeRulesProps,
} from './interfaces';
import { EventPattern, Rule } from 'aws-cdk-lib/aws-events';
import * as events from 'aws-cdk-lib/aws-events';
import { Construct } from 'constructs';
import {
  DEFAULT_PAYLOAD_VERSION,
  DRAFT_STATUS,
  DRAGEN_WGTS_DNA_WORKFLOW_NAME,
  ICAV2_WES_EVENT_SOURCE,
  ICAV2_WES_STATE_CHANGE_DETAIL_TYPE,
  READY_STATUS,
  STACK_PREFIX,
  SUCCEEDED_STATUS,
  WORKFLOW_MANAGER_EVENT_SOURCE,
  WORKFLOW_NAME,
  WORKFLOW_RUN_STATE_CHANGE_DETAIL_TYPE,
} from '../constants';

/*
https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-create-pattern-operators.html
*/

function buildIcav2AnalysisStateChangeEventPattern(): EventPattern {
  return {
    detailType: [ICAV2_WES_STATE_CHANGE_DETAIL_TYPE],
    source: [ICAV2_WES_EVENT_SOURCE],
    detail: {
      name: [
        {
          wildcard: `*--${WORKFLOW_NAME}--*`,
        },
      ],
    },
  };
}

function buildUpstreamSucceededEventPattern(): EventPattern {
  return {
    detailType: [WORKFLOW_RUN_STATE_CHANGE_DETAIL_TYPE],
    source: [WORKFLOW_MANAGER_EVENT_SOURCE],
    detail: {
      workflow: {
        name: [DRAGEN_WGTS_DNA_WORKFLOW_NAME],
      },
      status: [SUCCEEDED_STATUS],
    },
  };
}

function buildWorkflowManagerDraftEventPattern(): EventPattern {
  return {
    detailType: [WORKFLOW_RUN_STATE_CHANGE_DETAIL_TYPE],
    source: [WORKFLOW_MANAGER_EVENT_SOURCE],
    detail: {
      workflow: {
        name: [WORKFLOW_NAME],
      },
      status: [DRAFT_STATUS],
    },
  };
}

function buildWorkflowManagerReadyEventPattern(): EventPattern {
  return {
    detailType: [WORKFLOW_RUN_STATE_CHANGE_DETAIL_TYPE],
    source: [WORKFLOW_MANAGER_EVENT_SOURCE],
    detail: {
      workflow: {
        name: [WORKFLOW_NAME],
      },
      status: [READY_STATUS],
      payload: {
        version: [DEFAULT_PAYLOAD_VERSION],
      },
    },
  };
}

function buildEventRule(scope: Construct, props: EventBridgeRuleProps): Rule {
  return new events.Rule(scope, props.ruleName, {
    ruleName: `${STACK_PREFIX}-${props.ruleName}`,
    eventPattern: props.eventPattern,
    eventBus: props.eventBus,
  });
}

function buildIcav2WesAnalysisStateChangeRule(
  scope: Construct,
  props: BuildIcav2AnalysisStateChangeRuleProps
): Rule {
  return buildEventRule(scope, {
    ruleName: props.ruleName,
    eventPattern: buildIcav2AnalysisStateChangeEventPattern(),
    eventBus: props.eventBus,
  });
}

function buildUpstreamSucceededWorkflowRunStateChangeEventRule(
  scope: Construct,
  props: BuildDraftRuleProps
): Rule {
  return buildEventRule(scope, {
    ruleName: props.ruleName,
    eventPattern: buildUpstreamSucceededEventPattern(),
    eventBus: props.eventBus,
  });
}

function buildWorkflowRunStateChangeDraftEventRule(
  scope: Construct,
  props: BuildDraftRuleProps
): Rule {
  return buildEventRule(scope, {
    ruleName: props.ruleName,
    eventPattern: buildWorkflowManagerDraftEventPattern(),
    eventBus: props.eventBus,
  });
}

function buildWorkflowRunStateChangeReadyEventRule(
  scope: Construct,
  props: BuildReadyRuleProps
): Rule {
  return buildEventRule(scope, {
    ruleName: props.ruleName,
    eventPattern: buildWorkflowManagerReadyEventPattern(),
    eventBus: props.eventBus,
  });
}

export function buildAllEventRules(
  scope: Construct,
  props: EventBridgeRulesProps
): EventBridgeRuleObject[] {
  const eventBridgeRuleObjects: EventBridgeRuleObject[] = [];

  // Iterate over the eventBridgeNameList and create the event rules
  for (const ruleName of eventBridgeRuleNameList) {
    switch (ruleName) {
      // Upstream Succeeded (Dragen WGTS DNA)
      case 'upstreamSucceededEvent': {
        eventBridgeRuleObjects.push({
          ruleName: ruleName,
          ruleObject: buildUpstreamSucceededWorkflowRunStateChangeEventRule(scope, {
            ruleName: ruleName,
            eventBus: props.eventBus,
          }),
        });
        break;
      }
      // Draft Rules
      case 'wrscDraft': {
        eventBridgeRuleObjects.push({
          ruleName: ruleName,
          ruleObject: buildWorkflowRunStateChangeDraftEventRule(scope, {
            ruleName: ruleName,
            eventBus: props.eventBus,
          }),
        });
        break;
      }
      // Pre-ready
      case 'wrscReady': {
        eventBridgeRuleObjects.push({
          ruleName: ruleName,
          ruleObject: buildWorkflowRunStateChangeReadyEventRule(scope, {
            ruleName: ruleName,
            eventBus: props.eventBus,
          }),
        });
        break;
      }
      // Post-submitted
      case 'icav2WesAnalysisStateChange': {
        eventBridgeRuleObjects.push({
          ruleName: ruleName,
          ruleObject: buildIcav2WesAnalysisStateChangeRule(scope, {
            ruleName: ruleName,
            eventBus: props.eventBus,
          }),
        });
      }
    }
  }

  // Return the event bridge rule objects
  return eventBridgeRuleObjects;
}
