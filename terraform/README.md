# Terraform AWS Fargate Deployment

This directory contains Terraform configurations to deploy the moch-qna-bot service to AWS Fargate with a publicly accessible URL.

## Architecture

The infrastructure includes:

- **VPC**: Custom VPC with public and private subnets across 2 availability zones
- **NAT Gateways**: For private subnet internet access
- **Application Load Balancer (ALB)**: Public-facing load balancer with HTTP listener
- **ECS Fargate**: Serverless container service running the chatbot
- **ECR**: Docker container registry
- **CloudWatch**: Centralized logging
- **IAM Roles**: Permissions for ECS tasks to access AWS Bedrock
- **Auto Scaling**: Automatic scaling based on CPU and memory utilization

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
3. **Terraform** >= 1.0 installed
4. **Docker** installed
5. **AWS Credentials** for both:
   - Terraform deployment (configured via AWS CLI)
   - Application runtime (to access Bedrock)

## Quick Start

### 1. Configure Variables

Copy the example variables file:

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your values:

```hcl
# AWS Configuration
aws_region  = "us-east-1"
environment = "prod"

# AWS Credentials (for the application to access Bedrock)
aws_access_key_id     = "YOUR_AWS_ACCESS_KEY_ID"
aws_secret_access_key = "YOUR_AWS_SECRET_ACCESS_KEY"

# Container Configuration
container_cpu    = 512
container_memory = 1024
desired_count    = 2
```

**IMPORTANT**: The `aws_access_key_id` and `aws_secret_access_key` in `terraform.tfvars` are used by the **application** to access AWS Bedrock. These are different from the credentials Terraform uses to deploy the infrastructure.

### 2. Deploy Using the Script

From the project root directory:

```bash
./deploy.sh
```

This script will:
1. Initialize Terraform
2. Plan the deployment
3. Create all AWS resources
4. Build the Docker image
5. Push the image to ECR
6. Deploy the application to Fargate

### 3. Check Status

```bash
./status.sh
```

### 4. View Logs

```bash
./logs.sh
```

## Manual Deployment

If you prefer to deploy manually:

### Step 1: Initialize Terraform

```bash
cd terraform
terraform init
```

### Step 2: Plan Deployment

```bash
terraform plan
```

Review the planned changes.

### Step 3: Apply Infrastructure

```bash
terraform apply
```

Type `yes` to confirm.

### Step 4: Build and Push Docker Image

```bash
# Get ECR repository URL
ECR_REPO=$(terraform output -raw ecr_repository_url)

# Build image
cd ..
docker build -t moch-qna-bot:latest .

# Tag image
docker tag moch-qna-bot:latest $ECR_REPO:latest

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_REPO

# Push image
docker push $ECR_REPO:latest
```

### Step 5: Deploy to ECS

```bash
cd terraform
CLUSTER_NAME=$(terraform output -raw ecs_cluster_name)
SERVICE_NAME=$(terraform output -raw ecs_service_name)

aws ecs update-service \
    --cluster $CLUSTER_NAME \
    --service $SERVICE_NAME \
    --force-new-deployment \
    --region us-east-1
```

## Accessing the Application

After deployment, get your application URL:

```bash
cd terraform
terraform output alb_url
```

Access:
- **Web UI**: `http://<alb-dns-name>`
- **API Docs**: `http://<alb-dns-name>/docs`
- **Health Check**: `http://<alb-dns-name>/health`

## Configuration

### Variables

All configurable variables are in `variables.tf`:

| Variable | Description | Default |
|----------|-------------|---------|
| `aws_region` | AWS region | `us-east-1` |
| `environment` | Environment name | `prod` |
| `container_cpu` | Fargate CPU units | `512` |
| `container_memory` | Fargate memory (MB) | `1024` |
| `desired_count` | Number of tasks | `2` |
| `aws_access_key_id` | App AWS access key | Required |
| `aws_secret_access_key` | App AWS secret key | Required |

### Fargate CPU/Memory Combinations

Valid combinations:
- 256 CPU: 512, 1024, 2048 MB
- 512 CPU: 1024, 2048, 3072, 4096 MB
- 1024 CPU: 2048-8192 MB (1 GB increments)
- 2048 CPU: 4096-16384 MB (1 GB increments)
- 4096 CPU: 8192-30720 MB (1 GB increments)

## Auto Scaling

The service automatically scales between `desired_count` and 10 tasks based on:
- **CPU utilization**: Target 70%
- **Memory utilization**: Target 80%

## Monitoring

### View Logs

```bash
# Using the script
./logs.sh

# Or directly
aws logs tail /ecs/moch-qna-bot --follow --region us-east-1
```

### CloudWatch Metrics

View metrics in the AWS Console:
- ECS → Clusters → moch-qna-bot-cluster
- CloudWatch → Log groups → /ecs/moch-qna-bot

### Service Health

```bash
./status.sh
```

Or check the ALB target group health in the AWS Console.

## Updating the Application

To deploy a new version:

```bash
./deploy.sh
```

The script will:
1. Build the new Docker image
2. Push it to ECR
3. Force a new ECS deployment

The deployment uses a rolling update strategy with circuit breaker enabled.

## Costs

Estimated monthly costs (us-east-1, as of 2024):

- **NAT Gateways**: ~$65/month (2 gateways)
- **Application Load Balancer**: ~$25/month
- **Fargate tasks**: ~$30/month (2 tasks with 512 CPU, 1024 MB)
- **Data transfer**: Variable
- **CloudWatch Logs**: ~$5/month (7-day retention)

**Total**: ~$125-150/month

### Cost Optimization

To reduce costs:

1. **Use single NAT Gateway** (not recommended for production):
   - Modify `vpc.tf` to use only 1 NAT gateway
   - Saves ~$32/month

2. **Reduce task count**:
   ```hcl
   desired_count = 1
   ```
   - Saves ~$15/month
   - Less fault-tolerant

3. **Reduce Fargate resources**:
   ```hcl
   container_cpu    = 256
   container_memory = 512
   ```
   - Saves ~$15/month
   - May impact performance

## Security

### IAM Permissions

The ECS task role has permissions to:
- Invoke Bedrock models
- Write to CloudWatch Logs

### Network Security

- ALB is publicly accessible (HTTP port 80)
- ECS tasks run in private subnets
- ECS tasks only accept traffic from ALB
- Security groups enforce least privilege

### Secrets Management

Currently, AWS credentials are passed as environment variables. For production, consider:

1. **AWS Secrets Manager**:
   ```hcl
   secrets = [
     {
       name      = "AWS_ACCESS_KEY_ID"
       valueFrom = aws_secretsmanager_secret.credentials.arn
     }
   ]
   ```

2. **IAM Roles for Service Accounts**: Configure the task role to assume a role with Bedrock permissions

## Troubleshooting

### Tasks Won't Start

1. Check ECS service events:
   ```bash
   aws ecs describe-services --cluster moch-qna-bot-cluster --services moch-qna-bot-service
   ```

2. Check task logs:
   ```bash
   ./logs.sh
   ```

3. Common issues:
   - Invalid AWS credentials
   - Insufficient Fargate CPU/memory
   - Docker image not found in ECR

### Health Checks Failing

1. Check if the application is running:
   ```bash
   ./logs.sh
   ```

2. Verify the health check endpoint:
   - Path: `/health`
   - Expected response: HTTP 200

3. Check security groups allow traffic

### High Costs

1. Check running tasks:
   ```bash
   ./status.sh
   ```

2. Review auto-scaling metrics in CloudWatch

3. Consider cost optimization strategies above

## Clean Up

To destroy all resources:

```bash
./destroy.sh
```

Or manually:

```bash
cd terraform
terraform destroy
```

Type `yes` to confirm.

**Note**: This will permanently delete all resources including logs.

## Support

For issues:
1. Check CloudWatch logs
2. Review AWS Console for service health
3. Open an issue on GitHub
