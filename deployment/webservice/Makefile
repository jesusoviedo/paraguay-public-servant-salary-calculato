NAME:=salary-prediction-fp-py
LOCAL_TAG:=$(shell date +"%Y_%m_%d")
LOCAL_IMAGE_NAME:=${NAME}:${LOCAL_TAG}


test:
	pytest test/

quality_checks:
	isort .
	black .
	pylint --recursive=y .

build: quality_checks test
	docker build -t ${LOCAL_IMAGE_NAME} -f Dockerfile.${NAME} .

integration_test: build
	LOCAL_IMAGE_NAME=${LOCAL_IMAGE_NAME} cd ./integration-test ; ./run.sh

publish: build integration_test
	LOCAL_IMAGE_NAME=${LOCAL_IMAGE_NAME} scripts/publish.sh

setup:
	pipenv install --dev
	pre-commit install
