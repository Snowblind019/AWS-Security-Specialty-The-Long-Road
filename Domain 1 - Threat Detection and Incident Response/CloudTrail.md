# CloudTrail

The authoritative record of who did what, when, and from where across your AWS accounts. It captures control-plane API activity (management events) by default and, when you opt in, data-plane access to specific resources (data events). Logs are tamper-resistant, delivered to S3, and can stream to CloudWatch Logs and EventBridge.

The core idea: CloudTrail answers "what API call happened and who made it." It is the evidence layer for audits and investigations, not a live monitoring tool, and not a record of resource state (that is Config).

## How it works

- **Event History** — every account has a rolling 90-day searchable history of management events in the console/API, with no trail required. For longer retention or for data events, you create a trail.
- **Trails** deliver events to an S3 bucket as JSON (optionally SSE-KMS encrypted). A trail can be single-account, organization-wide (covers all member accounts including future ones), and multi-Region.
- Optional targets: **CloudWatch Logs** for near-real-time alerting, **EventBridge** for routing events to automation.
- **Log file integrity validation** produces signed digest files so you can cryptographically prove logs were not altered — relevant for forensics and regulated audits.
- **Event selectors / advanced event selectors** control what gets captured (read vs write, specific buckets/prefixes, Lambda ARNs) to manage cost and noise.

### Event types

- **Management events** — control-plane actions (`RunInstances`, `PutBucketPolicy`, `AssumeRole`). On by default; splittable into read-only and write-only.
- **Data events** — high-volume object/record access (S3 `GetObject`/`PutObject`, Lambda `InvokeFunction`, DynamoDB item operations). Off by default for cost reasons; enable surgically on sensitive resources.
- **Insights events** — anomaly detection on management-event patterns (e.g. spikes in error rates or unusual write volume).

Each event records the identity (`userIdentity`, including assumed-role session context), source IP and user agent, request parameters, and result. That is enough to tie an action to a principal and a time.

## CloudTrail vs neighbors

| Service | Answers | Relationship |
|---|---|---|
| CloudTrail | What API call happened, by whom | The evidence / audit trail |
| Config | What the resource state was over time | CloudTrail = the call that changed it; Config = the resulting state |
| CloudWatch | What is happening or hurting now (metrics, alarms) | Live signal vs immutable history |
| GuardDuty | Whether activity is a threat | Consumes CloudTrail as a signal source |
| Detective | How an entity behaved across events | Uses CloudTrail as a major graph input |
| CloudTrail Lake | SQL queries over long-retention events | Managed query layer over the same events (see separate note) |

## What gets tested

- Event History is 90 days, management events only, no trail needed. If a scenario needs longer retention or data events, you need a trail to S3.
- Data events are off by default. "We couldn't see who read the object" almost always means S3 data events were not enabled.
- Global service events (IAM, STS, CloudFront) are recorded in us-east-1; a multi-Region trail prevents blind spots.
- Organization trails cannot be modified or disabled by member accounts — the right answer for centralized, tamper-resistant org-wide logging.
- Log file integrity validation (digest files) is the answer when the question is about proving logs were not tampered with, or chain of custody.
- Detecting trail tampering = alarm or EventBridge rule on `StopLogging`, `DeleteTrail`, `UpdateTrail`, or disabling the trail's KMS key.
- KMS encryption requires the key policy to allow the CloudTrail service principal; a misconfigured key policy is a common "logs stopped delivering" cause.
- S3 Object Lock (WORM) for immutable, regulated retention of trail files.

## Limitations

- Not real-time on its own; delivery to S3 has latency (typically a few minutes). Use CloudWatch Logs or EventBridge for faster reaction.
- Not a record of resource configuration or drift — that is Config.
- Data events get expensive and noisy quickly; scope them deliberately.
- Field-level log-format memorization is deprioritized in C03 (removed from Task 2.5). Focus on what events let you correlate, not every JSON field.