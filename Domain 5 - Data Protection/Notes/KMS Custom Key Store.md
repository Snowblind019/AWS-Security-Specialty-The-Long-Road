# AWS KMS Custom Key Store (CKS)

## What Is the Service

A KMS Custom Key Store lets you use your own AWS CloudHSM cluster as the backend for AWS KMS.

This means:

- You still interact with KMS’s control plane (APIs, IAM policies, key policies, audit trails, etc.)
- But instead of storing keys in AWS-managed HSMs, they are stored in CloudHSMs that you control

**Why this matters:**

- Compliance-driven encryption often requires strict key material custody  
- You want AWS-native encryption workflows, but you can’t let AWS “own” the actual key material  
- You don’t want to fully manage encryption workflows (like you’d have to with raw CloudHSM)  
- You need FIPS 140-2 Level 3 hardware boundary, but still want to use things like SSE-KMS, Envelope Encryption, IAM grants, and audit logs

It’s a middle ground: you control the key material, but AWS handles the encryption logic.

---

## Cybersecurity Analogy

Think of AWS KMS like a lockbox service run by AWS — it manages the key lifecycle, auditing, and usage rules. You just tell it when to encrypt or decrypt.  
With a Custom Key Store, it’s as if you say:  
**“You can use the lockbox... but I want to install my own padlock. You can still manage when it opens and who has access — but I keep the key to that padlock in my own safe.”**  
KMS operates the box. But the physical key to that box lives in your HSM — not theirs.

---

## Real-World Analogy

Imagine you run a bank that uses a secure digital vault system (KMS) for customer documents. Normally, AWS controls the actual locks inside.  
But regulators say: “No, the keys must reside on your premises.”  
So you rent secure cages (CloudHSM) in a data center you control. AWS still manages the vault — when to open, who can access — but the vault checks with your cage every time it needs a key.  
AWS operates the vault with your keys inside it.

---

## How It Works

Let’s break it down into core components:

### 1. CloudHSM Cluster

- You deploy your own AWS CloudHSM cluster in your VPC.
- You own and manage it: scaling, backups, availability, credentials, etc.
- Keys stored here are never visible to AWS personnel or services — only KMS has runtime access.

### 2. Custom Key Store Configuration

- You configure a Custom Key Store (CKS) in AWS KMS and link it to your CloudHSM cluster.
- You still use the standard KMS APIs (CreateKey, Encrypt, Decrypt), but behind the scenes:
  - KMS forwards crypto operations to your CloudHSM
  - Your HSM performs the encryption, decryption, or signing
  - The result is returned to the calling service (e.g., S3, Lambda, EC2)

### 3. KMS Manages, HSM Performs

- KMS handles policies, IAM permissions, grants, CloudTrail logging, etc.
- But your CloudHSM cluster performs the actual cryptographic operation with your key material

### 4. You Control Key Lifecycle

- You create, delete, and back up keys using CloudHSM tools  
- KMS can use keys, but can’t export or rotate them unless you do it

### 5. Use With SSE-KMS, Envelope Encryption, etc.

- You can still use standard KMS-integrated features (S3 encryption, EBS, RDS, etc.)  
- But encryption is routed through your HSMs

---

## Pricing Model

You pay for:

- CloudHSM costs — per HSM instance  
- KMS request fees — same per-request charges as with standard KMS  
- Additional infrastructure costs — VPC traffic, HA clusters, backups

| Resource             | Pricing                             |
|----------------------|--------------------------------------|
| CloudHSM instance    | ~$1.45/hour (~$1,000/month)         |
| KMS usage fees       | Same as regular KMS                 |
| Key creation/backup  | Managed via CloudHSM tools          |

This is not a budget-friendly model — it’s purpose-built for high-compliance workloads.

---

## Use Cases

CKS is primarily used when you want:

- Regulatory compliance requiring full HSM-level custody  
- FIPS 140-2 Level 3 enforcement  
- KMS features like:  
- IAM integration  
- Logging  
- Grants  
- Service integration (S3, Lambda, EBS, etc.)  

…but with complete control over key storage.

**Common customers:**

- Financial services  
- Government workloads  
- Healthcare & pharmaceutical orgs  
- Global banks or payment processors needing deterministic custody

---

## Comparison Table

| Feature                    | AWS KMS (default) | Custom Key Store (CKS) | CloudHSM-only        | External Key Store (XKS)           |
|----------------------------|-------------------|-------------------------|-----------------------|-------------------------------------|
| **Key custody**            | AWS-owned HSMs    | Customer CloudHSM       | Customer CloudHSM     | External on-prem HSM/KMS            |
| **KMS APIs available**     | ✔️ Full           | ✔️ Full                 | ✖️ None (raw PKCS#11) | ✔️ Subset (XKS API)                 |
| **AWS-managed rotation**   | ✔️ Yes            | ✖️ No (you manage)      | ✖️ No                 | ✖️ No                               |
| **Integrated with S3/etc.**| ✔️ Yes            | ✔️ Yes                 | ✖️ No                 | ✔️ Limited (via XKS)                |
| **CloudTrail support**     | ✔️ Yes            | ✔️ Yes                 | ✖️ No                 | ✔️ Yes                              |
| **Use case**               | General purpose   | Compliance + AWS integration | Full HSM control | Hybrid on-prem + AWS KMS UX        |
| **Cost**                   | 💲                | 💲💲💲                  | 💲💲💲                | 💲💲💲 (requires external infra)     |

---

## Real-Life Example: SnowyBank Ltd.

SnowyBank handles sensitive customer loan documents in encrypted form.  
Regulators say the keys must be stored in a customer-controlled HSM — but Snowy also wants to use AWS-native services like:

- S3 with SSE-KMS  
- Lambda automation  
- CloudTrail logging of encryption usage

**The solution?**

- Deploy a CloudHSM cluster in their VPC  
- Configure it as a Custom Key Store  
- Use KMS’s APIs, IAM, and logging — but keep keys in their HSM  

**Result:**  
Regulatory compliance, HSM boundary enforced, full auditability, and zero plaintext key exposure to AWS

---

## Final Thoughts

AWS KMS Custom Key Store is a power tool — best suited for organizations with strong security operations maturity.  
It’s not about convenience — it’s about control.

- If you need to meet FIPS 140-2 Level 3 or custody compliance  
- If you want to delegate cryptography but not key ownership  
- If you want KMS UX with HSM boundaries  
**Then this is the best of both worlds.**

But if you just want full HSM control and don’t need KMS integration — go with CloudHSM.  
If your key must never enter AWS infrastructure at all — even via CloudHSM — then XKS (External Key Store) is your route.
