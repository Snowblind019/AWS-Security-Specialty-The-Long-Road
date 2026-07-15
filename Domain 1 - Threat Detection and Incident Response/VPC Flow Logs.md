# VPC Flow Logs

A feature that captures **Layer 3/4 metadata** about IP traffic going to and from network interfaces in your VPC: the 5-tuple (source and destination IP and port, protocol), packet and byte counts, a time window, and an **ACCEPT or REJECT** action. It records metadata, not packet contents. You enable it at the **VPC**, **subnet**, or **ENI** level and publish to **CloudWatch Logs**, **S3**, or **Kinesis Data Firehose**. In the exam it is the network-visibility and network-forensics answer, the record of who connected to whom over what port and whether it was allowed, and the tool for telling a security group problem apart from a NACL problem.

The mental model is metadata not packets, batched not real time. Flow logs answer "who talked to whom, on which port, allowed or denied," but never "what did they say." Deep packet inspection is VPC Traffic Mirroring, not this. And the single detail that trips people is `srcaddr` versus `pkt-srcaddr` once traffic passes through a NAT gateway, load balancer, or transit gateway.

## How it works

- **Levels**: VPC, subnet, or ENI. A subnet or VPC flow log covers every network interface inside it.
- **Traffic type filter**: capture **ACCEPT**, **REJECT**, or **ALL**.
- **Destinations**: **CloudWatch Logs** for Logs Insights queries and alarms, **S3** for cheap archival and Athena, **Kinesis Data Firehose** for streaming to a SIEM or OpenSearch. (Firehose is the third destination the older notes often omit.)
- **Timing**: the maximum aggregation interval is **10 minutes or 1 minute**, plus an additional publish delay, so it is **not real time**. On **Nitro-based instances the interval is always 1 minute or less** regardless of what you set.
- **Fields**: the default format gives version, account, interface-id, the 5-tuple, packets, bytes, start/end, action, and log-status. A **custom format** adds the fields that matter for investigation: `vpc-id`, `subnet-id`, `instance-id`, `tcp-flags`, `type`, `flow-direction`, `traffic-path`, `pkt-src-aws-service`/`pkt-dst-aws-service`, and crucially **`pkt-srcaddr`/`pkt-dstaddr`**.
- **`srcaddr` vs `pkt-srcaddr`**: `srcaddr`/`dstaddr` show the **immediate interface** address (the load balancer, the NAT gateway, or the ENI's primary private IP), while `pkt-srcaddr`/`pkt-dstaddr` show the **original packet** endpoints. To trace true source and destination through an intermediary, you must add the `pkt-*` fields.
- **Traffic that is NOT captured**: Amazon DNS server queries (traffic to your **own** DNS server is logged), Windows license activation, instance metadata at **169.254.169.254**, Amazon Time Sync at **169.254.169.123**, DHCP traffic, the reserved IP of the default VPC router, mirrored source traffic (you see the mirror target only), and traffic between an endpoint ENI and a Network Load Balancer ENI.
- **Immutability and scope**: after creation you **cannot change** a flow log's configuration or record format, you delete and recreate it. You cannot log a peered VPC unless the peer is in your account. `log-status` reports OK, NODATA, or SKIPDATA.

## Destination comparison

| Destination | Best for | Analysis tooling | Relative cost |
|---|---|---|---|
| CloudWatch Logs | Near-term monitoring, alarms | Logs Insights, metric filters, alarms | Higher per GB |
| S3 | Archival, bulk and forensic analysis | Athena (Parquet for cheap scans) | Lowest |
| Kinesis Data Firehose | Streaming out to a SIEM or OpenSearch | Downstream partner or AWS analytics | Delivery plus downstream |

## What gets tested

- Flow Logs capture network metadata (the 5-tuple plus ACCEPT/REJECT) at an interface, not packet contents. If a question needs actual payloads or packet capture, that is VPC Traffic Mirroring, not flow logs.
- Levels are VPC, subnet, and ENI, and a broader log covers every ENI inside.
- `srcaddr`/`dstaddr` show the immediate interface, `pkt-srcaddr`/`pkt-dstaddr` show the original endpoints. To find the true source or destination behind a NAT gateway, load balancer, or transit gateway you need the `pkt-*` fields from a custom format. This is a heavily tested distinction.
- Not real time. The aggregation interval (10 or 1 minute) plus a publish delay rules flow logs out whenever a scenario demands real-time telemetry. Nitro instances always aggregate at 1 minute or less.
- The not-captured list is a favorite trap. If a question asks why DNS, instance-metadata, Time Sync, or DHCP traffic is missing, this list is the answer. Traffic to a custom DNS server, by contrast, is logged.
- Diagnosing security group versus NACL: because security groups are stateful and NACLs are stateless, the ACCEPT/REJECT pattern distinguishes them. An allowed inbound flow with a blocked return points at a NACL missing the ephemeral-port rule, not the security group.
- Destinations map to needs: CloudWatch Logs for alarms and Logs Insights, S3 for Athena and cheap retention, Firehose for streaming to a SIEM.
- Configuration is immutable, so changing fields means deleting and recreating the flow log.

## Limitations

- Metadata only, at Layers 3 and 4. No payloads and no application-layer detail. Use Traffic Mirroring when you need packets.
- Not real time, because of the aggregation interval plus publish delay.
- Does not capture the excluded traffic listed above (DNS to Amazon, IMDS, Time Sync, DHCP, and the rest).
- Configuration cannot be edited after creation, and peered VPCs outside your account cannot be logged.
- Cost scales with traffic volume and the number of custom fields. For high-volume VPCs, S3 with Athena is far cheaper than CloudWatch Logs.
- A detection and forensic signal, not prevention. Pair with GuardDuty (which consumes flow logs), Athena, and threat-intel feeds to make them actionable.