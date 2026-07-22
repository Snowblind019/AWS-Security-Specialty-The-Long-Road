# Amazon CloudFront

Amazon CloudFront is AWS's content delivery network: a globally distributed cache that serves static and dynamic content from 600+ edge locations close to the viewer. For the exam it matters less as a performance tool and more as the internet-facing security perimeter. It terminates TLS at the edge, is the attachment point for AWS WAF and Shield, enforces geo-restrictions, hides origins behind Origin Access Control and VPC Origins, and produces the first access logs an incident touches. The thing to hold onto: CloudFront is the edge control plane, the layer where you authenticate viewers (signed URLs/cookies), authorize the origin (OAC/VPC Origins), inspect traffic (WAF), and absorb volumetric attacks (Shield), and questions test which of those four jobs the scenario is really asking for.

## How it works

- **Origins and OAC.** The origin is the source (S3, ALB, NLB, EC2, any custom HTTP endpoint). For an S3 origin, **Origin Access Control (OAC)** signs CloudFront-to-origin requests with SigV4 so the bucket can be locked to CloudFront only and stays private. OAC is now the sole option: OAI is legacy and, as of March 2026, cannot be attached to new distributions.
- **VPC Origins.** For compute origins (ALB, NLB, EC2) in private subnets, **VPC Origins** lets CloudFront reach them directly without any public IP, removing internet exposure at the origin entirely. For custom origins that must stay public, verify traffic with the CloudFront **managed prefix list** or a secret custom header so only CloudFront can reach them.
- **Distributions and behaviors.** A distribution holds routing, caching, logging, and security config. **Behaviors** are per-path rules choosing origin, cache policy, WAF association, allowed methods, header/query forwarding, and any **CloudFront Functions** (lightweight, viewer-event, sub-ms) or **Lambda@Edge** (heavier, all four events, full runtime) logic.
- **Viewer authentication.** **Signed URLs** (one file) and **signed cookies** (many files) grant time-limited, user-specific access to private content. Use **trusted key groups**, not the legacy account-wide trusted signers.
- **TLS.** Enforce HTTPS with a redirect or HTTPS-only viewer policy and a modern minimum-TLS security policy. The default `*.cloudfront.net` certificate pins the minimum to TLS 1.0; a custom ACM certificate (in **us-east-1** for CloudFront) is required to enforce TLS 1.2+.
- **WAF and Shield.** Attach a WAF Web ACL to the distribution for SQLi/XSS managed rules, rate-based rules, and bot control at the edge, before traffic reaches the origin. **Shield Standard** is automatic and free; **Shield Advanced** adds DRT support and cost protection.
- **Geo-restriction.** Allow or block by viewer country at the distribution level. For finer control use a WAF geo-match rule.
- **Field-level encryption.** Encrypt specific form fields (for example a card number) at the edge with a public key so even CloudFront edge nodes and downstream services never see plaintext; only the component holding the private key can decrypt.
- **Logging.** Standard access logs to S3 (every request), real-time logs to Kinesis Data Streams (near-instant to a SIEM), WAF logs via Firehose, Shield metrics to CloudWatch.

## CloudFront vs adjacent edge and origin-protection options

| Mechanism | Job | Use when |
|---|---|---|
| OAC | Lock an S3 origin to CloudFront only (SigV4) | Private S3 content, SSE-KMS objects, PUT/DELETE |
| VPC Origins | Reach ALB/NLB/EC2 in a private subnet with no public IP | Compute origin must not be internet-reachable |
| Managed prefix list / custom header | Restrict a public custom origin to CloudFront | Origin stays public but only CloudFront should hit it |
| Signed URLs / cookies | Time-limited, per-user viewer access | Paid or private content per viewer |
| WAF on CloudFront | L7 filtering (SQLi, XSS, bots, rate limit) | Application-layer attacks |
| Shield Advanced | Managed DDoS + DRT + cost protection | High-value internet-facing targets |
| API Gateway | Managed API front door with auth/throttle | API, not cacheable content delivery |

## What gets tested

- **OAC over OAI, always.** Any "restrict the S3 bucket to CloudFront" answer is OAC. OAI is the wrong/legacy choice, and specifically OAI cannot authenticate to **SSE-KMS** encrypted objects or support PUT/DELETE, which OAC does. Bucket policy still has to grant the CloudFront service principal.
- **Hide a compute origin.** "ALB/EC2 must not be reachable from the internet, only through CloudFront" is **VPC Origins** (private subnet) or, for a public origin, the managed prefix list plus a secret header. Not a security group rule alone, which does not identify CloudFront.
- **Signed URLs vs OAC.** These solve different problems and are a classic trap. OAC controls CloudFront-to-origin (keeps the bucket private). Signed URLs/cookies control viewer-to-CloudFront (who may request the object). A private-paid-content scenario usually needs both.
- **Where TLS and WAF live.** CloudFront terminates viewer TLS and is where the Web ACL attaches for edge filtering. WAF on CloudFront is global scope (deployed via us-east-1), distinct from a regional WAF on an ALB or API Gateway.
- **Field-level encryption vs TLS.** TLS protects data in transit to the edge; field-level encryption keeps a specific field encrypted through the edge and backend until a private-key holder decrypts it. When the requirement is "CloudFront and intermediate services must never see the plaintext field," it is field-level encryption, not TLS.
- **Custom certificate for modern TLS.** Enforcing TLS 1.2+ requires a custom ACM cert (us-east-1); the default CloudFront domain allows TLS 1.0. Watch for this in a "why is TLS 1.0 still accepted" question.
- **Trusted key groups.** The current mechanism for signed URLs/cookies is trusted key groups, not the root-account trusted-signer model.

## Limitations

- CloudFront and its ACM certificate are effectively global but anchored in **us-east-1**: the custom cert and the global WAF Web ACL must be created there, a common deployment gotcha.
- OAC/VPC Origins hide the origin from the internet but do not authenticate the *viewer*. Without signed URLs/cookies or WAF, anyone can still pull public objects through the distribution.
- Shield Standard covers network and transport (L3/L4) volumetric attacks only. Application-layer floods, scraping, and injection still require WAF and rate-based rules; Shield alone does not answer an L7 scenario.
- Cache invalidations propagate and are only free for the first 1,000 paths per month; rotating content by invalidation at scale has cost and latency. Versioned object names are the cheaper pattern.
- Field-level encryption covers a small number of specified fields, not whole payloads, and adds key-management overhead. It is not a substitute for encrypting the datastore.
- CloudFront does not currently support S3 Express One Zone (directory buckets) as a direct origin, and a same-name S3 origin moved to a new SigV4 Region can take up to an hour for OAC/OAI records to update.