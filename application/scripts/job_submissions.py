import json
import boto3
from botocore.exceptions import NoCredentialsError
from datetime import datetime
import logging
import os

# Environment variables
BENCHMARKS_TABLE_NAME = os.environ.get("BENCHMARKS_TABLE", "benchmarks")
USER_SCRIPTS_BUCKET_NAME = os.environ.get("USER_SCRIPTS_BUCKET_NAME", "jkpfactors-user-scripts")
SUBMISSIONS_TABLE_NAME = os.environ.get("SUBMISSIONS_TABLE", "submissions")
STATE_MACHINE_ARN = os.environ.get("STATE_MACHINE_ARN")
AWS_BATCH_JOB_QUEUE = os.environ.get("AWS_BATCH_JOB_QUEUE")
AWS_BATCH_JOB_DEFINITION = os.environ.get("AWS_BATCH_JOB_DEFINITION")

# Initialize AWS clients
dynamodb = boto3.resource("dynamodb")
batch_client = boto3.client("batch")
sfn_client = boto3.client("stepfunctions")
benchmarks_table = dynamodb.Table(BENCHMARKS_TABLE_NAME)
submissions_table = dynamodb.Table(SUBMISSIONS_TABLE_NAME)

# Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def scan_dynamodb(users_filter_list, start_time=None, end_time=None):
    # Build scan filter
    filter_expression = []
    expression_attribute_values = {}

    if users_filter_list:
        filter_expression.append('email IN (:emails)')
        expression_attribute_values[':emails'] = users_filter_list
    
    if start_time:
        filter_expression.append('timestamp >= :start_time')
        expression_attribute_values[':start_time'] = start_time
    
    if end_time:
        filter_expression.append('timestamp <= :end_time')
        expression_attribute_values[':end_time'] = end_time
    
    filter_expression = ' AND '.join(filter_expression)
    
    # Scan DynamoDB
    try:
        response = benchmarks_table.scan(
            FilterExpression=filter_expression,
            ExpressionAttributeValues=expression_attribute_values
        )
        items = response['Items']
        logger.info(f"Scanned {len(items)} items from DynamoDB.")
        return items
    except Exception as e:
        logger.error(f"Error scanning DynamoDB: {e}")
        raise

def submit_batch_jobs(items, retrain, dataset_year, should_perform_complete_training, should_perform_integrity_check):
    for item in items:
        # Set environment variables
        job_environment = {
            "INTEGRITY_CHECK_DATA_S3_URI": f"s3://jkpfactors-training-data/complete/{dataset_year}",
            "COMPLETE_DATA_S3_URI": f"s3://jkpfactors-training-data/complete/{dataset_year}",
            "RETRAIN": 'True' if retrain else 'False',
            "SHOULD_PERFORM_INTEGRITY_CHECK": 'True' if should_perform_integrity_check else 'False',
            "SHOULD_PERFORM_COMPLETE_TRAINING": 'True' if should_perform_complete_training else 'False'
        }

        try:
            response = batch_client.submit_job(
                jobName=f"job-{str(uuid.uuid4())}",
                jobQueue=AWS_BATCH_JOB_QUEUE,
                jobDefinition=AWS_BATCH_JOB_DEFINITION,
                containerOverrides={
                    'environment': [
                        {'name': key, 'value': value}
                        for key, value in job_environment.items()
                    ]
                }
            )
            logger.info(f"Submitted AWS Batch job: {response['jobId']}")
        except Exception as e:
            logger.error(f"Error submitting AWS Batch job: {e}")
            raise

if __name__  == "__main__":
    # Parse event
    users_filter_list = ['mfahadm8@gmail.com'] # leave it empty if you want to retrain all current submisions between specified timestamp
    start_time_str = "" 
    end_time_str = "" # if not empty , would be curent time
    retrain = True
    should_perform_complete_training = True
    should_perform_integrity_check = True
    dataset_year= "2024" # change this to 2025 in future
    
    
    start_time = str(int(datetime.fromisoformat(start_time_str).timestamp())) # epoch timestamp in seconds, 1970 (start of epoch time)
    end_time = str(int(datetime.fromisoformat(start_time_str).timestamp()))

    # Scan DynamoDB
    items = scan_dynamodb(users_filter_list, start_time, end_time)
    
    # Submit AWS Batch jobs
    submit_batch_jobs(items, retrain, dataset_year, should_perform_complete_training, should_perform_integrity_check)
    
