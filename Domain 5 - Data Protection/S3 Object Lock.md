# S3 Object Lock

S3 Object Lock enforces write-once-read-many (WORM) immutability on objects, so a version cannot be overwritten or deleted for a defined retention period or while a legal hold is in place. It is the core control for tamper-proof logs, ransomware resilience, and regulatory records retention (SEC 17a-4, FINRA, and similar), because it stops even a privileged attacker from destroying data to cover their tracks. Object Lock requires versioning and applies to object versions, and its behavior splits into two retention modes plus legal holds. The thing to hold onto: compliance mode is absolute (no one, including the root user, can delete or shorten retention until it expires) while governance mode can be bypassed by a principal with `s3:BypassGovernanceRetention`, legal holds are indefinite until removed, and Object Lock must be enabled with versioning (at bucket creation, or on an existing bucket via AWS support/API) rather than toggled casually.

## How it works

- **Object Lock requires versioning and locks versions.** It operates on object versions, so versioning must be on. A retained version cannot be overwritten or deleted until its retention lapses, and new writes create new versions rather than replacing the locked one.
- **Two retention modes.** Governance mode blocks deletion and retention-shortening except for principals granted `s3:BypassGovernanceRetention` (and the related permissions), useful when a small set of admins must retain override ability. Compliance mode blocks deletion and shortening for everyone, including the account root, until the retention date passes, with no override path.
- **Retention can be set per object or by default.** A default retention rule on the bucket applies a mode and duration to new objects, or you set retention per object version. Retention periods can be extended but, in compliance mode, never shortened.
- **Legal hold is separate and indefinite.** A legal hold (`s3:PutObjectLegalHold`) prevents deletion regardless of any retention period and stays until explicitly removed, independent of a retention date. It is the mechanism for litigation holds of unknown duration.
- **Lifecycle cannot override retention.** A lifecycle expiration rule will not delete an object still under Object Lock retention, so retention wins over lifecycle policies.
- **IAM must not undermine it.** The protection is only as strong as the scoping of `s3:BypassGovernanceRetention`, `s3:PutObjectRetention`, `s3:PutObjectLegalHold`, and version-delete permissions, so those must be tightly controlled.

## Object Lock modes and holds

| Control | Who can delete/shorten before expiry | Duration | Use for |
|---|---|---|---|
| **Governance mode** | Only principals with `s3:BypassGovernanceRetention` | Set retention, extendable | Internal WORM with admin override |
| **Compliance mode** | No one, including root | Set retention, never shortened | Regulatory WORM, strong ransomware defense |
| **Legal hold** | Blocked until hold removed | Indefinite | Litigation / investigation holds |

## What gets tested

- **Compliance vs governance mode.** "No one, not even root, can delete before retention expires" is compliance mode. "Blocked unless the principal has a bypass permission" is governance mode via `s3:BypassGovernanceRetention`. This is the most tested Object Lock distinction.
- **Ransomware and tamper-proof logs.** Protecting backups or logs from an attacker who tries to delete them is Object Lock in compliance mode plus versioning. Encryption alone does not stop deletion.
- **Object Lock requires versioning.** Any scenario enabling Object Lock implies versioning is (or must be) on, and Object Lock is set up with the bucket rather than flipped casually later.
- **Legal hold vs retention.** Indefinite retention for an investigation of unknown length is a legal hold, not a fixed retention period.
- **Lifecycle does not override retention.** A lifecycle rule cannot delete an object still under retention, so retention takes precedence, a common distractor.
- **IAM scoping around bypass.** Preventing an end-run means tightly scoping `s3:BypassGovernanceRetention` and version-delete permissions, since loose IAM defeats governance-mode protection.

## Limitations

- Compliance mode is intentionally irreversible for the retention window, so a mistaken mode or over-long duration traps the data and its storage cost with no override, even for root.
- Object Lock requires versioning and is arranged at bucket setup, so it is not a control you casually enable on an arbitrary long-standing bucket without planning.
- Governance mode's protection depends entirely on tightly scoping the bypass permission, so loose IAM turns it into no protection at all.
- Retained versions accumulate storage cost, and because lifecycle cannot delete them until retention expires, cost is locked in for the retention period.
- Object Lock defends against deletion and overwrite, not confidentiality. It pairs with encryption and access controls rather than replacing them.
- It protects object versions in the bucket, so a broader account compromise that could delete the bucket configuration or that predates the lock still needs separate guardrails (SCPs, MFA Delete, cross-account/isolated copies).