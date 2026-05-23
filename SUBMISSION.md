# Submission — DevOps Engineer Assignment

**Candidate name:** Lavit Tyagi
**Email:** lavittyagi2004@gmail.com
**Date submitted:** 2026-05-22
**Hours spent (approximate):** 8

## Deliverables checklist

- [x] Part A: Terraform code under /terraform applies cleanly on LocalStack
- [x] Part A: `terraform validate` and `terraform fmt -check` both pass
- [x] Part B: Janitor script runs in --dry-run mode and produces report.json
- [x] Part B: GitHub Actions workflow runs green on a fresh PR
- [x] Part B: --delete mode respects Protected=true tag
- [x] Part C: DESIGN.md is present and within 2 pages

## Walkthrough video
Loom link :- https://www.loom.com/share/7a789fb5c9d9421993a8ae00ec437f34
 

## Sample report

Path to a sample report.json produced by your script:
`Nimbuskart-e-commerce-sparklewood-assignment\janitor\report.example.json`

## Known limitations

- GitHub Actions workflow LocalStack health check may need extra wait time
  on slow runners
- Stopped EC2 age is calculated from LaunchTime not StopTime — CloudTrail
  integration needed for accurate stopped duration
- Delete mode currently only releases Elastic IPs — EBS and EC2 deletion
  needs additional safety checks before enabling
- No unit tests written — Moto-based tests would be the next addition
  

## AI usage disclosure

- **Claude (claude.ai)** — Used for boilerplate Terraform HCL structure and janitor.py file .
- **One thing AI got wrong** — The initial `janitor.py` had a bug: `if args.delete and not args.dry_run` would never execute because `--dry-run` defaults to `True`. Caught this during manual code review and fixed it to `if args.delete`. because localstack create a fake infra soo Ami id suggested by claude is also fake which creates a problem of block device mapping soo i had fetch the already existed ami id on local stack by using command (awslocal ec2 describe-images --output table --query 'Images[*].[ImageId,Name,State]') then first ami id i got i had replaced it with ami in main.tf file.
- **Written manually without AI** — i had written  Terraform stack for NimbusKart's baseline infra (VPC + EC2 + S3 + tagging policy), targeting LocalStack manually although to be very honest i had used hashicorp hcl extensions which suggest me the code syntax,  The `DESIGN.md` failure mode analysis (Section 3) was written manually because it required thinking through NimbusKart's specific operational context — a scheduled batch job scenario and a mid-snapshot detach scenario . 
