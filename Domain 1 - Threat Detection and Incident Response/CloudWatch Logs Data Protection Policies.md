# CloudWatch Logs Data Protection Policies

A policy on a log group (or the whole account) that detects sensitive data in log events and masks it. It uses AWS-managed data identifiers (100+ patterns for PII, PHI, financial data, and credentials like AWS secret keys and private keys) plus your own custom regex identifiers. This is the "data masking" control for logs in Task 5.3.4.

The crux: masking here is a display/access control, not guaranteed redaction at rest. Detection happens at ingestion and matched values show as asterisks at every egress point — but a principal with the `logs:Unmask` IAM permission can retrieve the original unmasked values, which means the original is still stored. If the requirement is that sensitive data is never stored at all, this is not enough; the stronger answer is to not log it in the first place.

## How it works

- A data protection policy has two kinds of statements: **Audit** (find sensitive data and send findings to a destination — a CloudWatch Logs group, S3, or Firehose; only one audit statement allowed) and **Deidentify/mask** (replace matches with asterisks).
- **Data identifiers**: AWS-**managed** (100+, continuously updated; categories include credentials, financial, PHI, PII) and **custom** (your regex, up to 10 per policy). Prefer managed identifiers over reimplementing patterns yourself.
- Scope: **account-level** (all log groups, existing and future) or **log-group-level** (one policy per log group). If both exist they combine — the union of identifiers applies.
- Masking applies only to events ingested **after** the policy is set; pre-existing events stay unmasked.
- By default everyone sees asterisks; **`logs:Unmask`** lets a principal call GetLogEvents/FilterLogEvents (or the Logs Insights `unmask` command) to see the original. You can condition that permission, e.g. by source IP.
- The **`LogEventsWithFindings`** metric tells you which log groups are emitting sensitive data; alarm on it.

## Where it fits vs other masking/discovery

| Control | What it does |
|---|---|
| CloudWatch Logs data protection | Masks sensitive data in log events (display-time, `logs:Unmask` gated) |
| SNS message data protection | Same identifier engine for SNS message payloads (can audit, mask, or block delivery) |
| Macie | Discovers sensitive data at rest in S3 (detection, not log masking) |

## What gets tested

- It detects and masks sensitive data in CloudWatch Logs using managed plus custom data identifiers — the log-masking answer for Task 5.3.4.
- The crux: masking is enforced at egress and gated by `logs:Unmask`; the original data is still stored and recoverable by authorized principals. It is access control over display, not a guarantee the data was never written. "Never store the secret" means don't log it (or strip it upstream), not just mask it.
- Masking covers all egress points: console, GetLogEvents, Logs Insights, metric filters, subscription filters, and downstream consumers.
- Only events after policy creation are masked; retroactive data is not.
- Account-level policies cover future log groups automatically — the answer for org-wide enforcement.
- Use the audit statement with a findings destination (S3/Firehose/Logs) and the `LogEventsWithFindings` metric to discover which apps are leaking sensitive data.
- Pair with SNS message data protection for the messaging side; both are distinct from Macie (S3 discovery).

## Limitations

- Not redaction-at-rest by default — `logs:Unmask` reveals the original, so it is insufficient when data must never be retained.
- Only masks data ingested after the policy is in place.
- Custom identifiers limited to 10 per policy; policy size cap of 30,720 characters.
- Managed identifiers are pattern/ML based — possible false negatives; not a guarantee every secret is caught.
- Applies to CloudWatch Logs only; other log destinations need their own controls.