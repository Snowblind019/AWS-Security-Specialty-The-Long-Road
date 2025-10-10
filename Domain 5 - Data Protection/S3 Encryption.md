# Amazon S3 Encryption

## What Is the Service

Amazon S3 (Simple Storage Service) is AWS’s massively scalable object storage platform — where terabytes of logs, backups, application data, analytics exports, and static websites often live.

S3 encryption protects **data at rest** by ensuring that the objects stored in your buckets are encrypted — either by AWS, by you, or by your applications. The goal is to ensure that even if someone gains unauthorized access to an object, they can't actually read it without also having access to the encryption key.

**Why this matters:**

S3 buckets are one of the most common breach points in AWS — whether due to public exposure, misconfigured policies, or compromised credentials. Encryption ensures that stolen data is useless, acting as a critical safeguard in the event of human error, insider threats, or policy missteps.

Many compliance standards (PCI-DSS, HIPAA, ISO 27001) require encryption at rest — and with S3 being the heart of most AWS workloads, this is one of the first places to get it right.

---

## Cybersecurity Analogy

Imagine your S3 bucket is a massive **library of file cabinets**.

- Without encryption, anyone who breaks in can just open the drawers and read what’s inside.
- With encryption, each drawer is locked with a unique key, and even if a thief gets inside the library, they walk away with a thousand locked boxes they can’t open.
- And if **you control the keys**, you control who can ever open a single drawer — even if they already accessed the building.

## Real-World Analogy

Think of S3 encryption like **password-protecting every file you store on your computer** — except instead of doing it manually, AWS does it for you, automatically, every time you upload a file.

- You can use your own password (CMK)
- Or let AWS manage the password for you

Either way, if someone copies your file to a USB stick and runs off, it’s useless without the decryption key.

---

## What It Secures / Controls / Intercepts

| Protected                                | Not Protected                                                 |
|------------------------------------------|----------------------------------------------------------------|
| Object data in S3                        | Bucket names, object key names (paths)                        |
| Backups and archives (Glacier, Deep Archive) | Metadata (unless client-side encrypted)                      |
| S3 replication destinations              | Logging or access records (separate from object data)         |
| Lifecycle transitions to lower-cost tiers|                                                                |
| Object versions                          |                                                                |
| **Data at rest only**                    | **Encryption in transit = TLS/HTTPS**                         |

---

## How It Works

There are four primary encryption options in S3:

### 1. SSE-S3 (Server-Side Encryption with Amazon S3-managed keys)
- AWS handles all keys.
- You upload an object, AWS encrypts it using AES-256, stores it, and decrypts it when you download.
- **Simple, free, compliant.**

### 2. SSE-KMS (Server-Side Encryption with AWS KMS-managed CMKs)
- AWS encrypts each object with a unique data key.
- That key is encrypted with your CMK in KMS.
- Supports:
  - Audit logs (CloudTrail)
  - Granular IAM policies
  - Grants, automatic key rotation
- **Best for fine-grained control and visibility.**

### 3. SSE-C (Server-Side Encryption with customer-provided keys)
- You provide a key during upload/download.
- AWS uses it to encrypt/decrypt but never stores it.
- Dangerous — if you lose the key, **AWS can’t help you**.
- Not logged in CloudTrail.
- **Rarely recommended.**

### 4. CSE (Client-Side Encryption)
- You encrypt the object before uploading to S3.
- You manage decryption client-side.
- Maximum control, but high operational burden.

> You can enforce **default encryption** at the bucket level to ensure all uploads are encrypted — even if the client forgets to request encryption.

---

## Pricing Models

| Option      | Encryption Cost                                                  |
|-------------|------------------------------------------------------------------|
| SSE-S3      | Free                                                             |
| SSE-KMS     | Free when using default AWS-managed CMKs                         |
| Custom CMKs | $1/month per CMK + $0.03 per 10,000 Encrypt/Decrypt API calls    |
| SSE-C / CSE | No AWS charges, but riskier and harder to manage                 |

> If you're encrypting **millions of objects per day** with SSE-KMS + CMK, expect KMS API call costs to spike, especially with frequent PUT/GET operations.

---

## Other Explanations

- You can **enforce encryption** via the S3 console or `PutBucketEncryption` API.
- IAM & bucket policies can **deny uploads** unless encryption is used:
  - Example: `s3:x-amz-server-side-encryption` condition
- **CloudTrail logs** all KMS key usage (Encrypt, Decrypt, GenerateDataKey, etc.)
- **Multi-Region Keys (MRKs)** now allow DR-friendly encryption across regions
- **Versioning**: Each version of an object is encrypted independently
- **Lifecycle rules and replication** maintain encryption unless overridden

---

## Real-Life Example

**Snowy** stores massive amounts of log data in Amazon S3:

- GuardDuty findings, CloudTrail logs, VPC Flow Logs, and user-uploaded data
- Default encryption is enabled at the bucket level using **SSE-KMS**
  - One CMK for security logs
  - One CMK for customer uploads
- **Bucket policy** blocks any upload that doesn’t use `SSE-KMS`
- **CloudTrail** monitors all encryption usage and decryption attempts
- **Amazon Macie** periodically scans the buckets to ensure no unencrypted or sensitive data exposure
- When an EC2 app accidentally uploaded unencrypted logs, the **default encryption policy still applied SSE-KMS** — saving the day

---

## Final Thoughts

> AWS makes encryption easy — but only **if you configure it**.
> **Encrypt by default. Monitor always. Assume nothing.**
