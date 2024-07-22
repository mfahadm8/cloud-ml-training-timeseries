import boto3
import subprocess  # nosec B404
import os
import sys
from checks.evalution_criteria import calculate_sharpe_ratio
from checks.runtime_checks import run_script_in_docker
from checks.static_checks import perform_static_checks
from utils.replace_func import update_script_with_template_functions


USER_SCRIPTS_BUCKET_NAME = os.environ.get("USER_SCRIPTS_BUCKET_NAME", "jkpfactors-user-scripts")
INTEGRITY_CHECK_DATA_S3_URI = "s3://jkpfactors-training-data/integrity-check/"
INTEGRITY_CHECK_DATA_LOCAL_PATH = "integrity-check/"
COMPLETE_DATA_S3_URI = "s3://jkpfactors-training-data/complete/"
COMPLETE_DATA_PATH = "data/"
SHOULD_PERFORM_COMPLETE_TRAINING= os.environ.get("SHOULD_PERFORM_COMPLETE_TRAINING",True)

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

def perform_integrity_check(script_file, output_file):
    # Step 1: Static Checks
    is_valid, message = perform_static_checks(script_file)
    if not is_valid:
        return False, message
    
    # Step 2: Runtime Checks
    is_valid, message = run_script_in_docker()
    if not is_valid:
        return False, message
    
    # Step 3: Evaluation Criteria
    is_valid, message = calculate_sharpe_ratio(output_file)
    if not is_valid:
        return False, message
    
    return True, "All checks passed"

def main(user_ml_script_s3_uri, user_ml_output_csv_s3_uri):
    # Define local paths
    script_file = "submitted_script.py"
    output_file = "output.csv"
    
    # Download the files from S3
    download_from_s3(user_ml_script_s3_uri, script_file)
    download_from_s3(user_ml_output_csv_s3_uri, output_file)
    download_from_s3(INTEGRITY_CHECK_DATA_S3_URI,INTEGRITY_CHECK_DATA_LOCAL_PATH)

    # replace data loading and export function in the script file
    update_script_with_template_functions(script_file)
    
    # Run integrity checks
    is_valid, message = perform_integrity_check(script_file, output_file)
    print(message)
    
    if is_valid:
        # Run the downloaded script
        result = subprocess.run([sys.executable, script_file], capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)
    else:
        print("Integrity checks failed. Exiting.")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Run integrity checks and execute user ML script.')
    parser.add_argument('user_ml_script_s3_uri', type=str, help='The S3 URI of the user ML script.')
    parser.add_argument('user_ml_output_csv_s3_uri', type=str, help='The S3 URI of the user ML output CSV.')

    args = parser.parse_args()
    main(args.user_ml_script_s3_uri, args.user_ml_output_csv_s3_uri)
