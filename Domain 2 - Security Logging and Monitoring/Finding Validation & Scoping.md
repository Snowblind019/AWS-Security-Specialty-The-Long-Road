# AWS Elastic Disaster Recovery (DRS)

A managed Disaster-Recovery-as-a-Service that continuously replicates **whole servers** (physical, virtual, or cloud) at the **block level** into a low-cost staging area in AWS, then launches them as **EC2 instances** during a drill or a real disaster. It is the successor to **CloudEndure Disaster Recovery**. In the exam it is the low-RPO/RTO answer for recovering entire servers fast, and a common ransomware-recovery answer because you can launch from a point in time before the infection.

The one-line role: DRS does continuous, block-level, whole-server replication with recovery into EC2, giving **sub-second RPO and an RTO of minutes**. That is its lane: not point-in-time snapshot backup (AWS Backup), not traffic or routing failover (ARC and Route 53), not database-native replication (Aurora Global Database). Reach for DRS when you must bring entire servers back quickly with minimal data loss, whether on-premises into AWS or EC2 into another Region.

## How it works

- **Replicate**: install the **AWS Replication Agent** on each source (physical, VMware, Hyper-V, or cloud VM), or use the **agentless** option for VMware vCenter. It continuously replicates disk blocks to a **low-cost staging area** (lightweight replication servers plus cheap EBS), with no application downtime and no snapshots. Replication is **TLS in transit** and **KMS-encrypted EBS at rest**, and can run over private connectivity (VPN or Direct Connect).
- **Recover**: a **launch template** defines the recovery instance type, subnet, and security groups. On failover or a drill, DRS converts the latest replica (or a chosen **point-in-time** recovery point) and boots it as an EC2 instance in minutes.
- **Point-in-time recovery**: multiple retained recovery points let you launch from a clean point **before** a ransomware infection rather than replaying the compromise.
- **Drills**: launch isolated, non-disruptive test instances any time, with no production impact, to prove the runbook works.
- **Failback**: after the event, replicate the recovery instance back to the source location or original Region.
- **Scope**: on-premises, physical, and VM sources into AWS, and also **EC2 cross-Region or cross-AZ** DR.

## DRS vs the rest of the DR stack

| Service | Job |
|---|---|
| Elastic Disaster Recovery (DRS) | Continuous block-level whole-server replication, recover into EC2, sub-second RPO |
| AWS Backup | Scheduled point-in-time snapshots per resource, cross-Region and cross-account copy |
| ARC / Route 53 | Traffic and routing failover, not server replication |
| Aurora Global DB / DynamoDB global tables | Database-native cross-Region replication |

## What gets tested

- DRS is continuous block-level whole-server replication into EC2, with sub-second RPO and an RTO of minutes. If a question asks to recover entire servers quickly with minimal data loss, that is DRS. Per-resource point-in-time snapshots are AWS Backup, and routing failover is ARC or Route 53.
- It is the successor to CloudEndure Disaster Recovery, so a stem mentioning CloudEndure migration points here.
- Cost model is a favorite angle: the staging area is low-cost (lightweight servers and cheap EBS), and you pay full EC2 and EBS only during a drill or an actual failover. This makes DRS an inexpensive way to run pilot-light-style DR.
- Ransomware recovery uses point-in-time launch from a known-good recovery point before the infection, and drills are isolated with no production impact.
- Scope covers on-premises, physical, and virtual sources into AWS, plus EC2 cross-Region and cross-AZ. Replication is agent-based, with an agentless option for vCenter.
- Security properties: TLS in transit, KMS-encrypted EBS at rest, IAM-scoped recovery roles, CloudTrail-audited actions, and replication over private connectivity when required.

## Limitations

- Recovers into EC2 only. It is server-level DR, not for managed services, so use native replication for RDS, DynamoDB, and S3.
- Requires the replication agent (or agentless vCenter) and continuous replication, and the source must be a supported OS and platform.
- The staging area is cheap but not free, full EC2 and EBS costs apply during drills and failovers, and failback data leaving AWS is charged.
- It replicates whatever is on the disk, malware included, so a clean recovery depends on point-in-time recovery points, not the latest replica.
- Recovery, not prevention, and the DNS or traffic cutover is a separate concern handled by Route 53 or ARC.