# Amazon Redshift Encryption

## What Redshift Encryption Covers

Encryption in Amazon Redshift is designed to protect:

- Sensitive analytical datasets (e.g., PII, financial reports, behavioral telemetry)
- Snapshots, backups, exports, and query results
- In-flight data across networks, APIs, and between services (S3, Spectrum, JDBC, etc.)

Redshift encryption helps enforce data confidentiality, residency, compliance, and least-privilege enforcement in modern data warehouses — especially in shared multi-team or regulated environments.

When enabled properly, encryption protects both:

- **Data at Rest** — physically stored blocks (disk, backups, snapshots)
- **Data in Transit** — across client connections, service integrations, and inter-cluster traffic

---

## Encryption at Rest in Redshift

Redshift supports **AES-256** encryption at rest, integrated with **AWS Key Management Service (KMS).**

All of the following are encrypted when encryption is enabled:

- User and system tables
- Temporary tables and metadata
- Result sets stored on disk
- Redshift Spectrum intermediate data
- Snapshots (automated and manual)
- Backups to S3
- Redshift Serverless namespaces and workgroups

> Once enabled, encryption cannot be disabled for a given cluster or serverless namespace.

---

## Encryption Scope

| Component                        | Encrypted |
|----------------------------------|-----------|
| Base Tables                      | ✔️        |
| Temp Tables                      | ✔️        |
| System Tables                    | ✔️        |
| Query Results on Disk           | ✔️        |
| Redshift Spectrum Query Results | ✔️        |
| Snapshots                        | ✔️        |
| Cluster Backups (in S3)         | ✔️        |
| WAL/Logs                         | ✔️        |

There are no partial encryption options — the entire storage layer is encrypted consistently once enabled.

---

## Key Types Supported

Redshift supports two types of KMS keys:

### 1. AWS-Managed Key (`aws/redshift`)
- Default option
- No cost
- No custom access control or rotation visibility
- No ability to restrict or audit fine-grained use

> Good for dev/test, but **not compliant** for regulated workloads.

### 2. Customer-Managed CMK
- Created and managed in **AWS KMS**
- Gives full control over:
  - Key rotation
  - IAM scoping
  - CloudTrail logging of key usage
  - Cross-account sharing (via resource policies)
  - Alias/label tagging and lifecycle

> Required for:
> - Regulatory environments (HIPAA, PCI, ISO 27001)
> - Exporting data to encrypted S3 buckets
> - Multi-tenant clusters or centralized audit pipelines

---

## How It Works Under the Hood

Redshift uses a **two-tiered encryption model**:

1. Uses KMS to generate a **data encryption key (DEK)** for the cluster
2. Uses the DEK to encrypt all data blocks, result sets, and temporary storage
3. The DEK is encrypted with the cluster's CMK
4. Encrypted DEK is stored persistently with the cluster metadata

- KMS usage is audited via **CloudTrail**
- DEKs are cached securely to minimize API calls during heavy query loads

---

## Encryption in Transit

Redshift enforces **TLS 1.2+** for all communications, including:

- Client connections via JDBC/ODBC
- COPY/UNLOAD to S3
- Redshift Spectrum interactions with Lake Formation, Glue, S3

- Queries across Redshift Serverless and classic clusters

To enforce encryption in transit:

- Set parameter `require_ssl = true` in cluster parameter group
- Configure BI tools and apps to connect using SSL-enabled drivers

- Use VPC endpoints or Direct Connect to limit exposure to internal networks

> No plaintext transport is allowed between services or across AWS Regions.

---

## Snapshots and Exported Data

Encrypted clusters produce **encrypted snapshots only.**

### Snapshot Behavior

- Snapshots inherit the **KMS key** of the source cluster
- Snapshots **cannot** be shared publicly
- To share encrypted snapshots across accounts, the recipient must:
  - Be granted **KMS key permissions**
  - Accept the snapshot share
  - Have a **compatible KMS key** in the destination Region (for cross-Region restores)

### Export Behavior

- Data exported to S3 via `UNLOAD` can use a **KMS key** in the destination bucket
- Redshift Spectrum also respects **S3 bucket encryption policies**
- Unauthorized exports can be blocked using:
  - S3 bucket policies
  - VPC endpoint scoping
  - Lake Formation permissions

---

## Redshift Serverless Encryption

In Redshift Serverless, **encryption is always enabled**, and you can specify:

- An AWS-managed key (`aws/redshift`) or
- A namespace-specific customer-managed **CMK**

Each **namespace and workgroup** in Redshift Serverless has its own encryption boundary, enabling:

- Departmental or tenant-level isolation
- Environment-based security (e.g., staging vs production)
- Fine-grained billing and audit trails

> Encryption works the same under the hood — DEK per namespace, encrypted via CMK.

---

## KMS Audit and Visibility

To monitor encryption and key usage in Redshift:

| Tool           | Function                                                                 |
|----------------|--------------------------------------------------------------------------|

| CloudTrail     | Logs every KMS API call (Encrypt, Decrypt, GenerateDataKey)             |
| CloudWatch     | Can alarm on sudden spikes in KMS usage                                  |
| AWS Config     | Detects non-compliant clusters (unencrypted or wrong key)                |
| Security Hub   | Surfaces misconfigured snapshot permissions or missing encryption        |
| Access Analyzer| Detects overly broad CMK permissions or unintended snapshot sharing      |

> **Best practice**: rotate CMKs annually (or per compliance policy) and monitor all `Decrypt` events from Redshift.

---

## Snowy’s Example: Encrypted BI Analytics Cluster

**Scenario**: Snowy is deploying Redshift to power internal dashboards and ML queries.

### Security Requirements:

- All data (transactions, telemetry, PII) must be encrypted at rest and in transit
- Snapshots must **never** be shareable outside Snowy’s AWS Org
- Exports to S3 must use Snowy’s hardened bucket encryption
- All key usage must be logged and alertable

### Implementation:

- Redshift cluster created with **CMK**: `alias/snowy-bi-redshift-key`
- KMS key scoped to `redshift.amazonaws.com` and Snowy's BI roles
- TLS enforced at the driver level (`require_ssl = true`)
- All snapshots encrypted, and shared only to Snowy's DR account via KMS policy
- `UNLOAD` commands specify S3 buckets with KMS-encrypted storage
- **CloudTrail + Security Hub** monitor KMS usage anomalies

> This architecture meets **compliance**, **observability**, **DR**, and **zero-trust** boundaries.

---

## Use Redshift Encryption (CMK) When:

- You need **regulatory compliance**
- You're exporting to encrypted S3 buckets
- You're building **multi-tenant analytics platforms**

- You require **auditable key control** with CloudTrail
- You're using **Serverless namespaces** across departments

---

## Avoid These Pitfalls:

- Using **AWS-managed keys** in regulated environments (lack of access control)
- Forgetting to include **Redshift service roles** in CMK key policy
- **Over-sharing snapshots** without scoping KMS access
- Failing to **enforce TLS** in JDBC/ODBC clients
- Assuming Redshift Serverless uses the **same key as the main cluster** (it doesn’t — it’s per-namespace)

---

## Final Thoughts

Redshift encryption isn’t just a compliance checkbox — it’s your **first layer of defense** and a **core control boundary** in shared analytics environments.

With proper use of **customer-managed KMS keys**, **snapshot controls**, **export policies**, and **TLS enforcement**, Redshift becomes a locked-down, auditable, enterprise-grade data platform.

Encryption in Redshift gives you:

- Confidence in the **privacy** of your data
- Control over **who can export, decrypt, or snapshot**
- Full **observability over key usage** and cross-service interactions

> **Done right, encryption transforms Redshift from a fast query engine into a secure, governed analytics backbone for critical data.**
