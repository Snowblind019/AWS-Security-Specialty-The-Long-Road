# Secure Defaults in AWS

## What Are Secure Defaults

A secure default means that if a user does nothing, the system’s baseline behavior is already designed to minimize risk.

In AWS terms:
- An S3 bucket should default to **private**
- A Security Group should default to **deny all inbound**
- A KMS key should default to **enable automatic rotation**
- A new IAM role should **not come with broad permissions**

**Why it matters:**

Most breaches don’t start with some elite zero-day. They start with someone forgetting to tighten permissions, turn on encryption, or block a public port. Secure defaults make it harder to accidentally create vulnerabilities.

---

## Cybersecurity Analogy

Think of AWS as a hotel.
Secure defaults mean that:
- Every door is locked by default
- Room keys expire automatically
- Hallway cameras are recording from Day 1
- Staff have least privilege access to just their floor

If someone wants to weaken security (like disabling cameras), they have to consciously do it and leave an audit trail — not just forget to enable something.

## Real-World Analogy

Imagine you buy a brand new house.
Would you expect:
- The front door to be unlocked by default?
- The windows to be wide open?
- The smoke detectors to be disabled unless you turn them on?

No.
You expect it to come with a basic level of security already set — so if you do nothing, you’re still reasonably protected.
**Same in the cloud.**

---

## Examples of Secure Defaults in AWS (And Weak Defaults to Watch Out For)

| AWS Feature              | Default Behavior                        | Secure? ✔️ / ✖️ | Notes                                                                 |
|--------------------------|-----------------------------------------|------------------|-----------------------------------------------------------------------|
| S3 Bucket ACLs           | Blocked by default (ACLs disabled)      | ✔️               | New buckets no longer support ACLs unless explicitly enabled         |
| S3 Bucket Access         | Private by default                      | ✔️               | But can be flipped via UI if not careful                             |
| Security Groups          | Allow no inbound, all outbound          | ✔️ for inbound   | Outbound could still pose risk depending on workload                 |
| IAM Users/Roles          | Start with zero permissions             | ✔️               | Follows least privilege                                               |
| KMS Keys (CMKs)          | Created with auto-rotation off          | ✖️               | Must explicitly enable rotation                                      |
| CloudTrail               | Not enabled by default                  | ✖️               | Must manually turn on auditing (account-level risk)                  |
| EBS Encryption           | Enabled by default (as of late 2021)    | ✔️               | Region-level default key can be changed                              |
| RDS Encryption           | Off unless specified                    | ✖️               | Must check box at creation                                           |
| VPC Endpoints            | Interface endpoints default to private  | ✔️               | No public IPs exposed                                                |
| Public IPs on EC2        | Auto-assigned for default subnets       | ✖️               | Must disable manually if needed                                      |
| CloudFront HTTPS         | HTTP & HTTPS enabled                    | ✖️               | Must enforce HTTPS only (Viewer Protocol Policy)                     |
| Secrets Manager          | Encrypted with KMS by default           | ✔️               | Tight integration with IAM                                           |
| SSM Session Manager Logs| Not logged unless configured            | ✖️               | Must explicitly enable logging to CloudWatch or S3                   |

---

## Why Secure Defaults Are Essential in Security Engineering

Security isn’t just about what you configure — it’s about what you **fail to configure**.

**Secure defaults:**
- Reduce the blast radius of mistakes
- Act as a safety net when teams move fast
- Enforce least privilege and least exposure
- Protect against “oops” moments in the console
- Aid in compliance (e.g., HIPAA, PCI) by aligning to security baselines

---

## Real Risk Example — Misconfigured Defaults

Snowy’s team spins up a test RDS instance during a late-night troubleshooting session.
They forget to check the “Enable encryption” box.

Weeks later, logs show that customer PII was backed up from prod to test — **unencrypted at rest**.

**What went wrong?**
- The default was insecure (encryption off)
- The team assumed encryption was automatic

This is exactly why default behavior needs to be secure — so the absence of a checklist item doesn’t equal a security gap.

---

## How to Enforce Secure Defaults at Scale

### 1. Use SCPs (Service Control Policies)

Block risky actions by default at the Org level:

- Deny s3:PutBucketPublicAccessBlock = false
- Deny RDS creation without encryption
- Deny EC2 with auto-assigned public IPs

```json
"Deny if public IP assigned": {
  "Effect": "Deny",
  "Action": "ec2:RunInstances",
  "Condition": {
    "Bool": {
      "ec2:AssociatePublicIpAddress": "true"
    }
  }
}
```

### 2. Use AWS Config Rules

Flag resources that don’t follow secure defaults:

- “S3 buckets must block public access”
- “RDS must have encryption enabled”
- “CloudFront must enforce HTTPS only”

**Add auto-remediation** via SSM documents or Lambda.

### 3. Use Custom AMIs and Launch Templates

- Lock down EC2 instances by default
- Enforce hardened OS images with secure defaults
- Predefine Security Groups, IAM Roles, encrypted volumes

### 4. Bake Into IaC Templates (CloudFormation / Terraform)

Never rely on human clicks in the Console:

- Hardcode HTTPS enforcement in CloudFront distributions
- Set KMS key aliases in all storage services
- Set `associate_public_ip_address = false` in EC2 launch code

---

## Final Thoughts

**Security should be the default, not the exception.**
AWS is trending toward more secure defaults (S3, EBS encryption), but many services still leave it up to you.

**Snowy’s Rule:**
*“If it can be misconfigured easily, you probably already misconfigured it once.”*

---

To win at scale:

- Audit defaults regularly
- Override weak defaults with Org-level controls
- Force everything through IaC or pipelines
- **Think like an attacker:** *where could you slip through?*
