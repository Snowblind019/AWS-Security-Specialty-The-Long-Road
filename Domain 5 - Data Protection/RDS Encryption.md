# Amazon RDS Encryption

RDS encryption protects the database at rest (storage, automated backups, manual snapshots, read replicas, and on-disk logs) with AES-256 via KMS, and in transit with SSL/TLS between the app and the database. As with Aurora, at-rest encryption is a create-time decision that cannot be toggled on a live instance, so the only path to encrypt an existing plaintext database is snapshot, copy-with-encryption, restore. The recurring security failure the exam leans on is not the encryption itself but snapshot exposure: unencrypted snapshots can be shared publicly or cross-account, which is how real breaches happen. The thing to hold onto: at-rest is create-time and cluster/instance-wide, encrypted snapshots cannot be made public and only share to accounts granted the KMS key, in-transit TLS is enforced separately per engine (`rds.force_ssl` for PostgreSQL, `require_secure_transport` for MySQL), and a customer-managed key is what buys cross-account sharing, auditing, and scoped access.

## How it works

- **At rest is AES-256 via KMS, chosen at creation.** Enabling encryption covers storage volumes, automated and manual backups, snapshots, read replicas, on-disk logs, and temp files. There is no per-instance opt-out, and it cannot be added later.
- **Remediation is snapshot-copy-restore.** To encrypt an existing unencrypted database: snapshot it, copy the snapshot with encryption enabled and a chosen key, then restore a new encrypted instance from the copy. This is the standard "bring a legacy DB into compliance" answer.
- **Key tier decides control.** The AWS-managed key `aws/rds` is easiest but cannot be shared cross-account or policy-scoped. A customer-managed key (CMK) gives you the key policy (who can decrypt), CloudTrail auditing, rotation, and cross-account grants, and is required for many compliance regimes and for cross-account snapshot sharing.
- **Snapshot sharing hinges on the key.** Unencrypted snapshots can be shared publicly or to other accounts, the classic exposure. Encrypted snapshots cannot be made public and can only be shared with accounts granted use of the CMK, so encryption plus a CMK closes the leak.
- **In transit is enforced per engine.** Clients connect with SSL using the RDS CA bundle, and you force it server-side with `rds.force_ssl=1` (PostgreSQL) or `require_secure_transport=ON` (MySQL) in a parameter group. At-rest encryption does not imply in-transit.
- **Cross-Region replicas need the key in the target Region.** An encrypted cross-Region read replica requires a usable CMK in the destination Region (a multi-Region key or replicated CMK). Missing this fails replication with a key mismatch.

## RDS encryption facts

| Dimension | Behavior | Exam trap |
|---|---|---|
| **At rest** | Create-time, instance-wide, KMS AES-256 | Cannot enable on a live DB |
| **Existing unencrypted DB** | Snapshot to encrypted copy to restore | "Just enable it" is wrong |
| **Key tier** | `aws/rds` or CMK | CMK required for cross-account and scoped policy |
| **Snapshot sharing** | Encrypted snapshots not public, need KMS grant | Unencrypted snapshots can leak publicly |
| **In transit** | Per-engine `force_ssl` / `require_secure_transport` | Separate from at-rest, not automatic |
| **Cross-Region replica** | Needs CMK usable in target Region | Key mismatch fails replication |

## What gets tested

- **No in-place encryption of an existing RDS instance.** The remediation is snapshot to encrypted copy to restore. Most tested RDS encryption fact.
- **Encrypted snapshots close the public-exposure risk.** If a scenario involves a leaked or publicly shared snapshot, the fix is encryption plus a CMK, since encrypted snapshots cannot be public and only share to KMS-granted accounts. Config rules and Security Hub detect unexpected sharing.
- **CMK for cross-account and audit.** Cross-account snapshot sharing, scoped key policies, and decrypt auditing require a customer-managed key. `aws/rds` cannot be shared cross-account.
- **At-rest and in-transit are independent.** An encrypted-at-rest RDS still accepts plaintext connections unless you force SSL per engine. Regulated data needs both.
- **Cross-Region encrypted replicas need target-Region keys.** Replication failures trace to the destination Region lacking the CMK. Multi-Region keys are the design answer.
- **Snapshots inherit the source key.** You cannot strip encryption by snapshotting, and copying lets you re-target a different CMK.

## Limitations

- No in-place encryption, so remediating an unencrypted database means a new instance and a cutover.
- Encryption is instance/cluster-wide, so you cannot selectively encrypt one part through this mechanism.
- `aws/rds` cannot be shared cross-account, forcing a CMK for cross-account snapshot workflows.
- At-rest encryption gives no MITM protection on the wire, so TLS must be enforced separately per engine, and legacy apps that cannot do SSL block that enforcement.
- Cross-Region replication is sensitive to key placement, so DR across Regions requires deliberate multi-Region key planning or it fails.
- Encryption protects confidentiality, not authorization. A principal with DB credentials and, for CMK tables, KMS access still reads the data, so IAM database authentication, Secrets Manager, and least privilege remain necessary.