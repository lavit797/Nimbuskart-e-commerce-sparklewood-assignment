
# Nimbuskart DevOps Assignment — Cost Hygiene & Automation

## Overview

This repository contains a complete cloud cost hygiene solution for NimbusKart, an e-commerce startup whose AWS bill grew from $400 to $2,100/month due to orphaned resources. It provisions baseline AWS infrastructure using Terraform on LocalStack, detects wasteful resources using a Python "Cost Janitor" script, and enforces cost hygiene continuously via GitHub Actions CI/CD.All these setups are done on my github codespace which provides me roughly 8gb ram. 

---


## How to Run Locally(Although too be very honest i had done this project on github codespace soo if some commands are error prone then soo sorry for it.)

### Prerequisites
```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/Nimbuskart-e-commerce-sparklewood-assignment.git
cd Nimbuskart-e-commerce-sparklewood-assignment

# 2. Install dependencies
pip install boto3 terraform-local awscli

# 3. Install Terraform
# https://developer.hashicorp.com/terraform/install
```

### Start LocalStack
```bash
## you must have an account on localstack pro
## you have to use personal auth token to start localstack 
docker run --rm -d -p 4566:4566 --name localstack localstack/localstack
sleep 30
curl http://localhost:4566/_localstack/health
```

### Apply Terraform
```bash
cd terraform
tflocal init
tflocal validate
tflocal fmt -check
tflocal apply -auto-approve
```

### Run Cost Janitor
```bash
cd ../janitor
python3 janitor.py --dry-run --endpoint-url http://localhost:4566
```

### View Report
```bash
cat report.json
cat report.md
```

---

## How I Run This project on Github Codespace
 1. Clone the Repo
 2. Install docker, terraform-local or terraform , pyhton3, botto3 , awscli
 3. To install local stack firstly you have to make account on localstack pro then take an personal  auth token. and then install local stack from  bash on your codespace 
 4. then use a command on bash(export LOCALSTACK_AUTH_TOKEN=Perosonal_auth_token).
 5. then use command localstack start -d to start local stack
 6. then verify localstack health by using command curl http://localhost:4566/_localstack/health
 7. then cd terraform
 8. then terraform init
 9. terraform validate
 10. terraform apply -auto-approve
 11. to run janitor.py switch directory to cd ../janitor
 12. then use command python3 janitor.py --dry-run
 13. you will get a report.json which you can add commit and oush in github repo name as report.json


## Architecture
┌─────────────────────────────────────────────────────────┐
│                    GitHub Actions CI                     │
│  PR opened → LocalStack → Terraform Apply → Janitor Scan│
│           → report.json artifact → PR Comment           │
└─────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────┐
│                 LocalStack (AWS Mock)                    │
│                                                         │
│  VPC (10.20.0.0/16)                                     │
│  ├── Subnet AZ-a (10.20.0.0/24)                        │
│  ├── Subnet AZ-b (10.20.1.0/24)                        │
│  ├── Security Group (80/443 open, 22 restricted)        │
│  ├── EC2 web-0 (t3.micro) [tagged: Tier=web]           │
│  ├── EC2 web-1 (t3.micro) [tagged: Tier=web]           │
│  ├── S3 Bucket (versioning + lifecycle 30d)             │
│  └── EBS Volume (unattached — intentional orphan)       │
└─────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────┐
│                   Cost Janitor                           │
│  ✓ Unattached EBS volumes                               │
│  ✓ Stopped EC2 > 14 days                               │
│  ✓ Unassociated Elastic IPs                             │
│  ✓ Resources missing required tags                      │
│  Output: report.json + report.md                        │
└─────────────────────────────────────────────────────────┘

---

## Decisions & Deviations

- **SSH CIDR changed from `0.0.0.0/0` to `10.0.0.0/8`** — Port 22 open to the entire internet is a critical security risk; restricted to private network range by default.
- **Added S3 public access block** — Spec did not mention it but a logs bucket should never be publicly accessible.
- **Used `aws_vpc_security_group_ingress_rule` instead of inline ingress/egress** — AWS provider v5 recommends separate rule resources to avoid conflicts.
- **EBS orphan intentionally unattached** — Created as a known test case for the Cost Janitor to detect in Part B.
- **`safe_to_auto_delete: false` for EC2 and EBS** — Stopped instances and unattached volumes could be legitimate (batch jobs, recent detach); human review required before deletion.

---

## Trade-offs

With one more week I would:
- Add CloudTrail integration to check when a volume was last detached before flagging it
- Implement multi-account scanning using AWS Organizations role chaining
- Add Slack notifications when waste exceeds a configurable threshold
- Write proper unit tests using Moto for all four janitor checks
- Add Terraform remote state with S3 backend and DynamoDB locking
- Build a simple web dashboard showing 30-day waste trend

---

## AI Usage Disclosure

- **Claude (claude.ai)** — Used for boilerplate Terraform HCL structure and janitor.py file .
- **One thing AI got wrong** — The initial `janitor.py` had a bug: `if args.delete and not args.dry_run` would never execute because `--dry-run` defaults to `True`. Caught this during manual code review and fixed it to `if args.delete`. because localstack create a fake infra soo Ami id suggested by claude is also fake which creates a problem of block device mapping soo i had fetch the already existed ami id on local stack by using command (awslocal ec2 describe-images --output table --query 'Images[*].[ImageId,Name,State]') then first ami id i got i had replaced it with ami in main.tf file.
- **Written manually without AI** — i had written  Terraform stack for NimbusKart's baseline infra (VPC + EC2 + S3 + tagging policy), targeting LocalStack manually although to be very honest i had used hashicorp hcl extensions which suggest me the code syntax,  The `DESIGN.md` failure mode analysis (Section 3) was written manually because it required thinking through NimbusKart's specific operational context — a scheduled batch job scenario and a mid-snapshot detach scenario . 
