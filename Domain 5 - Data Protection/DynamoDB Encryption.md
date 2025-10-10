# Amazon DynamoDB Encryption

## What DynamoDB Encryption Covers

DynamoDB is fully managed and **encrypts all data at rest and in transit by default**, with tight **AWS KMS integration**. This means:

- Every item written to a table is **encrypted before storage**
- All **replicated copies, backups, and streams** are encrypted
- Data flowing across the network is protected with **TLS 1.2+**

Encryption is **transparent to developers and apps**, but **critical to security teams** because DynamoDB often stores:

- Authentication tokens  
- **PII** (user profiles, emails, billing data)  
- Session state  
- Multi-tenant or **SaaS** customer data  

In cloud-native architectures where **there’s no SSH access, no open ports, and no middleware**, encryption becomes one of your **strongest control planes** — and DynamoDB gives you control **at the key level**.

---

## Encryption at Rest in DynamoDB

When you create a DynamoDB table, **encryption at rest is enabled by default** using **AWS KMS** and **AES-256 GCM** encryption.

All of the following are encrypted:

- Table data  
- Local and global secondary indexes  
- DynamoDB Streams  
- On-demand backups  
- Exported data (e.g., to S3)  
- Global table replication traffic  

**Once encryption is enabled, you cannot turn it off** — this protects against accidental data exposure during config changes.

---

## KMS Key Options

When configuring encryption, you have **two choices**:

### 1. AWS-Owned Key (`aws/dynamodb`)

- Enabled by default  
- Managed fully by AWS  
- No visibility into key usage or rotation  
- No **IAM** policy customization  

Good for quick setups, **but not compliant** for regulated industries or zero-trust orgs.

### 2. Customer-Managed Key (CMK)

- You create and manage the key via **AWS KMS**
- Fully audit key usage via **CloudTrail**
- Can scope **IAM** permissions to specific roles, services, or source **VPCs**
- Can rotate the key (automatically or manually)

Required for:

- Exporting to encrypted S3 buckets with specific keys  
- Cross-account access  
- Many compliance frameworks  

Using **CMKs** ensures you own the **blast radius, key access logic, and cross-account visibility**.

---

## KMS Permissions and Access Control

When a DynamoDB table uses a **CMK**, the **KMS** key policy must allow:

- The **DynamoDB service** to use the key  
- The caller or service role to invoke `Encrypt`, `Decrypt`, `GenerateDataKey`, etc.  
- **Audit tools** (like **CloudTrail**) to log key usage  

**Best practices:**

- Use `aws:SourceVpce` or `aws:SourceArn` conditions to scope key usage  
- Avoid `Principal = *` in key policies  
- Rotate **CMKs** annually (or as required by compliance)

---

## How DynamoDB Uses KMS Under the Hood

When a write request comes in:

1. DynamoDB requests a **data encryption key (DEK)** from **KMS**  
2. **KMS** returns the encrypted **DEK** and a plaintext **DEK**  
3. DynamoDB uses the plaintext **DEK** to encrypt the data  
4. The encrypted **DEK** is stored alongside the data in the table’s storage layer  
5. DynamoDB discards the plaintext **DEK**  

On reads, DynamoDB:

- Retrieves the encrypted **DEK**  
- Asks **KMS** to decrypt it  
- Uses it to decrypt the table item  

All of this is invisible to the app, but **logged in CloudTrail** if using a **CMK**.

---

## Encryption in Transit

DynamoDB enforces **TLS 1.2+** for all communications:

- Between AWS **SDK/CLI** and the DynamoDB service  
- Between regions in **Global Tables**  
- Between **Streams** and **Lambda** consumers  

There is **no configuration toggle** — TLS is **always on and cannot be disabled**.

This protects you from:

- Packet sniffing  
- **MITM** attacks  
- Data exfiltration via unencrypted APIs  

Apps must use **SDKs** or clients that support HTTPS (which all modern ones do).

---

## Monitoring and Auditing Encryption

| Tool                  | What It Tracks                                                                 |
|-----------------------|---------------------------------------------------------------------------------|
| **CloudTrail**        | All **KMS** key usage (Encrypt, Decrypt, `GenerateDataKey`)                    |
| **AWS Config**        | Detects if a table is unencrypted (rare) or missing **CMK**                    |
| **Security Hub**      | Flags **misconfigured** key access, public snapshot exports, weak policies     |
| **CloudWatch Alarms** | Can alert on unusual **KMS** usage patterns                                     |
| **Access Analyzer**   | Detects overly permissive key policies                                          |

> **Export to S3** actions are also audited — and only work if both the **source table** and **destination S3 bucket** use compatible encryption.

---

## Exporting Encrypted DynamoDB Tables

When exporting DynamoDB data (e.g., to S3), you can:

- Use **KMS-encrypted destinations**  
- Ensure **S3 bucket policy** allows access from the export job  
- Restrict exports via `dynamodb:ExportTableToPointInTime` **IAM** permissions  
- Log the operation using **CloudTrail** + **S3** + **KMS** logs  

This is a common compliance workflow for:

- Legal holds  
- Data portability  
- Offline analytics  

> **Misconfiguring** these exports is a common security mistake — especially if S3 buckets are not encrypted or publicly accessible.

---

## Cross-Region and Global Table Considerations

- DynamoDB encrypts **replication traffic** in Global Tables using **TLS** and **KMS**  
- Replicated data **remains encrypted at rest** using the source Region’s key  
- Each Region involved in replication must have:
  - Access to the source Region’s key (or an equivalent **CMK**)  
  - **KMS** policies allowing DynamoDB service in that Region to use the key  

If keys aren’t set up properly, Global Table replication will **silently fail or throttle**.

> **Best practice:** Use **multi-Region KMS keys** or replicate **CMKs manually**.

---

## Snowy’s Example: Encrypted Session Table

Snowy designs a DynamoDB-backed session table with the following goals:

- Encrypt all session data  
- Prevent any exposure during export  
- Require audit logs for all decryption activity  
- Block access outside **Snowy’s VPC**

**Implementation:**

- Table created with **CMK**: `alias/snowy-dynamodb-sessions`  
- **IAM** roles scoped to allow `dynamodb:*` only if `aws:SourceVpce` matches known **VPC** endpoint  
- **CMK** allows only:
  - `dynamodb.amazonaws.com` service  
  - Specific Lambda role  
- **TTL** enabled to auto-expire data  
- **CloudTrail** logs all **KMS** events  
- **Config** rules alert if another table is launched without encryption  

**Result:** A **compliant, encrypted, tightly-audited serverless session layer** — zero servers, zero risk of plaintext, and fully scoped key usage.

---

## When to Use CMK Encryption in DynamoDB

- You need **audit visibility** into who decrypted what and when  
- You're exporting data to encrypted S3 buckets  
- You're replicating data across Regions using **Global Tables**  
- You're working in **regulated environments** (HIPAA, PCI-DSS, etc.)  
- You want to enforce **least privilege over data access**

---

## Watch Out For

- Using **AWS-managed keys** (`aws/dynamodb`) in environments where compliance requires **CMK**  
- Forgetting to scope **CMK** access to only the roles that need it  
- Overlooking the need for **multi-Region key access** in Global Tables  
- Assuming “encryption at rest” alone is enough — you also need **auditing, alerts, and scoped access**

---

## Final Thoughts

DynamoDB encryption isn’t just “on by default” — it’s a system you can **deeply integrate** into your organization’s **KMS strategy**, **IAM design**, and **compliance posture**.

With proper **CMK** usage, **VPC** scoping, audit logging, and cross-Region replication awareness, you can make DynamoDB a **first-class secure data plane** — not just a fast one.

**Encryption in DynamoDB is non-optional**, but doing it intentionally transforms it from a checkbox into a **control boundary you can audit, limit, and prove.**
