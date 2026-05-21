# Nimbuskart-e-commerce-sparklewood-assignment
# Nimbuskart DevOps Assignment — Cost Hygiene & Automation

## Overview

This repository contains a complete cloud cost hygiene solution for NimbusKart, an e-commerce startup whose AWS bill grew from $400 to $2,100/month due to orphaned resources. It provisions baseline AWS infrastructure using Terraform on LocalStack, detects wasteful resources using a Python "Cost Janitor" script, and enforces cost hygiene continuously via GitHub Actions CI/CD.

---

## How to Run Locally

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

- **Claude (claude.ai)** — Used for boilerplate Terraform HCL structure and GitHub Actions workflow skeleton.
- **One thing AI got wrong** — The initial `janitor.py` had a bug: `if args.delete and not args.dry_run` would never execute because `--dry-run` defaults to `True`. Caught this during manual code review and fixed it to `if args.delete`.
- **Written manually without AI** — The `DESIGN.md` failure mode analysis (Section 3) was written manually because it required thinking through NimbusKart's specific operational context — a scheduled batch job scenario and a mid-snapshot detach scenario — which AI generated too generically.
EOF

Commit Karo:
bashcd /workspaces/Nimbuskart-e-commerce-sparklewood-assignment
git add .
git commit -m "docs: add README and DESIGN.md"
git push origin main
