include .env

.EXPORT_ALL_VARIABLES:

IMAGE_TAG_WITH_DIGEST := $(shell podman inspect --format='{{index .RepoDigests 0}}' ${IMAGE_TAG})
LT_QUIZ_VERSION=$(shell date)

SHELL=/bin/bash

dep-up:
	pipenv update --dev
	pipenv clean

gcp-auth:
	gcloud config configurations activate lt-quiz-bot
	gcloud auth application-default login
	gcloud auth configure-docker europe-central2-docker.pkg.dev

#######
# LOCAL
local-test:
	pipenv run pytest . --cov=src
	start htmlcov/index.html

local-generate:
	pipenv run python src/main.py generate

#######
# IMAGE
podman-login:
	gcloud auth print-access-token --quiet | podman login -u oauth2accesstoken --password-stdin ${GCP_ARTIFACT_REGISTRY}

######
# BOT
image-build:
	podman build . -t ${IMAGE_TAG} -f Containerfile

image-push:
	podman push ${IMAGE_TAG}

image-pull:
	podman pull ${IMAGE_TAG}

image-run:
	podman run ${IMAGE_TAG}

image-test:
	podman run ${IMAGE_TAG} pytest . --cov=src

cloud-run-deploy:
	podman run --env-file <(env | grep -e LT_QUIZ_ -e GOOGLE_APPLICATION_CREDENTIALS) \
		-v ~/.config/gcloud:/root/.config/gcloud \
		-v ${HOME}/work:${HOME}/work ${IMAGE_TAG} \
		python main.py migrate
	cat deploy/app/service.yaml | envsubst > tmp-service.yaml
	gcloud run services replace tmp-service.yaml --region europe-central2

cloud-run-make-public:
	gcloud run services add-iam-policy-binding ${SERVICE_NAME} --region europe-central2 --member="allUsers" --role="roles/run.invoker"