import boto3
import subprocess  # nosec B404
import os
import sys
from .integrity_checks.evalution_criteria import calculate_sharpe_ratio
from .integrity_checks.runtime_checks import run_script_in_docker
from .integrity_checks.static_checks import perform_static_checks

def download_from_s3(s3_uri, local_path):
    s3 = boto3.client('s3')
    bucket, key = s3_uri.replace("s3://", "").split("/", 1)
    s3.download_file(bucket, key, local_path)

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
