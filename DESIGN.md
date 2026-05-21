# Design Note — Cost Janitor: Hardening, Scale & Production

## 1. Multi-Cloud Reality

To support GCP (and later Azure) without rewriting core logic, the Janitor
uses a provider abstraction layer:
janitor/
├── core/
│   ├── base_provider.py     ← Abstract base class
│   └── scanner.py           ← Core loop (cloud-agnostic)
├── providers/
│   ├── aws_provider.py      ← AWS implementation
│   ├── gcp_provider.py      ← GCP implementation (future)
│   └── azure_provider.py    ← Azure implementation (future)
└── janitor.py               ← Entry point

Each provider implements these methods:
- `list_unattached_volumes()`
- `list_stopped_instances(days)`
- `list_idle_ips()`
- `list_untagged_resources(required_tags)`

The core scanner loop calls these methods without knowing which cloud it
is talking to. Adding GCP means writing one new `gcp_provider.py` — zero
changes to core logic.

---

## 2. Permissions

### Dry-Run Mode — Minimal IAM Policy (Read Only):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "JanitorReadOnly",
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeVolumes",
        "ec2:DescribeInstances",
        "ec2:DescribeAddresses",
        "ec2:DescribeTags",
        "ec2:DescribeSnapshots",
        "s3:ListAllMyBuckets",
        "s3:GetBucketTagging"
      ],
      "Resource": "*"
    }
  ]
}
```

### Delete Mode — Additional permissions needed:
- `ec2:DeleteVolume`
- `ec2:TerminateInstances`
- `ec2:ReleaseAddress`

These must be in a **separate IAM role** requiring MFA or approval
before assuming — never bundled with the read-only role.

---

## 3. Safety Net — Two Failure Modes

### Failure Mode 1: Stopped EC2 is a Scheduled Batch Job

A stopped instance might be a weekly batch job (e.g. runs every Sunday
night). It looks idle for 6 days but is critical infrastructure.
Naive auto-deletion would cause data loss and missed processing.

**Guardrails:**
- Require `DoNotDelete=true` tag for any scheduled job instances
- Check CloudTrail for last stop reason before flagging
- Require human approval for any termination over $50/month
- Send Slack alert 48 hours before any planned deletion

### Failure Mode 2: Recently Detached EBS Volume

A volume detached 10 minutes ago for a snapshot operation appears as
an "available" orphan immediately. Auto-deletion would permanently
destroy live production data.

**Guardrails:**
- Skip volumes detached less than 48 hours ago
- Never auto-delete volumes larger than 100 GB
- Always create a snapshot before deletion in --delete mode
- Set `safe_to_auto_delete: false` for all EBS volumes by default

---

## 4. Observability

| Metric | Source | Alert Threshold |
|--------|--------|-----------------|
| `janitor.orphans_found` | Janitor → CloudWatch | Alert if > 10 per scan |
| `janitor.estimated_waste_usd` | Janitor → CloudWatch | Alert if > $500/month |
| `janitor.scan_errors` | Janitor → CloudWatch | Alert if > 0 |
| `janitor.resources_deleted` | Janitor → CloudWatch | Alert if > 20 in one run |
| `janitor.scan_duration_seconds` | Janitor → CloudWatch | Alert if > 300 seconds |

A Grafana dashboard shows the 30-day trend of estimated waste so the
FinOps team can see whether the Janitor is actually reducing spend.

---

## 5. What I Did Not Build

I consciously left out the following to stay within the time budget:

- **Multi-account scanning** — Production needs role-chaining across
  all AWS accounts via AWS Organizations. Not practical in LocalStack demo.
- **GCP and Azure providers** — The abstraction layer is designed for
  them but only AWS is implemented in this submission.
- **Snapshot-before-delete** — Delete mode should snapshot EBS volumes
  before removing them. Skipped to keep the demo focused.
- **Slack and PagerDuty notifications** — CI posts a PR comment but a
  real deployment would push alerts to Slack with one-click approval links.
- **Terraform remote state** — Using local state for simplicity.
  Production needs S3 backend with DynamoDB locking to prevent conflicts.
