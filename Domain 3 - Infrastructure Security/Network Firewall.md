# AWS Network Firewall

AWS Network Firewall is a managed, stateful, scalable L3-L7 firewall you deploy inside a VPC to inspect and filter traffic that route tables steer through it. It does stateful connection tracking, deep packet inspection via a **Suricata**-compatible IDS/IPS engine, domain/FQDN filtering (HTTP Host and TLS SNI), IP/port/protocol filtering, optional TLS inspection, and central logging to CloudWatch, S3, or Kinesis. The thing to hold onto: Network Firewall is the VPC's managed IDS/IPS for north-south and east-west traffic, the control that inspects payloads and blocks domains/exfiltration where security groups and NACLs (which only see IP/port) cannot, and it only sees traffic that routing sends to its endpoint.

## How it works

- **Deployment.** A **firewall endpoint** lives in a dedicated firewall subnet per AZ. You edit VPC and IGW route tables to force traffic through that subnet (distributed, centralized-with-Transit-Gateway, or inspection-VPC patterns). Traffic that is not routed to the endpoint is never inspected.
- **Firewall, policy, rule groups.** The **firewall** binds to subnets; the **firewall policy** holds ordered stateless and stateful rule group references plus logging and default actions; **rule groups** are the reusable rule sets.
- **Stateless engine (runs first).** Examines each packet in isolation on the 5-tuple. Actions: `pass`, `drop`, or `aws:forward_to_sfe` (forward to the stateful engine). AWS best practice is to keep stateless rules minimal and set the stateless default to forward everything to the stateful engine, because stateless rules take precedence and can cause asymmetric-flow problems.
- **Stateful engine (Suricata).** Tracks connection state and inspects deeper. Three rule forms: **domain list** (allow/deny FQDNs via Host/SNI), **5-tuple**, and raw **Suricata** signatures. Suricata action order is `pass`, then `drop`, then `reject`, then `alert`, with optional priority, and strict-order mode lets you set a stateful default action. Supports the `geoip` keyword for country filtering.
- **Default behavior.** The stateful engine defaults to allow (like a permit-by-default posture), the opposite of a security group's default deny. You must add deny/alert rules or a strict default drop; leaving it open inspects nothing useful.
- **TLS inspection.** Optionally decrypts, inspects, and re-encrypts flows using a certificate (ACM), needed to see inside HTTPS for exfil detection. It adds latency and cost and is meant for high-risk egress paths, not inbound web traffic (WAF handles inbound).
- **Managed rule groups.** AWS-managed threat lists and an **active threat defense** group, plus Marketplace rule groups, so you are not hand-writing every signature.
- **Logging.** Alert and flow logs to CloudWatch/S3/Kinesis; findings can normalize into Security Hub, and Athena queries the S3 logs.

## Network Firewall vs the other network controls

| | Network Firewall | Security group | NACL | WAF | Gateway Load Balancer |
|---|---|---|---|---|---|
| Layer | L3-L7, stateful + DPI | L3/L4 stateful | L3/L4 stateless | L7 HTTP/S | Transparent bump-in-wire |
| Inspect payload / domains | Yes (Suricata, SNI/Host) | No | No | Yes (HTTP only) | Depends on appliance |
| Deny by domain / signature | Yes | No | No | Managed rules | Via third-party appliance |
| Scope | VPC traffic via routing | ENI | Subnet | CloudFront/ALB/API GW | Inserted appliance path |
| Best for | Egress control, IDS/IPS, east-west | Per-resource allow | Subnet-wide deny | App-layer web attacks | Inserting 3rd-party NGFW |

## What gets tested

- **Payload/domain filtering that SG and NACL cannot do.** "Block outbound to `*.badmalware.net`," "stop DNS-tunneling exfil," "detect a Cobalt Strike beacon," or "block egress by domain" all point to Network Firewall stateful rules, because SGs and NACLs only match IP/port.
- **Egress and east-west control.** Network Firewall is the answer for centralized outbound filtering and inter-VPC (east-west) inspection, typically in an inspection VPC behind a Transit Gateway. WAF and Shield are inbound/edge, not egress.
- **Network Firewall vs WAF.** WAF inspects inbound HTTP/S at CloudFront/ALB/API Gateway (SQLi, XSS). Network Firewall inspects arbitrary VPC traffic at L3-L7 including egress. "Filter inbound web app attacks" is WAF; "control what the VPC can talk out to" is Network Firewall.
- **Network Firewall vs Gateway Load Balancer.** GWLB inserts and scales third-party virtual appliances transparently. Network Firewall is AWS's own managed engine. When the requirement names a third-party/partner NGFW appliance, that is GWLB; when it is native managed inspection, that is Network Firewall.
- **Routing is mandatory.** The firewall only sees what route tables send it. A "traffic is bypassing the firewall" scenario is a route table not pointing at the firewall endpoint.
- **Stateful default is allow.** Unlike a security group, Network Firewall passes by default, so protection requires explicit deny/alert rules or a strict-order default drop.
- **Not a DDoS control.** Network Firewall filters and inspects but does not mitigate volumetric DDoS; that is Shield.

## Limitations

- Inspects only routed traffic. Misconfigured route tables silently bypass it, and asymmetric routing breaks stateful inspection.
- Stateful engine defaults to allow, so an unconfigured policy provides little protection; it is not deny-by-default like a security group.
- Stateless rules take precedence over stateful and can cause asymmetric-flow issues, which is why AWS recommends minimizing them and forwarding to the stateful engine.
- TLS inspection is required to see inside HTTPS but adds 5-20 ms latency and certificate/Private CA cost, so it is applied selectively to high-risk egress, not everywhere.
- It is not a DDoS mitigation and not a replacement for WAF on inbound web traffic; it complements Shield and WAF rather than replacing them.
- Cost scales with endpoint-hours per AZ plus data processed per GB, so high-volume deep inspection is expensive; reserve DPI for traffic that genuinely needs it.