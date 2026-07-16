# Transit Gateway Flow Logs

A feature of AWS Transit Gateway that captures metadata about the IP traffic going to and from your transit gateway and publishes it to CloudWatch Logs, Amazon S3, or Amazon Data Firehose. It is the VPC Flow Logs idea moved up to the hub: instead of instrumenting every ENI in every VPC, you get one flow record for traffic crossing the transit gateway, the router that ties your VPCs, accounts, and hybrid links (VPN and Direct Connect) together. Collection happens outside the data path, so it adds no throughput or latency cost.

For security work this is your centralized network-visibility source in a hub-and-spoke design. The thing to hold onto: TGW Flow Logs are the hub-level flow record, one place to see traffic crossing every attachment, at metadata granularity, delivered to S3, CloudWatch, or Firehose, and they observe but never block. Enforcement lives elsewhere (route tables, appliance-mode inspection); the flow log only tells you what happened.

## How it works

- **What it captures**: one record per network flow transiting the gateway, with source and destination address, ports, protocol, packet and byte counts, start and end times, and TCP flags. It captures only transit-gateway traffic; for traffic to and from ENIs inside a VPC you still use VPC Flow Logs.
- **TGW-specific fields**: richer than VPC Flow Logs. resource_type (Transit Gateway or attachment), tgw_id, tgw_attachment_id, the src and dst VPC, account, subnet, ENI, and AZ, tgw_pair_attachment_id, flow_direction (ingress or egress), and pkt_src_aws_service / pkt_dst_aws_service.
- **Drop-reason fields**: packets_lost_no_route, packets_lost_blackhole, packets_lost_mtu_exceeded, and packets_lost_ttl_expired. These are the security and troubleshooting gold: they turn a routing gap or a blackholed exfil attempt into something you can query for.
- **Record format**: default format includes all available fields, or use a custom format to select only the fields you want. Select all fields if you plan to query broadly in Athena.
- **Destinations**: CloudWatch Logs (view and alarm), S3 (forensics and long retention, ideally Parquet with Hive-compatible partitioning for cheap Athena scans), or Firehose (near-real-time stream to a SIEM or lake).
- **Delivery timing**: on the S3 path, records aggregate into files at roughly 5-minute intervals with a 75 MB file cap, so it is near-real-time at best, not live.
- **Encryption and access**: encrypt the destination. On S3 with SSE-KMS, an AWS managed key cannot do cross-account delivery; cross-account requires a customer managed key with the flow-logs delivery principal granted in the KMS key policy.
- **Analysis**: Athena, QuickSight, CloudWatch Contributor Insights, or a partner SIEM.

## Transit Gateway Flow Logs vs sibling network logs

| | TGW Flow Logs | VPC Flow Logs | Network Firewall logs | Route 53 Resolver query logs |
|---|---|---|---|---|
| Vantage point | The transit gateway hub | ENIs inside a VPC | The firewall endpoint | The Resolver (DNS) |
| Captures | Flow metadata across attachments, plus drop reasons | Flow metadata to and from ENIs | Allowed / denied flows, alerts, TLS SNI | DNS queries and responses |
| Enforces? | No, visibility only | No, visibility only | Yes, it blocks | No (DNS Firewall blocks separately) |
| Best for | Central cross-VPC, cross-account, hybrid visibility | Per-VPC traffic detail | Deep inspection and blocking | DNS-based detection and exfil |

## What gets tested

- TGW Flow Logs capture IP flow metadata for traffic transiting the transit gateway and publish to S3, CloudWatch Logs, or Firehose, collected off the data path with no latency impact.
- The distinction to know: TGW Flow Logs give the hub and cross-attachment view, VPC Flow Logs give the ENI-level view inside a VPC. For centralized visibility across many VPCs, accounts, and hybrid links joined by a transit gateway, TGW Flow Logs beat instrumenting every VPC.
- The TGW-only drop-reason fields (blackhole, no_route, mtu_exceeded, ttl_expired) plus flow_direction and pkt_src/dst_aws_service are the fields that make the log useful for spotting routing problems, dropped exfil, and lateral movement across attachments.
- Metadata only, no packet contents. For payload or DNS you add Network Firewall logs or Route 53 Resolver query logs.
- Cross-account S3 delivery with SSE-KMS requires a customer managed key, not an AWS managed key.
- Firehose is the near-real-time path into a SIEM or lake. S3 plus Athena is the ad-hoc forensics path, and Parquet plus partitioning keeps those scans cheap, the same lever as in the Athena notes.
- Trap: GuardDuty does not natively consume TGW Flow Logs. Its network source is VPC Flow Logs (plus DNS query logs and CloudTrail). Enabling TGW Flow Logs does not feed GuardDuty.

## Limitations

- Metadata only, no packet contents. Not a substitute for deep packet inspection (Network Firewall) or DNS logging.
- Multicast traffic is not supported, and Connect attachments are not supported; Connect flows show up under the transport attachment instead.
- Records can be skipped on rare occasions under capacity constraints or errors, so the logs are not authoritative for exact billing. Use the Cost and Usage Report for chargeback.
- Visibility, not enforcement. A transit gateway has no security groups. Segmentation is done with route tables and appliance-mode inspection through a security VPC; the flow log only reports the result.
- Not live on the S3 path (roughly 5-minute aggregation, 75 MB file cap). Use Firehose when you need near-real-time.