# Amazon RDS Encryption

## What RDS Encryption Actually Covers

Encryption in Amazon RDS is about protecting data at rest and in transit — ensuring that sensitive database contents, snapshots, backups, and logs are unreadable if stolen, intercepted, or mishandled.

Encryption is not optional in secure environments — it’s a compliance requirement for frameworks like **HIPAA, PCI-DSS, FedRAMP**, and **GDPR**.

In AWS, RDS encryption is powered by **AWS KMS** and follows the **shared responsibility model**:

- **AWS handles**: physical security, hardware-based key storage (HSM-backed), and encryption/decryption at the disk layer  
- **You handle**: when and how encryption is enabled, key policies, key rotation, access controls, and architecture decisions  

> A misstep like sharing a snapshot publicly or launching an unencrypted DB can still lead to a security incident — even if encryption is “enabled.”

---

## What Encryption at Rest Covers in RDS

When enabled, RDS encryption at rest applies to the following:

- Database storage volumes  
- Automated backups  
- Manual snapshots  
- Read replicas  
- Logs stored on disk  
- Temporary files on instance storage  

This ensures that everything written to disk is encrypted using **AES-256**, managed through **AWS KMS**.

> Once encrypted, the entire storage layer is encrypted, and you **cannot remove encryption later** — you must recreate the database unencrypted if needed.

## When You Enable Encryption

- Encryption **must be enabled at creation** of the RDS instance or cluster.  

- You cannot "turn on" encryption after the fact.

### Workaround:
1. Take a snapshot of an unencrypted DB  
2. Copy the snapshot and enable encryption during the copy  
3. Restore a new encrypted DB from that encrypted snapshot  

> This process is often used to migrate legacy databases into compliance without full re-architecture.

---

## Key Management with AWS KMS

Every encrypted RDS database is tied to a **KMS key** — which controls access to the encrypted data.

You can use:
- **AWS-managed KMS key (`aws/rds`)**
  - Easiest, least control  
- **Customer-managed key (CMK)**
  - Full control over permissions, lifecycle, rotation  
  - Enables fine-grained access policies  
  - Required for some compliance standards  

### Using a CMK allows you to:
- Control which users or roles can decrypt data  
- Audit every usage of the key via **CloudTrail**  
- Enforce automatic rotation (if enabled)

---

## RDS Encryption in Aurora

Aurora behaves the same as regular RDS engines, but with cluster-based nuances:

- Encryption is applied to **all storage nodes** in the Aurora cluster  
- Each Aurora DB cluster is associated with a **single KMS key**  
- You **cannot mix encrypted and unencrypted instances** within the same cluster  
- Aurora snapshots, backups, and replicas all follow the same encryption scope

---

## What Encryption in Transit Covers

RDS supports **SSL/TLS encryption** for connections between your application and the database.

- All supported RDS engines provide public SSL certificates  
- You must configure your app (JDBC, `psql`, MySQL CLI, etc.) to use SSL  
- You can enforce encrypted connections via **DB parameter groups**  
- Some databases (like PostgreSQL) support `rds.force_ssl = 1`, which requires all client connections to use SSL  

> This is important for:
> - Compliance  
> - Preventing MITM attacks  
> - Protecting secrets like credentials and queries

---

## Snapshot Sharing and Encryption Risk

By default, **unencrypted snapshots can be shared publicly or cross-account** — this is a major security risk.

### Encrypted snapshots:
- Cannot be shared publicly  
- Can only be shared with accounts that have access to the KMS key  
- Require **explicit KMS permissions** to be accessed or restored  

> Many known AWS breaches occurred when organizations:
> - Created unencrypted RDS snapshots  
> - Shared them with outside accounts or inadvertently marked them public  

**Best practice**:  
Never use unencrypted snapshots for production workloads, and monitor for unexpected snapshot sharing using **AWS Config rules** or **Security Hub**.

---

## Cross-Region Replication with Encryption

Encrypted RDS instances support **cross-region read replicas** — but only when:
- The target Region supports the same KMS key  
- Or a copy of the CMK exists in the destination Region  

> You must ensure **multi-Region key planning** if you want DR across geographies.  
> Otherwise, replication will fail due to key mismatch errors.

---

## Logging, Monitoring, and Auditing

You should monitor encrypted resources just like unencrypted ones — with **special attention to KMS usage**.

| Tool              | What to Monitor                                                                 |
|-------------------|----------------------------------------------------------------------------------|
| CloudTrail        | KMS Decrypt, Encrypt, ReEncrypt, GenerateDataKey calls                          |
| AWS Config        | Detect unencrypted RDS resources, snapshots, backups                            |
| Security Hub      | Surface non-compliant encryption settings via controls                          |
| RDS Logs          | No plaintext storage — logs are encrypted at rest                               |
| CloudWatch Alarms | Track API usage, snapshot creation, or key changes                              |

> Make sure key usage is limited, logged, and **never open to wildcards like `*`** in key policies.

---

## Snowy’s Example: Encrypted PostgreSQL in Production

**Snowy builds a secure audit trail system using RDS PostgreSQL.**

### Security Requirements:
- All data must be encrypted at rest  
- No public access to snapshots  
- Full audit trail of who accessed what and when  
- Cross-region replica in `us-east-2` for disaster recovery  

### Implementation:
- Snowy creates a **customer-managed KMS key**  
- Launches RDS in a **private subnet** with encryption enabled at creation  
- Configures DB parameter group to enforce SSL connections  
- Application uses **IAM-based authentication** and signed SSL connections  
- Snapshots are encrypted and **only shared with a backup account**  
- **CloudTrail logs** all KMS activity, with alerts if unexpected usage occurs  

> This setup satisfies internal controls and provides strong encryption boundaries across storage, access, replication, and backups.

---

## When to Use RDS Encryption

- All production databases with any sensitive data  
- Regulatory environments (HIPAA, PCI, SOC 2, FedRAMP, etc.)  
- Architectures with cross-account snapshot sharing  
- Workloads using Secrets Manager + IAM authentication  

---

## When Not to Use (Caution Required)

- Temporary dev/test databases that don’t store real data (but still often better to encrypt)  
- Scenarios where legacy applications don’t support SSL, and refactoring is not feasible  
- If you’re running databases manually on EC2 and want to use a different encryption model — in that case, you manage everything  

---

## Final Thoughts

RDS Encryption is **not a checkbox** — it’s a **commitment to layered data protection**.

Enabling encryption is only step one. To truly secure your database, you must:

- Use **customer-managed KMS keys**  
- Monitor all key usage and API calls  
- Lock down **snapshot sharing** and network exposure  
- Enforce **SSL/TLS** in transit  
- Pair with **IAM, Secrets Manager**, and **Config rules** for a full security envelope  

> Encryption doesn’t make your data untouchable — it makes mistakes traceable, policy violations auditable, and theft far more difficult.

When combined with **least privilege**, **monitoring**, and **intentional key architecture**, **RDS encryption becomes a powerful pillar of cloud data security.**

