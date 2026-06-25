# Route 53 Resolver Query Logging

Opt-in logging of the DNS queries that resources in your VPC make through the Route 53 Resolver (the VPC's built-in DNS at 169.254.169.253 / VPC+2). It records the domain names your workloads resolve — the question, not the full answer. Destinations: CloudWatch Logs, S3, or Kinesis Data Firehose.

Where it gets confused: DNS query logging is the detection side of Route 53 Resolver; Route 53 Resolver DNS Firewall is the prevention side (block/allow by domain list). Query logging shows you the domains being resolved, which VPC Flow Logs (IPs and ports only) and CloudTrail (API calls only) cannot, making it the signal for C2 beaconing, DNS exfiltration, and lookups to malicious or newly registered domains.

## How it works

- Enable a **resolver query log configuration** and associate it with one or more **VPCs**. Off by default.
- Destinations: **CloudWatch Logs** (alerting/dashboards), **S3** (archive plus Athena threat hunting), or **Firehose** (stream to a SIEM).
- Each record includes `queryName`, `queryType` (A/AAAA/MX...), `rcode` (NOERROR/NXDOMAIN...), the source instance/IP, and the VPC. It captures the query and response code, not the full resolved answer or payload.
- This is distinct from **public hosted zone query logging**, which logs queries hitting your authoritative public zones (to CloudWatch Logs). The Resolver version is the one for VPC egress visibility.

## Resolver query logging vs neighbors

| Source | Shows |
|---|---|
| Resolver query logging | Domain names resolved from the VPC (detect) |
| Route 53 Resolver DNS Firewall | Blocks/allows resolution by domain list (prevent) |
| VPC Flow Logs | IP/port/protocol flows; no domain names |
| CloudTrail | API calls; not DNS resolution |

## What gets tested

- Resolver query logging is how you see the domain names workloads resolve — the answer for detecting C2/beaconing and DNS exfiltration that Flow Logs (IPs only) and CloudTrail (APIs only) miss. "Which log shows the domain queried" is this.
- Per-VPC, opt-in; destinations are CloudWatch Logs, S3, or Firehose.
- Query logging detects; DNS Firewall blocks. If the scenario wants to stop resolution of bad domains, that is DNS Firewall, not query logging.
- DNS exfiltration appears as long or encoded subdomains and high query volume in `queryName`.
- Workloads that use a custom or external DNS resolver bypass Route 53 Resolver and will not be logged.
- Pair the S3 destination with Athena for retroactive IOC hunting.

## Limitations

- Logs the query and response code, not the full answer or payload — intent, not content.
- Only captures queries that go through the Route 53 Resolver; external resolvers bypass it.
- Opt-in and off by default.
- The destination (CloudWatch/S3/Firehose) carries its own cost.