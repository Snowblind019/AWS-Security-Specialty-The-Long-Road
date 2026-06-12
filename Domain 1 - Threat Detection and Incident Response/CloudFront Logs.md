# CloudFront Logs

CloudFront records every request hitting your distribution at the edge, including requests served from cache that never reach your origin. Two flavors: standard access logs (batch, to S3) for forensics and compliance, and real-time logs (streamed to Kinesis within seconds, field-selectable and sampled) for live detection.

The distinction that matters: standard logs are the complete, authoritative archive but arrive in batches; real-time logs are fast but sampled and limited to a chosen field subset. And the reason CloudFront logs matter beyond the ALB's own logs: cache hits are answered at the edge and never touch the origin, so they only appear here.

## How it works

- **Standard access logs** — every request, full field set, per distribution. Delivered to S3 (and in the newer standard-logging model, also to CloudWatch Logs or Data Firehose, with field selection and formats like Parquet). Batch delivery, so expect delay.
- **Real-time logs** — streamed to **Kinesis Data Streams** within seconds. You pick a field subset (up to ~24 of 40+) and a sampling rate (e.g. 100% or 10%). Built for SIEM, alerting, and automated response. More expensive.
- Useful fields: `c-ip`, `cs-method` / `cs-uri`, `sc-status`, `x-edge-location`, `x-edge-result-type` (cache Hit/Miss/Error), `ssl-protocol`, `cs(User-Agent)`, `x-forwarded-for`.
- Encrypt at rest (SSE-S3 or KMS); query the archived logs with Athena (partition for cost); route to OpenSearch or Security Lake via Firehose.

## Standard vs real-time

| | Standard access logs | Real-time logs |
|---|---|---|
| Destination | S3 / CloudWatch / Firehose | Kinesis Data Streams |
| Latency | Batch (minutes+) | Seconds |
| Completeness | Every request, all fields | Sampled, chosen fields |
| Best for | Forensics, compliance archive | Live detection, alerting |
| Cost | Storage only | Per-record, higher |

## What gets tested

- Cache hits are served at the edge and never reach the origin, so ALB/origin logs miss them. Only CloudFront logs (or the associated WAF) capture edge-served traffic. If a question needs visibility into requests that didn't hit the backend, that is CloudFront logs.
- Standard logs are authoritative, complete, and batch. Real-time logs are fast but sampled and field-limited. Pick real-time for live alerting, standard for the forensic record.
- WAF is associated with the CloudFront distribution; WAF logs show which requests matched or were blocked by rule, while CloudFront logs show all requests. Correlate the two.
- The `ssl-protocol` field surfaces weak or outdated TLS at the edge.
- Encrypt logs at rest and lock down the S3 bucket; logs reveal URIs and client IPs.
- Real-time logs are not a complete record — do not rely on them as the audit archive.
- Athena over the S3 archive is the standard query path; partition and use a columnar format for cost.

## Limitations

- Standard logs are batch — not suitable for real-time response on their own.
- Real-time logs cost more, are sampled, carry a limited field set, and need a Kinesis pipeline.
- No request or response bodies.
- Client IP appears as `c-ip`; behind additional proxies you rely on `x-forwarded-for`.