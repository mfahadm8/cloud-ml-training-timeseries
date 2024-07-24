from aws_cdk import (
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_apigateway as apigateway,
    aws_apigatewayv2 as apigatewayv2,
    aws_ec2 as ec2,
    aws_stepfunctions as sfn,
    Duration,
    CfnOutput,
    BundlingOptions,
    DockerImage,
    aws_logs as logs,
)
from typing import Dict
from constructs import Construct


class CrudLambda(Construct):
    _config: Dict

    def __init__(self, scope: Construct, id: str, config: Dict, sfn_state_machine: sfn.IStateMachine) -> None:
        super().__init__(scope, id)
        self._config = config
        self.__create_crud_lambda(sfn_state_machine)

    def __create_crud_lambda(self,sfn_state_machine:sfn.IStateMachine):
        # Create IAM Role for Lambda
        crud_role = iam.Role(
            self,
            "CrudLambdaRole"+self._config["stage"],
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            inline_policies={
                "CrudLambdaPermissions": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                                "logs:DescribeLogGroups",
                                "s3:*",
                                "dynamodb:*",
                                "lambda:*",
                            ],
                            effect=iam.Effect.ALLOW,
                            resources=["*"],
                        )
                    ]
                )
            },
            role_name="CrudLambdaRole"+self._config["stage"]
        )
        crud_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AWSStepFunctionsFullAccess"))
        
        self.crud_lambda = lambda_.Function(
            self,
            "MlCrudLambda"+self._config["stage"],
            function_name="MlCrudLambda"+self._config["stage"],
            runtime=lambda_.Runtime.PYTHON_3_10,
            handler="lambda_function.handler",
            environment={
                "USER_SCRIPTS_BUCKET_NAME": self._config["storage"]["s3"]["scripts_upload_bucket"],
                "BENCHMARKS_TABLE": self._config["storage"]["db"]["benchmarks_table"],
                "SUBMISSIONS_TABLE": self._config["storage"]["db"]["submissions_table"],
                "STATE_MACHINE_ARN": sfn_state_machine.state_machine_arn

            },
            code=lambda_.Code.from_asset(
                "src/api_stack/assets/MlCrudLambda",
                bundling=BundlingOptions(
                    image=DockerImage("python:3.10"),
                    command=[
                        "bash",
                        "-c",
                        "cp -r /asset-input/. /asset-output/. && cp -r /asset-input/*.py /asset-output/.  && pip install -r /asset-input/requirements.txt -t /asset-output",
                    ],
                    user="root",
                ),
            ),
            log_retention=logs.RetentionDays.ONE_DAY,
            role=crud_role,
            memory_size=512,
            timeout=Duration.seconds(600),
        )
