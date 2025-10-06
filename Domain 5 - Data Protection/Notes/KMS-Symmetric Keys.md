# AWS KMS: Symmetric Keys  

## What Are Symmetric Keys in KMS

A **symmetric key** in AWS KMS is a single cryptographic key used for both:

- **Encrypting** data  
- **Decrypting** that same data  

You create it once, store it in **KMS (never exported)**, and use AWS services or your own apps to request KMS to perform cryptographic operations using that key.

It's the **default and most common type** of KMS key used in AWS.

You can:

- Use it with `Encrypt` / `Decrypt`
- Generate data keys (`GenerateDataKey`)
- Use it with **built-in services** like S3, EBS, RDS, Lambda, Redshift, etc.
- **Audit** its use with CloudTrail
- Apply **fine-grained permissions** with IAM or grants
- Set **rotation policies** and enforce **encryption context** conditions

> Symmetric KMS keys are **never visible or exportable** — only used by reference.

---

## Cybersecurity Analogy

Think of a symmetric KMS key like a **secured vault inside a facility**, where you:

- Drop data in → it gets encrypted and stored  
- Ask the vault to hand it back → it decrypts and returns it  

You **never see** the vault’s internal mechanics.  
You just ask:

- “Can you encrypt this?”  
- “Can you decrypt this blob you encrypted earlier?”  

If:

- The **key policy** says yes  
- The **encryption context** matches  
- The **IAM role** allows it  

The operation **succeeds**.  
Otherwise? You get **denied**.

## Real-World Analogy

Imagine **Snowy** runs a **file processing service**:

- Raw files land in **S3**
- A **Lambda** function transforms them
- Processed files get **re-encrypted and stored**

Everything is encrypted at rest using a single **symmetric CMK**:

```
arn:aws:kms:us-west-2:123456:key/snowy-default
```

None of the developers ever see the raw key.

They just use the **KMS API**, securely and with IAM separation:

- S3 has `kms:Encrypt`  
- Lambda has `kms:Decrypt`  
- Billing has **read-only CloudTrail** logs showing **usage, not content**

---

## KMS Symmetric Key Operations

| **API**                          | **Description**                                      |
|----------------------------------|------------------------------------------------------|
| `Encrypt`                        | Encrypt plaintext using the CMK                      |
| `Decrypt`                        | Decrypt ciphertext encrypted with the CMK            |
| `GenerateDataKey`               | Get a DEK (plaintext + encrypted form)               |
| `GenerateDataKeyWithoutPlaintext` | Get only the encrypted DEK                          |
| `ReEncrypt`                      | Re-encrypt ciphertext under a new CMK                |
| `DescribeKey`                    | View metadata like state, policy, rotation           |

---

## How the Flow Works

Typical **envelope encryption** pattern:

1. App or AWS service calls `GenerateDataKey`
2. KMS returns:
   - A **plaintext Data Encryption Key (DEK)**
   - That same **DEK encrypted under the CMK**
3. App uses **plaintext DEK** to encrypt the actual data
4. App stores:

Later:

- Another app calls `Decrypt` on the encrypted DEK
- Gets back the plaintext DEK
- Uses that to decrypt the data

> The CMK **never touches your data directly** — it only protects the keys that protect your data.

---

## Key Properties


| **Feature**         | **Value**                                                        |
|----------------------|------------------------------------------------------------------|
| **Key Type**         | Symmetric AES-256 (AES-GCM under the hood)                      |

| **Exportable?**      | ✖️ No (except with External Key Store – XKS)                     |
| **Usage**            | Encrypt, Decrypt, ReEncrypt, GenerateDataKey                    |
| **Default for services?** | ✔️ Yes (S3, RDS, EBS, Lambda, CloudTrail, etc.)             |
| **Rotation supported?** | ✔️ Yes (annual automatic or manual rotation)                 |
| **Multiregion support?** | ✔️ Yes (if created as a multi-region key)                   |
| **Performance**      | Scales well, but latency-sensitive apps should use local DEKs   |

---

## Security Implications

- Apply **least privilege** — never use `kms:*` on `*`
- Encrypt with **EncryptionContext** to prevent misuse or replay attacks
- Detect overuse with **CloudTrail + KMS usage metrics**
- Use **grants** for short-lived delegation (instead of bloated key policies)
- Tie usage to **CloudWatch Alarms** for spikes in `Decrypt`

---

## Example IAM Policy for CMK Usage

```json
{
  "Effect": "Allow",
  "Action": [
    "kms:GenerateDataKey",
    "kms:Decrypt"
  ],
  "Resource": "arn:aws:kms:us-west-2:123456789012:key/snowy-data-key",
  "Condition": {
    "StringEquals": {
      "kms:EncryptionContext:Project": "SnowyPII"
    }
  }
}
```

---

## Monitoring and Detection

### Key CloudTrail Events:

- `Encrypt`, `Decrypt`
- `GenerateDataKey`
- `CreateGrant`, `RevokeGrant`
- `ScheduleKeyDeletion`
- `PutKeyPolicy`, `UpdateAlias`

### Watch for:

- Spikes in `Decrypt` usage from **new roles**
- Usage from **unexpected AWS regions**
- High rate of `GenerateDataKeyWithoutPlaintext` (can indicate **shadow data export**)
- **Grant creation** without matching IAM approval flow

---

## Real-Life Snowy Scenario

Snowy’s team stores **customer invoices** encrypted using KMS.

Everything works — until **GuardDuty fires** on a new Lambda that made **700 `Decrypt` calls in one hour**.

Snowy:

1. Pulls **CloudTrail logs**:
   - `eventSource = kms.amazonaws.com`
   - `eventName = Decrypt`
2. Identifies the **IAM role** used by Lambda
3. Realizes: an **unscoped `kms:Decrypt` permission** was included in a **reused role**

Immediate Fix:

- Apply **EncryptionContext conditions**
- **Rotate the CMK**
- Restrict **role assumption** to trusted services

- Alert on **cross-service or abnormal usage**

---

## When to Use Symmetric Keys vs Asymmetric

| **Requirement**                  | **Use Symmetric?** | **Use Asymmetric?** |
|----------------------------------|---------------------|----------------------|
| General data encryption          | ✔️ Yes              | ✖️ No               |
| Digital signatures / verification| ✖️ No               | ✔️ Yes              |
| Public key exchange with clients | ✖️ No               | ✔️ Yes              |
| Performance-sensitive bulk ops   | ✔️ Yes              | ✖️ No               |
| Encrypting AWS service data      | ✔️ Yes              | ✖️ No               |

---

## Final Thoughts

**Symmetric KMS keys** are the **invisible backbone of encryption at scale** in AWS.

They’re used by:

- Nearly every **managed AWS service**
- All **envelope encryption** flows
- **Thousands of workloads per second** in enterprise environments

But they’re often **mismanaged**:

- Too many principals have access
- Policies lack **EncryptionContext** scoping
- Rotation is forgotten
- Grant usage is invisible to governance

> If you're securing data at rest in AWS, you're using **symmetric keys** — whether you realize it or not.

