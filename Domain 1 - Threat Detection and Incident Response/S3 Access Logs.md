# Amazon S3 Server Access Logs

A per-bucket logging feature that records detailed **data-plane** access requests to a bucket (who, what object, which operation, source IP, status, size, latency, user agent) and writes them as Apache-style text log files into a separate target bucket. It is off by default and enabled per bucket. In the exam it is one of two ways to capture S3 object-level access, the other being CloudTrail S3 data events, and the distinction between the two is the whole point of the topic.

The mental split is Server Access Logs vs CloudTrail S3 data events. Server access logs are free, best-effort, plain text, and carry extra request-detail fields. Data events are structured JSON, near real-time, reliable, filterable, and billed per event. Reach for data events when you need a trustworthy, integrable audit trail. Reach for server access logs when you want cheap, detailed request records and do not need guaranteed completeness.

## How it works

- **Enablement**: turned on per source bucket. You set a **target bucket** and an optional **prefix** to organize entries. Logging is not retroactive, it starts from the moment you enable it.
- **Target bucket rules**: must be in the **same AWS Region** and owned by the **same account** as the source bucket. Never point logging at the source bucket itself, that creates a recursive loop of logs about the logs.
- **Delivery permissions**: with ACLs disabled (**bucket owner enforced**, the default for new buckets), you grant delivery with a **bucket policy** to the **`logging.s3.amazonaws.com`** service principal. The legacy method, still seen on older buckets, grants the S3 **Log Delivery** group through a bucket ACL. This shift is a common modern-S3 exam theme.
- **Format and content**: plaintext, one request per line, batched and delivered over time. Security-relevant fields include `requester`, `remote_ip`, `operation`, `key`, `http_status`, `error_code`, `user_agent`, `bytes_sent`, `object_size`, and `turnaround_time`. It records **metadata only**, never object contents.
- **Best-effort delivery**: entries can be **delayed by hours** and are **occasionally incomplete**. This is the caveat that decides exam questions: do not rely on server access logs when completeness or integrity is required.
- **Querying**: use **Athena** over the log bucket, and enable **date-based partitioning** in the log object key format to cut scan cost. (CloudTrail Lake is closed to new customers as of May 31, 2026, so it is not the default query path anymore.)

## Server Access Logs vs CloudTrail S3 data events

| Dimension | S3 Server Access Logs | CloudTrail S3 data events |
|---|---|---|
| Plane | Data plane (object access) | Data plane (object access) |
| Format | Apache-style text | Structured JSON |
| Delivery | Best-effort, can be delayed hours, may be incomplete | Reliable, near real-time |
| Cost | Free (pay log storage only) | Per-event charge |
| Filtering | None at capture; filter later in Athena | Advanced event selectors (by prefix, operation) |
| Integrations | Athena, SIEM after the fact | EventBridge, CloudWatch, Security Lake, near-real-time automation |
| Extra fields | Turnaround time, total time, object size, referer, bytes sent | IAM identity context, richer request metadata |
| Enablement | Explicit, per bucket | Opt-in data events on a trail |

## What gets tested

- Two ways to log object-level access: server access logs (free, best-effort, text) vs CloudTrail data events (structured JSON, reliable, filterable, integrable, per-event cost). If the stem wants a dependable or tamper-evident audit trail or near-real-time automation, the answer is CloudTrail data events, not server access logs.
- Best-effort delivery is the trap. Server access logs can lag by hours and can miss records, so they are never the right answer when the requirement is a complete or guaranteed audit trail.
- They do carry fields CloudTrail lacks (turnaround time, total time, object size, referer), which makes them useful for access and performance analysis, not only security.
- Permission model: ACLs disabled means grant delivery via bucket policy to `logging.s3.amazonaws.com`. Legacy buckets use the Log Delivery group ACL. Target bucket is same account, same Region, and never the source bucket.
- Neither option records payload. Both are metadata only. Sensitive-content discovery in S3 is Macie, not access logs.
- Query with Athena over the log bucket, partitioned by date for cost. Recognize that CloudTrail Lake is no longer available to new customers.

## Limitations

- Best-effort, delayed, sometimes incomplete, and not retroactive. Not a guaranteed audit trail.
- Plain text requires parsing (Athena) rather than arriving query-ready like structured JSON.
- Target bucket is limited to the same account and same Region as the source.
- Metadata only. To know what sensitive data an object holds, pair with Macie.
- Volume grows fast on busy buckets. Use lifecycle rules to expire or tier old logs, and keep the log bucket's own access tightly scoped.