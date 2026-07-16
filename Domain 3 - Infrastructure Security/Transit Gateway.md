# AWS Transit Gateway

AWS Transit Gateway (TGW) is a regional, fully managed network hub that connects your VPCs, on-premises networks (Site-to-Site VPN and Direct Connect gateway), and other transit gateways (peering) in a hub-and-spoke topology. It replaces the tangle of point-to-point VPC peering with one central router that scales to thousands of attachments and gives you transitive routing, which plain VPC peering cannot do.

For infrastructure security, TGW is the segmentation and centralized-inspection backbone of a multi-VPC, multi-account network. The thing to hold onto: TGW routes traffic, it does not filter it. Segmentation is done with route tables (who can reach whom), inspection is done by steering traffic through a firewall (an inspection VPC or a directly attached Network Firewall), and the TGW itself has no security groups. Get the route tables wrong and you silently connect environments that were meant to be isolated.

## How it works

- **Attachments**: VPC, Site-to-Site VPN, Direct Connect gateway, TGW peering (cross-Region and cross-account), Connect (GRE plus BGP for SD-WAN appliances), and network function attachments such as a directly attached Network Firewall.
- **Route tables, the segmentation control**: each attachment associates with exactly one TGW route table (what it can reach) and propagates its routes into one or more route tables (whose routes are advertised). The default route table gives a full mesh, so for real segmentation you disable default association and propagation and build a route table per routing domain to isolate prod from dev, or spokes from each other.
- **Static and blackhole routes**: add static routes to steer traffic, for example 0.0.0.0/0 to an inspection attachment, and blackhole routes to hard-block a CIDR.
- **Centralized inspection**: TGW does no inspection itself. Route traffic through a shared-services or inspection VPC running Network Firewall or a Gateway Load Balancer with third-party appliances, or attach Network Firewall directly to the TGW as a network function attachment, which provisions the endpoints for you and enables appliance mode automatically.
- **Appliance mode**: enable it on the appliance-mode VPC attachment so TGW pins a flow to a single appliance ENI and uses the same one for return traffic, keeping flow symmetry across Availability Zones. Without it, asymmetric routing can send forward and return traffic to different-AZ appliances and break stateful inspection. It needs route propagation enabled so TGW can see the source and destination AZs.
- **Security group referencing**: within a Region you can reference security groups in other VPCs attached to the TGW instead of IPs or CIDRs. It does not work across a Gateway Load Balancer or a Network Firewall inspection path.
- **Cross-account and cross-Region**: share the TGW across accounts with AWS RAM, usually from a central network account. Connect Regions with TGW peering, whose traffic is encrypted and stays on the AWS backbone.

## AWS Transit Gateway vs sibling options

| | Transit Gateway | VPC Peering | PrivateLink (VPC endpoints) | Transit VPC (legacy) |
|---|---|---|---|---|
| Topology | Hub and spoke | Point to point | Service to consumer | Hub via self-managed appliances |
| Transitive routing | Yes | No | N/A (single service) | Yes |
| Scale | Thousands of attachments | N-squared mesh | Per service | Limited by the appliance |
| Segmentation | Route tables, blackhole routes | All or nothing per pair | Exposes one service | Appliance config |
| Best for | Many VPCs, on-prem, central inspection | A few VPCs, simple | Privately expose or consume one service | Legacy, avoid |

## What gets tested

- TGW is the regional hub-and-spoke router connecting VPCs, VPN, Direct Connect, and other TGWs by peering. It gives transitive routing that VPC peering cannot.
- Segmentation is done with TGW route tables: association (the one route table an attachment uses, what it can reach) plus propagation (whose routes get advertised). Disable default association and propagation and build per-domain route tables to isolate prod from dev and spokes from each other. Blackhole routes hard-block a CIDR.
- TGW does not filter traffic and has no security groups. To inspect, route through an inspection VPC (Network Firewall or Gateway Load Balancer plus appliances) or attach Network Firewall directly to the TGW.
- Appliance mode keeps flow symmetry so stateful firewalls spread across AZs do not drop asymmetric return traffic. It requires route propagation to be enabled, and it is automatic when Network Firewall is attached directly.
- Security group referencing across VPCs works over the TGW within a Region, but not across a Gateway Load Balancer or Network Firewall inspection path.
- Cross-account: share the TGW via AWS RAM, typically from a central network account. Inter-Region peering traffic is encrypted on the AWS backbone. The inbound / firewall / outbound route-table pattern sends all traffic through inspection before it reaches the internet or other VPCs.
- Visibility comes from Transit Gateway Flow Logs, which record flows crossing the hub without affecting throughput.

## Limitations

- TGW routes, it does not filter. Security groups and NACLs stay in the VPCs, and deep inspection needs an appliance or Network Firewall.
- A misconfigured propagation can silently connect environments meant to be isolated. Verify routing after every change.
- It is a regional resource. Connecting Regions requires TGW peering.
- Data-processing charges apply per GB through the gateway, which adds up in a high-traffic hub.
- Security group referencing does not traverse a Gateway Load Balancer or Network Firewall inspection VPC.
- Appliance mode must be explicitly enabled (except with a directly attached Network Firewall, where it is automatic), or stateful inspection can break on asymmetric flows.