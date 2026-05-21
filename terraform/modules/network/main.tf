resource "aws_vpc" "main" {
    cidr_block = var.vpc_cidr
    tags = {
       Name        = "${var.project}-${var.environment}-vpc"
    Project     = var.project
    Environment = var.environment
    Owner       = var.owner
    ManagedBy   = "terraform"
    }
}

resource "aws_subnet" "public" {
    count = 2
    vpc_id = aws_vpc.main.id
    cidr_block = cidrsubnet(var.vpc_cidr, 8, count.index)
    availability_zone = var.availability_zones[count.index]
    tags = {
        Name        = "${var.project}-${var.environment}-public-subnet-${count.index + 1}"
        Project     = var.project
        Environment = var.environment
        Owner       = var.owner
        ManagedBy   = "terraform"
    }
}

resource "aws_security_group" "web"{
vpc_id = aws_vpc.main.id

ingress{

    description = "HTTP from anywhere"
    from_port = 80
    to_port = 80
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
}
 ingress{
    description = "HTTPS "
    from_port = 443
    to_port = 443
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]

 }
 ingress {
    description = "SSH from allowed CIDR"
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = [var.ssh_cidr]
 }

 egress = {
    description = "Allow all outbound traffic"
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
 }
tags = {
    Name        = "${var.project}-${var.environment}-web-sg"
    Project     = var.project
    Environment = var.environment
    Owner       = var.owner
    ManagedBy   = "terraform"
}
}