/** Step Function stuff */
import {
  BuildStepFunctionProps,
  BuildStepFunctionsProps,
  stateMachineNameList,
  StepFunctionObject,
  stepFunctionsRequirementsMap,
  stepFunctionToLambdasMap,
  WireUpPermissionsProps,
} from './interfaces';
import { NagSuppressions } from 'cdk-nag';
import * as sfn from 'aws-cdk-lib/aws-stepfunctions';
import path from 'path';
import {
  EVENT_SOURCE,
  ICAV2_WES_REQUEST_DETAIL_TYPE,
  READY_STATUS,
  STACK_PREFIX,
  STEP_FUNCTIONS_DIR,
  WORKFLOW_RUN_STATE_CHANGE_DETAIL_TYPE,
} from '../constants';
import { Construct } from 'constructs';
import { camelCaseToSnakeCase } from '../utils';

function createStateMachineDefinitionSubstitutions(props: BuildStepFunctionProps): {
  [key: string]: string;
} {
  const definitionSubstitutions: { [key: string]: string } = {};

  const sfnRequirements = stepFunctionsRequirementsMap[props.stateMachineName];
  const lambdaFunctionNamesInSfn = stepFunctionToLambdasMap[props.stateMachineName];
  const lambdaFunctions = props.lambdaObjects.filter((lambdaObject) =>
    lambdaFunctionNamesInSfn.includes(lambdaObject.lambdaName)
  );

  /* Substitute lambdas in the state machine definition */
  for (const lambdaObject of lambdaFunctions) {
    const sfnSubtitutionKey = `__${camelCaseToSnakeCase(lambdaObject.lambdaName)}_lambda_function_arn__`;
    definitionSubstitutions[sfnSubtitutionKey] =
      lambdaObject.lambdaFunction.currentVersion.functionArn;
  }

  /* Sfn Requirements */
  if (sfnRequirements.needsEventPutPermission) {
    definitionSubstitutions['__event_bus_name__'] = props.eventBus.eventBusName;
    definitionSubstitutions['__workflow_run_state_change_event_detail_type__'] =
      WORKFLOW_RUN_STATE_CHANGE_DETAIL_TYPE;
    definitionSubstitutions['__icav2_wes_request_detail_type__'] = ICAV2_WES_REQUEST_DETAIL_TYPE;
    definitionSubstitutions['__stack_source__'] = EVENT_SOURCE;
    definitionSubstitutions['__ready_event_status__'] = READY_STATUS;
    definitionSubstitutions['__new_workflow_manager_is_deployed__'] =
      props.isNewWorkflowManagerDeployed.toString();
  }

  return definitionSubstitutions;
}

function wireUpStateMachinePermissions(props: WireUpPermissionsProps): void {
  /* Wire up lambda permissions */
  const sfnRequirements = stepFunctionsRequirementsMap[props.stateMachineName];

  const lambdaFunctionNamesInSfn = stepFunctionToLambdasMap[props.stateMachineName];
  const lambdaFunctions = props.lambdaObjects.filter((lambdaObject) =>
    lambdaFunctionNamesInSfn.includes(lambdaObject.lambdaName)
  );

  if (sfnRequirements.needsEventPutPermission) {
    props.eventBus.grantPutEventsTo(props.sfnObject);
  }

  /* Allow the state machine to invoke the lambda function */
  for (const lambdaObject of lambdaFunctions) {
    lambdaObject.lambdaFunction.currentVersion.grantInvoke(props.sfnObject);
  }
}

function buildStepFunction(scope: Construct, props: BuildStepFunctionProps): StepFunctionObject {
  const sfnNameToSnakeCase = camelCaseToSnakeCase(props.stateMachineName);

  /* Create the state machine definition substitutions */
  const stateMachine = new sfn.StateMachine(scope, props.stateMachineName, {
    stateMachineName: `${STACK_PREFIX}-${props.stateMachineName}`,
    definitionBody: sfn.DefinitionBody.fromFile(
      path.join(STEP_FUNCTIONS_DIR, sfnNameToSnakeCase + `_sfn_template.asl.json`)
    ),
    definitionSubstitutions: createStateMachineDefinitionSubstitutions(props),
  });

  /* Grant the state machine permissions */
  wireUpStateMachinePermissions({
    sfnObject: stateMachine,
    ...props,
  });

  /* Nag Suppressions */
  /* AwsSolutions-SF1 - We don't need ALL events to be logged */
  /* AwsSolutions-SF2 - We also don't need X-Ray tracing */
  NagSuppressions.addResourceSuppressions(
    stateMachine,
    [
      {
        id: 'AwsSolutions-SF1',
        reason: 'We do not need all events to be logged',
      },
      {
        id: 'AwsSolutions-SF2',
        reason: 'We do not need X-Ray tracing',
      },
    ],
    true
  );

  /* Return as a state machine object property */
  return {
    ...props,
    sfnObject: stateMachine,
  };
}

export function buildAllStepFunctions(
  scope: Construct,
  props: BuildStepFunctionsProps
): StepFunctionObject[] {
  const stepFunctionObjects: StepFunctionObject[] = [];

  for (const stepFunctionName of stateMachineNameList) {
    stepFunctionObjects.push(
      buildStepFunction(scope, {
        stateMachineName: stepFunctionName,
        lambdaObjects: props.lambdaObjects,
        eventBus: props.eventBus,
        isNewWorkflowManagerDeployed: props.isNewWorkflowManagerDeployed,
      })
    );
  }

  return stepFunctionObjects;
}
