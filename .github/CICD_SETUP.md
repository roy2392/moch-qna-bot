# CI/CD Setup Guide

This guide explains how to set up the CI/CD pipeline using GitHub Actions for the MOCH QNA Bot.

## Overview

The CI/CD pipeline consists of two main workflows:

1. **PR Validation** (`pr-validation.yml`)
   - Runs on pull requests to `main`
   - Validates code, builds Docker image, runs tests
   - Ensures PR is safe to merge

2. **Production Deployment** (`deploy-production.yml`)
   - Runs when code is merged to `main`
   - Builds and pushes Docker image to ECR
   - Deploys to AWS ECS
   - Verifies deployment health

## GitHub Secrets Configuration

You need to configure the following secrets in your GitHub repository:

### Required Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions → New repository secret

| Secret Name | Description | Example Value |
|------------|-------------|---------------|
| `AWS_ACCESS_KEY_ID` | AWS access key with ECS and ECR permissions | `AKIAZQZLX2UG...` |
| `AWS_SECRET_ACCESS_KEY` | AWS secret access key | `ZpE5/otSkuxO...` |
| `DEFAULT_MODEL_ID` | Bedrock model ID | `anthropic.claude-3-sonnet-20240229-v1:0` |
| `LANGFUSE_SECRET_KEY` | Langfuse secret key | `sk-lf-...` |
| `LANGFUSE_PUBLIC_KEY` | Langfuse public key | `pk-lf-...` |
| `LANGFUSE_BASE_URL` | Langfuse base URL | `https://cloud.langfuse.com` |

### AWS IAM Permissions Required

The AWS user/role needs the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "ecr:PutImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecs:DescribeServices",
        "ecs:DescribeTasks",
        "ecs:ListTasks",
        "ecs:UpdateService"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "elasticloadbalancing:DescribeLoadBalancers"
      ],
      "Resource": "*"
    }
  ]
}
```

## Workflow Details

### PR Validation Workflow

**Triggers:** Pull requests to `main` branch

**Steps:**
1. Checkout code
2. Set up Python 3.11
3. Install dependencies
4. Run linting (optional)
5. Build Docker image
6. Test Docker container locally
7. Check health endpoint
8. Push image to ECR with tag `pr-<number>`
9. Comment on PR with results

**Protection:** PRs cannot be merged unless this workflow passes ✅

### Production Deployment Workflow

**Triggers:** Push to `main` branch (when PR is merged)

**Steps:**
1. Checkout code
2. Configure AWS credentials
3. Login to Amazon ECR
4. Build Docker image for AMD64
5. Tag with commit SHA and `latest`
6. Push to ECR
7. Force new ECS deployment
8. Wait for deployment to complete (up to 30 minutes)
9. Verify health endpoint
10. Create deployment summary

## Branch Protection Rules

To ensure CI/CD works properly, configure branch protection for `main`:

1. Go to Settings → Branches → Add rule
2. Branch name pattern: `main`
3. Enable:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - Select required status check: `Validate PR`
   - ✅ Do not allow bypassing the above settings

## Workflow Usage

### Creating a Pull Request

```bash
# Create a new branch
git checkout -b feature/my-new-feature

# Make changes
git add .
git commit -m "Add new feature"

# Push to GitHub
git push origin feature/my-new-feature

# Create PR on GitHub
# The PR validation workflow will run automatically
```

### Merging to Production

1. Create a PR from your feature branch to `main`
2. Wait for PR validation to pass ✅
3. Get code review approval (if required)
4. Merge the PR
5. Production deployment workflow runs automatically
6. Monitor deployment in GitHub Actions tab
7. Verify at the ALB URL

## Monitoring Deployments

### GitHub Actions Tab

- View all workflow runs
- See detailed logs for each step
- Download artifacts (if any)

### AWS Console

- **ECS Console:** Monitor service deployments
- **CloudWatch Logs:** View application logs (`/ecs/moch-qna-bot`)
- **Load Balancer:** Check target health

### Deployment Summary

After each production deployment, check the GitHub Actions summary for:
- Commit SHA deployed
- ECS cluster and service info
- Application URL
- Health check status

## Troubleshooting

### Deployment Fails Health Checks

```bash
# Check ECS logs
aws logs tail /ecs/moch-qna-bot --since 10m --region us-east-1

# Check ECS service events
aws ecs describe-services \
  --cluster moch-qna-bot-cluster \
  --services moch-qna-bot-service \
  --region us-east-1 \
  --query 'services[0].events[0:10]'
```

### PR Validation Fails

1. Check GitHub Actions logs for the specific failure
2. Common issues:
   - Docker build errors → Check Dockerfile
   - Health check timeout → Increase wait time or check app startup
   - ECR push errors → Verify AWS credentials

### Rollback Deployment

If a deployment causes issues:

```bash
# Force redeploy previous image
aws ecs update-service \
  --cluster moch-qna-bot-cluster \
  --service moch-qna-bot-service \
  --force-new-deployment \
  --region us-east-1

# Or manually update task definition to previous revision
```

## Manual Deployment (Bypass CI/CD)

If you need to deploy manually:

```bash
# Build and push
./deploy.sh

# Force new deployment
aws ecs update-service \
  --cluster moch-qna-bot-cluster \
  --service moch-qna-bot-service \
  --force-new-deployment \
  --region us-east-1
```

## Best Practices

1. **Always create PRs** - Don't push directly to `main`
2. **Write descriptive commit messages** - Helps with debugging
3. **Monitor deployments** - Watch the GitHub Actions logs
4. **Test locally first** - Use `docker-compose` or local testing
5. **Keep secrets secure** - Never commit secrets to git
6. **Review logs** - Check CloudWatch logs after deployment

## Support

- GitHub Actions Logs: Check the Actions tab
- AWS Logs: `/ecs/moch-qna-bot` in CloudWatch
- Issues: Open an issue in the GitHub repository
