# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import os
import random
import string

from aws_cdk import Stack
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_stepfunctions as stepfunctions
from constructs import Construct
from from_root import from_here

from typing import Dict


class SfnStack(Stack):
    """AWS Step Function executes AWS Batch ML Trainings jobs for a list of S3
    objects."""

    sfn_state_machine = None   

    def __init__(
        self, scope: Construct, construct_id: str, config:Dict,s3_bucket: s3.IBucket,job_definition_name:str,job_queue_name:str,**kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        account=config["aws_account"]
        region=config["aws_region"]

        # IAM
        iam_role_state = iam.Role(
            self,
            "state-role-"+config["stage"],
            description="AWS Batch ML Trainings : IAM Role used by AWS Step Functions ",
            assumed_by=iam.ServicePrincipal("states.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AWSXrayWriteOnlyAccess"
                ),
            ],
            inline_policies={
                "batch-job-management": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "batch:SubmitJob",
                                "batch:DescribeJobs",
                                "batch:TerminateJob",
                            ],
                            resources=["*"],
                        ),
                        iam.PolicyStatement(
                            actions=[
                                "events:PutTargets",
                                "events:PutRule",
                                "events:DescribeRule",
                            ],
                            resources=[
                                f"arn:aws:events:{region}:{account}:rule/StepFunctionsGetEventsForBatchJobsRule"
                            ],
                        ),
                    ]
                ),
                "step-start-execution": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=["states:StartExecution"],
                            resources=[
                                f"arn:aws:states:{region}:{account}:stateMachine:batch-mltraining-state-machine-"+config["stage"]
                            ],
                        ),
                        iam.PolicyStatement(
                            actions=[
                                "states:DescribeExecution",
                                "states:StopExecution",
                            ],
                            resources=["*"],
                        ),
                        iam.PolicyStatement(
                            actions=[
                                "events:PutTargets",
                                "events:PutRule",
                                "events:DescribeRule",
                            ],
                            resources=[
                                f"arn:aws:events:{region}:{account}:rule/StepFunctionsGetEventsForStepFunctionsExecutionRule"
                            ],
                        ),
                    ]
                ),
            },
        )
        s3_bucket.grant_read_write(iam_role_state)

        # Logs
        uid = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=5)  # nosec CWE-330
        )
        log_group = logs.LogGroup(
            self,
            "sfn-logs",
            log_group_name=f"/aws/vendedlogs/states/batch-mltraining-{uid}-"+config["stage"],
        )

        # State Machine
        self.sfn_state_machine = stepfunctions.StateMachine(
            self,
            "main",
            comment="AWS Batch ML Trainings Stack",
            tracing_enabled=True,
            role=iam_role_state,
            logs=stepfunctions.LogOptions(
                destination=log_group, level=stepfunctions.LogLevel.ALL
            ),
            state_machine_name="batch-mltraining-state-machine-"+config["stage"],
            definition_body=stepfunctions.DefinitionBody.from_file(
                from_here("assets","main_state.asl.json").as_posix()
            ),
            definition_substitutions={"REGION": region, "ACCOUNT": account,"STAGE":config["stage"],"JOB_QUEUE":job_queue_name,"JOB_DEFINITION":job_definition_name},
        )
