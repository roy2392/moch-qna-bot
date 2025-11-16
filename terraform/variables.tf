variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "moch-qna-bot"
}

variable "container_port" {
  description = "Port exposed by the container"
  type        = number
  default     = 8000
}

variable "container_cpu" {
  description = "Fargate task CPU units (256, 512, 1024, 2048, 4096)"
  type        = number
  default     = 512
}

variable "container_memory" {
  description = "Fargate task memory in MB (must be compatible with CPU)"
  type        = number
  default     = 1024
}

variable "desired_count" {
  description = "Desired number of Fargate tasks"
  type        = number
  default     = 2
}

variable "health_check_path" {
  description = "Health check endpoint path"
  type        = string
  default     = "/health"
}

variable "aws_access_key_id" {
  description = "AWS Access Key ID for the application"
  type        = string
  sensitive   = true
}

variable "aws_secret_access_key" {
  description = "AWS Secret Access Key for the application"
  type        = string
  sensitive   = true
}

variable "default_model_id" {
  description = "Default Bedrock model ID"
  type        = string
  default     = "anthropic.claude-3-sonnet-20240229-v1:0"
}

variable "default_temperature" {
  description = "Default temperature for model responses"
  type        = string
  default     = "0.7"
}

variable "default_max_tokens" {
  description = "Default max tokens for model responses"
  type        = string
  default     = "2048"
}

variable "log_level" {
  description = "Application log level"
  type        = string
  default     = "INFO"
}

variable "langfuse_secret_key" {
  description = "Langfuse secret key for prompt management"
  type        = string
  sensitive   = true
}

variable "langfuse_public_key" {
  description = "Langfuse public key for prompt management"
  type        = string
  sensitive   = true
}

variable "langfuse_base_url" {
  description = "Langfuse base URL"
  type        = string
  default     = "https://cloud.langfuse.com"
}
