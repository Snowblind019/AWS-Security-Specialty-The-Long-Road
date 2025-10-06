# Drift Detection in AWS

## What Is Drift Detection

Drift refers to any **difference between the actual state of your AWS resources and the expected (declared) state in your infrastructure-as-code (IaC) templates**.

In simpler terms:

- You say in your **CloudFormation** or **Terraform** file: *"This EC2 instance should have Tag: Environment = Production"*
- Someone manually removes that tag from the AWS Console
- Now your deployed environment has **drifted**

That drift:

- Might break automation scripts  
- Could violate compliance rules  
- Might silently weaken your security posture (e.g., open a port, remove encryption, change a logging destination)

---

## Cybersecurity Analogy

Drift detection is like **tripwire sensors** on the windows of a secure building.

The blueprint (your **IaC**) says every window should have a sensor.

If someone opens a window and disables the sensor, **you need to know** — because now there's a gap in your perimeter, and your monitoring won’t trigger.

## Real-World Analogy

Imagine you're running a **datacenter** and your blueprints specify:

- 3 fire extinguishers per floor  
- Security cameras in each hallway  
- Locks on every door  

If someone removes a fire extinguisher or disables a camera, and nobody knows — you've got risk.

**Cloud drift is the same.**  
What you *think* you’ve deployed… might not be what’s really there.

---

## Common Causes of Drift

| Cause                         | Example                                         |
|------------------------------|-------------------------------------------------|
| Manual changes via Console   | Security Group rule deleted manually            |
| Out-of-band scripts          | DevOps runs `aws ec2 modify-instance-attr`      |
| Changes in dependent resources | Replacing a Lambda that breaks S3 trigger     |
| Policy overwrites            | SCPs or org-wide tagging policies               |
| Accidental admin actions     | IAM role updated without IaC update             |

---

## How AWS Detects Drift

### 1. AWS CloudFormation Drift Detection

CloudFormation supports drift detection for:

- **Stacks**  
- **Stack sets**  
- **Supported resource types** (not all are supported)

**How it works:**

- You click “Detect Drift” (or call the API)
- AWS compares live resource configurations vs. what’s defined in the template
- You get a drift status per resource:
  - `IN_SYNC`: matches the template  
  - `MODIFIED`: has drift  
  - `DELETED`: resource was removed  
  - `NOT_CHECKED`: unsupported resource type  

```bash
aws cloudformation detect-stack-drift --stack-name MyStack
```
> Results shown in AWS Console or via `describe-stack-resource-drifts`

### 2. Terraform Drift Detection (Plan vs Apply)

- `terraform plan` compares:
  - Current live infrastructure (via state + refresh)
  - Against the `.tf` files (expected config)
  - Any drifted resources show up as proposed changes

- Useful to catch changes even if nobody touched your `.tf` file  
- But there's no auto-alert mechanism unless you script it

---

## Why Drift Detection Matters for Security

| Drift Scenario                          | Risk Introduced                                |
|----------------------------------------|------------------------------------------------|
| Logging configuration removed from S3 bucket | No audit trail, blind spot              |
| EC2 loses encryption-at-rest setting   | Data compliance failure                         |
| Security Group changed to open port 22 to 0.0.0.0 | Remote attack surface exposed         |
| IAM Role policy altered manually       | Privilege escalation or lateral movement risk   |
| CloudWatch Alarms disabled manually    | Incident response delayed                       |

---

## Use Cases in Cloud Security

| Use Case                        | Drift Detection Role                                 |
|--------------------------------|------------------------------------------------------|
| Compliance Automation (HIPAA/NIST) | Verify encryption, tags, logging still intact   |
| IAM Governance                 | Detect unexpected privilege escalation              |
| Guardrails Enforcement         | Trigger alerts when guardrails are bypassed         |
| Threat Detection Integrity     | Ensure logging pipelines haven’t been disabled      |
| Multi-account Drift            | Use StackSets with drift checks across accounts      |

---

## How to Enforce Drift Detection

### CloudFormation Approach (StackSets + Drift)

1. Deploy infrastructure via **StackSets**  
2. Enable **automatic drift detection**:
   - Schedule checks (via **Lambda/EventBridge**)  
   - Alert to **SNS** if drift found  
3. Add to security audit dashboard

```bash
aws cloudformation detect-stack-set-drift --stack-set-name CoreInfra
```

### Terraform Approach (Plan + GitOps)

1. Run `terraform plan` daily via CI/CD  
2. Pipe output to GitHub Action or **CodeBuild**  
3. Notify on drifted resources

### Add Drift Checks to GuardDuty/Config Workflow

- Use **AWS Config Rules** to define expected state:
  - e.g., “S3 buckets must have versioning enabled”
- Detect drift outside of **IaC** using **Config Remediation**
- Pair with **GuardDuty** to catch changes + anomalies

### Logging and Alerting

Use this flow:

**Detect Drift →  
Log to CloudWatch Logs / Security Hub →  
Trigger EventBridge →  
Notify SOC or NOC →  
Optionally auto-remediate via Lambda**

---

## Real-Life Example (Snowy’s Zero-Drift Promise)

Snowy rolls out 27 **CloudFormation** stacks to multiple accounts.

A week later, an engineer **hotfixes** a security group manually to allow `0.0.0.0/0` SSH access — without going through **IaC**.

Drift detection catches it.

**Steps taken:**

- Stack status marked `MODIFIED`  
- **CloudWatch** alarm fires from **EventBridge** rule  
- **Security Hub** note generated  
- **Lambda** rolls back to template-defined SG rule  
- Engineer reminded to use **IaC** workflows  

✔️ Breach avoided  
✔️ Template remains source of truth  
✔️ Audit trail intact

---

## Final Thoughts

**Drift detection is your cloud version of file integrity monitoring.**

Without it, you’re relying on *assumptions*. With it, you’re enforcing *declarations*.

In AWS:

- **CloudFormation** gives you native, audited drift detection  
- **Terraform** gives you drift detection during CI/CD  
- **AWS Config** gives you policy compliance beyond **IaC**  
- **EventBridge** + Lambda gives you auto-remediation  

**Clouds drift. Security shouldn’t.**
