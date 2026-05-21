output "vpc_id" {
  description = "VPC ID"
  value       = module.network.vpc_id
}

output "subnet_ids" {
  description = "Public subnet IDs"
  value       = module.network.subnet_ids
}

output "bucket_name" {
  description = "S3 logs bucket name"
  value       = aws_s3_bucket.logs.id
}

output "web_instance_ids" {
  description = "Web EC2 instance IDs"
  value       = aws_instance.web[*].id
}

output "orphan_ebs_id" {
  description = "Intentional orphan EBS volume ID"
  value       = aws_ebs_volume.orphan.id
}