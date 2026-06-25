# Macie

A managed data security service that discovers and classifies sensitive data in S3 (PII, financial, health, credentials, secrets) and assesses S3 bucket posture (public access, encryption, cross-account sharing). It answers "where is our sensitive data, and is any of it exposed." S3-only.

The one-line role: Macie finds and classifies sensitive data in S3 and flags risky bucket posture. That is its lane — not threat detection (GuardDuty), not vulnerability scanning (Inspector), not config compliance (Config). Custom data identifiers get their own note; this is the service overview.

## How it works

- **Two discovery modes**:
  - **Automated Sensitive Data Discovery (ASDD)** — continuously samples objects across your S3 estate to surface where sensitive data tends to live. Low-effort, ongoing posture awareness.
  - **Classification jobs** — one-time or scheduled, scoped by bucket/prefix/tag/file-type/last-modified/size, billed per GB scanned. For audits, pre-sharing checks, and investigations.
- **What it detects**: managed data identifiers (common PII, national IDs, financial, health, secrets/keys) plus **custom data identifiers** (your regex + context — see the CDI note) and **allow lists** to mute known-benign matches.
- **Bucket posture** is assessed continuously without scanning contents: public access / Block Public Access state, default encryption/KMS, cross-account sharing, and policy risks. Cheap signal on "public + unencrypted" buckets.
- **Findings** come in two families: `SensitiveData:S3Object` (sensitive content found) and `Policy:S3Bucket*` (exposure/posture). Route to **Security Hub**, **EventBridge**, **SNS**, or **SSM Automation** for remediation.
- **Multi-account** via a delegated administrator / Organizations.

## Macie vs the rest of the stack

| Service | Job |
|---|---|
| Macie | Discovers/classifies sensitive data in S3; flags bucket exposure |
| GuardDuty | Detects active threats (incl. S3 threat activity with S3 Protection) |
| Inspector | Scans compute for CVEs |
| Config | Resource configuration compliance |
| Security Hub | Aggregates findings, posture scoring |

## What gets tested

- Macie is the "find/classify sensitive data (PII) in S3" answer. Match the verb against GuardDuty (threats), Inspector (vulns), Config (configuration), Security Hub (aggregation).
- S3-only — not RDS, DynamoDB, EBS, or CloudTrail. A sensitive-data-discovery question about another store is not Macie.
- Two modes: ASDD (continuous sampling, posture awareness) vs classification jobs (targeted, GB-scanned, for audits and pre-sharing). Pick jobs when you need a definitive scan of a specific scope.
- Bucket posture assessment flags public, unencrypted, or over-shared buckets without scanning contents.
- Findings drive remediation via EventBridge to SSM (block public access, quarantine the object, enforce encryption).
- Do not confuse Macie (sensitive-data classification) with GuardDuty S3 Protection (threat detection on S3 data events) or GuardDuty Malware Protection for S3 (malware scanning) — different jobs on the same store.

## Limitations

- S3-only.
- ASDD samples rather than scanning everything; jobs only cover the scope you set.
- Cost scales with data scanned (GB) for jobs.
- Detection and classification, not prevention — pair with remediation.