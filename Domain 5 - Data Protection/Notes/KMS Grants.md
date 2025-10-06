# AWS KMS Grants  

## What Is a KMS Grant

A **KMS Grant** is a mechanism for temporarily delegating access to a KMS key, **without having to edit the key policy** or give someone long-term access through IAM.

It allows a principal (like a role, Lambda function, or AWS service) to perform a limited set of actions — such as:

- `Encrypt`
- `Decrypt`
- `GenerateDataKey`
- …and more

Grants:

- Live **outside** the key policy  
- Can be **time-limited** (until revoked)  
- Can include **constraints** (e.g., only usable by a specific encryption context)  
- Can be **revoked at any time**  
- Are automatically **auditable via CloudTrail**

> This gives you **surgical, ephemeral permissions** to use a CMK — which is crucial for least privilege, scoped delegation, and dynamic services like **S3, EBS, RDS, and Lambda**.

---

## Cybersecurity Analogy

Imagine your encryption key is a **vault**.  
The key policy defines who has the **master keys** to open it permanently.

A **KMS Grant** is like giving someone a **temporary access badge**:

- Valid for only **one locker**
- Can be **revoked** at any time
- Works only under **specific conditions**
- Doesn’t change the **master key list**

It’s perfect for **contractors, time-bound access**, or **short-lived processes** that need to use, but not own, the key.

## Real-World Analogy

Let’s say **Winterday** is managing a fleet of **Lambda functions** that encrypt logs before storing them in S3.

Instead of:

- Giving each Lambda long-term `kms:Encrypt` permissions in the key policy  
- Editing the IAM role every time  

**Snowy creates a KMS grant** that says:

> “This Lambda execution role can call `Encrypt` using this CMK — only for requests tagged with context `LambdaEncrypt: true` — and nothing else.”

- No need to change the key policy  
- No persistent permission  
- Fully revocable  

---

## How It Works

### Grant Participants

| Component           | Description                                                                 |
|---------------------|-----------------------------------------------------------------------------|
| **Key Policy**       | Must allow the grant creator to create the grant                           |
| **Grantee Principal**| The identity (IAM role, user, or service) that uses the grant               |
| **Operations**       | Allowed actions (`Encrypt`, `Decrypt`, `GenerateDataKey`, etc.)             |
| **Constraints**      | Optional: encryption context, source account, etc.                          |
| **Retiring Principal**| Who can retire (delete) the grant besides the creator                     |
---

## Lifecycle of a Grant

1. **Grant is created**  
   → via `CreateGrant` API or implicitly by services like **S3**, **EBS**, or **Lambda**


2. **Grantee gets grant token**  
   → used by services (like **DynamoDB**, **Lambda**) to perform actions immediately

3. **Grantee performs allowed operations**  
   → only those defined in the grant under allowed conditions

4. **Grant is revoked or retired**  
   → at any time via `RevokeGrant` or `RetireGrant`

---

## Grant Permissions Are Independent from IAM

Even if your IAM principal has **no** `kms:Encrypt` permission, it **can still perform encryption** if a valid **grant** exists.

KMS checks permissions in this order:

1. Valid **Grants**
2. **Key Policy**
3. **IAM Policy**

> This makes grants **stealthy but powerful** — perfect for automation, dangerous if misused.

---

## Common Operations Allowed via Grants

| **Operation**                    | **Meaning**                                 |
|----------------------------------|----------------------------------------------|
| `Encrypt`                        | Encrypt plaintext with the CMK               |
| `Decrypt`                        | Decrypt ciphertext using the CMK             |
| `ReEncryptFrom` / `ReEncryptTo` | Re-encrypt data to/from another CMK          |
| `GenerateDataKey`               | Generate a DEK wrapped by the CMK            |
| `GenerateDataKeyWithoutPlaintext` | Return encrypted DEK only                   |
| `DescribeKey`                   | View key metadata (but not use it)           |

---

## Detection and Forensics Implications

Grants can be:

- Created by **users, roles, or services**
- **Invisible** unless queried via `ListGrants`
- **Revoked silently**
- **Misused** if grant constraints are too loose

Key events to monitor in **CloudTrail**:

- `CreateGrant`
- `RetireGrant`
- `RevokeGrant`
- Any `Decrypt`, `Encrypt`, etc. call **without matching IAM permissions** (i.e., **via grant**)

---

## Grant Constraints (Security Controls)

You can scope a grant to:

- **Encryption Context** (key-value pairs required on request)
- **Source Account** (limit to a specific AWS account)
- **Grant Token** (bind to STS session or transaction)

**Example constraint block**:

```json
{
  "EncryptionContextEquals": {
    "LambdaLogEncrypt": "true"
  }
}
```

> Only requests with that exact context can use the grant.

---

## Grant Types

| **Type**           | **Who Can Use It**        | **When Used**                               |
|--------------------|----------------------------|----------------------------------------------|
| **User-Created**    | IAM principals              | When calling `CreateGrant` manually          |
| **Service-Created** | AWS services (e.g., S3)     | Automatically managed behind the scenes      |
| **Grant Token-Based** | Temporary tokens         | STS integration, transient access            |

---

## Revoking and Retiring Grants

| **Action**       | **Who Does It**                 | **Effect**                                     |
|------------------|----------------------------------|------------------------------------------------|
| `RevokeGrant`    | Admin or grant creator           | Forcefully removes the grant immediately       |
| `RetireGrant`    | Grantee                          | Voluntarily ends their own grant               |

> If a grant is revoked, the grantee **immediately** loses access — even **mid-session**.

---

## Real-Life Snowy Scenario

You’re building a **forensic pipeline**:

- Logs encrypted by Lambda  
- Stored in S3  
- Decrypted by a Redshift **copy job**

You don’t want to:

- Grant the Redshift cluster `kms:Decrypt` full-time  
- Modify the key policy for every pipeline stage  

Instead:

- Create a **grant scoped to Redshift’s role**
- Allow **`Decrypt` only** when `encryptionContext = LogStage:FinalLoad`
- Monitor `CreateGrant` and `Decrypt` calls via **CloudTrail**

> Every stage gets **just enough access**, and revoking the grant **kills access instantly** — with no policy edits or credential cleanup.

---

## Key Difference: Key Policies vs Grants

| **Feature**                | **Key Policy**              | **KMS Grant**                                 |
|----------------------------|-----------------------------|-----------------------------------------------|
| **Scope**                  | Long-term, foundational     | Temporary, scoped                             |
| **Lives In**               | Key metadata                | Separate grant object                         |
| **Requires IAM Changes?**  | ✔️ Yes                      | ✖️ No                                          |
| **Can Be Revoked Instantly?** | ✖️ No (policy edit required) | ✔️ Yes                                      |
| **Visible in Console?**    | ✖️ Not always clearly        | ✖️ Only via `ListGrants` or CloudTrail         |
| **Best For**               | Admin/root access           | Scoped delegation (services, sessions)         |

