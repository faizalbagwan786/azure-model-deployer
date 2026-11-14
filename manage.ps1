<#
.SYNOPSIS
    Management and deployment helper script for Azure AI Model Deployer on Windows.
#>

param (
    [Parameter(Mandatory=$false)]
    [ValidateSet("build", "up", "down", "logs", "test", "deploy-dev", "deploy-prod", "help")]
    [string]$Action = "help",

    [Parameter(Mandatory=$false)]
    [string]$ModelKey = "smolvlm-500m",

    [Parameter(Mandatory=$false)]
    [string]$Env = "dev"
)

switch ($Action) {
    "build" {
        Write-Host "🐳 Building Docker images..." -ForegroundColor Cyan
        docker-compose build
    }
    "up" {
        Write-Host "🚀 Starting local containers (GPT-2 on 8080, SmolVLM on 8081)..." -ForegroundColor Green
        docker-compose up -d
    }
    "down" {
        Write-Host "🛑 Stopping containers..." -ForegroundColor Yellow
        docker-compose down
    }
    "logs" {
        docker-compose logs -f
    }
    "test" {
        Write-Host "🧪 Running test suite..." -ForegroundColor Cyan
        pytest tests/ -v
    }
    "deploy-dev" {
        Write-Host "☁️ Deploying to Azure dev environment..." -ForegroundColor Cyan
        python src/deployment/deploy_model.py --model-key $ModelKey --env "dev"
    }
    "deploy-prod" {
        Write-Host "☁️ Deploying to Azure prod environment..." -ForegroundColor Cyan
        python src/deployment/deploy_model.py --model-key $ModelKey --env "prod"
    }
    default {
        Write-Host "Azure AI Model Deployer Management Script" -ForegroundColor Yellow
        Write-Host "Usage: .\manage.ps1 -Action <build|up|down|logs|test|deploy-dev|deploy-prod>"
        Write-Host ""
        Write-Host "Examples:"
        Write-Host "  .\manage.ps1 -Action up"
        Write-Host "  .\manage.ps1 -Action test"
        Write-Host "  .\manage.ps1 -Action deploy-dev -ModelKey smolvlm-500m"
    }
}

