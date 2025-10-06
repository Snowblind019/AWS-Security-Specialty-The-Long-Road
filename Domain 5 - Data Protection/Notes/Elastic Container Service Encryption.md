# ECS Encryption

## What Does “ECS Encryption” Actually Mean?

ECS doesn’t encrypt anything by default.  
There’s no magic switch labeled “encrypt this task.”

When people say “ECS encryption,” they’re usually talking about the components around the task, like:

- EBS volumes attached to ECS on EC2  
- EFS volumes mounted into containers  
- Secrets fetched from Secrets Manager / SSM  
- Container images stored in ECR  
- Logs written to CloudWatch  
- Network traffic in and out of the task  

And every one of those layers has its own encryption model, its own KMS behavior, and its own set of things you can screw up.

Let’s break it down.

---

## Cybersecurity Analogy

Running ECS without encryption is like building a bank with fancy walls, cameras, guards — and then sending all your money around in unlocked, unmarked duffel bags.

You don’t get security just because the system looks “isolated.”  
If you’re not encrypting at rest, in transit, and in use, then you’re relying on luck and obscurity.

## Real-World Analogy

**Winterday** runs ECS tasks that process customer billing statements.

They:

- Pull secrets from SSM  
- Write output logs to CloudWatch  
- Store PDF reports on EFS  
- Use EC2 mode (with EBS volumes)

But:

- The EBS volume isn’t encrypted  
- CloudWatch logs are accessible to too many devs  
- EFS has no in-transit encryption  
- KMS access isn’t scoped per task

Now a low-priv dev with read-only access to EFS + logs can access customer PII — and there’s no audit trail for it.

Everything technically “worked” — but nothing was secured.

---

## ECS Encryption Layers (And What You Control)

### 1. EBS Volume Encryption (EC2 Mode Only)

If you're running ECS on EC2, and mounting EBS volumes for scratch space or persistent storage:

- Volumes must be encrypted manually when created  
- You can use `aws/ebs` (default key) or a custom CMK  
- Data, snapshots, and AMIs are all encrypted at rest  
- You can’t change encryption after creation

**What to do:**

- Use encrypted AMIs  
- Enforce encryption via SCP or Config rules (`ec2:CreateVolume`)  
- Monitor `kms:Decrypt` usage via CloudTrail  
- Limit KMS grants to specific IAM principals and ARNs  

### 2. EFS Encryption (At Rest + In Transit)

When your ECS tasks mount EFS:

- At-rest encryption is enabled at file system creation time  
- In-transit encryption is optional and must be explicitly configured  

If in-transit TLS isn’t set up:

- Data between the container and EFS moves over plaintext  
- Anyone sniffing traffic on the VPC (misconfigured mirror port, compromised node, etc.) could read data  

**What to do:**

- Always enable in-transit encryption  
- Use TLS-enabled mount helpers or `stunnel`  
- Monitor access using CloudTrail + VPC Flow Logs  
- Tag EFS volumes and audit encryption settings in AWS Config  

### 3. Container Image Encryption (Amazon ECR)

Images stored in Amazon ECR are encrypted at rest using KMS.

- By default, uses the `aws/ecr` managed CMK  
- You can configure ECR to use your own CMK  
- Encryption is transparent — it happens automatically when you push/pull

**Why this matters:**

- If an attacker somehow gains access to your ECR repo, they can pull images — encryption doesn’t stop that  
- But encryption does protect against S3 disk theft, physical compromise, etc.

**What to do:**

- Use private ECR repos only  
- Monitor image pulls with CloudTrail  
- Set lifecycle policies so old images don’t linger unencrypted forever  
- Limit `ecr:GetDownloadUrlForLayer` and `ecr:BatchGetImage` to CI/CD pipelines only  

### 4. Secrets Encryption (Secrets Manager & SSM)

ECS integrates with:

- Secrets Manager  
- SSM Parameter Store (SecureString)

Secrets are:

- Encrypted at rest with KMS  
- Decrypted just-in-time during task start  
- Passed to the container as environment variables or mount points  

**Your security depends entirely on:**

- IAM permissions to access the secret  
- KMS permissions to decrypt it  
- What your app does with it (if it logs it, it’s game over)  

**What to do:**

- Use CMKs per environment (e.g., `alias/ecs-prod-secrets`)  
- Rotate secrets regularly  
- Set IAM Conditions like `secretsmanager:SecretId`, `aws:username`, `aws:SourceVpc`  
- Audit secrets access via CloudTrail + GuardDuty  
- Prevent secrets from being injected into stdout  

### 5. CloudWatch Logs Encryption

Logs are often ignored, but they can contain:

- Stack traces  
- PII  
- JWTs  
- Full API requests  
- Secrets (accidentally logged)

CloudWatch Logs are:

- Encrypted at rest by default with `aws/logs`  
- You can configure custom CMKs  
- Logs are accessible by any principal with `logs:GetLogEvents`  

**What to do:**

- Use dedicated CMKs for sensitive log groups  
- Scope log access via IAM  
- Use resource policies to restrict log ingestion or access  
- Set retention policies to auto-delete logs after 30–90 days  
- Enable CloudTrail + Config rules to audit log group encryption  

### 6. Task Network Traffic (In-Transit Encryption)

ECS does **not** encrypt network traffic between:

- Containers on the same host  
- Tasks in the same VPC  
- Services talking to each other over HTTP  

**You need to enforce it manually:**

- Use HTTPS everywhere  
- Use mutual TLS (mTLS) between services  
- Use Service Mesh (App Mesh) with TLS enabled  
- Use NLB or ALB with TLS listeners  

**What to do:**

- Enforce TLS with ACM certs  
- Add IAM Conditions like `aws:SecureTransport = true`  
- Monitor VPC Flow Logs for traffic over plain `TCP/80`  
- Use WAF to enforce HTTPS  

---

## IAM + KMS: The Actual Gatekeepers

Everything in ECS encryption depends on:

- **IAM**: who can pull images, decrypt secrets, write to logs  
- **KMS**: who can use the CMKs for encryption/decryption  

If you:

- Use the same CMK for all secrets, images, and logs  
- Grant `kms:Decrypt` to broad roles  
- Don’t audit `kms:CreateGrant` or `kms:ReEncrypt`  

Then encryption becomes **theater** — not protection.

---

## Pricing Model (Security-Relevant)

| **Feature**             | **Notes**                                             |
|-------------------------|-------------------------------------------------------|
| EBS / EFS Encryption    | Free to encrypt, storage billed separately            |
| Secrets Manager         | $0.40/secret/month + $0.05 per 10K API calls          |
| KMS CMKs                | $1/month per key + $0.03 per 10K usage                |
| CloudWatch Logs         | Ingestion + storage billing                           |
| Inspector (ECR scanning)| Charged per image scanned                             |

> **Encryption is cheap compared to breach recovery — always enable it.**

---

## Snowy Real-Life Example

**BlizzardCloud** runs ECS on EC2 with EFS mounted for file processing.  
Logs are shipped to CloudWatch.  
Secrets come from SSM.  
Everything looks good... until a red teamer drops this:

- They compromise a task with outdated `flask==1.0.2`  
- Use SSRF to hit the metadata endpoint, grab IAM creds  
- Use the task role to pull secrets from SSM  
- Secret is decrypted using the CMK that also decrypts **all** other prod secrets  
- CloudWatch logs the entire POST request body, which includes a plaintext OAuth token  

**No GuardDuty finding.**  
**No logging of the internal data breach.**

Encryption was enabled — but the **IAM and KMS scoping was wide open**.

---

## Final Thoughts

**Encryption in ECS isn’t a checkbox.**  
It’s a stack of layers:

- Volumes  
- Secrets  
- Images  
- Logs  
- Network  
- IAM  
- KMS  

If any layer leaks — the whole thing leaks.

So:

- Encrypt everything  
- Scope every CMK  
- Tag every task  
- Log every decryption  
- Trust nothing that isn’t auditable
