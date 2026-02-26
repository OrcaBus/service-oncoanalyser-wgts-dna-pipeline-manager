import { EventPattern, IEventBus, Rule } from 'aws-cdk-lib/aws-events';

/**
 * EventBridge Rules Interfaces
 */
export type EventBridgeRuleName =
  // Upstream Succeeded (Dragen WGTS DNA)
  | 'upstreamSucceededEvent'
  // Draft Rules
  | 'wrscDraft'
  // Pre-ready
  | 'wrscReady'
  // Post-submitted
  | 'icav2WesAnalysisStateChange';

export const eventBridgeRuleNameList: EventBridgeRuleName[] = [
  // Upstream Succeeded (Dragen WGTS DNA)
  'upstreamSucceededEvent',
  // Draft Rules
  'wrscDraft',
  // Pre-ready
  'wrscReady',
  // Post-submitted
  'icav2WesAnalysisStateChange',
];

export interface EventBridgeRuleProps {
  ruleName: EventBridgeRuleName;
  eventBus: IEventBus;
  eventPattern: EventPattern;
}

export interface EventBridgeRulesProps {
  eventBus: IEventBus;
}

export interface EventBridgeRuleObject {
  ruleName: EventBridgeRuleName;
  ruleObject: Rule;
}

export type BuildIcav2AnalysisStateChangeRuleProps = Omit<EventBridgeRuleProps, 'eventPattern'>;
export type BuildDraftRuleProps = Omit<EventBridgeRuleProps, 'eventPattern'>;
export type BuildReadyRuleProps = Omit<EventBridgeRuleProps, 'eventPattern'>;
