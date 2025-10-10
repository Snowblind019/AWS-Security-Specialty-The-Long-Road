# Amazon Aurora Encryption

## What Aurora Encryption Covers

Aurora encryption provides **at-rest** and **in-transit** protection for all data stored in Amazon Aurora clusters. Just like standard RDS engines, encryption is **KMS-integrated**, **transparent to applications**, and **non-negotiable for compliance workloads** (HIPAA, PCI-DSS, FedRAMP, CJIS, etc.).

What makes Aurora encryption stand out is that it operates over a **shared distributed storage layer** — meaning **all replicas, backups, logs, and snapshots** are inherently tied to the encryption of the cluster as a whole.

Aurora’s high-performance design doesn’t compromise encryption. Instead, it builds encryption **directly into the distributed storage fabric** and replicates encrypted data across three AZs — ensuring redundancy without exposing sensitive data at any stage.

---

## What Gets Encrypted in Aurora (At Rest)

When encryption is enabled, Aurora encrypts **everything that touches disk**, including:

- Database storage volumes (across all 6 copies per page)  
- Write-ahead logs (WALs)  
- System tables and temporary tables  
- Query caches  
- Backups stored in S3  
- Manual and automated snapshots  
- Aurora Replicas  
- Aurora Global Database cross-Region replication streams (when supported)  
- Restore jobs and point-in-time recovery  

Encryption is handled via **AES-256 using AWS Key Management Service (KMS).**

---

## When You Enable Aurora Encryption

✔️ **Must be enabled at cluster creation.**  
✖️ **Cannot be turned on later for an existing unencrypted cluster.**

To migrate from unencrypted to encrypted:

1. Create a snapshot of the unencrypted cluster  
2. Copy the snapshot and enable encryption during the copy  
3. Restore a new encrypted cluster from the encrypted snapshot  

This is the **only supported path**. Aurora **doesn’t allow toggling encryption on a live cluster**.

---

## KMS Key Behavior

Aurora supports two types of KMS keys:

- **AWS-managed keys** (default: `aws/rds`)  
- **Customer-managed keys (CMKs)**  

CMKs are preferred for secure workloads because they offer:

- Full control over who can use the key  
- Auditability via CloudTrail  
- Cross-account permissions  
- Key rotation (automated or manual)  
- Required for some compliance frameworks  

> Key rotation applies only to **new data**. Old encrypted blocks remain under the previous key until rewritten.

---
## Cluster-Level KMS Binding


Aurora encryption is **bound to the cluster**, not individual instances.

- Every instance in the cluster inherits the same encryption status and key  
- You **cannot mix encrypted and unencrypted instances** within the same cluster  

- For Aurora Global Database:  
  - All secondary clusters must use the **same or compatible KMS key**  

  - Cross-Region encryption planning is **required** to avoid replication or failover failures  


---

## Snapshot and Backup Encryption

- Encrypted clusters produce **only encrypted snapshots**  
- Snapshots **inherit the KMS key** from the source cluster  

- You can **copy encrypted snapshots** to another Region using a **different CMK**  
- You **cannot share encrypted snapshots publicly**  
- You **can** share them with other AWS accounts **if those accounts have KMS access**

This eliminates a major risk present in traditional RDS: **public snapshot leakage**.

---

## Cross-Region Replication (Aurora Global Database)

Aurora Global Database supports **cross-Region replication of encrypted clusters**.  
However:

- Both Regions must support Aurora encryption  
- The target Region must have access to the CMK (or a **CMK with the same key material and alias**)  
- If KMS keys aren’t configured properly, **setup or failover will fail**

> **Best Practice:** Use **replicated CMKs** or **multi-Region keys** in AWS KMS when designing global Aurora architectures.

---

## Encryption in Transit

Aurora supports **SSL/TLS encryption** for all client connections. It is compatible with:

- PostgreSQL's native `sslmode=require`  
- MySQL / JDBC `?ssl=true`  
- RDS/Aurora-specific parameter group: `rds.force_ssl`

This ensures:

- **End-to-end encryption** from application to database  
- **Protection against MITM (man-in-the-middle) attacks**  
- **Alignment with Zero Trust principles**  

While AWS does **not log plaintext client data**, **in-transit encryption is required** for regulated workloads.

---

## Audit, Logging, and Visibility

| **Tool**        | **Encryption Visibility**                                                     |
|-----------------|--------------------------------------------------------------------------------|
| CloudTrail      | Captures all KMS key usage events, snapshot copy actions, cluster restores     |
| CloudWatch Logs | All logs from Aurora instances (if exported) are encrypted at rest             |
| Security Hub    | Detects non-compliant configurations (e.g., unencrypted clusters)              |
| AWS Config      | Triggers rules if unencrypted DBs or snapshots are detected                    |
| GuardDuty       | Monitors for suspicious snapshot activity (when trail + share is enabled)      |

> Combine these tools to **enforce encryption**, monitor **drift**, and detect **violations** in real-time.

---

## Data Residency and Compliance Notes

Aurora encryption plays a **critical role** in **data residency** and **sovereignty** controls.

- All data at rest is **encrypted and regionally scoped** unless using Global Database  
- If data must remain in a specific country, combine **encryption + regional controls**  

- Global Database **replicates encrypted data**, but **may violate residency** if misconfigured  
- Always align Aurora KMS usage with your **legal and compliance teams' data boundaries**

---

## Snowy’s Example: Encrypted Global Reporting DB


Snowy builds a **centralized reporting database** for **financial compliance records**.

### **Requirements:**

- Must be encrypted at rest and in transit  
- Accessible from `us-west-2` and `eu-west-1`  

- Credentials rotated every 30 days  
- Snapshots cannot be shared publicly  


### **Architecture:**

- Aurora PostgreSQL with CMK encryption at creation  
- CMK is **multi-Region**, replicated across `us-west-2` and `eu-west-1`  
- TLS required on all JDBC connections  
- Credentials stored in **Secrets Manager** with rotation  
- Snapshots are encrypted and restricted via **resource-based policies**  
- **CloudTrail** monitors all KMS activity  
- **AWS Config rules** enforce “no unencrypted DBs” and “no public snapshot sharing”  

This setup enforces encryption, enables compliance, and provides **global observability with strong access control**.

---

## ✔️ Use Aurora Encryption When:

- You're storing **PII**, **payment data**, **healthcare data**, or **sensitive business records**  
- You must meet **HIPAA**, **PCI-DSS**, **FedRAMP**, or **GDPR**  
- You're using **Aurora Global Database across Regions**  
- You're integrating with **Secrets Manager**, **KMS**, and **audit pipelines**

---

## ✖️ Avoid Pitfalls Like:

- Launching an **unencrypted cluster by mistake** (you cannot encrypt later)  
- Sharing **snapshots without KMS permission boundaries**  
- Failing to **replicate KMS keys across Regions** for DR or Global Database  
- Skipping **SSL/TLS enforcement** in your app connection logic

---

## Final Thoughts

Aurora encryption isn’t just something you “enable” — it’s a **core part of your database design**.

It touches **everything**:


- KMS keys  

- Snapshots  
- DR plans  
- Logs  
- Global replication  
- Compliance posture  


If you’re not deliberate about your **KMS architecture**, **parameter groups**, and **access controls**, you risk creating an **encrypted system that still leaks data** or **breaks during recovery**.


**Done right, Aurora encryption gives you:**


- Strong at-rest and in-transit protection  
- Snapshot confidentiality  
- Multi-Region resilience  
- Seamless integration with IAM and Secrets Manager  
- Proof of compliance, **by design**

