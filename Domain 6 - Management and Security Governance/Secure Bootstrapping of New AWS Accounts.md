# Secure Bootstrapping of New AWS Accounts

## What It Is

Bootstrapping refers to the initial setup and configuration of a newly created AWS account — especially in a multi-account organization using AWS Organizations, Control Tower, or custom automation.
By default, new AWS accounts are:

- Bare
- Unsecured
- Logging-disabled
- Lacking SCPs or controls
- Possibly vulnerable to drift or misconfigurations

Without a secure bootstrapping process, every new account is a potential security hole — no guardrails, no logging, no automation, no standards.
**Goal:** As soon as a new account is created, apply all necessary security baselines automatically — before human access even begins.

---

## Cybersecurity Analogy

Imagine a company adds a new employee, but doesn’t:

- Give them a badge
- Set up their workstation
- Add them to security policies
- Enable endpoint monitoring
- Provide secure communication channels

That’s what launching a raw AWS account is like.
Secure bootstrapping is your IT onboarding playbook — but for cloud accounts.
Without it, attackers get a playground, and compliance auditors get a heart attack.

---

## What Needs to Be Bootstrapped

For every new AWS account, you typically want to immediately:

| Category           | Example                                                                 |
|--------------------|-------------------------------------------------------------------------|
| Access Controls    | Create baseline IAM roles (Break Glass, ReadOnly, Admin), enable MFA    |
| Logging            | Enable CloudTrail, Config, GuardDuty, Security Hub, and centralize logs |
| Billing            | Attach cost tags, budgets, and alerts                                   |
| Networking         | Create default VPC or restrict network access                           |
| Governance         | Attach SCPs (Service Control Policies), tag policies, and backup plans  |
| Detection/Alerting | Enable SNS alerts for security findings or drift                        |
| Automation         | Deploy baseline CloudFormation stacks, SSM docs, or Terraform modules   |

You’re building a secure, standardized baseline, so every account is born “compliant and observed.”

---

## Common Bootstrapping Approaches

There are 3 major strategies:

### 1. AWS Control Tower (Native, Semi-Automated)
- Uses Account Factory via AWS Service Catalog
- Automatically applies guardrails, SCPs, baselines
- Integrates with AWS Organizations
- Great for org-wide standardization
- Can customize with Customizations for Control Tower (CfCT)

### 2. Custom Bootstrapping via Automation
- Use EventBridge + Lambda/Terraform/SSM triggered on CreateAccount events
- Use Org Management account to assume roles in child account
- Deploy CloudFormation StackSets, baseline policies, logging
- Great for fine-grained control and non-Control Tower orgs

### 3. Delegated Admin with Service Catalog / SSM / CDK Pipelines
- Build self-service account creation systems for engineers
- Enforce IaC templates on account creation (e.g., Landing Zone)
- Integrate approval flows via ServiceNow/Jira if needed

---

## Secure Bootstrapping Flow (Example)

- Create Account in AWS Organizations (via console, API, or Account Factory)
- Trigger EventBridge Rule on CreateAccountResult
- Lambda Function assumes role in new account and deploys:
  - CloudTrail → centralized S3 bucket
  - GuardDuty → enabled + findings to Security Hub
  - Baseline IAM roles (e.g., Snowy-ReadOnly, Snowy-Admin)
  - SCPs → restrict non-approved regions and services
  - Config → delivery to audit account
  - Tagging → apply account type, owner, cost center
  - Optional: Enable VPC Flow Logs or default deny all traffic
- Send Notification (e.g., to SnowySecOps Slack channel)
- Optional Compliance Scan via AWS Config Custom Rules

---

## Security Relevance

| Risk If Skipped         | How Bootstrapping Helps                        |
| Inconsistent IAM policies | Ensures baseline roles and access             |
| No logging                | Enables CloudTrail, Config, GuardDuty         |
| Misconfigured VPCs        | Denies traffic or deploys standard network    |
| Drifting compliance       | SCPs enforce guardrails                       |

| Shadow IT or sprawl       | Tagging and budgets flag rogue accounts       |
| No detection              | GuardDuty + Security Hub + SNS gives visibility |

Bootstrapping reduces time to governance from **days to minutes**.

---

## Bonus: Integration with Security Tools

| Tool                     | Role in Bootstrapping                  |
|--------------------------|----------------------------------------|
| CloudTrail               | Enabled and centralized                |
| Config                   | Captures resource drift from start     |
| GuardDuty                | Monitors for threats day-one           |
| Security Hub             | Central findings dashboard             |
| Inspector / Macie        | Optional early scans                   |
| SSM                      | Enables post-creation hardening        |
| Tag policies             | Enforces compliance tagging            |
| Service Control Policies (SCPs) | Block unapproved services or Regions |
| Budgets / Cost Explorer  | Alert on cost spikes early             |

---

## Final Thoughts

A secure AWS account is not born — **it’s bootstrapped**.
Whether you use Control Tower, custom EventBridge/Lambda automation, or Terraform/CDK StackSets, the outcome should be the same:

- Logs flow from minute 1
- IAM is clean and enforced
- Regions and services are restricted
- Findings are visible in Security Hub
- Every account is accounted for

**SnowyCorp** doesn’t let fresh accounts sit naked and unmonitored.
Every account gets the same hoodie, badge, and alarm system — *before* it’s handed to an engineer.
