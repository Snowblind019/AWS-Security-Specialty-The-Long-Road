# Amazon Route 53

Amazon Route 53 is AWS's highly available DNS service, doing three jobs: authoritative DNS resolution (hosted zones and records), endpoint health checks with traffic routing, and domain registration. It sits at the front door of everything you expose, so a misconfiguration or a hijack makes what is behind it unreachable, impersonated, or exposed, regardless of how well IAM and encryption are done. The thing to hold onto: for the exam Route 53 is a security control surface, not just name resolution, and the graded distinctions are DNSSEC (protects response integrity), DNS Firewall (blocks what a VPC can resolve), Resolver query logging (visibility into DNS-based exfiltration), and private hosted zones (keeps internal names off the public internet).

## How it works

- **Hosted zones and records.** A hosted zone is a namespace (`example.com`) holding record sets (A, AAAA, CNAME, alias, MX, TXT, CAA, etc.). Alias records point at AWS resources (ALB, CloudFront, S3 website, API Gateway), work at the zone apex, and are free for AWS targets.
- **Routing policies.** Simple, weighted, latency-based, failover, geolocation, geoproximity (with bias), multivalue answer, and IP-based. Failover and multivalue tie into health checks to keep traffic on healthy endpoints.
- **Health checks.** HTTP/HTTPS/TCP endpoint monitoring, calculated and CloudWatch-metric checks. On failure Route 53 stops returning the endpoint and can drive failover routing; also feeds Shield Advanced health-based detection.
- **DNSSEC signing.** Cryptographically signs responses so a resolver can detect spoofed/man-in-the-middle answers. Route 53 manages the Zone Signing Key automatically; you manage the Key Signing Key via a **KMS key in us-east-1** with the `ECC_NIST_P256` spec, then publish a **DS record** at the registrar to complete the chain of trust. Watch `DNSSECInternalFailure` and `DNSSECKeySigningKeysNeedingAction` metrics, because a broken DS/KSK chain fails resolution.
- **Resolver.** The VPC+2 resolver (`169.254.169.253`) answers in-VPC queries. **Inbound endpoints** let on-prem resolve into AWS; **outbound endpoints** plus resolver rules forward VPC queries to on-prem or filter them.
- **Private hosted zones.** Resolve internal names (`db.internal.example.local`) only from associated VPCs, keeping internal records off public DNS.
- **DNS Firewall.** Resolver rule groups that allow, block, or alert on domains (custom lists or AWS managed lists for malware, DGA, and DNS tunneling) for queries leaving your VPC. Findings go to Security Hub/EventBridge; actions appear in Resolver query logs.
- **Resolver query logging.** Logs unique VPC DNS queries and responses to CloudWatch, S3, or Kinesis (cache hits are not re-logged), the primary source for spotting DNS tunneling and exfiltration.
- **Registrar security.** As registrar, enable transfer lock, keep WHOIS/contact current, enable auto-renew, and manage the DS record, to prevent domain takeover and lapse.

## Route 53 security features by threat

| Threat | Route 53 control |
|---|---|
| Spoofed/forged DNS responses (MITM) | DNSSEC signing (+ DS at registrar) |
| Malicious domain resolution from a VPC | Resolver DNS Firewall (managed/custom lists) |
| DNS tunneling / TXT-record exfiltration | Resolver query logging + Athena, DNS Firewall DGA/tunneling lists |
| Internal names exposed publicly | Private hosted zones |
| Domain takeover / expiry | Registrar transfer lock, auto-renew, WHOIS hygiene |
| Endpoint compromise / outage | Health checks + failover routing |

## What gets tested

- **DNSSEC protects integrity, not confidentiality.** "Prevent attackers from returning forged DNS answers / DNS spoofing" is DNSSEC signing, and the exam-favorite details are the **KSK in KMS us-east-1** and the **DS record at the registrar**. DNSSEC does not encrypt queries.
- **DNS Firewall is not a NACL.** NACLs and security groups cannot filter DNS to the VPC resolver. "Block a VPC from resolving `*.malware.net`" or "stop DNS-based exfiltration by domain" is **Resolver DNS Firewall**, distinct from Network Firewall (traffic) and NACLs (IP/port).
- **Resolver query logging for DNS visibility.** Detecting tunneling, DGA domains, or TXT-record exfil means enabling Resolver query logs and querying them (Athena), often alongside GuardDuty. It logs unique queries, not cache hits.
- **Private hosted zone to hide internal names.** Internal-only resolution scoped to VPCs is a private hosted zone; a public zone for an internal service is the misconfiguration to flag.
- **Inbound vs outbound Resolver endpoints.** On-prem resolving AWS private names uses an **inbound** endpoint; VPC queries forwarded to on-prem or filtered use an **outbound** endpoint with resolver rules. Scenarios map direction to endpoint type.
- **Registrar-level takeover defense.** Preventing hijack via the registrar is transfer lock, contact/WHOIS hygiene, auto-renew, and DS management, separate from record-level DNS security.
- **Health-check failover for resilience.** Auto-routing away from an unhealthy or compromised endpoint is failover (or multivalue) routing backed by health checks, with no redeploy.

## Limitations

- DNSSEC signs but does not encrypt queries, and it only helps against DNSSEC-validating resolvers. A wrong enable/disable order (signing before the DS exists, or removing the KSK before the DS) breaks resolution for validating clients, so the KMS us-east-1 KSK and DS lifecycle must be handled carefully.
- DNS Firewall filters by domain for queries through the VPC resolver; it does not inspect packet payloads or non-DNS traffic. Deep or L7 filtering is Network Firewall/WAF.
- Resolver query logs record only unique, non-cached queries, so cached repeats and very short-TTL noise can distort exfiltration analysis.
- Private hosted zones resolve only from associated VPCs; hybrid on-prem resolution additionally needs inbound/outbound Resolver endpoints, which are not free.
- Route 53 routing improves availability and geographic accuracy but is not a DDoS control; volumetric protection is Shield, and application-layer filtering is WAF.
- Domain security depends on registrar hygiene. Even with DNSSEC and private zones, a lapsed registration, stale WHOIS, or missing transfer lock allows takeover that DNS-record controls cannot prevent.