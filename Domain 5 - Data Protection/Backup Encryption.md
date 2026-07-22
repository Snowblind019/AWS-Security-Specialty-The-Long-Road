# Backup Encryption in AWS

Backup encryption is the discipline of making sure every snapshot and recovery point (EBS, RDS, Aurora, DynamoDB, EFS, and centralized AWS Backup vaults) is encrypted at rest with KMS so a copy of your data cannot be restored and read by whoever gets hold of it. A backup is a full, high-value duplicate of production, secrets and all, so an unencrypted snapshot is a standing exfiltration path that survives every other control. The exam angle is about key custody and key movement: which key encrypts the recovery point, and whether the account or Region you are copying to can actually use that key. The thing to hold onto: encryption follows the key, not the resource, so cross-account and cross-Region backup copies fail or leak based on KMS key access, and Vault Lock is the separate control that stops an attacker from deleting the backups to cover their tracks.

## How it works

- **At rest is KMS, per backup type.** You choose an AWS-managed key (`aws/...`, free, easy) or a customer-managed key (CMK, for policy control, auditing, and cross-account grants). EBS snapshots inherit the source volume's key or take a new one, RDS and Aurora snapshots carry the cluster/DB key, DynamoDB PITR and backups are KMS-encrypted by default, and EFS backups use the file system's key.
- **AWS Backup vaults are encrypted at the vault level.** You pick a KMS key at vault creation and every recovery point stored inside inherits it, independent of whatever key the source service used. This is why a restore can involve two keys: the vault key that protected the recovery point and the target resource's key.
- **Restore can require both keys.** Restoring a backup encrypted under Vault A's key (KMS-A) into a resource that uses KMS-B means the restoring identity needs access to both keys, or the data is re-encrypted under the destination key. Missing grants show up as a failed or denied restore.
- **Cross-Region copy needs a destination-Region key.** A snapshot copied to another Region must be re-encrypted with a key that exists in that Region, because a KMS key is Regional. You specify the destination key on the copy.
- **Cross-account copy needs key sharing.** The destination account must be granted use of the source CMK, or the copy must land under a CMK the destination account owns. AWS-managed keys cannot be shared cross-account, which forces a CMK for these flows.
- **Vault Lock protects against deletion.** Separate from encryption, Vault Lock enforces a write-once retention policy so recovery points cannot be shortened, altered, or deleted, even by an attacker with strong permissions. Encryption stops reading, Vault Lock stops destroying.

## Backup key behavior by dimension

| Dimension | Behavior | Where it breaks |
|---|---|---|
| **Key type** | AWS-managed (free) or CMK (control, sharing) | AWS-managed keys cannot be shared cross-account |
| **Vault encryption** | Vault key applies to all recovery points inside | Independent of the source service's key |
| **Restore** | May need both vault key and target key | Missing grant on either key blocks restore |
| **Cross-Region copy** | Re-encrypts under a destination-Region key | No key in target Region means copy fails |
| **Cross-account copy** | Destination account must use source CMK or its own | AWS-managed key cannot cross accounts |
| **Vault Lock** | Immutable retention, blocks deletion | Not encryption, layer it separately |

## What gets tested

- **Cross-account or cross-Region backup sharing forces a CMK.** If a scenario copies snapshots to another account or Region, the correct design uses a customer-managed key with the destination granted access. AWS-managed keys cannot be shared.
- **Restore failures trace to KMS access.** A denied or failed restore across accounts or from a vault usually means the restoring principal lacks a grant on the vault key, the source key, or the target key. The fix is a key grant, not a backup-config change.
- **Vault Lock vs encryption.** Encryption answers confidentiality (an attacker cannot read the backup). Vault Lock answers integrity and availability of the backups (an attacker cannot delete them). If the requirement is anti-tamper or ransomware resilience, that is Vault Lock.
- **Cross-Region needs a Region-local key.** You cannot use a key from Region A to encrypt a copy landing in Region B. Multi-Region keys or a destination-Region CMK is the answer.
- **Default vs custom key.** Some services encrypt backups by default with an AWS-managed key. Choosing a CMK is what unlocks custom key policies, cross-account use, and CloudTrail-based auditing of decrypt calls.

## Limitations

- Encryption protects a backup at rest only. It does nothing about who has restore permissions, so IAM scoping on restore and copy actions is a separate, necessary control.
- AWS-managed keys cannot be shared across accounts, so any cross-account backup strategy must be built on CMKs from the start.
- A key is Regional. Cross-Region copies always involve re-encryption under a destination-Region key, which must exist and be accessible before the copy runs.
- Vault-level and source-level keys can differ, so restores can silently require access to multiple keys. This is an easy thing to miss until a restore is denied during an incident.
- Encryption does not stop deletion. Without Vault Lock, an attacker with sufficient permissions can delete encrypted recovery points, which is why encryption and Vault Lock are complementary, not substitutes.
- Heavy use of many CMKs and aggressive backup schedules drives up KMS request and key costs, so key sprawl has a real bill attached.