#!/usr/bin/env python3

import sys
from aws_cdk import App, Environment

from src.network_stack.network_stack import NetworkStack
from src.storage_stack.storage_stack import StorageStack
from src.api_stack.api_stack import ApiStack
from src.batch_stack.batch_stack import BatchJobStack
from src.sfn_stack.sfn_stack import SfnStack

import aws_cdk.aws_servicecatalogappregistry_alpha as appreg

from utils import config_util

app = App()

# Get target stage from cdk context
stage = app.node.try_get_context("stage")
if stage is None or stage == "unknown":
    sys.exit(
        "You need to set the target stage." " USAGE: cdk <command> -c stage=dev <stack>"
    )

# Load stage config and set cdk environment
config = config_util.load_config(stage)
env = Environment(
    account=config["aws_account"],
    region=config["aws_region"],
)

network_stack = NetworkStack(
    app, "network-stack-" + config["stage"], config=config, env=env
)

storage_stack = StorageStack(
    app,
    "batch-storage-stack-"+config["stage"],
    env=env,
    config=config,
    description="AWS Batch ML Training"
)

batch_stack = BatchJobStack(
    app,
    "batch-job-stack-"+config["stage"],
    ecr_registry=storage_stack.ecr_registry,
    env=env,
    config=config,
    vpc=network_stack.vpc,
    scripts_s3_bucket=storage_stack.scripts_s3_bucket,
    training_data_s3_bucket=storage_stack.training_data_s3_bucket,
    ml_batch_jobs_bucket = storage_stack.ml_batch_jobs_bucket,
    description="AWS Batch for ML Training: Main stack",
)


sfn_stack = SfnStack(
    app,
    "batch-mltraining-sfn-stack-"+config["stage"],
    config=config,
    s3_bucket=storage_stack.ml_batch_jobs_bucket,
    job_definition_name=batch_stack.mltraining_nvidia_job.job_definition_name,
    job_queue_name=batch_stack.mltraining_nvidia_job.job_queue_name,
    env=env,
    description="AWS Batch ML Training : AWS Step Functions",
)

api_stack = ApiStack(
    app,
    "batch-mltraining-api-stack-"+config["stage"],
    ml_jobs=batch_stack.ml_jobs,
    sfn_state_machine=sfn_stack.sfn_state_machine,
    env=env,
    config=config,
    description="AWS Batch ML Training : API Gateway",
)

# application = appreg.ApplicationAssociator(
#     app,
#     "batch-mltraining-app-"+config["stage"],
#     applications=[
#         appreg.TargetApplication.create_application_stack(
#             application_name="batch-mltraining",
#             description="AWS Batch ML Training : Application",
#             stack_name="batch-mltraining-application",
#             env=env,
#         )
#     ],
# )
# application.node.add_dependency(network_stack)
# application.node.add_dependency(storage_stack)
# application.node.add_dependency(api_stack)
# application.node.add_dependency(batch_stack)

app.synth()
