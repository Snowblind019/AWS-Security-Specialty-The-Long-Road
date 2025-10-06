# SSE-S3

## What Is SSE-S3

SSE-S3 stands for **Server-Side Encryption with Amazon S3-Managed Keys**.
It’s the simplest encryption method offered by AWS S3, and it’s designed for customers who want data encryption at rest without needing to think about key creation, management, access controls, or logging.

When SSE-S3 is enabled:

- AWS automatically encrypts your S3 objects using **AES-256**
- AWS manages all key rotation, durability, and protection
- Keys are not exposed to you in any form
- You don’t use **KMS**, **IAM** policies, grants, or **CMK** conditions
- You can’t audit key usage via **CloudTrail**

**The result:**
Your objects are encrypted at rest, but the **control, visibility, and accountability stay with AWS.**

---

## Cybersecurity Analogy

Imagine Snowy’s team stores logs in a locked filing cabinet, and AWS is the janitor.

With SSE-S3:

- You drop the file into the cabinet
- AWS locks it for you using its own master key
- You have no idea which key was used, when it rotated, or how the lock works
- But you’re told: “It’s safe, don’t worry.”

That’s SSE-S3.
You get encryption at rest.
You get compliance checkmarks.
But you don’t own the lock or see the key.

---

## Real-World Analogy

Think of SSE-S3 like storing luggage at the airport:

- **TSA** puts it in their secure locker system
- They handle the keys
- You can request your bag later, and they retrieve it for you
- But you don’t know where it was stored or which key was used

Now compare that to using **KMS-managed encryption**, where you **define the lock**, monitor key usage, and even revoke access based on tags or IAM.

---

## How It Works Behind the Scenes

When you `PUT` an object into an SSE-S3–protected bucket:

1. AWS automatically encrypts the object with a **unique data key (DEK)**
2. That **DEK** is encrypted with an **S3-managed master key**, entirely managed by AWS
3. The encrypted object + encrypted **DEK** are stored in S3
4. When you `GET` the object, AWS decrypts it transparently

You don’t see any of this.
You just upload and download as usual.

---

## Enabling SSE-S3

You can enable it via:

- **Bucket default encryption** (applies to all new objects)
- **Per-object encryption** (in `PutObject` request headers)

**Example header:**

```http
x-amz-server-side-encryption: AES256
```

You can also enforce it via **bucket policy**:

```json
{
  "Effect": "Deny",
  "Principal": "*",
  "Action": "s3:PutObject",
  "Resource": "arn:aws:s3:::snowy-logs/*",
  "Condition": {
    "StringNotEquals": {
      "s3:x-amz-server-side-encryption": "AES256"
    }
  }
}
```

This forces clients to use SSE-S3 or else the write is denied.

---

## Key Traits of SSE-S3

| Feature                     | SSE-S3                     |
|-----------------------------|-----------------------------|
| Encryption Algorithm        | AES-256                     |
| Key Control                 | AWS only (S3-managed)       |
| KMS Integration             | ✖️ None                     |
| IAM/KMS Grants              | ✖️ Not applicable           |
| Auditability via CloudTrail | ✖️ None                     |
| Automatic Key Rotation      | ✔️ Managed by AWS silently |
| Cost                        | ✔️ Free (no KMS cost)       |
| Revocation/Granularity      | ✖️ Not supported            |

---

## When SSE-S3 Is Appropriate

**Best for:**

- Public, open data sets (no strict audit trail required)
- Internal logging buckets with minimal sensitivity
- Bulk ingestion workflows where simplicity matters more than fine-grained access control
- Organizations that need **encryption at rest for compliance** but don’t need key management control

**Not good for:**

- Data requiring encryption event logging
- Anything where you must prove who decrypted what
- Workloads where you want to enforce encryption context or tag-based key conditions
- Environments using SCPs or permission boundaries tied to CMKs

---

## Security Limitations

| Limitation                        | Why It Matters                                                                 |
|----------------------------------|---------------------------------------------------------------------------------|
| No CloudTrail logs for encrypt/decrypt events | You can’t see who accessed encrypted content or when                  |
| No IAM control over the key      | Everyone with S3 access can read/write as long as object permissions allow it  |
| No fine-grained key rotation control | You can’t manually rotate or retire keys                                |
| No KMS conditions (e.g., tag-based encryption) | You lose conditional enforcement based on environment or use case    |
| No grants or delegation          | Can't create scoped or temporary access to encryption                        |

In short:
You don’t get **cryptographic-level access control** — only object-level S3 permissions.

---

## Default Bucket Encryption Behavior

If you set SSE-S3 as **default encryption**, all future `PutObject` requests (without any SSE header) will be encrypted using AES256.

But:

- It won’t encrypt existing objects retroactively.
- It also won’t stop someone from specifying **no encryption** unless you add a **bucket policy condition**.

---

## Real-Life Snowy Scenario

Snowy’s team runs a public COVID-19 dataset.
It’s stored in S3, browsable by researchers, but compliance requires that all data be encrypted at rest.

- They enable SSE-S3 as default encryption on the bucket
- Add a policy denying non-AES256 uploads
- All data is automatically encrypted, no KMS charges
- No audit trail needed, since data is public anyway
- It’s simple, compliant, cheap, and good enough

But when they later store **internal security logs** in the same bucket, they realize:

- No one can prove who accessed the logs
- CloudTrail can’t show any decrypt events
- Red team exfiltrated logs by assuming a role with basic S3 permissions

**Moral of the story?**
SSE-S3 is a trade-off — security **without governance.**

---

## Final Thoughts

SSE-S3 is **encryption without ownership.**

It gets you:

- AES256 encryption at rest
- Compliance checkboxes
- Simplicity

But at the cost of:

- ❌ No visibility into key usage
- ❌ No revocation
- ❌ No control

**Use SSE-S3 when encryption is required, but key control isn’t.**
For everything else — especially sensitive logs, customer data, regulated workloads — use **SSE-KMS with customer-managed keys.**
