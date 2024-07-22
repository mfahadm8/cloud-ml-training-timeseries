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

BENCHMARKS_TABLE_NAME = os.environ.get("BRANDS_TABLE","Brands-dev")
USER_SCRIPTS_BUCKET_NAME=os.environ.get("aquacontrol_blob_bucket","jkpfactors-user-scripts")

dynamodb = boto3.resource("dynamodb")
benchmarks_table = dynamodb.Table(BENCHMARKS_TABLE_NAME)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)


def generate_presigned_url(
    bucket_name, object_name, expiration_time=3600, action="put_object"
):
    s3_client = s3_client = boto3.client('s3', config=boto3.session.Config(signature_version='s3v4'))

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
    object_name = (
        f"unprocessed/submissions/{email}/{submission_timestamp}/{file_name}"
    )
    
    # Generate the pre-signed URL
    presigned_url = generate_presigned_url(USER_SCRIPTS_BUCKET_NAME, object_name)


    if presigned_url:
        print(f"Presigned URL: {presigned_url}")
        # Provide this URL to your client-side application for uploading the PDF.
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
        "body": json.dumps(
            {"brands": brands},
            cls=DecimalEncoder
        ),
    }

def add_submission():
     
     return {
            "statusCode": 200,
            "body": json.dumps("Job Submitted!"),
        }

def add_cors(response):
    response["headers"]= {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "OPTIONS, POST, GET, PUT, DELETE",
    }
    return response


def handler(event, context):
    logger.info(f"Got event: {event}")
    try:
        if event["httpMethod"] == "OPTIONS":
            # Handle preflight CORS request
            return {
                "statusCode": 200,
                'headers': {
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS, POST, GET, PUT, DELETE'
                },
            }
        elif event["httpMethod"] == "POST":
            if event["path"] == "/crud/submission":
                return add_cors(add_submission(event))
        elif event["httpMethod"] == "GET":
            if event["path"] == "/crud/benchmarks":
                return add_cors(get_benchmarks(event))
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
        return add_cors({"statusCode":500,"body": str(traceback.format_exc())})