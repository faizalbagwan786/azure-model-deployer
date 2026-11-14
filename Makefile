.PHONY: help build run stop test deploy-dev deploy-prod

help:
	@echo "Azure AI Model Deployer Commands:"
	@echo "  make build         - Build local Docker containers"
	@echo "  make run           - Run services locally with docker-compose"
	@echo "  make stop          - Stop all local containers"
	@echo "  make test          - Run pytest test suite"
	@echo "  make deploy-dev    - Deploy dev model to Azure Container Apps"
	@echo "  make deploy-prod   - Deploy prod model to Azure Container Apps"

build:
	docker-compose build

run:
	docker-compose up -d

stop:
	docker-compose down

test:
	pytest tests/ -v

deploy-dev:
	python src/deployment/deploy_model.py --model-key smolvlm-500m --env dev

deploy-prod:
	python src/deployment/deploy_model.py --model-key smolvlm-2.2b --env prod

