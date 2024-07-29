docker build -t ml-batch-job-prod .
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 637423239508.dkr.ecr.us-east-1.amazonaws.com
docker tag ml-batch-job-prod:latest 637423239508.dkr.ecr.us-east-1.amazonaws.com/ml-batch-job-prod:latest
docker push 637423239508.dkr.ecr.us-east-1.amazonaws.com/ml-batch-job-prod:latest