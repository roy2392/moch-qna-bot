#!/bin/bash

# Script to destroy all AWS resources
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${RED}=== WARNING: This will destroy ALL AWS resources ===${NC}\n"

read -p "Are you sure you want to destroy all resources? (type 'yes' to confirm): " confirm

if [ "$confirm" != "yes" ]; then
    echo -e "${YELLOW}Destruction cancelled.${NC}"
    exit 0
fi

echo -e "\n${YELLOW}Destroying AWS resources...${NC}\n"

cd terraform

# First, scale down the ECS service to 0
echo -e "${YELLOW}Scaling down ECS service...${NC}"
CLUSTER_NAME=$(terraform output -raw ecs_cluster_name 2>/dev/null || echo "")
SERVICE_NAME=$(terraform output -raw ecs_service_name 2>/dev/null || echo "")
AWS_REGION=${AWS_REGION:-us-east-1}

if [ ! -z "$CLUSTER_NAME" ] && [ ! -z "$SERVICE_NAME" ]; then
    aws ecs update-service \
        --cluster $CLUSTER_NAME \
        --service $SERVICE_NAME \
        --desired-count 0 \
        --region $AWS_REGION \
        2>/dev/null || true

    echo -e "${YELLOW}Waiting for tasks to drain...${NC}"
    sleep 30
fi

# Destroy all Terraform resources
terraform destroy -auto-approve

echo -e "\n${GREEN}=== All resources destroyed ===${NC}\n"
