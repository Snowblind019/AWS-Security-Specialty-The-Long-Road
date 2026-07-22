# Amazon VPC

Amazon VPC is a logically isolated virtual network in AWS where you define IP ranges, subnets, routing, internet access points, and firewall layers. Every EC2, RDS, in-VPC Lambda, container task, and interface endpoint lives inside a VPC. It is not just addressing, it is the security perimeter and the segmentation layer: it decides what is public versus private, who can talk to whom, whether a resource reaches the internet, and how traffic flows across accounts and Regions. The thing to hold onto: the network is software-defined and open only where you route it, so VPC security is layered controls (route tables, security groups, NACLs, endpoints, flow logs) plus newer authoritative guardrails like VPC Block Public Access, and the exam tests both north-south exposure and east-west segmentation, not just the perimeter.

## How it works

- **CIDR and subnets.** A VPC owns an IP range (`10.0.0.0/16`); subnets carve it into zonal, tiered segments. A subnet is public only if its route table sends `0.0.0.0/0` to an internet gateway; otherwise it is private. Plan CIDRs to avoid overlap and exhaustion.
- **Routing.** Route tables decide a packet's fate (local, IGW, NAT, egress-only IGW, peering, TGW, endpoint). Routing, not naming, determines public versus private.
- **Layered firewalls.** **Security groups** are stateful, allow-only, at the ENI. **NACLs** are stateless, allow and deny, at the subnet. They stack for defense in depth; a packet must pass both.
- **Private service access.** Gateway endpoints (S3/DynamoDB) and interface endpoints (PrivateLink) reach AWS services without the internet, and bucket/endpoint policies can require the endpoint.
- **Connectivity.** VPC peering (1:1, non-transitive), Transit Gateway (hub-and-spoke, transitive, segmented route tables), Site-to-Site VPN (IPsec to on-prem), Direct Connect (private fiber, optional MACsec).
- **VPC Block Public Access (BPA).** An account/Region authoritative declarative control that blocks internet traffic through IGWs and egress-only IGWs regardless of route tables or security groups. Modes: **bidirectional** (block all internet) or **ingress-only** (allow NAT/EOIGW egress, block inbound), with per-VPC or per-subnet **exclusions** (max 50/account). Supersedes other settings and can be enforced org-wide via declarative policy; SGs and NACLs still apply to excluded resources.
- **Network Access Analyzer.** Evaluates actual network paths (across SGs, NACLs, route tables, peering, TGW, endpoints, ELB) to find unintended internet or cross-segment reachability, the impact-analysis tool before enabling BPA.
- **VPC Encryption Controls.** A per-VPC control that can monitor or enforce in-transit encryption, flagging `cleartext` flows (billed hourly since March 2026 after a free intro period).
- **VPC Flow Logs.** Capture accepted/rejected traffic metadata at VPC, subnet, or ENI level to CloudWatch, S3, or Kinesis, feeding GuardDuty and investigations.

## VPC security controls at a glance

| Control | Layer | Job |
|---|---|---|
| Route tables | Routing | Public vs private, path selection |
| Security groups | ENI, stateful | Per-resource allow-listing |
| NACLs | Subnet, stateless | Subnet-wide allow/deny, block CIDRs |
| VPC endpoints | Service access | Private AWS-service reach, no internet |
| VPC Block Public Access | Account/Region | Authoritative "no internet" guardrail |
| Network Access Analyzer | Analysis | Find unintended reachability paths |
| VPC Flow Logs | Observability | Traffic metadata for detection/audit |

## What gets tested

- **Public vs private is routing.** A subnet is public only because a route sends `0.0.0.0/0` to an IGW. "Private resources are internet-reachable" is a misrouted table, and the authoritative fix is **VPC Block Public Access**, not just editing each route table.
- **BPA as the org-wide guardrail.** To centrally guarantee no VPC can reach the internet regardless of local config, use VPC BPA (bidirectional or ingress-only) with narrow subnet exclusions, deployed via declarative policy across the org. This is stronger than auditing route tables and is the "prevent public exposure everywhere" answer.
- **East-west matters, not just north-south.** Segmentation between tiers and VPCs (private subnets, separate VPCs per environment, TGW route-table domains, SG-to-SG references) contains lateral movement after a breach. Flat networks are the finding.
- **SG vs NACL.** Per-resource allow-listing is a security group; subnet-wide deny or blocking a CIDR is a NACL. SGs cannot deny.
- **Private service access to stop exfil.** Reaching S3/DynamoDB/Secrets Manager without the internet is VPC endpoints, plus `aws:SourceVpce` on the bucket policy to prevent data leaving to the public internet.
- **Network Access Analyzer for reachability proof.** "Prove nothing unintended can reach the internet / this database" is Network Access Analyzer, which evaluates the combined effect of SGs, NACLs, routes, and peering rather than manual review.
- **Flow Logs for detection and audit.** Absence of Flow Logs means no network forensics; enable at subnet/ENI level and feed GuardDuty. This is the standard "we had no visibility into the traffic" remediation.

## Limitations

- The network is open where you route it. A single misconfigured route or `0.0.0.0/0` security-group rule can expose a resource regardless of other controls, which is why BPA exists as an authoritative override.
- Security groups cannot deny and NACLs are stateless and coarse; neither inspects payloads. Application-layer and domain filtering need WAF, Network Firewall, or DNS Firewall.
- VPC BPA blocks internet-gateway paths but SGs and NACLs still apply to excluded resources, and detaching the declarative policy rolls back to the prior state, so rollback must be planned. Exclusions are capped (50/account).
- Flow Logs, Network Access Analyzer runs, endpoints, NAT, TGW, and Encryption Controls all carry cost or effort and are opt-in; a VPC with none of them is a black box.
- Peering is non-transitive and full-mesh; scaling many VPCs or centralizing inspection/egress is a Transit Gateway pattern, not peering.
- VPC boundaries do not stop an attacker already inside. Segmentation, least-privilege SGs, endpoint policies, and monitoring are what limit blast radius past the first wall.