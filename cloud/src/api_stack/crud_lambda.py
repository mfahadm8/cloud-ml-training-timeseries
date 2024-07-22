from aws_cdk import (
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_apigateway as apigateway,
    aws_apigatewayv2 as apigatewayv2,
    aws_ec2 as ec2,
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

    def __init__(self, scope: Construct, id: str, config: Dict) -> None:
        super().__init__(scope, id)
        self._config = config
        self.__create_crud_lambda()

    def __create_crud_lambda(self):
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

        self.crud_lambda = lambda_.Function(
            self,
            "MlCrudLambda"+self._config["stage"],
            function_name="MlCrudLambda"+self._config["stage"],
            runtime=lambda_.Runtime.PYTHON_3_10,
            handler="lambda_function.handler",
            environment={
                # "JOBS_TABLE": self._config["storage"]["db"]["JOBS_TABLE"],
                "BENCHMARK_TABLE": self._config["storage"]["db"]["BENCHMARKS_TABLE"]
            },
            code=lambda_.Code.from_asset(
                "assets/MlCrudLambda",
            ),
            log_retention=logs.RetentionDays.ONE_DAY,
            role=crud_role,
            memory_size=512,
            timeout=Duration.seconds(600),
        )
