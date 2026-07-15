# Amazon OpenSearch Service

A managed search-and-analytics engine (an open-source fork of Elasticsearch and Kibana) used as the log-analytics and SIEM-style layer in AWS. You stream logs in, they land in time-based indexes, and you search, correlate, visualize, and alert on them in near real time. In the security exam this is the Detection-domain destination where CloudTrail, VPC Flow Logs, GuardDuty findings, and application logs get indexed for threat hunting and post-incident forensics.

The one-line role: OpenSearch is the interactive search / correlate / visualize layer over your log estate. That is its lane: not durable cheap storage (S3), not ad-hoc SQL over S3 with no infrastructure (Athena), not native queries over recent CloudWatch log groups (CloudWatch Logs Insights). Pick it when you need a live, filterable console with dashboards, monitors, and cross-source correlation.

## How it works

- **Cluster model**: a managed *domain* of data nodes plus dedicated master nodes, with data held in time-based indexes (shards and replicas). AWS handles patching and scaling. **UltraWarm** and **cold storage** tiers hold older data cheaply; **Index State Management (ISM)** rolls over and deletes aged indexes to control cost.
- **Ingestion paths**: see the table below. The modern native path is **OpenSearch Ingestion** (a managed Data Prepper pipeline); **Kinesis Data Firehose** has a native OpenSearch destination; **CloudWatch Logs** flows in via subscription filters.
- **Query and visualize**: **OpenSearch Dashboards** (the Kibana fork) for charts and filters, with Lucene, DQL, or the SQL plugin. Correlate chains like `AssumeRole` then `s3:GetObject` then KMS `Decrypt` across sources to trace a compromised principal.
- **Monitors and anomaly detection**: query-based monitors and ML anomaly detectors fire to **SNS**, **Lambda**, or a webhook.
- **Security config (what the exam leans on)**: **encryption at rest (KMS)**, **in transit (TLS/HTTPS)**, and **node-to-node encryption**, which must be enabled at domain creation and cannot be added later. **Fine-grained access control (FGAC)** gives index / document / field-level RBAC backed by an internal user database or IAM, often federated through **Cognito or SAML** for Dashboards. FGAC requires encryption at rest, node-to-node encryption, and HTTPS enforcement all turned on. A resource-based **domain access policy** controls who can reach the endpoint, and a **VPC-hosted domain** keeps it off the public internet. Enabling FGAC also unlocks **audit logs**.

| Source | How logs reach OpenSearch |
|---|---|
| CloudWatch Logs | Subscription filter to Lambda, or to OpenSearch Ingestion |
| S3 (Flow Logs, ELB, access logs) | Kinesis Data Firehose (native destination) or OpenSearch Ingestion |
| EC2 / on-host logs | Fluent Bit, Filebeat, or Fluentd agents |
| Third-party / telemetry | HTTP API, OpenTelemetry, Data Prepper |

## OpenSearch vs Athena vs CloudWatch Logs Insights

| Feature | OpenSearch | Athena | CloudWatch Logs Insights |
|---|---|---|---|
| Best for | Real-time, visual, correlated analytics | Ad-hoc SQL over S3 | Querying recent CloudWatch log data |
| Query language | Lucene / DQL / SQL plugin | ANSI SQL | Logs Insights syntax |
| Visualization | Yes (Dashboards) | No | Basic charts only |
| Live alerting | Yes (monitors to SNS/Lambda) | No | Yes (metric filters and alarms) |
| Cost model | Running cluster (nodes + storage) | Pay per query (data scanned) | Pay per GB ingested and retained |
| Standing infra | Yes, always on | None (serverless) | None (native to CloudWatch) |

## What gets tested

- Verb match: search, correlate, and visualize logs in near real time with dashboards and alerting is OpenSearch. Ad-hoc SQL over S3 with no infrastructure is Athena. Querying recent CloudWatch log groups is Logs Insights.
- FGAC prerequisites are a classic trap: it will not turn on unless encryption at rest, node-to-node encryption, and HTTPS enforcement are all enabled. Node-to-node encryption is creation-time only, so retrofitting means a new domain (blue-green).
- Access control layers stack: the domain access policy governs endpoint reachability, IAM governs API actions, and FGAC governs index / document / field visibility. A VPC domain removes the public endpoint entirely.
- Ingestion answers: CloudWatch Logs via subscription filter, Firehose via native delivery, OpenSearch Ingestion as the managed Data Prepper pipeline. Do not confuse the delivery mechanism with the store.
- It is the centralized SIEM / threat-hunting destination that pairs with GuardDuty, CloudTrail, and VPC Flow Logs, and can be fed from Security Lake.
- Cost contrast drives the choice: a standing cluster (pay whether or not you query, plus dashboards and monitors) favors OpenSearch; sporadic investigations over data already in S3 favor Athena.

## Limitations

- A cluster you size and pay for continuously, even when idle. More operational overhead than serverless options. **OpenSearch Serverless** exists to shed the node management, at a different cost profile.
- Node-to-node encryption and some domain settings are set at creation only. Changing them requires a new domain.
- Not durable cheap storage. Keep raw logs in S3 and index a working set, then age indexes out with ISM plus UltraWarm and cold tiers.
- Detection and analysis, not prevention. Pair with the services that act on what it surfaces.