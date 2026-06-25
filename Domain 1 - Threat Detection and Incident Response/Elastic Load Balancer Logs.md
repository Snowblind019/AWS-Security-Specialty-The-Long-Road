# Elastic Load Balancer Logs

Access logs for the load balancers that front your apps: opt-in, delivered to S3 as gzip files in batches. The key thing for the exam is that the three load-balancer types log very differently, so "ELB logs" is not one thing. The ALB Access Logs note covers ALB in depth; this note is the cross-type picture and where each type leaves gaps.

What changes by type: ALB logs at Layer 7 (every HTTP request, with URL, status, TLS), NLB only logs TLS-listener connections at Layer 4 (no HTTP, and nothing at all for plain TCP/UDP), and Gateway Load Balancer has no access logs. Wherever a type does not log, the fallback is VPC Flow Logs.

## How it works

- Opt-in per load balancer; delivered to an **S3 bucket** (gzip), in batches roughly every 5 minutes. Not real-time.
- The S3 bucket policy must grant the ELB log-delivery principal (`logdelivery.elasticloadbalancing.amazonaws.com`, or the regional ELB account ID in older Regions) `PutObject`, or delivery fails silently.
- **ALB**: per-HTTP-request access logs (client, request line, `elb`/`target` status, processing times, `user_agent`, `ssl_protocol`/`ssl_cipher`). Connection logs are a separate ALB feature. See the ALB Access Logs note.
- **NLB**: access logs are generated **only for TLS listeners**, recording connection-level info (no HTTP). Plain TCP/UDP listeners produce no access logs.
- **GWLB**: no access logs; visibility comes from VPC Flow Logs or the inline appliance.

## Logging by load balancer type

| Type | Layer | Access logs cover |
|---|---|---|
| ALB | L7 | Every HTTP request (URL, method, status, TLS) |
| NLB | L4 | TLS-listener connections only; none for TCP/UDP |
| GWLB | L3 | None — use VPC Flow Logs / the appliance |

## What gets tested

- ALB access logs give HTTP-layer detail (URL, method, status). NLB access logs cover only TLS listeners at the connection level; there are none for plain TCP/UDP, so use VPC Flow Logs there. GWLB has no access logs at all.
- All ELB access logs are opt-in, batch to S3 (~5 min), gzip. The bucket policy must allow the log-delivery principal or delivery silently fails.
- For application-layer questions (which URL, which status) the answer is ALB access logs; for raw L3/L4 flow on NLB or GWLB it is VPC Flow Logs.
- The TLS `ssl_protocol` / `ssl_cipher` fields surface weak or downgraded TLS at the edge.
- Correlate with WAF logs (ALB), CloudTrail (control plane), and VPC Flow Logs (network).

## Limitations

- No request or response payloads.
- NLB logs only TLS-listener connections; nothing for TCP/UDP pass-through.
- GWLB produces no access logs.
- Batch delivery (~5 min), not real-time.
- Opt-in, and a misconfigured bucket policy fails silently.