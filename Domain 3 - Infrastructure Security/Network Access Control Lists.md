# Network ACLs (NACLs)

A Network ACL is a subnet-level firewall in a VPC that evaluates traffic entering or leaving an entire subnet, before it reaches any instance's security group. NACLs are stateless: every packet is evaluated independently in both directions, with no memory of prior connections, so return traffic is not automatically allowed. They also support explicit DENY, which security groups cannot. The thing to hold onto: the NACL is the coarse, ordered, stateless perimeter around a subnet whose one superpower over security groups is the ability to DENY, so the exam reaches for a NACL exactly when the requirement is "block this CIDR/port across a whole subnet," and punishes you for forgetting the ephemeral-port return rule.

## How it works

- **Two ordered rule sets.** Separate inbound and outbound lists. Each rule has a number (1 to 32766, lowest first, first match wins), protocol, port range, a CIDR source (inbound) or destination (outbound), and ALLOW or DENY. CIDR only, no security-group references.
- **Default vs custom.** The **default NACL** allows all inbound and outbound. A **custom NACL** starts as deny-all in both directions; you must add explicit allow rules, in both directions, because it is stateless.
- **Stateless return traffic.** Allowing inbound 443 does not allow the response out. The reply leaves from the server on an **ephemeral port**, so you must allow the ephemeral range explicitly. Ranges depend on the responder: Linux 1024-65535, Windows Server 2008+ 49152-65535, and NAT gateway, ELB, and Lambda all use 1024-65535. In practice open 1024-65535 for return traffic and layer targeted DENY rules for known-bad ports.
- **Association.** A subnet has exactly one NACL at a time, but one NACL can be attached to many subnets. Replacing the association removes the old one.
- **Evaluation with security groups.** Both layers are checked independently. A packet must pass the NACL (subnet) and the ENI's security group. Either layer denying drops it, which is what makes NACL + SG a defense-in-depth pair.
- **Logging.** NACLs have no native per-rule logging; use **VPC Flow Logs** to see allowed and denied flows.

## NACL vs security group

| | NACL | Security group |
|---|---|---|
| Scope | Subnet | ENI / resource |
| State | Stateless (both directions explicit) | Stateful (return auto-allowed) |
| Rules | Allow and Deny | Allow only |
| Evaluation | Numbered order, first match wins | All rules, most-permissive |
| References | CIDR only | CIDR or SG ID |
| Default object | Allows all | Denies all inbound |
| Best for | Subnet-wide deny, block a CIDR/port, tier isolation | Precise per-resource allow-listing |

## What gets tested

- **DENY is the NACL's job.** Security groups cannot deny. "Block this specific malicious CIDR" or "block port X across the whole subnet regardless of instance" is a NACL DENY rule. This is the single most common reason a scenario's answer is NACL over SG.
- **Stateless ephemeral-port trap.** "Requests are accepted but responses are dropped" means the outbound (or inbound, for instance-initiated traffic) ephemeral range 1024-65535 is missing. Recognize the stateless symptom instantly.
- **Rule order matters.** Lowest number wins, so a low-numbered DENY overrides a higher-numbered ALLOW. A misordered rule silently blocks or permits traffic; verify numbering.
- **One NACL per subnet, reusable across subnets.** Know the association cardinality; a subnet cannot carry two NACLs.
- **NACL cannot filter the Route 53 Resolver.** NACLs (and SGs) can't block DNS to/from the VPC+2 resolver address. To filter DNS, use **Route 53 Resolver DNS Firewall**, not a NACL rule.
- **NAT gateway uses NACLs, not SGs.** A NAT gateway has no security group, so subnet-level control for it is the NACL. Scenarios about restricting NAT traffic point at the NACL.
- **Automated response fit.** Because a NACL can DENY a whole CIDR at the subnet edge, it is the natural target for GuardDuty-to-EventBridge-to-Lambda auto-remediation that blocks a scanning source, distinct from an SG which could only stop allowing it.

## Limitations

- Stateless design makes NACLs error-prone: every allow needs a matching return rule, and a single missing ephemeral rule blackholes traffic with no per-rule log to say why.
- CIDR-only matching means no security-group references and no identity awareness, so NACLs cannot express "allow from this SG" the way security groups can. They are coarse by design.
- There is a per-NACL rule quota (default 20 inbound and 20 outbound, adjustable to a hard ceiling), so long deny-lists of individual CIDRs do not scale; aggregate ranges or use Network Firewall for large or L7 filtering.
- No stateful inspection, no L7 awareness, no logging of its own. For application-layer filtering, deep inspection, or managed threat feeds, the answer is AWS Network Firewall or WAF, not a NACL.
- NACLs cannot filter Route 53 Resolver DNS traffic; DNS-layer filtering requires DNS Firewall.
- Ordered first-match evaluation means changes are easy to get wrong under pressure; a low-numbered rule added for one purpose can shadow existing allows across the whole subnet.