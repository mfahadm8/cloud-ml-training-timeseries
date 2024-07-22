import aws_cdk as cdk
from aws_cdk import Stack
from aws_cdk import aws_apigateway as apig
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as cwlogs
from aws_cdk import aws_stepfunctions as sfn
from constructs import Construct
from typing import Dict, List
import time

from .crud_lambda import CrudLambda
class ApiStack(Stack):
    """API Gateway of the solution."""
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        config: Dict,
        ml_jobs: List,
        sfn_state_machine: sfn.IStateMachine,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self._account = config["aws_account"]
        self._region = config["aws_region"]
        
        api_role = iam.Role(
            self,
            "RestAPIRole",
            assumed_by=iam.ServicePrincipal("apigateway.amazonaws.com"),
        )

        api = apig.RestApi(
            self,
            "api-batch-mltraining",
            rest_api_name="api-batch-mltraining-" + config["stage"],
            description="ML training managed by AWS Batch",
            deploy_options=apig.StageOptions(
                metrics_enabled=True,
                caching_enabled=True,
                cache_data_encrypted=True,
                logging_level=apig.MethodLoggingLevel.INFO,
                tracing_enabled=True,
                access_log_destination=apig.LogGroupLogDestination(
                    cwlogs.LogGroup(self, "prod-api-logs")
                ),
            ),
        )

        
        self._api_sfn_execute(api, api_role, sfn_state_machine)
        self._api_crud(api,config)

        cdk.CfnOutput(
            self,
            "batch-mltraining-api",
            export_name="mltraining-batch-api",
            value=api.url,
            description="ML training Batch API",
        )
        cdk.CfnOutput(
            self,
            "batch-mltraining-api-id",
            export_name="mltraining-batch-api-id",
            value=api.rest_api_id,
            description="ML training Batch API ID",
        )

    def _api_sfn_execute(
        self,
        api: apig.RestApi,
        api_role: iam.IRole,
        sfn_state_machine: sfn.IStateMachine,
    ):
        api_resource = api.root.add_resource("state")
        api_role.add_to_policy(
            iam.PolicyStatement(
                actions=["states:StartExecution"],
                resources=[f"{sfn_state_machine.state_machine_arn}"],
            )
        )

        api_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AWSStepFunctionsFullAccess"))

        request_model = api.add_model(
            "sfn-request-model",
            content_type="application/json",
            schema=apig.JsonSchema(
                schema=apig.JsonSchemaVersion.DRAFT4,
                title="sfn-request-schema",
                type=apig.JsonSchemaType.OBJECT,
                properties={
                    "name": apig.JsonSchema(type=apig.JsonSchemaType.STRING),
                    "compute": apig.JsonSchema(type=apig.JsonSchemaType.STRING),
                    "user_ml_output_csv_s3_uri": apig.JsonSchema(type=apig.JsonSchemaType.STRING),
                    "user_ml_script_s3_uri": apig.JsonSchema(type=apig.JsonSchemaType.STRING),
                    "model_name": apig.JsonSchema(type=apig.JsonSchemaType.STRING),
                    "user_name": apig.JsonSchema(type=apig.JsonSchemaType.STRING),
                    "email": apig.JsonSchema(type=apig.JsonSchemaType.STRING),
                },
                required=[
                    "name", "compute", "user_ml_output_csv_s3_uri",
                    "user_ml_script_s3_uri", "model_name", "user_name", "email"
                ],
            ),
        )

        time.strftime("%Y%m%d-%H%M%S")
        integration_request_mapping_template = f"""
            #set($data = $util.escapeJavaScript($input.json('$')))
            {{
                "input": "$data",
                "stateMachineArn": "{sfn_state_machine.state_machine_arn}"
              }}
          """
        integration_response_mapping_template = """
          {
              "executionArn":$input.json('$.executionArn')
          }
          """
        integration_response = apig.IntegrationResponse(
            status_code="200",
            response_templates={
                "application/json": integration_response_mapping_template
            },
        )

        api_integration_options = apig.IntegrationOptions(
            credentials_role=api_role,
            integration_responses=[integration_response],
            request_templates={
                "application/json": integration_request_mapping_template
            },
            passthrough_behavior=apig.PassthroughBehavior.NEVER,
            request_parameters={
                "integration.request.header.Content-Type": "'application/x-www-form-urlencoded'"
            },
        )

        # https://docs.aws.amazon.com/fr_fr/step-functions/latest/dg/tutorial-api-gateway.html
        api_integration = apig.AwsIntegration(
            service="states",
            action="StartExecution",
            options=api_integration_options,
        )
        # Step Function API
        method_response = apig.MethodResponse(
            status_code="200",
        )
        api_resource_execute = api_resource.add_resource("execute")
        api_resource_execute.add_method(
            "POST",
            integration=api_integration,
            method_responses=[method_response],
            authorization_type=apig.AuthorizationType.IAM,
            request_models={"application/json": request_model},
            request_parameters=None,
            request_validator=apig.RequestValidator(
                self,
                "sfn-execution-body-validator",
                rest_api=api,
                validate_request_body=True,
                validate_request_parameters=True,
            ),
        )


    def _api_crud(self, api: apig.RestApi,config):
        crud_lambda = CrudLambda(self, "MlCrudLambda", config)
        # Add Lambda Integration
        integration_crud = apig.LambdaIntegration(
            crud_lambda,
            integration_responses=[
                {
                    "statusCode": "200",
                }
            ],
        )

        resource_crud_base = api.root.add_resource("crud")
        resource_crud_proxy = resource_crud_base.add_resource("{proxy+}")
        crud_method = resource_crud_proxy.add_method(
            "ANY",
            integration_crud,
            method_responses=[
                {
                    "statusCode": "200",
                }
            ],
        )