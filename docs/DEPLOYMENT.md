# Deployment Guide

## Prerequisites

- AWS Account with Bedrock access enabled
- AWS credentials with appropriate permissions
- Docker (for containerized deployment)
- Python 3.11+ (for local deployment)

## AWS Setup

### 1. Enable AWS Bedrock

1. Log into AWS Console
2. Navigate to AWS Bedrock service
3. Request model access for Claude models:
   - Claude 3 Sonnet
   - Claude 3 Haiku
   - Claude 3 Opus
4. Wait for access approval (usually instant)

### 2. Create IAM User/Role

Create an IAM user or role with the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "arn:aws:bedrock:*::foundation-model/*"
    }
  ]
}
```

## Local Deployment

### 1. Clone Repository

```bash
git clone <repository-url>
cd moch-qna-bot
```

### 2. Setup Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

### 3. Run Service

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Docker Deployment

### 1. Build Image

```bash
docker build -t bedrock-chatbot .
```

### 2. Run Container

```bash
docker run -d \
  -p 8000:8000 \
  -e AWS_REGION=us-east-1 \
  -e AWS_ACCESS_KEY_ID=your_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret \
  --name bedrock-chatbot \
  bedrock-chatbot
```

### 3. Using Docker Compose

```bash
# Ensure .env file is configured
docker-compose up -d
```

## AWS Deployment Options

### Option 1: AWS ECS (Elastic Container Service)

1. Push Docker image to ECR:
```bash
aws ecr create-repository --repository-name bedrock-chatbot
docker tag bedrock-chatbot:latest <account-id>.dkr.ecr.<region>.amazonaws.com/bedrock-chatbot:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/bedrock-chatbot:latest
```

2. Create ECS task definition
3. Create ECS service with your task
4. Configure Application Load Balancer

### Option 2: AWS App Runner

1. Push image to ECR (as above)
2. Create App Runner service from ECR image
3. Configure environment variables
4. Deploy

### Option 3: AWS Lambda + API Gateway

For serverless deployment, modify the code to use Mangum adapter:

```bash
pip install mangum
```

Modify `main.py`:
```python
from mangum import Mangum
# ... existing code ...
handler = Mangum(app)
```

Deploy using AWS SAM or Serverless Framework.

## Environment Variables

Ensure these are set in production:

```bash
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>
DEFAULT_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
LOG_LEVEL=INFO
```

## Security Considerations

1. **Never commit credentials** - Use .env files or AWS Secrets Manager
2. **Use IAM roles** - Prefer IAM roles over access keys when possible
3. **Enable HTTPS** - Use SSL/TLS in production
4. **Rate limiting** - Implement rate limiting to prevent abuse
5. **API authentication** - Add authentication layer for production

## Monitoring

### Health Checks

The service provides health check endpoints:
- `GET /health`
- `GET /`

### Logging

Logs are output to stdout/stderr. Configure log aggregation:
- CloudWatch Logs (AWS)
- ELK Stack
- Datadog

### Metrics

Consider implementing:
- Request count
- Response times
- Error rates
- Token usage
- Cost tracking

## Scaling

### Horizontal Scaling

- Use container orchestration (ECS, Kubernetes)
- Configure auto-scaling based on CPU/memory
- Use load balancers

### Vertical Scaling

- Increase container resources
- Use larger EC2 instances

## Cost Optimization

1. **Use appropriate models** - Claude Haiku for simple tasks, Sonnet for complex
2. **Set max_tokens limits** - Control response length
3. **Implement caching** - Cache common responses
4. **Monitor usage** - Track AWS Bedrock costs in Cost Explorer

## Troubleshooting

### Common Issues

**Connection errors:**
- Check AWS credentials
- Verify Bedrock is available in your region
- Ensure model access is approved

**Timeout errors:**
- Increase timeout settings
- Reduce max_tokens
- Check network connectivity

**Permission denied:**
- Verify IAM permissions
- Check resource policies

## Production Checklist

- [ ] Environment variables configured
- [ ] AWS credentials secured
- [ ] Health checks working
- [ ] Logging configured
- [ ] Monitoring set up
- [ ] Rate limiting implemented
- [ ] Authentication enabled
- [ ] HTTPS configured
- [ ] Backup strategy defined
- [ ] Cost alerts configured
