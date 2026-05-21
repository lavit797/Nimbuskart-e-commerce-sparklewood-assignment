variable "project" {
  description = "Project name"
  type        = string
}
variable "enviornment" {
description = "Environment name"
  type        = string
  
}

variable "owner" {
description = "Owner name"
    type        = string
}

variable "vpc_cidr" {
description = "CIDR block for the VPC"
  type        = string
  default     = "10.20.0.0/16"
  
}

variable  "availability_zones" {
description = "List of availability zones"
    type        = list(string)
    default     = ["us-east-1a", "us-east-1b"]

}

variable "ssh_cidr" {
  description = "CIDR allowed for SSH — do NOT use 0.0.0.0/0 in production"
  type        = string
  default     = "10.0.0.0/8"
}