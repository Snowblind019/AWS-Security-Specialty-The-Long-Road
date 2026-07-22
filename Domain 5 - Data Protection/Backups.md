# AWS Backup

AWS Backup is the policy-based, centralized backup manager that automates and governs backups across services (EBS, RDS, Aurora, DynamoDB, EFS, FSx, Storage Gateway, and EC2 via EBS) from one place, instead of scripting per-service snapshots and hoping the cron job ran. Security-wise its value is orchestration plus enforceable guarantees: a backup plan says what gets backed up and for how long, a vault controls the key and access, and Vault Lock makes recovery points immutable so not even root can delete them before retention expires. That immutability is the piece that turns backups into a real ransomware and insider-tamper control rather than just a DR convenience. The thing to hold onto: AWS Backup centralizes the policy, the vault holds the key and the access boundary, and Vault Lock (WORM) is the separate control that stops deletion, so encryption protects reading and Vault Lock protects existing.

## How it works

- **A backup plan is the policy.** It defines frequency (daily, weekly, monthly), lifecycle transitions to cold storage, retention, and copy actions. This is the declarative schedule that replaces manual snapshots.
- **A backup selection decides scope.** Resources join a plan by tag (for example `Backup=true`) or explicit ARN, so tag-based selection scales across an account without editing the plan each time a resource is created.
- **A vault holds recovery points and sets the key.** You choose a KMS key at vault creation and every recovery point inside inherits it. The vault is also the IAM boundary, so vault access can be separated from resource ownership to enforce separation of duties.
- **Vault Lock enforces WORM.** Once locked in compliance mode, retention cannot be shortened and recovery points cannot be deleted before expiry, by anyone, root included. This is the anti-tamper guarantee auditors and ransomware playbooks want.
- **Cross-Region and cross-account copy provide isolation.** Copies to another Region survive a regional event, and copies to a separate account survive compromise of the primary account. Both are the standard blast-radius controls, and both depend on KMS key access in the destination.
- **Everything is observable.** CloudTrail logs backup and restore API activity, and Backup Audit Manager tracks backup jobs against compliance controls (skipped jobs, missing coverage, deleted recovery points), surfacing drift you can route into Security Hub.

## AWS Backup components at a glance

| Component | Role | Security relevance |
|---|---|---|
| **Backup plan** | Frequency, lifecycle, retention | Enforces consistent, auditable coverage |
| **Backup selection** | Tag or ARN scoping | Scales protection without per-resource edits |
| **Vault** | Container, KMS key, access policy | Key custody plus separation of duties |
| **Vault Lock** | WORM immutability | Blocks deletion, even by root, until retention ends |
| **Recovery point** | The actual snapshot/copy | The thing you restore from |
| **Cross-account/Region copy** | Isolated second copy | Survives account or regional compromise |
| **Audit Manager** | Compliance tracking | Detects skipped or deleted backups |

## What gets tested

- **Vault Lock is the immutability answer.** If the scenario is ransomware, insider deletion, or "prevent anyone including root from deleting backups before retention," that is Vault Lock in compliance mode, not IAM policy alone.
- **Cross-account backup for blast-radius isolation.** When a compromised primary account must not be able to reach the backups, copy recovery points into a separate, locked-down account. Cross-Region handles regional failure, not account compromise.
- **Tag-based selection.** The scalable way to enroll resources is tags, so a fleet-wide "back up everything tagged X" requirement points at tag-based backup selection.
- **S3 is not a first-class AWS Backup target in the same way.** S3 durability and immutability come from versioning plus Object Lock and lifecycle, so an S3 protection question leans on Object Lock rather than AWS Backup vaults.
- **Separation of duties.** Vault access can and should be distinct from the identity that owns the source resource, so an attacker who compromises the workload cannot also purge its backups.
- **Restore testing and audit evidence.** Proving recoverability uses Backup Audit Manager and periodic restore tests, not just the existence of a backup plan.

## Limitations

- Coverage is limited to supported services. S3 in particular is protected through versioning and Object Lock, not native AWS Backup, so it needs its own handling.
- Cross-Region and cross-account copies depend on KMS key access in the destination. Without a usable key there, the copy fails, which ties AWS Backup tightly to your KMS design.
- Vault Lock in compliance mode is deliberately irreversible for the locked retention, so a misconfigured lock (too long, wrong policy) cannot be undone, which is a governance risk of its own.
- Backups protect against loss and tampering, not confidentiality on their own. Encryption plus tight restore permissions are still required so a recovery point is not a soft exfiltration path.
- Costs accrue per GB-month plus restore and cross-Region transfer, so aggressive schedules, long retention, and many copies add up even though Vault Lock and Audit Manager themselves are free.
- EC2 is captured via EBS snapshots and AMIs, so instance-level metadata is not backed up the way the block volumes are, which matters for full-instance reconstruction.