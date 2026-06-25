# Network Load Balancer Logs

Connection-level logs for a Network Load Balancer (Layer 4). They record TLS connection metadata: client and target IP/port, handshake times, and the negotiated TLS protocol, cipher, and ALPN — not HTTP. The one fact that drives everything: NLB access logs are generated only for TLS listeners.

The trap to internalize: an NLB only writes access logs for **TLS listeners**. If the NLB uses plain TCP or UDP listeners (no TLS termination), it produces no access logs at all, and your only network visibility is VPC Flow Logs. So "NLB logs" is conditional on TLS termination.

## How it works

- Off by default; enabled per NLB, delivered to an **S3 bucket** as gzip files. The bucket policy must allow the ELB log-delivery principal or delivery fails silently.
- **Only TLS listeners** generate entries. Each entry is connection/TLS-level: timestamp, listener, client and target IP:port, connection and handshake times, bytes, and the negotiated **TLS version, cipher, and ALPN** (e.g. HTTP/2, gRPC), plus the certificate ARN.
- No HTTP detail (no URL, method, status) — that is Layer 7, which is ALB.
- For TCP/UDP listeners or any non-TLS traffic, there are no access logs; use **VPC Flow Logs** for the IP/port/protocol flow.
- Query with Athena; route to Security Lake, OpenSearch, or a SIEM.

Example — top talkers:

```sql
SELECT client_ip, COUNT(*) AS connections
FROM nlb_logs
WHERE day = '2025-09-27'
GROUP BY client_ip
ORDER BY connections DESC
LIMIT 20;
```

## NLB access logs vs neighbors

| Source | Layer | Covers |
|---|---|---|
| NLB access logs | L4 (TLS) | TLS-listener connections only (cipher, ALPN, client/target) |
| VPC Flow Logs | L3/L4 | All IP/port/protocol flows; no TLS detail |
| ALB access logs | L7 | HTTP requests (URL, method, status) |

## What gets tested

- NLB access logs are generated only for TLS listeners. No TLS listener means no access logs — fall back to VPC Flow Logs for TCP/UDP visibility. This is the canonical NLB-logging trap.
- They are connection and TLS level (cipher, protocol, ALPN, client/target), not HTTP. URL/method/status is ALB territory.
- The TLS protocol/cipher fields surface weak or downgraded TLS (e.g. TLS 1.0/1.1) for compliance.
- Off by default, batch-delivered to S3 (gzip); the bucket policy must allow the log-delivery principal.
- For raw L3/L4 flow regardless of listener type, VPC Flow Logs are the source; NLB access logs add TLS detail on top, only where TLS is terminated.

## Limitations

- Only TLS listeners produce logs; plain TCP/UDP pass-through produces none.
- No application-layer (HTTP) detail and no payloads.
- Off by default; batch delivery to S3, not real-time.
- Silent failure if the bucket policy is misconfigured.