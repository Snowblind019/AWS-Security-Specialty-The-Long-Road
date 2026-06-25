# Kinesis Data Streams

A real-time streaming service that ingests high-volume data with millisecond latency and lets you build your own consumers. Data lives in shards and can be replayed within the retention window. For security it is the streaming backbone when you need custom real-time processing of telemetry, multiple independent consumers, replay, or per-shard ordering — as opposed to just landing logs in a destination.

The fork that matters: Data Streams gives you control (custom consumers, replay, ordering, ms latency); Firehose gives you a no-code managed pipe to a destination. If you just need logs in S3/OpenSearch/Splunk, that is Firehose; if you need to process the stream yourself or fan it out to several consumers with replay, that is Data Streams.

## How it works

- Capacity is in **shards**: ~1 MB/s or 1,000 records/s write and 2 MB/s read each. **On-demand mode** scales shards automatically.
- **Producers** push records (apps, agents, the KPL, AWS services); a **partition key** routes related records to the same shard for ordering.
- **Consumers**: Lambda, KCL apps on EC2, or Firehose. **Enhanced fan-out** gives each consumer a dedicated 2 MB/s-per-shard low-latency pipe so multiple consumers do not contend.
- **Retention**: 24 hours by default, extendable up to 365 days, enabling **replay** within the window.
- **Encryption**: KMS at rest, TLS in transit. CloudTrail logs the control-plane API actions.

## Kinesis Data Streams vs Firehose

| | Data Streams | Firehose |
|---|---|---|
| Role | Custom real-time processing | Managed delivery to a destination |
| Code | You write consumers (Lambda/KCL) | None |
| Latency | ~ms | ~60s+ (buffered) |
| Replay / ordering | Yes (within retention; per shard) | No |
| Use | Multiple consumers, custom logic | Land logs in S3/OpenSearch/SIEM |

## What gets tested

- Data Streams is the answer when you need custom real-time processing, multiple independent consumers, replay, or strict ordering. Firehose is the answer when you just need a managed pipe into a destination with no code.
- Retention is 24h by default, extendable up to 365 days, which is what enables replay.
- Ordering is per shard, controlled by the partition key — not global across the stream.
- Enhanced fan-out is how you give several consumers low-latency parallel reads without contending for the shard's 2 MB/s.
- Encrypt at rest with KMS and rely on TLS in transit; a Lambda consumer can mask or redact fields before forwarding.
- vs SQS/SNS: those are queue/pub-sub without replay or per-shard ordering; Kinesis is streaming with replay and ordering. vs MSK (Kafka): similar streaming model with more operational control.

## Limitations

- You build and operate the consumers — more effort than Firehose.
- Shard throughput is capped (1 MB/s write, 2 MB/s read) unless you scale shards or use on-demand.
- Ordering is per shard only, not global.
- Replay is bounded by the retention window.