#!/usr/bin/env python3
"""Cost Janitor — detects orphaned AWS resources."""

import argparse
import json
import sys
from datetime import datetime, timezone
import boto3
from constants import EBS_GP3_PER_GB_MONTH, EIP_IDLE_PER_MONTH, EC2_T3_MICRO_PER_MONTH

REQUIRED_TAGS = ["Project", "Environment", "Owner"]
STOPPED_THRESHOLD_DAYS = 14


def get_client(service, endpoint_url, region):
    return boto3.client(
        service,
        endpoint_url=endpoint_url,
        region_name=region,
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )


def check_orphan_ebs(ec2, findings):
    """Find EBS volumes in available (unattached) state."""
    vols = ec2.describe_volumes(
        Filters=[{"Name": "status", "Values": ["available"]}]
    )
    for vol in vols["Volumes"]:
        tags = {t["Key"]: t["Value"] for t in vol.get("Tags", [])}
        if tags.get("Protected") == "true":
            continue
        age = (datetime.now(timezone.utc) - vol["CreateTime"]).days
        size = vol.get("Size", 0)
        cost = size * EBS_GP3_PER_GB_MONTH
        findings.append({
            "resource_id": vol["VolumeId"],
            "resource_type": "ebs_volume",
            "reason": "unattached",
            "age_days": age,
            "estimated_monthly_cost_usd": round(cost, 2),
            "tags": {k: tags.get(k) for k in REQUIRED_TAGS},
            "suggested_action": "delete",
            "safe_to_auto_delete": False,
        })


def check_stopped_ec2(ec2, findings, stopped_days):
    """Find EC2 instances stopped for more than N days."""
    resp = ec2.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": ["stopped"]}]
    )
    for r in resp["Reservations"]:
        for inst in r["Instances"]:
            tags = {t["Key"]: t["Value"] for t in inst.get("Tags", [])}
            if tags.get("Protected") == "true":
                continue
            age = (datetime.now(timezone.utc) - inst["LaunchTime"]).days
            if age >= stopped_days:
                findings.append({
                    "resource_id": inst["InstanceId"],
                    "resource_type": "ec2_instance",
                    "reason": f"stopped_over_{stopped_days}_days",
                    "age_days": age,
                    "estimated_monthly_cost_usd": EC2_T3_MICRO_PER_MONTH,
                    "tags": {k: tags.get(k) for k in REQUIRED_TAGS},
                    "suggested_action": "terminate",
                    "safe_to_auto_delete": False,
                })


def check_unassociated_eips(ec2, findings):
    """Find Elastic IPs not associated with any instance."""
    resp = ec2.describe_addresses()
    for addr in resp["Addresses"]:
        if "InstanceId" not in addr and "NetworkInterfaceId" not in addr:
            tags = {t["Key"]: t["Value"] for t in addr.get("Tags", [])}
            if tags.get("Protected") == "true":
                continue
            findings.append({
                "resource_id": addr.get("AllocationId", addr.get("PublicIp")),
                "resource_type": "elastic_ip",
                "reason": "unassociated",
                "age_days": 0,
                "estimated_monthly_cost_usd": EIP_IDLE_PER_MONTH,
                "tags": {k: tags.get(k) for k in REQUIRED_TAGS},
                "suggested_action": "release",
                "safe_to_auto_delete": True,
            })


def check_missing_tags(ec2, findings):
    """Find resources missing required tags."""
    resp = ec2.describe_instances()
    for r in resp["Reservations"]:
        for inst in r["Instances"]:
            if inst["State"]["Name"] == "terminated":
                continue
            tags = {t["Key"]: t["Value"] for t in inst.get("Tags", [])}
            missing = [k for k in REQUIRED_TAGS if k not in tags]
            if missing:
                findings.append({
                    "resource_id": inst["InstanceId"],
                    "resource_type": "ec2_instance",
                    "reason": f"missing_tags:{','.join(missing)}",
                    "age_days": 0,
                    "estimated_monthly_cost_usd": 0.0,
                    "tags": {k: tags.get(k) for k in REQUIRED_TAGS},
                    "suggested_action": "tag",
                    "safe_to_auto_delete": False,
                })


def delete_resources(ec2, findings):
    """Delete orphaned resources — skip Protected=true."""
    for f in findings:
        if not f["safe_to_auto_delete"]:
            print(f"  SKIP (not safe): {f['resource_id']}")
            continue
        tags = f.get("tags", {})
        if tags.get("Protected") == "true":
            print(f"  SKIP (protected): {f['resource_id']}")
            continue
        if f["resource_type"] == "elastic_ip":
            ec2.release_address(AllocationId=f["resource_id"])
            print(f"  DELETED EIP: {f['resource_id']}")


def generate_markdown(report):
    lines = [
        "## 🧹 Cost Janitor Report",
        f"**Scan time:** {report['scan_timestamp']}",
        f"**Total orphans:** {report['summary']['total_orphans']}",
        f"**Estimated monthly waste:** ${report['summary']['estimated_monthly_waste_usd']}",
        "",
        "| Resource ID | Type | Reason | Age (days) | Est. Cost/mo |",
        "|---|---|---|---|---|",
    ]
    for f in report["findings"]:
        lines.append(
            f"| {f['resource_id']} | {f['resource_type']} | "
            f"{f['reason']} | {f['age_days']} | ${f['estimated_monthly_cost_usd']} |"
        )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Cost Janitor — AWS orphan detector")
    parser.add_argument("--dry-run", action="store_true", default=True,
                        help="Only scan, do not delete (default)")
    parser.add_argument("--delete", action="store_true",
                        help="Actually delete safe orphans")
    parser.add_argument("--endpoint-url", default="http://localhost:4566",
                        help="AWS/LocalStack endpoint URL")
    parser.add_argument("--region", default="us-east-1")
    parser.add_argument("--stopped-days", type=int, default=STOPPED_THRESHOLD_DAYS)
    args = parser.parse_args()

    ec2 = get_client("ec2", args.endpoint_url, args.region)

    findings = []
    check_orphan_ebs(ec2, findings)
    check_stopped_ec2(ec2, findings, args.stopped_days)
    check_unassociated_eips(ec2, findings)
    check_missing_tags(ec2, findings)

    # Deduplicate by resource_id
    seen = set()
    unique_findings = []
    for f in findings:
        if f["resource_id"] not in seen:
            seen.add(f["resource_id"])
            unique_findings.append(f)
    findings = unique_findings

    total_cost = sum(f["estimated_monthly_cost_usd"] for f in findings)

    report = {
        "scan_timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "account_id": "000000000000",
        "region": args.region,
        "summary": {
            "total_orphans": len(findings),
            "estimated_monthly_waste_usd": round(total_cost, 2),
        },
        "findings": findings,
    }

    with open("report.json", "w") as f:
        json.dump(report, f, indent=2)

    md = generate_markdown(report)
    with open("report.md", "w") as f:
        f.write(md)

    print(md)

    if args.delete:
        print("\n🗑️  DELETE MODE — removing safe orphans...")
        delete_resources(ec2, findings)

    if findings:
        sys.exit(1)


if __name__ == "__main__":
    main()