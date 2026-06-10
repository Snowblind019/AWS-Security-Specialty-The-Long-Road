# CloudTrail Lake

A managed, immutable event data store that lets you run SQL queries over CloudTrail (and other) events without standing up your own S3 + Glue + Athena pipeline. Built for investigation and audit over long timeframes, not real-time detection.

The distinction that matters: plain CloudTrail drops JSON event files into S3, and querying them means wiring up Athena yourself. CloudTrail Lake ingests those same events into a structured, queryable store with retention measured in years, and you query it directly.

## How it works

- You create an **event data store (EDS)** and define what it ingests via event selectors: management events, data events, org-wide events, Config configuration items, or custom/non-AWS events.
- Events are ingested continuously and normalized into a fixed schema.
- You query the EDS with a SQL dialect, filtering on fields like `eventName`, `userIdentity.arn`, `sourceIPAddress`, and `eventTime`:

```sql
SELECT eventTime, eventName, userIdentity.arn, sourceIPAddress
FROM <event-data-store-id>
WHERE eventName = 'DeleteBucket'
  AND eventTime > timestamp '2025-01-01 00:00:00'
```

- Retention is configurable up to 7 years (a longer-retention tier extends further). Data is immutable once written.
- An EDS can be federated to Athena when you need to join Lake data against other tables.

## CloudTrail vs CloudTrail Lake

| | CloudTrail (to S3) | CloudTrail Lake |
|---|---|---|
| Storage | Your S3 bucket | Managed event data store |
| Querying | Set up Athena/ETL yourself | Native SQL, no setup |
| Retention | You manage via S3 lifecycle | Up to 7 years, built in |
| Mutability | Depends on your bucket controls | Immutable by design |
| Sources | AWS API events | AWS events + Config items + custom events |

## What gets tested

- Lake is for investigation, threat hunting, and audit, not real-time alerting. If a scenario wants immediate detection or notification, that points to GuardDuty / EventBridge / Security Hub, not Lake.
- Immutability makes it the right answer for forensic integrity / chain of custody and multi-year compliance retention.
- It can ingest non-AWS and custom events, so it fits when you need one queryable store spanning AWS and external sources.
- Org-level event data stores aggregate across all accounts in the organization.
- Encrypted at rest with KMS; access gated by IAM. Access to Lake is itself logged in CloudTrail.

## Limitations

- Not a SIEM. No built-in real-time correlation or alerting; integrate CloudWatch or Security Hub for that.
- Query language is constrained to the Lake schema, not arbitrary complex joins. Federate to Athena if you need more.
- Not on by default. You must create and configure the EDS.