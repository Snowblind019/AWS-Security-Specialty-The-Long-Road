# VPC Reachability Analyzer

Amazon VPC Reachability Analyzer is a static configuration analysis tool that tests whether one specific destination is reachable from one specific source, by reasoning over your network configuration rather than sending packets. When the path is reachable it shows the hop-by-hop route; when it is not, it names the exact component that blocks it. It is a debugging and verification tool for a single path, the point-to-point counterpart to Network Access Analyzer.

For infrastructure security its value is verifying connectivity intent without generating traffic. The thing to hold onto: because it analyzes config and sends nothing, you can confirm that a sensitive resource is not reachable from the internet gateway, or that app traffic is forced through the firewall, even when everything is locked down, and you get the precise blocking component for change validation.

## How it works

- **Define a path**: pick a source and a destination, and optionally a protocol (TCP or UDP), a destination port, and a source or destination IP. Supported endpoints include instances, network interfaces, internet gateways, transit gateways and their attachments, VPC endpoints and endpoint services, peering connections, and VPN gateways, plus a destination IP address inside or outside AWS.
- **Static analysis, no packets**: it examines security groups, NACLs, route tables, gateways, peering, transit gateways, VPC endpoints, and, more recently, Gateway Load Balancer, Network Firewall, and PrivateLink. Because it is config-based, you can diagnose even when traffic is fully blocked.
- **Result**: Reachable returns the ordered hop-by-hop path, and the shortest route when several exist. Not reachable names the exact blocking component (security group, NACL, route table, load balancer, or firewall rule) and the reason.
- **Scope**: within a VPC, or across VPCs joined by peering or Transit Gateway. Cross-account within an Organization must be explicitly enabled for cross-account analysis (shared via AWS RAM), otherwise it is single-account and single-Region, and cross-Region needs transit gateway inter-Region peering.
- **Automation**: verify connectivity intent as configuration changes by running analyses from the API after each change.

## VPC Reachability Analyzer vs sibling tools

| | Reachability Analyzer | Network Access Analyzer | VPC Flow Logs | ping / traceroute |
|---|---|---|---|---|
| Question | Can A reach B on this port, and what blocks it? | What paths match or violate my scope? | What traffic actually flowed? | Does live traffic get there now? |
| Approach | Static config, hop-by-hop | Static config, whole-network audit | Observed telemetry | Live packets |
| Sends packets? | No | No | Records real flows | Yes |
| Scope | One source-destination path | Many-to-many across the network | Per-ENI or hub | One live path |
| Best for | Debugging or verifying one connection | Exposure and segmentation auditing | Forensics and detection | Quick live check |

## What gets tested

- Reachability Analyzer is a static configuration analysis tool that tests reachability between one source and one destination, optionally on a protocol and port. It analyzes config and does not send packets, so you can diagnose even when traffic is fully blocked.
- Reachable returns the hop-by-hop path, and not reachable names the exact blocking component (security group, NACL, route table, load balancer, or firewall rule) and the reason.
- The distinction the exam tests: Reachability Analyzer is the point-to-point debug and verify tool (can A reach B on port X), while Network Access Analyzer is the broad scope audit (what can reach the internet, does anything bypass the firewall). One path versus whole-network posture.
- Supported endpoints include instances, ENIs, internet gateways, transit gateways and attachments, VPC endpoints and endpoint services, peering connections, and VPN gateways, plus a destination IP address. It now traces through Gateway Load Balancer, Network Firewall, and PrivateLink, so it can tell you whether a firewall rule is the blocker.
- Scope: within a VPC, or across VPCs joined by peering or Transit Gateway. Cross-account within an Organization must be explicitly enabled for cross-account analysis, otherwise it is single-account and single-Region.
- Security uses: verify connectivity intent after changes, confirm traffic is forced through inspection, and confirm a resource is not reachable from an internet gateway.

## Limitations

- Static configuration only, no live traffic. It confirms a path is possible, not that an application actually works, so it will not catch app-layer, DNS, or OS-firewall issues. VPC Flow Logs show what actually flowed.
- One path per analysis. For a whole-network exposure audit, use Network Access Analyzer.
- Cross-account and cross-Region analysis need explicit enablement (RAM), and cross-Region needs transit gateway inter-Region peering, otherwise you get NO_POSSIBLE_DESTINATION at the boundary.
- Per-analysis cost, so automated intent verification across many paths adds up.
- It reasons about network reachability, not identity or payload. It does not evaluate IAM, and it does not inspect content.
- It only analyzes shared resources it can fully describe as the calling principal.