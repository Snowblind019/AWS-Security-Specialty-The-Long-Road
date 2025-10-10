# Security Baselines in AWS — Deep Dive (Snowy Edition)

## What Is a Security Baseline (And Why It’s Important)

A **security baseline** is a standardized, predefined set of security controls, settings, and configurations that every AWS resource or environment must comply with — regardless of team, service, or workload.

It's the **minimum viable security posture** — the default security wall you should never go below.  
Anything more secure is a bonus. Anything less is unacceptable.

**Security baselines help ensure:**

- Consistency across teams and environments  
- Compliance with frameworks (CIS, NIST, PCI-DSS, etc.)  
- Least privilege access  
- Monitoring, logging, and alerting are always in place  
- Avoidance of misconfigurations or drift over time  

You can think of baselines as **“security guardrails”** that apply from **Day 0**.

---

## Cybersecurity Analogy

Imagine you’re building a new apartment complex. Every unit must, at a minimum, include:

- Deadbolt locks on all doors  
- Smoke detectors  
- Fire extinguishers  
- Carbon monoxide detectors  
- Secure windows  
- Evacuation maps  

**That’s the baseline.**  
Tenants are free to add cameras, alarms, or watchdogs — but those base protections can’t be skipped, ever.

## Real-World AWS Analogy

- Launch public EC2s without logging  
- Store data in S3 buckets open to the world  

- Use default VPCs without NACLs or proper route tables  
- Disable GuardDuty and Config  
- Create IAM roles with wildcard privileges (`*:*`)  

- Leave CloudTrail off  

Multiply that across environments… and you've built a **chaos factory**.

But with a security baseline baked into every account via:

- **Organizations SCPs**  
- **AWS Config rules**  
- **Infrastructure as Code (IaC)**  

You guarantee that:

- CloudTrail is enabled  
- S3 buckets are private by default  
- MFA is required for root accounts  
- IAM roles follow least privilege  
- GuardDuty + Security Hub are enabled  
- Logging + encryption are enforced  

Even if a dev team forgets — **the baseline catches them.**

---

## What’s in a Good AWS Security Baseline?

| **Category**           | **Baseline Controls** |
|------------------------|------------------------|
| **Identity & Access**  | Root account MFA, strong password policy, no hardcoded keys, least privilege IAM roles |
| **Logging & Monitoring** | CloudTrail enabled, Config enabled, S3 access logs, VPC Flow Logs, GuardDuty on |
| **Encryption**         | EBS/S3/RDS encryption at rest, HTTPS/TLS enforced in transit, KMS key rotation |
| **Network Security**   | Default deny NACLs, strict Security Groups, no `0.0.0.0/0` SSH, private subnets preferred |
| **Compute Hardening**  | Patch management, use of hardened AMIs, disable IMDSv1, install SSM Agent |
| **Secrets Management** | Use Secrets Manager or SSM Parameter Store, no secrets in environment variables |
| **Compliance**         | Use Config rules + Security Hub to enforce compliance and detect drift |
| **Backup & Resilience** | Enable backup plans, versioning, lifecycle policies, test restores |

---

## Where Security Baselines Come From

AWS provides multiple sources and tools for building baselines:

**AWS Well-Architected Framework – Security Pillar**  
Guides secure-by-design choices for cloud workloads.

**AWS Security Reference Architecture (SRA)**  
Defines a multi-account, multi-layer security design pattern.

**CIS AWS Foundations Benchmark**  
Industry baseline. Scored assessment of 40+ controls like:

- Ensure CloudTrail is enabled in all regions  
- Ensure S3 buckets are not public  
- Ensure IAM policies do not allow full `*:*` access  

Use this as a **starting point for automated compliance.**

**NIST 800-53 / ISO 27001**  
More strict. Required for **GovCloud** and **FedRAMP** workloads.

---

## How to Implement Security Baselines in AWS

**1. Use Organizations SCPs (Service Control Policies)**  
Apply deny rules globally.  
*Example:* Deny EC2 without EBS encryption  
SCPs apply **regardless** of what IAM allows.

**2. Use AWS Config Rules**  
Deploy managed (or custom) rules that check:

- Whether S3 buckets block public access  
- Whether IAM roles follow naming conventions  
- Whether RDS instances are encrypted  

Trigger remediation with **Lambda** or **Systems Manager**.

**3. Use Infrastructure as Code (IaC)**  
Define security settings in:

- **CloudFormation**  
- **Terraform**  
- **AWS CDK**  

Bake in baseline controls — encryption, logging, IAM roles — into your **IaC templates** so every deployment **inherits the baseline**.

**4. Use Guardrails from AWS Control Tower**  
If using **Control Tower**, you get built-in **preventive + detective controls** via SCPs and Config.

---

## How to Monitor & Enforce Baselines

| **Tool**           | **Purpose**                               |
|--------------------|--------------------------------------------|
| **AWS Config**     | Continuous compliance checks               |
| **Security Hub**   | Central view of misconfigs + scorecard     |
| **AWS Organizations** | Enforce SCPs across accounts           |
| **AWS Inspector**  | Detect unpatched EC2s or vulnerable images |
| **GuardDuty**      | Threat detection on top of misconfigs      |
| **Audit Manager**  | Generate evidence for controls like CIS/NIST |

---

## Real-Life Example

Snowy’s company manages **12 AWS accounts** across dev/staging/prod. He sets up:

- **SCPs** that deny IAM wildcard roles  
- **Config rules** for required S3 encryption + MFA delete  
- **CloudFormation templates** that force:  
  - Encrypted EBS volumes  
  - Hardened AMIs with IMDSv2 only  
  - VPC Flow Logs  
- **GuardDuty + Security Hub** enabled Org-wide  
- **Compliance reports** via Security Hub and Audit Manager  

Whenever a new account is created or new infra is deployed, it’s **already aligned with the baseline** — not after the fact.

---

## Final Thoughts

Security baselines are like the **immune system** of your AWS environment.

They don’t stop every threat, but they raise the **minimum bar** so that:

- You reduce attack surface  
- You avoid drift and sprawl  
- You gain visibility and control  
- You build secure-by-default infrastructure  

**Without baselines?** Every developer makes their own rules.  
**With baselines?** Every workload starts on solid ground — and you scale securely.

