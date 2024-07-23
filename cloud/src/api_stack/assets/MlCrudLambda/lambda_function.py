import json
import boto3
from botocore.exceptions import NoCredentialsError
from urllib.parse import urlparse
import logging
import os
from datetime import datetime
from decimal import Decimal
from urllib.parse import unquote
import traceback
import uuid
import jsonschema
from jsonschema import validate

# Environment variables
BENCHMARKS_TABLE_NAME = os.environ.get("BENCHMARKS_TABLE", "benchmarks")
USER_SCRIPTS_BUCKET_NAME = os.environ.get("USER_SCRIPTS_BUCKET_NAME", "jkpfactors-user-scripts")
SUBMISSIONS_TABLE_NAME = os.environ.get("SUBMISSIONS_TABLE", "submissions")

# Initialize DynamoDB
dynamodb = boto3.resource("dynamodb")
benchmarks_table = dynamodb.Table(BENCHMARKS_TABLE_NAME)
submissions_table = dynamodb.Table(SUBMISSIONS_TABLE_NAME)

# Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# JSON schema for validation
schema = {
    "type": "object",
    "properties": {
        "submission_timestamp": { "type": "string" },
        "user_ml_output_csv_s3_uri": { "type": "string" },
        "user_ml_script_s3_uri": { "type": "string" },
        "model_name": { "type": "string" },
        "user_name": { "type": "string" },
        "email": { "type": "string", "format": "email" }
    },
    "required": [
        "submission_timestamp",
        "user_ml_output_csv_s3_uri",
        "user_ml_script_s3_uri",
        "model_name",
        "user_name",
        "email"
    ]
}

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)

def generate_presigned_url(bucket_name, object_name, expiration_time=3600, action="put_object"):
    s3_client = boto3.client('s3', config=boto3.session.Config(signature_version='s3v4'))
    try:
        response = s3_client.generate_presigned_url(
            action,
            Params={"Bucket": bucket_name, "Key": object_name},
            ExpiresIn=expiration_time,
        )
        return response
    except NoCredentialsError:
        print("Credentials not available")
        return None

def get_file_upload_link(event):
    file_name = unquote(event.get("queryStringParameters", {}).get("file_name"))
    email = unquote(event.get("queryStringParameters", {}).get("email"))
    submission_timestamp = unquote(event.get("queryStringParameters", {}).get("submission_timestamp"))
    object_name = f"unprocessed/submissions/{email}/{submission_timestamp}/{file_name}"
    
    presigned_url = generate_presigned_url(USER_SCRIPTS_BUCKET_NAME, object_name)

    if presigned_url:
        print(f"Presigned URL: {presigned_url}")
        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "presigned_url": presigned_url,
                    "image_s3_path": f"s3://{USER_SCRIPTS_BUCKET_NAME}/{object_name}",
                }
            ),
        }
    else:
        print("Failed to generate presigned URL.")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to generate presigned URL"}),
        }

def get_benchmarks():
    benchmarks_response = benchmarks_table.scan()
    brands = benchmarks_response.get("Items", {})

    return {
        "statusCode": 200,
        "body": json.dumps({"brands": brands}, cls=DecimalEncoder),
    }

def add_submission(event):
    # Parse and validate the payload
    payload = json.loads(event["body"])
    try:
        validate(instance=payload, schema=schema)
    except jsonschema.exceptions.ValidationError as err:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Invalid payload: {err.message}"})
        }
    
    # Put the item in the DynamoDB table
    try:
        submissions_table.put_item(Item=payload)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Job Submitted!"})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Error adding submission: {e}"})
        }

def add_cors(response):
    response["headers"] = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "OPTIONS, POST, GET, PUT, DELETE",
    }
    return response

def handler(event, context):
    logger.info(f"Got event: {event}")
    try:
        if event["httpMethod"] == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "OPTIONS, POST, GET, PUT, DELETE"
                },
            }
        elif event["httpMethod"] == "POST":
            if event["path"] == "/crud/submission":
                return add_cors(add_submission(event))
        elif event["httpMethod"] == "GET":
            if event["path"] == "/crud/benchmarks":
                return add_cors(get_benchmarks())
            elif event["path"] == "/crud/get_file_upload_link":
                return add_cors(get_file_upload_link(event))
            return {
                "statusCode": 404,
                "body": json.dumps("Invalid API resource path!"),
            }
        else:
            return {
                "statusCode": 404,
                "body": json.dumps("Invalid Method type!"),
            }
    except Exception as e:
        return add_cors({
            "statusCode": 500,
            "body": json.dumps({"error": str(traceback.format_exc())})
        })
