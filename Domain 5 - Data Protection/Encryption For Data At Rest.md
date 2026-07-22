# Encryption for Data at Rest

Data at rest is anything sitting on persistent media: EBS volumes, S3 objects, RDS and DynamoDB storage, SSM parameters, logs, snapshots, and exports. Encryption at rest protects it against the threats that do not involve the network, physical disk theft, a rogue admin browsing stored files, exposed backups or snapshots, and lateral movement after an intrusion. Across AWS the pattern is the same: AES-256 with KMS handling key creation, rotation, policy, and audit, applied transparently on write and read. The thing to hold onto: encryption at rest converts "who can reach the data" into "who can use the key," so the KMS key policy becomes a second authorization gate on top of IAM, and choosing a customer-managed key (over an AWS-managed or AWS-owned key) is what buys you scoped access, CloudTrail visibility, and cross-account control.

## How it works

- **KMS is the backbone.** Nearly every service encrypts at rest with a KMS key: an AWS-owned key (invisible, no control), an AWS-managed service key (`aws/s3`, `aws/ebs`, etc., logged but no custom policy), or a customer-managed CMK (scoped policy, rotation, cross-account, full CloudTrail). The tier you pick determines your control and auditability.
- **Envelope encryption keeps it fast.** KMS issues a data key, the service encrypts the data locally with it, stores the wrapped data key beside the data, and calls KMS only to unwrap on read. This is why bulk data does not stream through KMS and why per-object keys scale.
- **The key policy is a distinct authorization layer.** IAM says who can call the service action, the KMS key policy says who can decrypt. Denying a role on the CMK blocks reads even when IAM allows the action, which is how you stop a compromised role or Lambda from reading a snapshot or object.
- **S3 has three server-side modes.** SSE-S3 (AWS-managed keys, simplest), SSE-KMS (your CMK, auditable and policy-controlled), and SSE-C (you supply the raw key per request, niche and operationally heavy). Bucket policies can require encryption on upload via the `x-amz-server-side-encryption` header or `aws:SecureTransport`.
- **Some services encrypt at creation only.** RDS and Aurora set encryption at creation and cannot toggle it later (snapshot-copy-restore to remediate), DynamoDB is always encrypted, and EBS supports default encryption per Region for new volumes. Knowing which are create-time is exam-relevant.
- **Governance enforces it fleet-wide.** Default encryption settings, SCPs denying unencrypted resource creation, Config rules detecting unencrypted resources, and Security Hub findings turn "should be encrypted" into "cannot be created unencrypted."

## Key management tiers

| Tier | Control | CloudTrail visibility | Cross-account |
|---|---|---|---|
| **AWS-owned** | None | No | No |
| **AWS-managed (`aws/service`)** | Service-scoped, no custom policy | Yes | Limited |
| **Customer-managed (CMK)** | Full key policy, rotation, grants | Yes | Yes |
| **SSE-C (S3 only)** | You hold the raw key | Limited | You manage entirely |

## What gets tested

- **CMK is the answer for control and audit.** Scoped decrypt access, "who decrypted what and when," cross-account, and most compliance mandates require a customer-managed key. AWS-owned and AWS-managed keys cannot be policy-scoped or shared the same way.
- **The key policy blocks reads independent of IAM.** A common correct answer to "stop a compromised role from reading encrypted data" is denying that principal on the KMS key, not only tightening IAM.
- **Enforce encryption on upload with S3 policies.** Requiring `x-amz-server-side-encryption` (or a specific SSE-KMS key) via bucket policy is how you guarantee objects land encrypted, since default encryption alone can be overridden by a request specifying otherwise.
- **Create-time encryption services.** RDS and Aurora cannot be encrypted in place, so remediation is snapshot-copy-restore. DynamoDB is always encrypted (choose the key tier), and EBS default encryption is per Region for new volumes.
- **Grants to roles, not users.** Least-privilege key access uses KMS grants or key-policy statements scoped to specific service roles, not broad principals, to enforce separation of duties.
- **Encryption vs access.** Encryption protects confidentiality of stored bytes, it does not authorize access. A public bucket of encrypted objects is still safe from reading without the key, but IAM and bucket policy still govern who can call GET.

## Limitations

- Encryption at rest does nothing for data in transit or in use. It protects stored bytes only, so TLS and in-memory protections are separate concerns.
- It does not stop an authorized principal who holds both the IAM permission and key access. A compromised role with `kms:Decrypt` reads the data, so key-policy scoping and monitoring are essential.
- Several services encrypt only at creation (RDS, Aurora), so remediation means recreating resources rather than flipping a setting.
- AWS-owned and AWS-managed keys cannot be scoped with custom policies or shared cross-account, so those requirements force CMKs and the key management that comes with them.
- SSE-C puts the entire burden of key custody, availability, and rotation on you, with no KMS safety net, which is why it is rarely the right choice.
- Heavy KMS request volume and many CMKs carry real cost, so per-workload key separation must be balanced against the per-key and per-request bill.