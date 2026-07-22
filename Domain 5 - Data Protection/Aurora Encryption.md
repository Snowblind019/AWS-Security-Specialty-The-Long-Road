# Amazon Aurora Encryption

Aurora encryption provides at-rest and in-transit protection for an Aurora cluster, integrated with KMS and transparent to the application, exactly as it is on standard RDS engines. What is specific to Aurora is that encryption binds to the cluster's shared distributed storage layer, so every replica, snapshot, log, and backup inherits the cluster's encryption state and key by default, you never have a half-encrypted cluster. The catch that dominates exam questions: at-rest encryption must be chosen at cluster creation and cannot be toggled on later, so the only way to encrypt an existing plaintext cluster is the snapshot-copy-restore path. The thing to hold onto: at-rest encryption is a create-time, cluster-wide, KMS-bound decision, in-transit is a separate TLS enforcement you turn on with parameters, and Global Database only works when the target Region can actually use the key.

## How it works

- **At rest is AES-256 via KMS, cluster-wide.** Enabling encryption covers the storage volumes, write-ahead logs, system and temp tables, automated and manual snapshots, backups in S3, replicas, and point-in-time restores. There is no per-instance opt-out inside a cluster.
- **The key choice is AWS-managed (`aws/rds`) or a customer-managed key.** CMKs are preferred for regulated workloads because they give you the key policy (who can use the key), CloudTrail auditability, cross-account grants, and rotation. Automatic rotation re-encrypts only new data, older blocks stay under the prior key material until rewritten, which is fine because KMS tracks the version.
- **Encryption is a create-time decision.** You cannot enable it on a live unencrypted cluster. The supported migration is: snapshot the unencrypted cluster, copy the snapshot with encryption enabled and a chosen key, restore a new encrypted cluster from that copy. This is the answer whenever a scenario has an existing plaintext database that now needs encryption.
- **Snapshots inherit the source key and cannot be shared publicly.** An encrypted snapshot is always encrypted, carries the cluster's key, and can be shared with specific accounts only if those accounts are granted use of the KMS key. This closes the classic RDS public-snapshot leak.
- **In transit is TLS, enforced separately.** Aurora accepts SSL/TLS on client connections (`sslmode=require` for PostgreSQL, `?ssl=true` for MySQL/JDBC), and `rds.force_ssl` in the parameter group makes it mandatory rather than optional. At-rest encryption does not imply in-transit, you enforce each independently.
- **Global Database needs the key in every Region.** Cross-Region encrypted replication requires the target Region to have access to the CMK, which in practice means a multi-Region KMS key or a properly replicated key. Miss this and setup or failover fails outright.

## Aurora encryption decisions at a glance

| Dimension | Behavior | Exam trap |
|---|---|---|
| **At rest** | Chosen at creation, cluster-wide, KMS AES-256 | Cannot be enabled later on a live cluster |
| **Existing unencrypted cluster** | Snapshot to copy (encrypt) to restore | "Just enable encryption" is wrong |
| **Key type** | `aws/rds` or CMK | CMK required for cross-account and fine-grained control |
| **Snapshots** | Inherit source key, never public | Shareable to accounts only with KMS grant |
| **In transit** | TLS via `rds.force_ssl` parameter | Separate from at-rest, not automatic |
| **Global Database** | Needs CMK usable in target Region | Multi-Region key or replication required |

## What gets tested

- **You cannot encrypt an existing unencrypted Aurora cluster in place.** The correct remediation is snapshot to encrypted copy to restore. This is the single most tested Aurora encryption fact.
- **Encryption is cluster-wide, not per-instance.** You cannot mix encrypted and unencrypted instances in one cluster, and all instances share the same key.
- **CMK vs AWS-managed key.** Cross-account snapshot sharing, custom key policies, and certain compliance requirements force a CMK. `aws/rds` cannot be shared cross-account.
- **At-rest and in-transit are independent.** A cluster encrypted at rest can still accept plaintext connections unless `rds.force_ssl` is set. Regulated scenarios usually need both.
- **Global Database key placement.** Cross-Region replication or failure to fail over traces back to the target Region lacking access to the CMK. Multi-Region keys are the design answer.
- **Snapshot exposure.** Encrypted snapshots cannot be made public and only share to accounts with KMS access, so "public snapshot leak" is only a risk on unencrypted clusters.

## Limitations

- No in-place encryption of a running unencrypted cluster. The snapshot-copy-restore migration is the only path and it means a new cluster and a cutover.
- Cluster-level binding means you cannot selectively encrypt one instance or one table through this mechanism. It is all or nothing per cluster.
- Automatic key rotation re-encrypts only newly written data, so old blocks remain under earlier key material until rewritten. This is transparent but worth knowing for key-compromise reasoning.
- Global Database replication will not stand up or fail over cleanly if the target Region cannot use the key, so cross-Region KMS design is a hard prerequisite, not an afterthought.
- At-rest encryption gives no protection against MITM on the wire. Without TLS enforcement the data is exposed in transit despite being encrypted on disk.
- Encryption does not by itself satisfy data residency. Global Database can replicate encrypted data out of a jurisdiction, so residency needs Region and replication controls layered on top.