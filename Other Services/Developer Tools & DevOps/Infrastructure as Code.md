# Infrastructure As Code (IaC)

## What Is Infrastructure As Code

Infrastructure as Code (IaC) means managing and provisioning cloud infrastructure through **code**, not manual clicks in the console.

Instead of going into the AWS Management Console and manually clicking to create an EC2 instance, subnet, or IAM role, you write **code that defines those resources** — then deploy it in a predictable, repeatable way.

IaC turns infrastructure into versioned artifacts, just like application code:

- You can track changes over time (Git)  
- You can automate deployments (CI/CD)  
- You can enforce review policies (PRs, approvals)  
- You can audit everything — down to the exact line that created a security group rule  

In a **cloud security** context, IaC gives you **visibility, control, and consistency** — all of which are vital for preventing misconfigurations, enforcing least privilege, and locking down your environment.

---

## Cybersecurity Analogy

IaC is like using a **secured, signed blueprint** to build a house — instead of letting every worker freelance the wiring and plumbing.

In traditional cloud setups, humans manually create things. One admin might forget MFA on an IAM user. Another might leave SSH open to the world.

With IaC, everything is **codified**.  
If the blueprint says “no public access,” no one can sneak in a side door — and if they try, the blueprint catches the **drift**.

## Real-World Analogy

Imagine you’re building IKEA furniture:

- Without instructions (manual): You try to eyeball it. One leg’s longer. You forget a screw. Now it’s unstable.  
- With step-by-step instructions (IaC): You follow precise, repeatable instructions. If it breaks, you rebuild it exactly the same. Or tear it down cleanly.  

IaC lets you **destroy and rebuild environments with confidence** — whether it’s dev, test, prod, or recovery.

---

## Core IaC Tools In AWS Ecosystem

| Tool               | Description                                           | Security Relevance                                        |
|--------------------|-------------------------------------------------------|------------------------------------------------------------|
| AWS CloudFormation | Native IaC tool for defining AWS resources (YAML/JSON) | Tight IAM controls, rollback, drift detection              |
| Terraform          | Open-source tool by HashiCorp (HCL syntax)            | Multi-cloud, supports AWS + others, security modules       |
| Pulumi             | IaC with general-purpose languages                    | More flexibility, less adoption in AWS-heavy shops         |
| CDK (Cloud Dev Kit)| AWS’s code-based IaC (Python/TS → CloudFormation)     | Dev-friendly, security constructs, still CFN under the hood|

---

## Security Benefits Of IaC

**Auditability**  
Every change is tracked in Git. Want to know who opened a security group to `0.0.0.0/0`? Look at the commit history.

**Consistent Least Privilege**  
You can define IAM policies, KMS keys, bucket ACLs, etc. in templates — and ensure no one adds permissions manually after the fact.

**Drift Detection**  
With CloudFormation Drift Detection, you can detect when someone changes a resource **outside the template** — and flag or revert it.

**Automated Security Scanning**  
Tools like:
- Checkov  
- TFSec  
- CFN-Nag  
- KICS  
- Snyk IaC  
- cfn-guard  

Can scan your templates **before deployment** and catch things like:
- Open security groups  
- Over-permissive IAM roles  
- Unencrypted volumes  
- Disabled logging  

You can plug these into your **CI/CD pipeline** to block insecure changes automatically.

---

## Security Risks Of IaC (If Misused)

| Risk                 | Description                                         |
|----------------------|-----------------------------------------------------|
| Credential Leakage    | Hardcoded access keys or secrets in templates       |
| Over-permissioned Roles | Admin policies granted by accident or laziness   |
| Drift from Manual Edits | Console edits break IaC control loops            |
| Lack of Guardrails    | Without pre-deployment scanning, bad configs deploy |
| Insecure Defaults     | Dev teams copy-paste unsafe patterns (e.g., public S3 buckets) |

---

## Real-Life Example (Snowy & The Dev Team)

Snowy, the cloud security engineer at **WinterCorp**, notices a trend:

- Dev teams keep opening ports in security groups for testing — and forgetting to close them  
- IAM roles are being created manually, and nobody is logging changes  
- Some resources don’t even have tags or logging  

**Snowy proposes a shift:**

- All infrastructure must be deployed via **CloudFormation or Terraform**  
- Each PR is scanned with **Checkov + CFN-Nag**  
- Only **signed Git commits** can be merged to the main infra branch  
- All stacks have **drift detection** enabled and checked weekly  
- Production stacks are protected with **StackSets + SCPs** to prevent direct console edits  

**After 3 months:**

- 90% reduction in open ports  
- 100% of IAM roles tied to Git  
- Audit trail for every KMS policy and S3 ACL  
- Drift report is clean  

**IaC turned chaos into confidence.**

---

## Security Best Practices For IaC In AWS

| Practice                          | Description                                                     |
|----------------------------------|-----------------------------------------------------------------|
| Use IAM conditions & explicit denies | Prevent privilege escalation in your templates             |
| Enforce encryption               | Add `Encrypted: true` to EBS, S3, RDS, etc. explicitly          |
| Scan templates pre-deployment    | Use open-source or commercial IaC scanners                      |
| Version control everything       | Use Git, pull requests, approvals                               |
| Restrict manual console edits    | Use CloudFormation StackSets and drift detection                |
| Use Parameter Store or Secrets Manager | Never hardcode secrets in templates                         |
| Tag all resources                | For cost, compliance, and inventory tracking                    |
| Use Change Sets or Plan mode     | Preview changes before deployment (like `terraform plan`)       |
| Apply least privilege in IAM roles/policies | Never default to `*:*` permissions                        |

---

## Pricing Model

IaC tools themselves are usually **free (open-source)**, but what you deploy is **not**.

That means:
- If IaC creates **100 TB of EBS snapshots**? You pay for storage.  
- If a template accidentally creates **5 NAT gateways**? Enjoy the surprise bill.  
- If drift causes **unintended duplication** of resources? Double the cost.  

**IaC amplifies mistakes** — so you need strong **review and policy gates**.

---

## Final Thoughts

**IaC is the foundation of secure, scalable cloud architecture.**  
But like any tool, it can either **protect** or **expose** you — depending on how it's used.

In the hands of a DevOps team without guardrails, IaC can deploy insecure resources **faster than ever**.

But in the hands of a **cloud security engineer** with strong review pipelines, scanning tools, and access control, IaC becomes:
- A **compliance enforcer**  
- A **security policy engine**  
- A **single source of truth**  

This isn’t optional anymore.  
If you're serious about security in AWS — you're serious about **Infrastructure as Code**.
