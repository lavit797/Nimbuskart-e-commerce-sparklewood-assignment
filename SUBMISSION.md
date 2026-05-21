# Submission — DevOps Engineer Assignment

**Candidate name:** Lavit (apna full name likho)
**Email:** apni@email.com
**Date submitted:** 2026-05-21
**Hours spent (approximate):** 8

## Deliverables checklist

- [x] Part A: Terraform code under /terraform applies cleanly on LocalStack
- [x] Part A: `terraform validate` and `terraform fmt -check` both pass
- [x] Part B: Janitor script runs in --dry-run mode and produces report.json
- [ ] Part B: GitHub Actions workflow runs green on a fresh PR
- [x] Part B: --delete mode respects Protected=true tag
- [x] Part C: DESIGN.md is present and within 2 pages

## Walkthrough video

Link (Loom / YouTube unlisted / Google Drive): (video record karne ke baad link yahan add karo)
Length: max 5 minutes

## Sample report

Path to a sample report.json produced by your script:
`samples/report.example.json`

## Known limitations

- GitHub Actions workflow LocalStack health check may need extra wait time
  on slow runners
- Stopped EC2 age is calculated from LaunchTime not StopTime — CloudTrail
  integration needed for accurate stopped duration
- Delete mode currently only releases Elastic IPs — EBS and EC2 deletion
  needs additional safety checks before enabling
- No unit tests written — Moto-based tests would be the next addition
- Walkthrough video to be recorded before final submission

## AI usage disclosure

- **Claude (claude.ai)** used for Terraform HCL boilerplate, GitHub Actions
  workflow skeleton, and janitor.py structure.
- **One thing AI got wrong:** Initial janitor.py had a bug —
  `if args.delete and not args.dry_run` would never execute because
  `--dry-run` defaults to True. Caught this during manual code review
  and fixed to `if args.delete`.
- **Written manually without AI:** The DESIGN.md failure mode analysis
  (Section 3) — specifically the batch job and mid-snapshot detach
  scenarios — was written manually because AI generated these too
  generically without thinking through NimbusKart's specific context.
