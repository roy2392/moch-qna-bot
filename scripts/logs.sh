#!/bin/bash

# Script to view CloudWatch logs
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Viewing Application Logs ===${NC}\n"

cd terraform

LOG_GROUP=$(terraform output -raw cloudwatch_log_group)
AWS_REGION=${AWS_REGION:-us-east-1}

echo -e "${YELLOW}Log Group: ${LOG_GROUP}${NC}"
echo -e "${YELLOW}Showing logs from the last 10 minutes...${NC}\n"

aws logs tail $LOG_GROUP \
    --follow \
    --format short \
    --region $AWS_REGION \
    --since 10m
