# AWS Global Accelerator

AWS Global Accelerator is a global traffic-steering service that improves availability, performance, and failover for internet-facing applications by pulling user traffic onto the AWS backbone at the nearest edge instead of routing it over the public internet. It hands you static anycast IPs as a stable front door, then forwards over AWS fiber to the optimal healthy Regional endpoint. The thing to hold onto: Global Accelerator is a Layer 3/4 (TCP/UDP) routing layer, not a CDN and not a firewall. It does not cache, does not terminate TLS, and does not inspect payloads. Its security value is a fixed static-IP ingress, a Shield-protected edge, origin-IP hiding, and instant Region failover without DNS delay.

## How it works

- **Static anycast IPs.** You get two static IPv4 addresses (or bring your own with **BYOIP**), announced from every AWS edge via BGP anycast, so a user's connection enters the nearest PoP. Map a custom domain to them in Route 53. Standard accelerators also support **dual-stack** IPv4/IPv6.
- **Backbone routing.** From the edge, traffic crosses the AWS private global network to the endpoint, cutting latency variance, packet loss, and congestion versus the public internet. This is transport optimization, not encryption; Global Accelerator does not encrypt the payload.
- **Endpoint groups.** One group per Region, each holding endpoints (internet-facing ALB, NLB, EC2 with EIP, or Elastic IPs), with per-endpoint **traffic weights** and **health checks**.
- **Failover.** Continuous health checks reroute traffic to healthy endpoints in the same or another Region automatically, with no DNS TTL or propagation delay. Suits active-active and active-passive multi-Region designs.
- **Traffic dials.** Per-endpoint-group dial (0 to 100 percent) for maintenance drains, percentage-based canary rollouts, or instant DR cutover, again without DNS caching effects.
- **Client IP preservation.** For internet-facing ALB, NLB (with security groups), and EC2 endpoints, the backend sees the original client IP rather than the accelerator's, so backend security groups, WAF, and logs can act on the real source.
- **DDoS protection.** **Shield Standard** is automatic on the accelerator's static IPs. **Shield Advanced** adds resource-specific detection, DRT/SRT access, cost protection, and attack visibility for standard accelerators.
- **Accelerator types.** **Standard** accelerators route to the optimal endpoint; **custom routing** accelerators deterministically map ranges of ports to specific EC2 instances (VoIP, gaming, virtual desktops).
- **Observability.** Global Accelerator **Flow Logs** capture traffic records for the accelerator, feeding CloudWatch and SIEM analysis.

## Global Accelerator vs adjacent edge services

| | Global Accelerator | CloudFront | Route 53 |
|---|---|---|---|
| Layer | L3/L4 (TCP/UDP) | L7 (HTTP/S) | DNS |
| Caches content | No | Yes | No |
| Static ingress IPs | Yes (2, or BYOIP) | No (edge DNS names) | No |
| Failover mechanism | Health-checked, instant, no DNS wait | Origin failover | DNS with TTL delay |
| TLS termination | No (at backend) | Yes (at edge) | No |
| WAF attaches here | No (put on backend ALB/CloudFront) | Yes | No |
| Best for | Static-IP, low-latency TCP/UDP frontends, fast Region failover | Cacheable HTTP content, edge WAF/TLS | Name resolution and DNS routing policies |

## What gets tested

- **Not a CDN, not a DNS service.** "Cache content at the edge" is CloudFront; "resolve names / latency-based DNS" is Route 53. Global Accelerator is the answer only when the need is static IPs, non-HTTP (TCP/UDP) acceleration, or instant health-based Region failover without DNS TTL.
- **Static IPs for firewall allow-listing.** When partners must whitelist a fixed set of ingress IPs, or compliance requires stable entry points, Global Accelerator's two static anycast IPs (or BYOIP) are the answer; ALB/NLB IPs are dynamic.
- **WAF goes on the backend, not the accelerator.** Because Global Accelerator is L4, you cannot attach a WAF Web ACL to it. To inspect L7, put WAF on the internet-facing ALB behind the accelerator, or front the app with CloudFront. A "add SQLi/XSS filtering to my accelerated app" answer targets the ALB/CloudFront.
- **Shield tiers.** Shield Standard is automatic. Shield Advanced is the paid answer for large/sophisticated DDoS with DRT and cost protection, and Global Accelerator is one of its supported resource types alongside CloudFront, ELB, EC2/EIP, and Route 53.
- **Client IP preservation for backend controls.** When the backend must see and filter on the true client IP (SG rules, WAF, logging), enable client IP preservation; without it the backend sees the accelerator IP.
- **Instant failover vs DNS.** "Fail over between Regions without waiting for DNS TTL" is Global Accelerator's health-checked rerouting, distinct from Route 53 failover which is bounded by resolver caching.
- **Origin-IP obfuscation.** Because clients only ever see the static anycast IPs, backend endpoint IPs are not exposed to scanning or enumeration, a modest hardening benefit.

## Limitations

- No encryption and no payload inspection. Global Accelerator moves TCP/UDP over the backbone but does not add confidentiality; TLS must be terminated at the backend ALB/NLB, and treating "AWS backbone" as "encrypted" is the design error to avoid.
- No WAF attachment. L7 filtering requires a WAF on the backend ALB or CloudFront; the accelerator itself cannot do content inspection or rate-based application rules.
- Firewall Manager does not support Shield Advanced policies for standard accelerators (or Route 53 hosted zones), so multi-account Shield automation cannot cover Global Accelerator the way it covers ALB/CloudFront/EC2. Protection has to be applied directly.
- Not for bulk content delivery. It optimizes latency and resiliency for frontends, but for large media at scale CloudFront is more cost-effective; Global Accelerator adds a fixed hourly charge plus a data-transfer premium on top of backend costs.
- Two static IPs are a small, fixed ingress set. That is the point for allow-listing, but it also concentrates the entry point, so Shield and backend controls still matter.
- Health-based failover depends on well-configured health checks. Misconfigured checks either fail to drain an unhealthy Region or flap traffic, so the failover guarantee is only as good as the check definition.