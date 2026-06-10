# ALB Access Logs

Per-request, Layer 7 logs for an Application Load Balancer, written to S3. Each line records one HTTP/HTTPS request: client IP, the request line, ALB and target status codes, processing times, user-agent, and TLS protocol/cipher. Off by default.

For security work they answer "who hit which endpoint, when, with what result, and over what TLS" — application-layer visibility that VPC Flow Logs can't give you, since those stop at IP and port. They do not capture request bodies; for payload inspection or active blocking you need WAF.

## How it works

- Enabled per load balancer (EC2 → Load Balancers → Attributes → Access logs). You pick an S3 bucket and an optional prefix.
- The S3 bucket policy must grant the Elastic Load Balancing log-delivery principal (`logdelivery.elasticloadbalancing.amazonaws.com`, or the regional ELB account ID in older Regions) `PutObject`. If it does not, delivery fails silently.
- Logs are space-delimited, one line per request, gzip-compressed, delivered to S3 in batches roughly every 5 minutes — not real-time.
- The security-relevant fields per line: `client:port`, the full `request` line (method + URL), `elb_status_code` and `target_status_code`, the processing-time fields, `user_agent`, and `ssl_protocol` / `ssl_cipher` for HTTPS.
- Query with Athena (partition by date for performance); centralize via Security Lake, OpenSearch, or a third-party SIEM. EventBridge/Lambda can act on patterns, e.g. push offending IPs to a WAF blocklist.
- Connection logs are a separate ALB feature that records connection and TLS-handshake detail even for requests that never complete.

## ALB access logs vs neighbors

| Source | Layer | Best for |
|---|---|---|
| ALB access logs | L7 (HTTP) | Which URL/method/status/TLS per request |
| VPC Flow Logs | L3/L4 | IP/port/protocol flows; no URL or payload |
| WAF logs | L7 + rules | Which requests matched or were blocked, and by which rule |
| CloudTrail | API | Control-plane changes to the ALB itself |

## What gets tested

- Off by default; enable per ALB. "No record of requests to the ALB" means access logs were not enabled.
- Delivered to S3, not CloudWatch Logs, in ~5-minute gzip batches. Treat as near-real-time at best.
- A missing or wrong S3 bucket policy makes delivery fail silently; the log-delivery principal needs `PutObject`.
- ALB logs give application-layer detail (URL, method, user-agent) that VPC Flow Logs cannot. Pick them when the question needs to know what was requested, not just which IP connected.
- The `ssl_protocol` / `ssl_cipher` fields surface weak or downgraded TLS.
- No request or response bodies. If the scenario needs payload inspection or active blocking, that is WAF, not access logs.
- Common pairing: Athena for ad-hoc queries, Security Lake or OpenSearch for centralization, and GuardDuty findings correlated back to the requests a flagged IP made.

## Limitations

- No payloads, and no headers beyond the fixed schema; cannot see request/response bodies.
- Not real-time; S3 batch delivery every ~5 minutes.
- Silent failure if the bucket policy is misconfigured.
- ALB-specific. NLB and the legacy Classic Load Balancer have their own log formats.