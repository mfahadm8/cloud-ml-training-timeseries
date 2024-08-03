import boto3
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import json

def download_from_s3(s3_uri, local_path):
    s3 = boto3.client('s3')
    bucket, key = s3_uri.replace("s3://", "").split("/", 1)
    
    if not key.endswith('/'):
        s3.download_file(bucket, key, local_path)
    else:
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket, Prefix=key)
        
        for page in pages:
            for obj in page.get('Contents', []):
                file_key = obj['Key']
                if file_key.endswith('/'):
                    # Skip folders within the folder
                    continue
                # Create local directories if they do not exist
                local_file_path = os.path.join(local_path, os.path.relpath(file_key, key))
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                s3.download_file(bucket, file_key, local_file_path)


def upload_script_to_s3(script_file,output_file, bucket_name, email, submission_timestamp):
    s3 = boto3.client('s3')
    accepted_script_key = f"unprocessed/accepted/{email}/{submission_timestamp}/{script_file}"
    accepted_output_key = f"unprocessed/accepted/{email}/{submission_timestamp}/{output_file}"
    s3.upload_file(script_file, bucket_name, accepted_script_key)
    s3.upload_file(script_file, bucket_name, accepted_output_key)


def upload_weights_to_s3(bucket_name, email, submission_timestamp):
    s3 = boto3.client('s3')
    output_key = f"unprocessed/trainings/{email}/{submission_timestamp}/{'training_results.csv'}"
    s3.upload_file('data/training_results.csv', bucket_name, output_key)

def get_ssm_parameter(name):
    ssm_client = boto3.client('ssm',region_name="us-east-1")
    response = ssm_client.get_parameter(
        Name=name,
        WithDecryption=True
    )
    return response['Parameter']['Value']

def send_failure_email(email, message):
    # get SES SMTP email credentials from SSM Parameter Store
    smtp_username = get_ssm_parameter('SMTP_USER')
    smtp_password = get_ssm_parameter('SMTP_PASSWORD')
    smtp_host = get_ssm_parameter('SMTP_ENDPOINT')
    smtp_port = get_ssm_parameter('SMTP_PORT')

    # create email
    msg = MIMEMultipart()
    msg['From'] = "no-reply@jkpfactors.com"
    msg['To'] = email
    msg['Subject'] = "Script Integrity Check Failed"
    msg.attach(MIMEText(message, 'plain'))

    # send email
    server = smtplib.SMTP(smtp_host, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()

def store_sharpe_ratio_in_dynamodb(sharpe_ratio, submission_timestamp, email, user_name, model_name):
    dynamodb = boto3.client('dynamodb')
    dynamodb.put_item(
        TableName='benchmarks',
        Item={
            'sharpe': {'S': sharpe_ratio},
            'submission_timestamp': {'S': submission_timestamp},
            'email': {'S': email},
            'user_name': {'S': user_name},
            'model_name': {'S': model_name}
        }
    )
