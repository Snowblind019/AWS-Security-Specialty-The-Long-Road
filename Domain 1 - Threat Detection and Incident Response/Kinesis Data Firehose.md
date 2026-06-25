# Kinesis Data Firehose

A fully managed delivery stream that captures streaming data and lands it in destinations like S3, OpenSearch, Redshift, Splunk, and HTTP endpoints, with no consumers to write and no scaling to manage (now branded Amazon Data Firehose). For security it is the transport layer of the log pipeline: the standard way to move CloudWatch Logs, VPC Flow, CloudFront, and WAF telemetry into storage, indexing, or a SIEM.

This is a supporting/reference service, but it shows up constantly as the pipe in detection architectures. The key fork: Firehose is managed delivery (you do not write a consumer, ~60s+ latency, no replay); Kinesis Data Streams is for custom real-time processing (ms latency, replay, ordering). Its one security-relevant trick is the optional Lambda transform that can mask or redact data in transit before delivery.

## How it works

- **Destinations**: S3, OpenSearch, Redshift, Splunk, generic HTTP endpoints, and partner destinations.
- **Buffering**: batches by size or time (near-real-time, ~60s minimum); compresses (gzip/Snappy) and can convert to Parquet/ORC.
- **Transformation**: an optional **Lambda** transforms each record — mask PII/secrets, enrich, or reformat before delivery.
- **Reliability**: retries failed deliveries and backs up failed records to S3. **No ordering guarantee.**
- **Encryption**: SSE with **KMS** for data in the stream; destination encryption is configured separately.
- **Common sources**: a CloudWatch Logs subscription filter, VPC Flow Logs, CloudFront real-time logs, WAF logs, and custom apps via `PutRecord` / `PutRecordBatch`. Security Lake and many SIEM integrations use Firehose.

## Firehose vs Kinesis Data Streams

| | Firehose | Data Streams |
|---|---|---|
| Role | Managed delivery to a destination | Custom real-time processing |
| Code | None | You write consumers |
| Latency | ~60s+ (buffered) | ~ms |
| Replay / ordering | No | Yes (per shard) |
| Use | Land logs in S3/OpenSearch/SIEM | Multiple consumers, custom logic |

## What gets tested

- Firehose is the managed pipe for delivering streaming logs/telemetry to S3, OpenSearch, Redshift, Splunk, or an HTTP/SIEM endpoint — no consumer code, near-real-time. The "get these logs into a destination" answer.
- vs Kinesis Data Streams: if the scenario needs custom processing, multiple consumers, replay, or strict ordering, that is Data Streams; if it just needs to land data in a destination, Firehose.
- The optional Lambda transform can mask or redact sensitive fields in transit before delivery — a data-protection control in the pipeline.
- Encrypt the delivery stream with KMS; failed records back up to S3.
- Near-real-time only (buffering delay), and no ordering guarantee.
- Frequently the glue from a CloudWatch Logs subscription or service logs into OpenSearch, Security Lake, or a SIEM.

## Limitations

- Buffered near-real-time (~60s min), not sub-second.
- No ordering guarantee and no replay — single delivery to the destination.
- Delivery-only; no custom multi-consumer stream processing (use Data Streams).
- Transformation adds Lambda cost and latency.