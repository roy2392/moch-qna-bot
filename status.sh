#!/bin/bash

# Script to check deployment status
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Checking Deployment Status ===${NC}\n"

cd terraform

# Check if terraform state exists
if [ ! -f "terraform.tfstate" ]; then
    echo -e "${RED}No deployment found. Please run ./deploy.sh first.${NC}"
    exit 1
fi

CLUSTER_NAME=$(terraform output -raw ecs_cluster_name)
SERVICE_NAME=$(terraform output -raw ecs_service_name)
AWS_REGION=${AWS_REGION:-us-east-1}
ALB_URL=$(terraform output -raw alb_url)

echo -e "${YELLOW}ECS Service Status:${NC}"
aws ecs describe-services \
    --cluster $CLUSTER_NAME \
    --services $SERVICE_NAME \
    --region $AWS_REGION \
    --query 'services[0].{Status:status,DesiredCount:desiredCount,RunningCount:runningCount,PendingCount:pendingCount}' \
    --output table

echo -e "\n${YELLOW}Recent Tasks:${NC}"
aws ecs list-tasks \
    --cluster $CLUSTER_NAME \
    --service-name $SERVICE_NAME \
    --region $AWS_REGION \
    --query 'taskArns[0:5]' \
    --output table

echo -e "\n${YELLOW}Health Check:${NC}"
echo -e "Testing URL: ${ALB_URL}/health"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" ${ALB_URL}/health || echo "000")

if [ "$HTTP_CODE" == "200" ]; then
    echo -e "${GREEN}✓ Service is healthy!${NC}"
else
    echo -e "${RED}✗ Service is not responding correctly (HTTP $HTTP_CODE)${NC}"
    echo -e "${YELLOW}This is normal immediately after deployment. Wait a few minutes and try again.${NC}"
fi

echo -e "\n${GREEN}Application URL: ${ALB_URL}${NC}"
echo -e "${GREEN}API Docs: ${ALB_URL}/docs${NC}"
echo -e "\n${YELLOW}View logs with: ./logs.sh${NC}\n"
