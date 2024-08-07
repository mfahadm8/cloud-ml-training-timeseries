import copy
import os

import aws_cdk as cdk
from aws_cdk import Stack
from aws_cdk import aws_batch as batch
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3
from constructs import Construct

from typing import Dict

from .ml_batch_job import MlTrainingBatchJob


def concatenate_seq(sequences):
    iterable = iter(sequences)
    head = next(iterable)
    concatenated_sequence = copy.copy(head)
    for sequence in iterable:
        concatenated_sequence += sequence
    return concatenated_sequence


class BatchJobStack(Stack):
    """Main stack with AWS Batch."""

    # AWS Batch Jobs
    ml_jobs = []
    _xilinx_regions = ["us-west-2", "us-east-1", "eu-west-1"]
    _account = None
    _region = None

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.Vpc,
        config: Dict,
        ecr_registry: ecr.Repository,
        scripts_s3_bucket: s3.IBucket,
        training_data_s3_bucket: s3.IBucket,
        ml_batch_jobs_bucket: s3.IBucket,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self._account = config["aws_account"]
        self._region = config["aws_region"]

        subnet_selection = ec2.SubnetSelection(
            subnet_type=ec2.SubnetType.PUBLIC
        )

        # Security Group
        sg_batch = ec2.SecurityGroup(
            self,
            id="sg-batch",
            vpc=vpc,
            description="AWS Batch mltraining workers",
        )

        # IAM
        batch_instance_role = iam.Role(
            self,
            "batch-job-instance-role",
            description="AWS Batch for ML Training : IAM Instance Role used by Instance Profile in AWS Batch Compute Environment",
            assumed_by=iam.CompositePrincipal(
                iam.ServicePrincipal("ec2.amazonaws.com"),
                iam.ServicePrincipal("ecs.amazonaws.com"),
                iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            ),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonEC2ContainerServiceforEC2Role"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AWSXrayWriteOnlyAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSESFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess"),
            ],
        )

        training_data_s3_bucket.grant_read_write(batch_instance_role)
        scripts_s3_bucket.grant_read_write(batch_instance_role)
        ml_batch_jobs_bucket.grant_read_write(batch_instance_role)

        lustre_fs = None

        batch_job_role = iam.Role(
            self,
            "batch-job-role",
            description="AWS Batch for ML Training : IAM Role for Batch Container Job Definition",
            assumed_by=iam.CompositePrincipal(
                iam.ServicePrincipal("ecs.amazonaws.com"),
                iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            ),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AmazonECSTaskExecutionRolePolicy"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AWSXrayWriteOnlyAccess"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonEC2ContainerServiceforEC2Role"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AWSXrayWriteOnlyAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSESFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess"),
            ],
            inline_policies={
                "get-ssm-parameters": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "ssm:GetParameters",
                                "ssm:GetParameter",
                                "ssm:GetParametersByPath",
                                "secretsmanager:GetSecretValue",
                                "kms:Decrypt",
                            ],
                            resources=[
                                f"arn:aws:ssm:{self._region}:{self._account}:parameter/batch-mltraining/*",
                                f"arn:aws:ssm:{self._region}:{self._account}:parameter/batch-mltraining",
                            ],
                        )
                    ]
                )
            }
        )

        training_data_s3_bucket.grant_read_write(batch_job_role)
        scripts_s3_bucket.grant_read_write(batch_job_role)
        ml_batch_jobs_bucket.grant_read_write(batch_job_role)

        batch_execution_role = iam.Role(
            self,
            "batch-mltraining-job-execution-role",
            description="AWS Batch for ML Training : IAMExecution Role for Batch Container Job Definition",
            assumed_by=iam.CompositePrincipal(
                iam.ServicePrincipal("ecs.amazonaws.com"),
                iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            ),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AmazonECSTaskExecutionRolePolicy"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AWSXrayWriteOnlyAccess"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonSSMReadOnlyAccess"
                ),
            ],
        )

        ecs_nvidia_ami = ec2.MachineImage.from_ssm_parameter(
            "/aws/service/ecs/optimized-ami/amazon-linux-2/gpu/recommended/image_id"
        )

        batch_compute_instance_classes_nvidia = [ec2.InstanceClass.G4DN]
        if self._region not in ["eu-west-3"]:
            instances_classes_not_available = [ec2.InstanceClass.G5]
            batch_compute_instance_classes_nvidia = concatenate_seq([
                batch_compute_instance_classes_nvidia,
                instances_classes_not_available,
            ])

        mltraining_python_script_command = [
            "python",
            "run.py",
            "--user_ml_script_s3_uri",
            "Ref::user_ml_script_s3_uri",
            "--user_ml_output_csv_s3_uri",
            "Ref::user_ml_output_csv_s3_uri",
            "--model_name",
            "Ref::model_name",
            "--user_name",
            "Ref::user_name",
            "--email",
            "Ref::email",
            "--submission_timestamp",
            "Ref::submission_timestamp",
        ]

        mltraining_python_script_default_values = {
            "user_ml_script_s3_uri": "null",
            "user_ml_output_csv_s3_uri": "null",
            "model_name": "null",
            "user_name": "null",
            "email": "null",
            "submission_timestamp": "null",
        }

        job_definition_container_env_base = {
            "AWS_XRAY_SDK_ENABLED": "true",
            "S3_BUCKET": ml_batch_jobs_bucket.bucket_name,
            "USER_SCRIPTS_BUCKET_NAME": scripts_s3_bucket.bucket_name,
            "AWS_DEFAULT_REGION": config["aws_region"],
        }

        batchjob_env = config["compute"]["batchjob"]["env"]
        for key, value in batchjob_env.items():
            job_definition_container_env_base[key] = value

        job_definition_container_env = job_definition_container_env_base.copy()
        lustre_volumes = None

        nvidia_tag = "latest"
        batch_jobdef_nvidia_container = batch.EcsEc2ContainerDefinition(
            self,
            "container-def-nvidia",
            image=ecs.ContainerImage.from_ecr_repository(ecr_registry, nvidia_tag),
            command=mltraining_python_script_command,
            environment=job_definition_container_env,
            execution_role=batch_execution_role,
            job_role=batch_job_role,
            gpu=1,
            cpu=4,
            memory=cdk.Size.mebibytes(8192),
            volumes=lustre_volumes,
        )

        self.mltraining_nvidia_job = MlTrainingBatchJob(
            self,
            construct_id="nvidia-job",
            proc_name="nvidia",
            config=config,
            ec2_ami=ecs_nvidia_ami,
            ec2_vpc=vpc,
            ec2_vpc_sg=sg_batch,
            ec2_vpc_subnets=subnet_selection,
            batch_compute_instance_classes=batch_compute_instance_classes_nvidia,
            batch_jobdef_container=batch_jobdef_nvidia_container,
            batch_jobdef_parameters=mltraining_python_script_default_values,
            batch_compute_env_instance_role=batch_instance_role,
            lustre_fs=lustre_fs,
        )
        self.ml_jobs.append(self.mltraining_nvidia_job)
