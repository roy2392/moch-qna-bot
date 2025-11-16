#!/bin/bash

# GitHub Secrets Setup Helper Script
# This script helps you configure GitHub secrets using GitHub CLI (gh)

echo "🔐 GitHub Secrets Setup for moch-qna-bot"
echo "========================================="
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed."
    echo "📦 Install it from: https://cli.github.com/"
    echo ""
    echo "Or add secrets manually at:"
    echo "https://github.com/roy2392/moch-qna-bot/settings/secrets/actions"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub CLI"
    echo "🔑 Run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI is ready!"
echo ""

# Read secrets from terraform.tfvars
TFVARS_FILE="terraform/terraform.tfvars"

if [ ! -f "$TFVARS_FILE" ]; then
    echo "❌ terraform.tfvars not found at $TFVARS_FILE"
    exit 1
fi

# Extract values from terraform.tfvars
AWS_ACCESS_KEY_ID=$(grep 'aws_access_key_id' "$TFVARS_FILE" | cut -d'"' -f2)
AWS_SECRET_ACCESS_KEY=$(grep 'aws_secret_access_key' "$TFVARS_FILE" | cut -d'"' -f2)
DEFAULT_MODEL_ID=$(grep 'default_model_id' "$TFVARS_FILE" | cut -d'"' -f2)
LANGFUSE_SECRET_KEY=$(grep 'langfuse_secret_key' "$TFVARS_FILE" | cut -d'"' -f2)
LANGFUSE_PUBLIC_KEY=$(grep 'langfuse_public_key' "$TFVARS_FILE" | cut -d'"' -f2)
LANGFUSE_BASE_URL=$(grep 'langfuse_base_url' "$TFVARS_FILE" | cut -d'"' -f2)

echo "📋 Found the following secrets from terraform.tfvars:"
echo "  - AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID:0:10}..."
echo "  - AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY:0:10}..."
echo "  - DEFAULT_MODEL_ID: $DEFAULT_MODEL_ID"
echo "  - LANGFUSE_SECRET_KEY: ${LANGFUSE_SECRET_KEY:0:10}..."
echo "  - LANGFUSE_PUBLIC_KEY: ${LANGFUSE_PUBLIC_KEY:0:10}..."
echo "  - LANGFUSE_BASE_URL: $LANGFUSE_BASE_URL"
echo ""

read -p "❓ Do you want to add these secrets to GitHub? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cancelled"
    exit 1
fi

echo ""
echo "🚀 Adding secrets to GitHub repository..."
echo ""

# Add secrets to GitHub
gh secret set AWS_ACCESS_KEY_ID -b"$AWS_ACCESS_KEY_ID" && echo "✅ AWS_ACCESS_KEY_ID added"
gh secret set AWS_SECRET_ACCESS_KEY -b"$AWS_SECRET_ACCESS_KEY" && echo "✅ AWS_SECRET_ACCESS_KEY added"
gh secret set DEFAULT_MODEL_ID -b"$DEFAULT_MODEL_ID" && echo "✅ DEFAULT_MODEL_ID added"
gh secret set LANGFUSE_SECRET_KEY -b"$LANGFUSE_SECRET_KEY" && echo "✅ LANGFUSE_SECRET_KEY added"
gh secret set LANGFUSE_PUBLIC_KEY -b"$LANGFUSE_PUBLIC_KEY" && echo "✅ LANGFUSE_PUBLIC_KEY added"
gh secret set LANGFUSE_BASE_URL -b"$LANGFUSE_BASE_URL" && echo "✅ LANGFUSE_BASE_URL added"

echo ""
echo "🎉 All secrets have been added successfully!"
echo ""
echo "📌 Next steps:"
echo "1. Go to: https://github.com/roy2392/moch-qna-bot/actions"
echo "2. Find the failed 'Deploy to Production' workflow"
echo "3. Click 'Re-run all jobs'"
echo ""
echo "Or trigger a new deployment by making a commit:"
echo "  git commit --allow-empty -m 'Trigger deployment with secrets configured'"
echo "  git push origin main"
