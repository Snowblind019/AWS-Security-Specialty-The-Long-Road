# CloudWatch Logs Insights

A serverless, interactive query tool built into CloudWatch for analyzing logs that already live in CloudWatch Logs groups. It has a purpose-built query language (fields, filter, parse, stats, sort, limit), auto-discovered fields, and returns results in seconds with no setup. For security it is the fast first-pass investigation tool over CloudTrail, VPC Flow, Lambda, ECS, and API Gateway logs.

The fork that matters: Logs Insights queries logs in CloudWatch Logs (recent, subject to retention); Athena queries logs archived in S3 (historical, needs a schema). Reach for Logs Insights for fresh interactive investigation, Athena for long-term forensics. It is ad-hoc — a notepad for asking questions, not a continuous detector.

## How it works

- Queries one or more **log groups** with the Logs Insights language: `fields`, `filter`, `parse` (regex/delimiter extraction), `stats` (count/sum/avg/min/max), `sort`, `limit`, `display`.
- Auto-discovered fields like `@timestamp`, `@message`, `@logStream`; service logs (CloudTrail, VPC Flow) expose their own fields.
- Pay **per GB scanned**, so narrow the time window and filter early.
- Save queries, add results to dashboards, and query across accounts and Regions via CloudWatch cross-account observability.
- For ongoing detection, turn a pattern into a **metric filter + alarm**; Logs Insights itself is interactive, not a standing alert.

Example — console login failures:

```
fields @timestamp, userIdentity.arn, sourceIPAddress
| filter eventName = "ConsoleLogin" and responseElements.ConsoleLogin = "Failure"
| sort @timestamp desc
```

## Logs Insights vs Athena

| | Logs Insights | Athena |
|---|---|---|
| Data location | CloudWatch Logs | S3 |
| Language | Logs Insights query language | ANSI SQL |
| Setup | None | Table/schema (Glue) |
| Best for | Recent, near-real-time investigation | Historical / forensic archive |
| Cost | Per GB scanned | Per TB scanned |
| Integration | CW dashboards, metrics, alarms | Standalone |

## What gets tested

- Logs Insights queries logs that are in CloudWatch Logs, with no setup and near-real-time; Athena queries logs archived in S3. The decision hinges on where the logs live and how far back you need to look.
- CloudWatch Logs retention bounds how far back you can query. For long-term or historical analysis, export or subscribe logs to S3 and use Athena.
- Cost is per GB scanned — narrow time windows and put `filter` early.
- It is ad-hoc, not a continuous detector. For standing detection, convert the pattern to a metric filter and alarm, or drive it from EventBridge.
- Distinct from Contributor Insights, which ranks top-N contributors from a rule; Logs Insights runs arbitrary queries.
- Cross-account investigation uses CloudWatch cross-account observability or a centralized logging account.
- Access governed by IAM; query activity audited in CloudTrail.

## Limitations

- Only queries logs currently in CloudWatch Logs (bounded by retention); not a long-term store.
- Per-GB-scanned cost grows with window and log-group size.
- Custom query language, not SQL.
- Interactive by nature — no built-in continuous alerting; pair with metric filters or EventBridge.