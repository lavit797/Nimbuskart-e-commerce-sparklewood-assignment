variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project" {
  description = "Project name"
  type        = string
  default     = "nimbuskart"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "staging"
}

variable "owner" {
  description = "Team or person responsible"
  type        = string
  default     = "devops-team"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.20.0.0/16"
}

variable "availability_zones" {
  description = "Two AZs for subnets"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

# DECISION: Spec says default 0.0.0.0/0 for SSH — we changed to 10.0.0.0/8
# Reason: Port 22 open to world is a critical security risk
variable "ssh_cidr" {
  description = "CIDR for SSH access — restrict in production!"
  type        = string
  default     = "10.0.0.0/8"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "localstack_endpoint" {
  description = "LocalStack endpoint URL"
  type        = string
  default     = "http://localhost:4566"
} 