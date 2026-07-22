# Data Retention and Lifecycle Management of Logs and Security Findings

Retention and lifecycle management is the discipline of keeping logs and security findings long enough to have forensic and compliance value, then aging them into cheaper storage or deleting them on a defined schedule. It matters because detection is rarely immediate: breaches surface weeks or months later, and if the trail expired at 30 days there is no timeline, no root cause, and no impact analysis to work from. The balance is the whole game, keep too little and you are blind, keep everything forever and you drown in cost. The thing to hold onto: findings services (GuardDuty, Macie, Inspector, Security Hub) have short default retention and must be exported to durable storage before they age out, while log durability and tamper-resistance come from a centralized S3 bucket with Object Lock, versioning, and lifecycle transitions, backed by CloudTrail log-file validation.

## How it works

- **Findings have short defaults and must be exported.** GuardDuty, Macie, Inspector, and Security Hub retain findings only for roughly 30 to 90 days. The durable pattern is EventBridge on new findings triggering export to S3 (or a security data lake / SIEM) so evidence survives past the service's own window. Relying on default retention loses evidence.
- **Logs land in a centralized, immutable S3 bucket.** Send CloudTrail, VPC Flow Logs, S3 access logs, and Lambda logs to a dedicated logging bucket with versioning on, Object Lock in compliance mode (WORM), KMS encryption, and bucket policies plus SCPs that block delete and overwrite. This is what makes the logs tamper-proof and legally defensible.
- **Lifecycle rules tier the storage by age.** A typical S3 lifecycle moves objects Standard for the hot window, to Glacier for the mid term, to Glacier Deep Archive for long retention, then expires them at the regulatory boundary. This keeps forensic reach while controlling cost.
- **Integrity is proven, not assumed.** CloudTrail log-file integrity validation produces signed digests so you can prove logs were not altered, and hashing exports (sha256) gives the same assurance for finding archives. Versioning prevents silent overwrites.
- **Retention is mapped to both incidents and regulations.** Retention must outlive the incident lifecycle (detection, investigation, RCA, reporting, retrospective hunting), which argues for a 180-day floor on general logs and a year or more on security and audit logs, then reconciled against the framework requirements that apply.

## Retention targets by data type

| Data | Typical retention | Note |
|---|---|---|
| **CloudTrail** | 1 to 7 years, never under 90 days | Primary forensic source, enable log validation |
| **VPC Flow Logs** | 90 days to 1 year | Network activity for scoping lateral movement |
| **GuardDuty findings** | Export before ~90-day default | EventBridge to S3/SIEM |
| **Macie findings** | 30 to 90 days | Export for anything beyond triage |
| **App/debug logs** | Risk-based, expire faster | Downsample low-signal noise |

## Compliance retention anchors

| Framework | Retention driver |
|---|---|
| **PCI DSS** | 1 year, with about 3 months immediately available |
| **HIPAA** | 6 years for access logs |
| **SOX** | 7 years |
| **ISO 27001** | Organization-defined, must be documented |

## What gets tested

- **Findings must be exported, not left at default.** If a scenario needs findings retained for investigation or audit beyond the service default, the answer is an EventBridge-driven export to S3, Security Lake, or a SIEM, not "raise the retention setting," which those services do not really offer.
- **Object Lock for tamper-proof logs.** Preventing anyone, including privileged users, from deleting or altering logs before a retention period is S3 Object Lock in compliance mode, reinforced by SCPs. Governance mode allows override by authorized principals, compliance mode does not.
- **CloudTrail log-file validation for integrity.** Proving logs were not tampered with is log-file integrity validation (signed digests), which is a distinct control from encryption.
- **Lifecycle transitions for cost vs reach.** Standard to Glacier to Deep Archive with a final expiry is the expected pattern to hold long retention affordably. Deep Archive trades retrieval latency for cost.
- **Retention driven by the strictest applicable framework.** When multiple regimes apply, retention is set to the longest requirement for that data type (for example 7 years for SOX-scoped records).
- **CloudTrail is the forensic backbone.** For "who did what, when, from where," CloudTrail is the source, and it should never be set below 90 days.

## Limitations

- Findings services are not archives. Their short default retention means anything of lasting value has to be exported, and an export pipeline that silently fails leaves gaps you only notice during an investigation.
- Object Lock in compliance mode is deliberately irreversible for the locked window, so an over-long or misconfigured retention cannot be undone and can trap data and cost.
- Deep Archive tiers cut storage cost but add retrieval latency measured in hours, which can slow an active investigation if the only copy is deeply archived.
- Encryption protects confidentiality of logs but not their integrity or availability. Log-file validation and Object Lock are separate controls you must add.
- Long retention has a real bill and a privacy footprint. Keeping personal-data-bearing logs longer than required can itself become a compliance liability, so retention must be bounded, not just maximized.
- Access logging and SCPs guard the log store, but a gap in those controls (a principal able to delete the bucket or disable the trail) undermines everything downstream, so the logging account and its guardrails are themselves high-value targets.