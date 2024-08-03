LOCAL_VENV_NAME=.venv
PYTHON=python
STACK?=network-stack

STAGE?= prod
AWS_ACCOUNT_ID=998293780211
ifeq ($(STAGE), prod)
	AWS_REGION=eu-west-2
	ECR_TAG=latest
else
	AWS_REGION=eu-west-2
	ECR_TAG=dev-latest
endif

install-nvm:
	curl https://raw.githubusercontent.com/creationix/nvm/master/install.sh | bash
	source ~/.bashrc
	exec bash --login

init:
	nvm install 16
	nvm use 16
	npm install -g aws-cdk
	make local-venv
	source .venv/bin/activate
	make install-dependencies

local-venv:
	$(PYTHON) -m venv .venv

install-dependencies:
	pip install -r requirements.txt

lint:
	flake8 $(shell git ls-files '*.py')

test:
	pytest

synth:
	@cdk synth -c stage=$(STAGE) --output=cdk.out/$(STAGE)

deploy: synth
	echo $(STACK)-$(STAGE)
	@cdk deploy --app=cdk.out/$(STAGE) $(STACK)-$(STAGE) 

diff:
	@cdk diff -c stage=$(STAGE) $(STACK)-$(STAGE)

destroy:
	@cdk destroy -c stage=$(STAGE) $(STACK)-$(STAGE)

bootstrap-cdk:
	@cdk bootstrap aws://$(AWS_ACCOUNT_ID)/$(AWS_REGION) -c stage=$(STAGE)


push:
	AWS_REGION="us-east-1"
	docker build -t playwright-app:$(ECR_TAG) ../backend/
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com

	docker tag playwright-app:$(ECR_TAG) $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/external_report_retrieval:$(ECR_TAG)

	docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/external_report_retrieval:$(ECR_TAG)