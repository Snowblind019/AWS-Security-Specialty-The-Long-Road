# Recycle Bin in AWS (S3 Versioning + Object Lock + MFA Delete)

AWS has no single "Recycle Bin" service for S3, you build soft-delete plus anti-purge protection by combining S3 Versioning (keeps every version and turns a delete into a recoverable delete marker), S3 Object Lock (WORM immutability that blocks deletion for a retention period), and MFA Delete (requires an MFA device to permanently remove versions or disable versioning). Together they give you undelete, legal hold, and ransomware resilience natively. Note that there is also a separate, actual AWS service literally named Recycle Bin, but that one is for recovering deleted EBS snapshots and AMIs, distinct from this S3 pattern. The thing to hold onto: Versioning gives recoverability, Object Lock gives immutability (governance mode can be bypassed with a special permission, compliance mode cannot be bypassed by anyone including root), MFA Delete adds a human factor and is API/CLI-only, and Object Lock requires versioning and is set at bucket creation.

## How it works

- **Versioning makes delete recoverable.** With versioning on, deleting an object writes a delete marker while prior versions persist, so you restore by removing the marker or retrieving an earlier version. This is the "recycle bin" recoverability layer.
- **Object Lock enforces WORM immutability.** In governance mode, retention can be overridden only by principals with `s3:BypassGovernanceRetention`. In compliance mode, no one, including the root user, can delete or shorten retention until it expires. Legal holds are a separate, indefinite lock until removed. Object Lock requires versioning.
- **MFA Delete adds a human authorization factor.** When enabled, permanently deleting a version or disabling versioning requires the root user's MFA. It is configurable only via API/CLI (not the console) and is deliberately hard to disable.
- **Lifecycle rules manage version sprawl, within limits.** Lifecycle policies expire or archive noncurrent versions to control cost, but they cannot delete objects still under an Object Lock retention window, so retention wins over lifecycle.
- **IAM must not allow bypass.** The protection is only as strong as the permissions around it, so `s3:BypassGovernanceRetention`, version deletion, and versioning-configuration changes must be tightly scoped to avoid an end-run around the recycle-bin design.

## The three layers and what each defends

| Feature | Defends against | Key detail |
|---|---|---|
| **Versioning** | Accidental delete/overwrite | Delete becomes a recoverable marker |
| **Object Lock (governance)** | Casual/rogue deletion | Bypassable with `s3:BypassGovernanceRetention` |
| **Object Lock (compliance)** | Any deletion, incl. root | Immutable until retention expires, no bypass |
| **Legal hold** | Deletion during investigation | Indefinite until explicitly removed |
| **MFA Delete** | Unauthorized permanent purge | Root MFA required, API/CLI only |

## What gets tested

- **Compliance vs governance mode.** "No one, not even root, can delete before retention expires" is compliance mode. "Delete blocked unless a principal has a special bypass permission" is governance mode (`s3:BypassGovernanceRetention`). This distinction is the most tested Object Lock fact.
- **Object Lock requires versioning and is set at creation.** You enable Object Lock when creating the bucket (with versioning), not casually afterward on an arbitrary existing bucket. A scenario needing immutability on a bucket without versioning implies recreating or enabling versioning plus lock support.
- **Versioning for accidental-delete recovery.** Recovering an accidentally deleted object is versioning (remove the delete marker), not Object Lock.
- **Ransomware and legal hold.** Protecting originals from an attacker who tries to delete or overwrite is Object Lock (compliance) plus versioning, and legal hold covers indefinite investigation retention.
- **Lifecycle cannot override Object Lock.** A lifecycle rule will not delete an object still under retention, so retention takes precedence.
- **MFA Delete specifics.** It requires root MFA, is API/CLI-only, and protects against unauthorized permanent deletion, distinct from Object Lock.
- **S3 recycle-bin pattern vs the EBS/AMI Recycle Bin service.** For recovering deleted EBS snapshots or AMIs, the answer is the actual Recycle Bin service with retention rules, not S3 versioning.

## Limitations

- Versioning multiplies storage cost because every version persists, so lifecycle rules to expire noncurrent versions are needed to control spend.
- Object Lock (and versioning support for it) must be arranged at bucket setup, so it is not a switch you casually flip on a long-standing bucket.
- Compliance mode is intentionally irreversible for the retention window, so a misconfigured retention traps data and cost with no override, even for root.
- MFA Delete is root-only and API/CLI-only, which makes it operationally awkward and is why many teams skip it despite its value.
- The whole design can be undermined by loose IAM: a principal able to bypass governance retention, delete versions, or disable versioning defeats the recycle bin.
- These controls protect against deletion and overwrite, not confidentiality. They pair with encryption and access controls rather than replacing them.