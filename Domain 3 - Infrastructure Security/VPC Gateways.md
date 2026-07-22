# VPC Gateways

"VPC gateway" is a category, not one service: the entry and exit points that move traffic between a VPC and the internet, on-premises, other VPCs, or AWS services. Each type carries a different security implication, because gateways plus route tables decide what can reach in, what can reach out, and whether that path is private, encrypted, logged, and segmented. The thing to hold onto: gateways do not filter traffic themselves; the **route table** decides a subnet's fate (a `0.0.0.0/0` route to an IGW makes it public, to a NAT gateway makes it private egress-only), so most gateway exam traps are really routing and segmentation questions, and the sharpest distinctions are IGW vs NAT vs egress-only, and VGW vs TGW for transitive routing.

## How it works

- **Internet Gateway (IGW).** Bidirectional public internet path for a VPC. A subnet is "public" only when its route table sends `0.0.0.0/0` to the IGW and instances have public/Elastic IPs. One IGW per VPC. Accidentally routing a private subnet to the IGW exposes it.
- **NAT Gateway (NGW).** Lets private-subnet resources initiate outbound to the internet without being reachable inbound. It sits in a public subnet with an EIP; private route tables point `0.0.0.0/0` at the NAT gateway. Deploy one per AZ for HA. It has no security group (control it with subnet NACLs), and it is IPv4 only.
- **Egress-Only Internet Gateway (EOIGW).** The IPv6 equivalent of a NAT gateway: outbound-only for **IPv6**. It is not a NAT (no address translation) and does not work for IPv4, a common misconception.
- **Virtual Private Gateway (VGW).** The AWS-side terminator for a Site-to-Site **IPsec VPN** (or Direct Connect) to one VPC. Uses static or BGP routing. Transitive routing (site-to-site through AWS) works only with **BGP/dynamic routing** (VPN CloudHub), not static, and a VGW attaches to a single VPC.
- **Transit Gateway (TGW).** A regional **hub-and-spoke** router connecting many VPCs, VPNs, and Direct Connect. Supports transitive routing, inter-Region peering, and **multiple route tables with associations and propagations** to segment traffic (production vs non-production, or an inspection domain). Shareable cross-account with **RAM**. Traffic stays on the AWS backbone.
- **Route tables tie it together.** Gateways only carry traffic that routing sends them, so subnet route tables, propagations, and TGW route-table segmentation are where control actually lives.

## Gateway selection

| Need | Gateway |
|---|---|
| Public inbound + outbound (IPv4) | Internet Gateway |
| Private subnet outbound only (IPv4) | NAT Gateway |
| Private subnet outbound only (IPv6) | Egress-Only IGW |
| On-prem VPN to a single VPC | Virtual Private Gateway |
| Many VPCs + VPN/DX, segmented, transitive | Transit Gateway |
| Two VPCs, simple, non-transitive | VPC Peering |
| Private AWS-service access | VPC Endpoint (gateway/interface) |

## What gets tested

- **Route table decides public vs private.** The difference between a public and private subnet is which gateway `0.0.0.0/0` points to (IGW vs NAT), not the subnet name. "Private instances are internet-reachable" is a route pointing at the IGW.
- **NAT vs egress-only IGW by IP version.** IPv4 private egress is a NAT gateway; IPv6 private egress is an egress-only IGW. Using a NAT gateway for IPv6, or an EOIGW for IPv4, is wrong.
- **VGW vs TGW transitive routing.** A single-VPC IPsec VPN terminates on a **VGW**. Connecting many VPCs with transitive routing, segmentation, and central inspection is a **TGW**. VGW site-to-site transit needs BGP (CloudHub); static does not transit.
- **TGW segmentation prevents lateral movement.** A flat TGW route table lets one compromised VPC reach all others. The control is separate TGW route tables per domain with scoped associations/propagations. "Isolate prod from dev over the shared hub" is TGW route-table segmentation.
- **VPC peering is not transitive.** If A peers B and B peers C, A cannot reach C. Full-mesh peering scales poorly; that is the reason to move to a TGW hub. Watch scenarios that assume transit over peering.
- **NAT gateway has no security group.** You cannot attach an SG to a NAT gateway or IGW; subnet-level control there is the NACL. Traffic can still leak through a misrouted table regardless of instance SGs.
- **VPC Block Public Access.** To centrally guarantee subnets cannot reach the internet regardless of route tables, VPC Block Public Access (account/Region, with exclusions) is the org-wide guardrail, stronger than auditing individual route tables.
- **Visibility.** VPC Flow Logs (and TGW Flow Logs) plus CloudTrail are how you watch ingress via IGW and egress via NAT; `PacketDropCountBlackhole` on a TGW flags routes with no destination.

## Limitations

- Gateways do not inspect or filter. They move traffic; enforcement is route tables, NACLs, security groups, and (for inspection) Network Firewall or a GWLB appliance. A misconfigured route bypasses every instance-level control.
- One IGW per VPC and a VGW attaches to a single VPC; scaling connectivity across many VPCs is what TGW is for.
- NAT gateways are IPv4-only, per-AZ for HA, and charge per hour plus per-GB processed, so large egress volumes get expensive; they also have no SG.
- VGW site-to-site transitive routing requires BGP; static routing does not transit, and VGW does not provide VPC-to-VPC transit the way TGW does.
- VPC peering is non-transitive and full-mesh, so it does not scale and cannot centralize inspection or shared egress; that is a TGW pattern.
- TGW adds per-attachment and per-GB cost and, if left as a flat route table, becomes a lateral-movement highway; segmentation is a deliberate design step, not a default.