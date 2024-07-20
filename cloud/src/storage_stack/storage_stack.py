# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import logging
import os

import aws_cdk as cdk
from aws_cdk import Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_fsx as fsx
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_ssm as ssm
from constructs import Construct

from typing import Dict

LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
logging.basicConfig(level=LOGLEVEL)
logger = logging.getLogger()
logger.setLevel(LOGLEVEL)


class StorageStack(Stack):
    """Storage layer of the solution."""

    ecr_registry = None
    scripts_s3_bucket = None
    training_data_s3_bucket = None
    ml_batch_jobs_bucket = None

    def __init__(self, scope: Construct, construct_id: str, config:Dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        scripts_s3_bucket = s3.Bucket.from_bucket_name(
            self,
            id="scripts-upload-bucket",
            bucket_name=config["storage"]["s3"]["scripts_upload_bucket"]
        )
        self.scripts_s3_bucket = scripts_s3_bucket

        training_data_s3_bucket = s3.Bucket.from_bucket_name(
            self,
            id="trainings-data-bucket",
            bucket_name=config["storage"]["s3"]["trainings_data_bucket"]
        )
        
        ml_batch_jobs_bucket = s3.Bucket.from_bucket_name(
            self,
            id="ml-batch-jobs-bucket",
            bucket_name=config["storage"]["s3"]["ml_batch_jobs_bucket"]
        )
        self.scripts_s3_bucket = scripts_s3_bucket
        self.training_data_s3_bucket = training_data_s3_bucket
        self.ml_batch_jobs_bucket = ml_batch_jobs_bucket

        # Containers registry
        ecr_registry = ecr.Repository(
            self,
            "ecr",
            repository_name="ml-batch-job-"+config["stage"]
        )
        self.ecr_registry = ecr_registry


        # Cloudformation outputs
        cdk.CfnOutput(
            self,
            "S3ScriptsBucket",
            value=scripts_s3_bucket.bucket_name,
            description="AWS Batch: Scripts Bucket",
        )
        cdk.CfnOutput(
            self,
            "S3TrainingDataBucket",
            value=training_data_s3_bucket.bucket_name,
            description="AWS Batch: Training Data Bucket",
        )
        cdk.CfnOutput(
            self,
            "S3MlBatchProcessingDataBucket",
            value=training_data_s3_bucket.bucket_name,
            description="AWS Batch: ML Batch Processing Bucket",
        )
        cdk.CfnOutput(
            self,
            "EcrRegistry",
            value=ecr_registry.repository_name,
            description="AWS Batch: Container registry",
        )
