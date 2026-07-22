# Amazon Redshift Encryption

Redshift encryption protects the data warehouse at rest (tables, temp tables, result sets, Spectrum intermediate data, snapshots, and backups to S3) with AES-256 via KMS, and in transit with TLS 1.2+ for JDBC/ODBC, COPY/UNLOAD to S3, and Spectrum. Unlike RDS and EBS, Redshift is more flexible about at-rest encryption: you can enable it on an existing cluster (Redshift runs a background migration to a new encrypted cluster), and you can rotate or switch the KMS key on a running cluster. Redshift also has its own key hierarchy layered on top of KMS. The thing to hold onto: at-rest encryption can be enabled on an existing Redshift cluster (a distinction from RDS/EBS snapshot-copy-restore), a customer-managed key gives auditing, cross-account snapshot sharing, and scoped access, in-transit is enforced with `require_ssl=true`, and Redshift Serverless encrypts per namespace with its own key, not the classic cluster's key.

## How it works

- **At rest is AES-256 with a layered key hierarchy.** Redshift uses KMS to protect a hierarchy of keys (cluster key, database key, and data encryption keys) that encrypt the data blocks. You pick the AWS-managed key `aws/redshift` or a customer-managed CMK. Once enabled, encryption cannot be disabled.
- **You can enable encryption on an existing cluster.** Turning on encryption (or changing the KMS key) triggers a background migration to a new encrypted cluster while the old one stays available, then cuts over. This is more flexible than RDS/EBS, which require snapshot-copy-restore.
- **Key rotation exists at two levels.** KMS can rotate the CMK, and Redshift has its own `rotate-encryption-key` operation that re-encrypts the cluster's key hierarchy. Both are supported.
- **In transit is TLS, enforced per cluster.** Set `require_ssl=true` in the cluster parameter group to force SSL on client connections, and use SSL-enabled drivers. COPY/UNLOAD to S3 and Spectrum interactions are TLS as well.
- **Snapshots inherit the key and cannot be public.** Encrypted clusters produce only encrypted snapshots carrying the source key. Sharing across accounts requires granting the recipient KMS access and a compatible key in the destination Region for cross-Region restores. Encrypted snapshots cannot be shared publicly.
- **Serverless encrypts per namespace.** Redshift Serverless is always encrypted, and each namespace has its own encryption boundary with an AWS-managed or namespace-specific CMK. It does not share the classic cluster's key, enabling per-department or per-environment isolation.

## Redshift encryption facts

| Dimension | Behavior | Note |
|---|---|---|
| **At rest** | AES-256, KMS, layered key hierarchy | Cannot be disabled once on |
| **Enable on existing cluster** | Yes, background migration | Unlike RDS/EBS create-time-only |
| **Key rotation** | KMS rotation + Redshift `rotate-encryption-key` | Two mechanisms |
| **In transit** | TLS via `require_ssl=true` | Enforced per cluster |
| **Snapshots** | Inherit key, not public, KMS grant to share | Compatible key needed in target Region |
| **Serverless** | Always on, per-namespace key | Not the classic cluster's key |

## What gets tested

- **Redshift can encrypt an existing cluster.** Unlike RDS and EBS, enabling encryption on a running Redshift cluster is supported via background migration. A question assuming Redshift needs snapshot-copy-restore like RDS is testing this distinction.
- **CMK for audit, cross-account, and compliance.** Scoped key access, CloudTrail decrypt visibility, and cross-account snapshot sharing require a customer-managed key. `aws/redshift` gives none of those.
- **`require_ssl=true` for in-transit enforcement.** Forcing encrypted client connections is the parameter-group setting, not just using an SSL driver.
- **Snapshot sharing needs KMS grants.** Cross-account encrypted snapshot sharing requires granting KMS access and, for cross-Region restore, a compatible key in the destination. Encrypted snapshots cannot be public.
- **Serverless per-namespace keys.** Assuming Serverless uses the same key as the classic cluster is wrong. Each namespace has its own encryption boundary and key.
- **Include the Redshift service role in the CMK policy.** A common misconfiguration is a CMK policy that omits `redshift.amazonaws.com` or the relevant roles, breaking cluster operations.

## Limitations

- Once enabled, encryption cannot be disabled on a cluster, so it is a one-way decision even though it can be turned on later.
- Enabling encryption or changing the key runs a background migration, which has a performance and time cost during the operation, unlike an instantaneous toggle.
- `aws/redshift` cannot be scoped, audited finely, or shared cross-account, forcing a CMK for regulated and multi-account use.
- Cross-Region snapshot restore needs a compatible key in the destination Region, so DR planning must account for key placement.
- At-rest encryption gives no in-transit protection, so `require_ssl` and SSL drivers are separately required, and legacy BI clients that cannot do SSL block enforcement.
- Encryption protects confidentiality, not authorization or exfiltration. UNLOAD to a misconfigured or public S3 bucket still leaks data, so export controls (bucket policy, VPC endpoint scoping, Lake Formation) are separate necessary controls.