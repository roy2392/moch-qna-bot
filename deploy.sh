#!/bin/bash

# Deployment script for moch-qna-bot to AWS Fargate
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Deploying moch-qna-bot to AWS Fargate ===${NC}\n"

# Check if required commands are installed
command -v aws >/dev/null 2>&1 || { echo -e "${RED}AWS CLI is required but not installed. Aborting.${NC}" >&2; exit 1; }
command -v docker >/dev/null 2>&1 || { echo -e "${RED}Docker is required but not installed. Aborting.${NC}" >&2; exit 1; }
command -v terraform >/dev/null 2>&1 || { echo -e "${RED}Terraform is required but not installed. Aborting.${NC}" >&2; exit 1; }

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=${AWS_REGION:-us-east-1}

echo -e "${YELLOW}Step 1: Initialize Terraform${NC}"
cd terraform
terraform init

echo -e "\n${YELLOW}Step 2: Plan Terraform deployment${NC}"
terraform plan -out=tfplan

echo -e "\n${YELLOW}Step 3: Apply Terraform (creating infrastructure)${NC}"
terraform apply tfplan

# Get ECR repository URL
ECR_REPO=$(terraform output -raw ecr_repository_url)

echo -e "\n${YELLOW}Step 4: Build Docker image${NC}"
cd ..
docker build -t moch-qna-bot:latest .

echo -e "\n${YELLOW}Step 5: Tag Docker image${NC}"
docker tag moch-qna-bot:latest $ECR_REPO:latest

echo -e "\n${YELLOW}Step 6: Login to ECR${NC}"
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO

echo -e "\n${YELLOW}Step 7: Push Docker image to ECR${NC}"
docker push $ECR_REPO:latest

echo -e "\n${YELLOW}Step 8: Force new ECS deployment${NC}"
cd terraform
CLUSTER_NAME=$(terraform output -raw ecs_cluster_name)
SERVICE_NAME=$(terraform output -raw ecs_service_name)

aws ecs update-service \
    --cluster $CLUSTER_NAME \
    --service $SERVICE_NAME \
    --force-new-deployment \
    --region $AWS_REGION

echo -e "\n${GREEN}=== Deployment Complete ===${NC}\n"

echo -e "${GREEN}Your application is being deployed!${NC}"
echo -e "${GREEN}URL: $(terraform output -raw alb_url)${NC}"
echo -e "\n${YELLOW}Note: It may take 2-3 minutes for the service to become healthy.${NC}"
echo -e "${YELLOW}You can check the status with: ./status.sh${NC}\n"
