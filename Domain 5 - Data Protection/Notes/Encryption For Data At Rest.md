# Encryption for Data at Rest

## What Is It 

Data at rest refers to any data stored on persistent media — whether on an EBS volume, in an S3 bucket, in RDS databases, DynamoDB tables, or SSM parameters.  
When data is not moving across the network, it’s at rest. And it must be protected.

Encryption at rest protects this data from:

- Physical theft (e.g., someone steals a hard drive from a data center)  
- Insider access (e.g., a rogue admin browsing stored files)  
- Compromise of backups, snapshots, or database exports  
- Lateral movement after initial intrusion  
- Accidental exposure (e.g., public S3 buckets with sensitive files)

AWS makes this easy, but understanding how it works and where it applies is essential for building secure architectures.

---

## Cybersecurity Analogy

Imagine your company’s documents are stored in a warehouse.  
Even if someone breaks in, every single box is locked with its own key. And those keys are in a secure vault.

Even if a thief walks off with a few boxes, unless they also stole the vault and knew how to open it — the documents are worthless.

That’s data at rest encryption.

## Real-World Analogy

Think of a lost USB stick. If it’s encrypted:

- You lose the device, but not the data  
- No one can open it without the password/key  
- Even if they clone the storage, it’s gibberish

In the cloud, we don’t worry about misplaced USBs — but we do worry about snapshots, logs, EBS volumes, and exports being accessed improperly.  
**Encryption neutralizes that risk.**

---

## How It Works in AWS

All AWS storage services offer encryption-at-rest using **AES-256 encryption**.  
Most use the **AWS Key Management Service (KMS)** for key creation, rotation, and access control.

AWS gives you three key management options:

| Key Type                      | Who Manages It         | Use Case                                      |
|------------------------------|------------------------|-----------------------------------------------|
| SSE-S3 / AWS-Managed         | AWS fully manages keys | Easy default encryption with minimal config   |
| SSE-KMS / Customer Managed   | You manage in KMS      | Fine-grained control, auditing, grants        |

| SSE-C (Customer-provided)    | You bring raw key      | Least used — high-risk, niche use cases       |

When enabled, encryption happens automatically *before* write, and decryption occurs on *read* — transparently to your application.  

No need to modify your code, unless you want to specify CMKs explicitly.

---

## Encryption at Rest by Service

| Service        | Encryption Support                        | KMS Integration |
|----------------|--------------------------------------------|------------------|
| S3             | SSE-S3, SSE-KMS, SSE-C                    | Yes              |
| EBS            | Yes (default on or opt-in)                | Yes              |
| RDS            | Yes (at cluster creation only)            | Yes              |
| DynamoDB       | Always encrypted at rest (SSE enabled)    | Yes              |
| SQS            | Optional SSE for message bodies           | Yes              |
| S3 Glacier     | Always encrypted                          | Yes              |
| EFS            | Supports encryption at rest + in transit  | Yes              |
| Lambda Env Vars| Optional encryption                       | Yes              |
| SSM Parameters | SecureString types use KMS                | Yes              |

---

## SnowySec Encryption Flow Example

**Snowy’s application stores user uploads in S3, logs in CloudWatch, and backups in RDS snapshots.**

To enforce airtight encryption-at-rest posture:

- Enable S3 bucket default encryption using CMK: `snowy-prod-data-key`
- Apply bucket policy that denies `PutObject` unless `x-amz-server-side-encryption` is set
- Use EBS volume encryption by default on all AMIs with the same CMK
- Encrypt RDS instances at creation and tag snapshots with `Confidential=true`
- Configure CloudWatch Logs with KMS key for log group encryption
- Rotate all KMS CMKs every 12 months automatically
- Monitor key usage via CloudTrail + CloudWatch Alarms
- Set up grants so only specific IAM roles (not users) can use encryption keys
- Audit access with KMS key usage logs + query with Athena

**Result:**  
Even if a compromised Lambda accesses a snapshot or S3 object, it won’t have key permissions — and the data stays safe.

---

## Security Use Cases

| Threat                                 | Encryption Mitigation                                        |
|----------------------------------------|--------------------------------------------------------------|
| Stolen snapshot from RDS/S3/EBS        | Encrypted object is unreadable without key access           |
| Insider with EC2 access mounts EBS     | IAM policy blocks decryption without correct key grants     |
| Exfiltration of data via Lambda        | CMK access policy limits use to specific services/roles     |
| Backup files publicly exposed          | Data is encrypted; attacker cannot read the files           |
| Compromised CloudTrail logs            | Encrypted logs unreadable without key access                |

---

## Security Best Practices

- Use customer-managed KMS keys for sensitive data (logs, backups, app storage)  
- Rotate CMKs regularly (AWS auto-rotation or manually)  
- Use resource-based policies + grants to tightly control access  
- Enable encryption by default in service settings (EBS, S3, etc.)  
- Audit key usage in CloudTrail — look for anomalous decryption attempts  
- Tag sensitive keys for easy inventory and cost tracking  
- Don’t share CMKs across unrelated workloads — enforce separation of duties  

---

## Integration with Other Services

| Service        | Why It Matters for Encryption                          |
|----------------|---------------------------------------------------------|
| KMS            | Key creation, rotation, policy, usage logs             |
| CloudTrail     | Logs every encryption/decryption attempt for auditing  |
| Config         | Can track whether encryption is enabled per resource   |
| Security Hub   | Flags misconfigured encryption settings                |
| S3 Policies    | Can enforce mandatory encryption headers               |
| IAM            | Controls which roles can access/decrypt keys           |
| CloudWatch     | Alarm on abnormal KMS activity or access patterns      |

---

## Pricing Overview

| Item                        | Pricing                                      |
|-----------------------------|----------------------------------------------|
| KMS API calls (Encrypt/Decrypt) | ~$0.03 per 10,000 requests (as of 2025)     |
| KMS CMK storage                 | ~$1.00/month per key                        |
| S3 default encryption          | Free (SSE-S3), KMS usage applies if SSE-KMS |
| EBS, RDS, DynamoDB encryption  | No extra charge (unless KMS usage is high)  |

---

## Final Thoughts

Encryption at rest is invisible when done right — but *indispensable* when something goes wrong.

If an attacker dumps your database, grabs your logs, or copies your backups…  
**The encryption key is the lock they’ll never have.**

SnowySec doesn’t just store data — it safeguards it.

From the logs in S3, to the secrets in SSM, to the audit trails in CloudTrail —  
Every byte is wrapped in AES-256 and protected with policies that say:

> “Unless you are who you say you are… this data is just noise.”

**Data at rest encryption is the seatbelt of cloud security.**  
- It’s not exciting.  
- It’s not flashy.  
- But one day, it will save you.

