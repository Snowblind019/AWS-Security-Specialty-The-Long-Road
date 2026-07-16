# Network Access Analyzer

Amazon VPC Network Access Analyzer identifies unintended network access to your resources. You describe what access should or should not exist as a Network Access Scope, and it analyzes your entire network configuration to find every path that violates it. It is an audit tool, not a debugging tool: it answers questions like what in my VPC can be reached from the internet, and does any path to the internet bypass the firewall.

For infrastructure security this is the prove-the-network-is-segmented-and-not-exposed tool. The thing to hold onto: it evaluates the whole path together, the internet gateway, route tables, NACLs, public IPs, and security groups, so it flags only resources that are truly reachable, and each finding is the exact hop-by-hop path that creates the access. That is the difference from eyeballing security groups, which cannot tell you whether an open rule is actually reachable.

## How it works

- **Network Access Scopes**: the input. A scope defines sources, destinations, and packet details (protocol, ports) with MatchPaths (the paths you care about) and ExcludePaths (legitimate exceptions). A finding is a path that matches and is not excluded. Use Amazon-managed built-in scopes or write custom ones.
- **Whole-path evaluation**: to decide whether something is internet-reachable, it evaluates the internet gateway, VPC route tables, network ACLs, public IPs on ENIs, and security groups together. If any component blocks the path, there is no finding, which keeps results high fidelity.
- **Findings**: each shows the full hop-by-hop path, for example Internet Gateway to Network ACL to Security Group (port 3306 open to all) to RDS network interface, naming the exact resource and rule at every hop so remediation is targeted.
- **Uses**: verify segmentation (prod isolated from dev), confirm all egress traverses inspection, find internet-exposed resources, and generate compliance evidence. It can run across an Organization for org-wide exposure reports.
- **Static analysis**: it reasons over configuration, not live traffic, so it tells you what is possible. VPC Flow Logs tell you what actually flowed.

## Network Access Analyzer vs sibling tools

| | Network Access Analyzer | Reachability Analyzer | VPC Flow Logs | Config / Security Hub rules |
|---|---|---|---|---|
| Question | What paths match or violate my scope? | Can A reach B on this port? | What traffic actually flowed? | Is this resource misconfigured? |
| Approach | Static, whole-network path analysis | Static, point-to-point path | Observed telemetry | Config-state rules |
| Live traffic? | No | No | Yes, records real flows | No |
| Best for | Segmentation and exposure auditing | Debugging one connection | Forensics and detection | Per-resource compliance checks |

## What gets tested

- Network Access Analyzer identifies unintended network access. You define Network Access Scopes (source, destination, protocol and ports) with MatchPaths and ExcludePaths, and findings are the paths that match and are not excluded. Use built-in scopes or custom ones.
- The distinction that gets tested: Network Access Analyzer is the broad audit (what can reach the internet, does anything bypass the firewall, are prod and dev isolated), while Reachability Analyzer is the point-to-point test (can A reach B on port X). One is a posture audit, the other is a single-path debug.
- It is static and evaluates the whole path (internet gateway, route tables, NACLs, public IPs on ENIs, security groups), so it flags only truly reachable resources. An open security group on an instance with no route to an internet gateway produces no finding, which keeps results high fidelity.
- Findings show the full hop-by-hop path with the exact resource and rule at each hop.
- Common uses: verify segmentation, confirm all egress traverses the firewall, find internet-exposed resources, and produce compliance evidence. It can run org-wide across multiple accounts.
- It analyzes configuration, not observed traffic. VPC Flow Logs are what tell you what actually flowed.

## Limitations

- Static configuration analysis, not live traffic. It tells you what is possible, not what happened, so pair it with VPC Flow Logs for observed activity.
- Point-in-time. Run it on a schedule or after changes, because a new security group or route can open a path between runs.
- Custom scopes take care. A poorly defined scope misses real exposure or floods you with noise, so start from built-in scopes and exclude known-good paths.
- It answers network reachability, not identity. It does not evaluate IAM or resource policies (that is IAM Access Analyzer), and it does not inspect payloads.
- Per-analysis cost, and org-wide multi-account analysis needs automation to orchestrate and aggregate the findings.