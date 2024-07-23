import boto3

def upload_script_to_s3(script_file,output_file, bucket_name, email, submission_timestamp):
    s3 = boto3.client('s3')
    accepted_script_key = f"unprocessed/accepted/{email}/{submission_timestamp}/{script_file}"
    accepted_output_key = f"unprocessed/accepted/{email}/{submission_timestamp}/{output_file}"
    s3.upload_file(script_file, bucket_name, accepted_script_key)
    s3.upload_file(script_file, bucket_name, accepted_output_key)

def send_failure_email(email, message):
    ses = boto3.client('ses')
    ses.send_email(
        Source='your-email@example.com',
        Destination={
            'ToAddresses': [email],
        },
        Message={
            'Subject': {
                'Data': 'Script Integrity Check Failed',
            },
            'Body': {
                'Text': {
                    'Data': message,
                },
            },
        }
    )

def store_sharpe_ratio_in_dynamodb(sharpe_ratio, submission_timestamp, email, user_name, model_name):
    dynamodb = boto3.client('dynamodb')
    dynamodb.put_item(
        TableName='benchmarks',
        Item={
            'SharpeRatio': {'S': sharpe_ratio},
            'SubmissionTimestamp': {'S': submission_timestamp},
            'Email': {'S': email},
            'UserName': {'S': user_name},
            'ModelName': {'S': model_name}
        }
    )
