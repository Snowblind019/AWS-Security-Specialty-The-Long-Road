# Avoiding Insecure Configurations
## What Is an Insecure Configuration

An **insecure configuration** is when a cloud resource is deployed with **unsafe defaults**, **overly permissive settings**, or **missing critical controls**. These misconfigurations often don’t violate AWS limits or fail CI/CD pipelines — but they silently introduce **attack vectors**.

### Examples:
- An S3 bucket with **public read access**  
- A security group open to `0.0.0.0/0` on port 22 or 3389  
- An IAM policy with `*:*` permissions  
- An EC2 instance with **no CloudWatch logging** or **IMDSv2 disabled**  
- An RDS instance with **public accessibility enabled**  

**Why it matters:**  
Most breaches in cloud environments stem from **misconfigurations**, not zero-day exploits. Preventing these from getting deployed in the first place is critical for a **preventative security posture**.

---

## Cybersecurity Analogy

Imagine giving your house keys to a housekeeper… but also giving them your **alarm code**, **garage opener**, **master password**, and **ATM PIN**.  
That’s what `iam:*` does — **way more than necessary**.  
Insecure configs are like **putting your valuables on the front porch and hoping nobody notices**.

## Real-World Analogy

Let’s say Snowy buys a new router, plugs it in, and never changes the **default admin password** or **Wi-Fi name**.

Technically, it works.  
But anyone nearby can brute-force or guess the default credentials — and boom, **network compromised**.

Insecure configs are like **using factory defaults** and assuming nobody will check.

---

## Common Insecure Config Patterns in AWS

| **Resource**      | **Insecure Configuration Example**                  | **Why It’s Dangerous**                         |
|-------------------|-----------------------------------------------------|------------------------------------------------|
| S3 Bucket         | `BlockPublicAccess = false`                         | Public data leaks                              |
| Security Group    | Inbound rule: `0.0.0.0/0 -> port 22`                | Open to SSH brute-force                        |
| IAM Role/Policy   | `Action: "*", Resource: "*"`                        | No least privilege                             |
| EC2 Instance      | Public IP + SSH open + no IMDSv2                    | Complete takeover risk                         |
| RDS               | `Publicly Accessible = true`                        | Attack surface exposed                         |
| Lambda            | No environment variable encryption                  | Secrets in plaintext                           |
| ECS Task          | No IAM role, accesses resources via env vars        | Secret sprawl                                  |
| CloudFront        | `Viewer Protocol Policy = Allow HTTP`               | No encryption in transit                       |
| API Gateway       | No usage plan or throttling                         | DoS risk, overuse                              |

---

## How to Prevent Insecure Configurations

### 1. Use Secure Baselines (Modules)

- Start with **hardened IaC modules** (Terraform, CloudFormation)  
- Embed guardrails: **least privilege**, **deny policies**, **logging**, **encryption**

### 2. Enable AWS Config Rules

Use built-in rules like:

- `s3-bucket-public-read-prohibited`  
- `iam-user-no-policies-check`  
- `ec2-instance-no-public-ip`  

Apply **Conformance Packs** for frameworks like **CIS**, **PCI**, **NIST**.

### 3. Use Static Analysis & Linters

Tools for scanning IaC:

- **Checkov** (Terraform/CFN)  
- **tfsec**  
- **cfn-lint**  
- **cfn-guard**  
- **AWS CloudFormation Guard**

Catch dangerous patterns like:

```hcl
resource "aws_security_group" "bad" {
  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
  }
}
```

### 4. Leverage Service Control Policies (SCPs)

At the **organization level**, SCPs help enforce guardrails **before anything gets deployed**.

Use SCPs to:

- Prevent dangerous permissions like `iam:*` or `kms:Decrypt` from being assigned freely  
- Block creation of **public S3 buckets**, **unencrypted RDS instances**, etc.  
- Restrict usage of **unsupported Regions** or services  

**SCPs act as permissions boundaries** — even if someone tries to deploy insecure infra, the request is blocked at the org level.

### 5. Guard Your CI/CD Pipelines

Security can’t be left until runtime — it must be embedded in your **CI/CD tooling**.

Enforce:

- **Template scans before merge/deploy**  
- Blocking of **high-risk resource types** unless approved  
- Manual approvals for **IAM/Security Group changes**  

Integrate tools like:
- **GitHub Actions**  
- **OPA (Open Policy Agent)**  
- **AWS CodePipeline**  
- **Custom pre-commit hooks**

### 6. Enable Logging

**Insecure = unobservable**.  
If you can't see what's happening, you can't secure it.

Turn on logging across all layers:

- **AWS CloudTrail (org-wide)** — API-level visibility  
- **S3 Server Access Logs** — track access to sensitive buckets  
- **VPC Flow Logs** — detect lateral movement or data exfiltration  

- **Lambda Execution Logs** — catch insecure runtime behavior  
- **Route 53 Resolver Logs** — monitor DNS queries for suspicious patterns  

Logging is also required for **forensics**, **audits**, and **compliance**.

---

## Drift Detection Is Your Backup Alarm

Even if your IaC is perfect, **manual changes** happen:

> "Quick fix in prod…"  
> "Just testing something in the console…"  
> "It’s only temporary…"  


Drift introduces silent risk.

Use:

- **AWS Config** — tracks resource compliance and drift  
- **CloudFormation Drift Detection** — detects differences between template and live stack  

- **Terraform plan/apply** — compare actual vs intended state  

Make drift detection part of your **daily security hygiene**.

---

## Snowy’s Team Strategy

Snowy’s org has **4 teams with production access**. To prevent misconfigurations:

- All **Terraform runs** must pass **Checkov + tfsec**  
- **GitHub** enforces **OPA policies** to block public S3 modules  
- **AWS Config** sends **Slack alerts** when security groups are changed  
- **SCPs** prevent **RDS instances with public IPs** from being created  

> ❗ No one can say “I didn’t know.”  
> ❗ It’s enforced **by design**, not by memory or hope.

---

## Final Thoughts

Cloud misconfigurations don’t always come from **carelessness**.  
They come from:

- **Speed**  
- **Copy-paste culture**  
- **Lack of visibility**

---

### Snowy’s Rule:

> **If it’s possible to misconfigure, someone eventually will.**

So we:

- **Embed guardrails** into IaC and pipelines  
- **Block insecure patterns** with policies and controls  
- **Audit continuously** with logs, Config rules, and drift detection  

That’s how you stay secure — even when everything is moving fast.

