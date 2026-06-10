# Athena

A serverless, pay-per-query SQL engine that reads data directly in S3 — no cluster, no ingestion pipeline. Built on Trino. For security work it is the query layer for log forensics: run ad-hoc SQL over logs that already live in S3 (CloudTrail, VPC Flow Logs, ELB/ALB/CloudFront/S3 access logs, GuardDuty exports) without moving them into a SIEM first.

This is a supporting/reference service, but it shows up in detection scenarios as the tool you reach for to interrogate logs. The thing to hold onto: you query the data where it lives, you pay per TB scanned, and the answer to almost every "Athena is slow or expensive" question is partitioning plus a columnar format.

## How it works

- You define a table (schema-on-read DDL) that maps S3 objects to columns, usually registered in the **Glue Data Catalog**. A Glue Crawler can infer the schema, and AWS publishes ready-made table definitions for CloudTrail and other log sources.
- Write standard SQL; Athena scans the matching S3 objects and returns results in seconds to minutes.
- Results are written to an S3 **query result location**, which can contain sensitive log data, so encrypt and restrict it.
- **Workgroups** separate teams and workloads, enforce per-query data-scan limits and cost controls, and can force encryption of query results.
- Cost is per TB scanned. Partitioning (by date/Region), columnar **Parquet**, and compression cut both cost and latency.

Example — bucket-policy change during an incident window:

```sql
SELECT eventtime, useridentity.username, requestparameters
FROM cloudtrail_logs
WHERE eventname = 'PutBucketPolicy'
  AND eventtime BETWEEN '2025-01-01T02:00:00Z' AND '2025-01-01T03:00:00Z'
```

## Athena vs other query options

| | Athena | OpenSearch | Redshift Spectrum | CloudTrail Lake |
|---|---|---|---|---|
| Infra | None | Cluster | Redshift cluster | None (managed) |
| Language | ANSI SQL | Lucene / DSL | SQL | SQL |
| Data | S3 | Indexed (+S3) | S3 external | Managed event store |
| Best for | Ad-hoc log forensics | Real-time dashboards / alerting | Warehouse joins | CloudTrail-specific queries |

## What gets tested

- Athena is the answer for ad-hoc SQL investigation of logs already in S3 with no infrastructure to stand up. CloudTrail, VPC Flow, and access-log forensics is the classic use.
- Cost is per TB scanned. "Athena is too slow or expensive" points to partitioning the data and converting it to Parquet.
- Query results land in an S3 location that may hold sensitive data; encrypt it (SSE-S3 or SSE-KMS) and lock down access. Workgroups can enforce result encryption.
- Access control is layered: IAM governs who can query and which workgroup, the S3 bucket policy governs the underlying data, and KMS governs encryption. Athena queries are themselves logged in CloudTrail.
- It needs a schema — Glue Data Catalog or a Crawler builds it. Not a turnkey "just search" tool like OpenSearch.
- Pick OpenSearch over Athena when the scenario needs real-time dashboards or alerting; pick CloudTrail Lake when it is CloudTrail-specific and you want managed retention without building tables.

## Limitations

- Not real-time and not a SIEM; no built-in alerting (integrate CloudWatch/EventBridge).
- Schema-on-read — you maintain the table definitions.
- Unoptimized queries scan, and bill for, far more data than needed.
- Latency grows with scan size.