terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider  "aws "{
region = var.region
 access_key                  = "test"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  endpoints {
  ec2 = var.localstack_endpoint
  s3  = var.localstack_endpoint
  iam = var.localstack_endpoint
}

}

module "network" {
  source             = "./modules/network"
  project            = var.project
  environment        = var.environment
  owner              = var.owner
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
  ssh_cidr           = var.ssh_cidr
}

resource "aws_instance" "web" {
  count         = 2
  ami           = "ami-00000000"
  instance_type = var.instance_type
  subnet_id     = module.network.subnet_ids[count.index]

  tags = {
    Name        = "${var.project}-${var.environment}-web-${count.index}"
    Project     = var.project
    Environment = var.environment
    Owner       = var.owner
    ManagedBy   = "terraform"
    Tier        = "web"
  }
}

resource "aws_s3_bucket" "logs" {
  bucket        = "${var.project}-${var.environment}-applogs"
  force_destroy = true

  tags = {
    Name        = "${var.project}-${var.environment}-applogs"
    Project     = var.project
    Environment = var.environment
    Owner       = var.owner
    ManagedBy   = "terraform"
  }
}

resource "aws_s3_bucket_versioning" "logs" {
  bucket = aws_s3_bucket.logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id

  rule {
    id     = "expire-noncurrent-versions"
    status = "Enabled"

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}

resource "aws_s3_bucket_public_access_block" "logs" {
  bucket                  = aws_s3_bucket.logs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_ebs_volume" "orphan" {
  availability_zone = var.availability_zones[0]
  size              = 20
  type              = "gp3"

  tags = {
    Name        = "${var.project}-${var.environment}-orphan-vol"
    Project     = var.project
    Environment = var.environment
    Owner       = var.owner
    ManagedBy   = "terraform"
    Note        = "intentional-orphan-for-testing"
  }
}
