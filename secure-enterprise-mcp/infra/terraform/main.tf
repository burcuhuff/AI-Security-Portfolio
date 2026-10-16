terraform {
  required_version = ">= 1.16.0, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region              = "us-east-1"
  profile             = "mcp-sandbox"
  allowed_account_ids = [var.aws_account_id]

  default_tags {
    tags = {
      Project     = "secure-enterprise-mcp"
      Environment = "sandbox"
      ManagedBy   = "terraform"
    }
  }
}

variable "aws_account_id" {
  description = "AWS sandbox account permitted for this deployment."
  type        = string

  validation {
    condition     = can(regex("^[0-9]{12}$", var.aws_account_id))
    error_message = "Provide a 12-digit AWS account ID."
  }
}

resource "aws_ecr_repository" "mcp" {
  name                 = "secure-enterprise-mcp"
  image_tag_mutability = "IMMUTABLE"
  force_delete         = false

  encryption_configuration {
    encryption_type = "AES256"
  }
}

output "repository_url" {
  description = "Registry address used to tag and push the MCP image."
  value       = aws_ecr_repository.mcp.repository_url
}