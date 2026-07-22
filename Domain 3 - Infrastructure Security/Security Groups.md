# Security Groups (SGs)

Security groups are stateful virtual firewalls attached at the **ENI** level, guarding EC2, RDS, Lambda-in-VPC, ECS tasks, and most other VPC resources. They are **allow-only** (no deny rules) and **deny-by-default**: nothing is permitted until an explicit allow rule matches. Being stateful, a permitted inbound connection has its return traffic automatically allowed out, regardless of outbound rules. The thing to hold onto: a security group is the per-resource allow-list that answers "who may reach this specific workload," and the exam's recurring point is that it can only allow (never deny), so any "block this CIDR" requirement is a NACL, while any "let only the app tier reach the DB" requirement is a security-group reference.

## How it works

- **Two rule sets.** Inbound and outbound, each rule specifying protocol, port or port range, and a source (inbound) or destination (outbound). IPv4 and IPv6 rules are separate and counted separately.
- **Source/destination can be a security group.** Referencing another SG (App SG allowed to reach DB SG) creates identity-based trust that follows instances as they scale, instead of brittle CIDR lists. **Managed prefix lists** collapse many CIDRs into one referenced object to save rule count.
- **Stateful.** Return traffic for an allowed flow is automatically permitted, so you rarely manage both directions the way NACLs require. Note connection-tracking nuance: some flows (for example certain ephemeral or long-idle connections) are tracked and can hit connection-tracking limits.
- **Additive across attached SGs.** An ENI can have multiple SGs and all their rules combine; the most permissive matching rule wins. Up to 5 SGs per ENI by default (raisable), bounded by a hard ceiling of about 1,000 combined rules per ENI, so raising SGs-per-ENI forces lowering rules-per-SG.
- **Default posture.** A new custom SG denies all inbound and allows all outbound; the default VPC SG also allows traffic from other resources in the same SG. Tighten egress deliberately.
- **Rule metadata.** Every rule has an ID and a description field (immutable audit note); use descriptions to record who requested a rule and why.

## Security group vs NACL

| | Security group | NACL |
|---|---|---|
| Scope | ENI / resource | Subnet |
| State | Stateful (return auto-allowed) | Stateless (both directions explicit) |
| Rules | Allow only | Allow and Deny |
| Evaluation | All rules, most-permissive | Numbered order, first match |
| References | CIDR, SG ID, prefix list | CIDR only |
| Default object | Deny inbound / allow outbound | Allows all |
| Best for | Per-resource allow-listing, tier trust | Subnet-wide deny, block a CIDR |

## What gets tested

- **SGs cannot deny.** The single most tested trait. "Block a specific malicious IP" or "explicitly deny a port" is a **NACL**, because a security group can only add allows. Removing an allow stops permitting traffic but is not a deny.
- **SG referencing for tier-to-tier trust.** "Only the app tier may reach the database," "only the ALB may reach the app" is solved by referencing the source SG, not hardcoding instance CIDRs. This adapts automatically as instances scale and is the least-privilege answer.
- **Never 0.0.0.0/0 on SSH/RDP.** Open 22 or 3389 to the world is the canonical finding (Config, Security Hub, GuardDuty). The fix is scoping to known ranges or, better, replacing SSH with SSM Session Manager.
- **Egress least privilege.** Wide-open outbound enables exfiltration (DNS tunneling, C2). Restrict egress to required destinations, using SG references and prefix lists, and use VPC endpoints so service traffic stays private.
- **SGs cannot filter the Route 53 Resolver.** Neither SGs nor NACLs can block DNS to the VPC+2 resolver; DNS-domain filtering is **Resolver DNS Firewall**. Watch this in "block malicious domain resolution" scenarios.
- **NAT gateway has no SG.** A NAT gateway is controlled by the subnet NACL, not a security group; do not answer "attach an SG to the NAT gateway."
- **Auto-remediation of drift.** SG changes are CloudTrail events, so an open-port change can trigger EventBridge to a Lambda that reverts it. This is the standard SG guardrail pattern, distinct from preventative controls.

## Limitations

- Allow-only means no explicit block. Anything requiring a deny (a bad CIDR, a compromised range across a subnet) needs a NACL or Network Firewall, not a security group.
- Rules are IP/port/protocol and SG-reference only. Security groups have no payload, domain, or L7 awareness, so application-layer filtering is WAF and domain filtering is DNS Firewall or Network Firewall.
- Cannot filter Route 53 Resolver DNS traffic; that requires DNS Firewall.
- Rule counts are bounded per ENI (about 1,000 combined), so sprawling CIDR lists do not scale; consolidate with SG references and prefix lists rather than raising limits indefinitely.
- Stateful connection tracking has capacity limits; very high connection volumes can exhaust tracking and cause dropped flows, a scaling consideration for busy instances.
- A security group only controls reachability to the resource. It does not stop lateral movement once a workload is compromised, nor does VPC Block Public Access or an SG substitute for host hardening and least-privilege IAM.