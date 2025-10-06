# AWS Elastic Disaster Recovery (DRS)

## What Is It

**AWS Elastic Disaster Recovery (DRS)** is a fully-managed **Disaster Recovery as a Service (DRaaS)** that replicates your on-premises or cloud-based servers (whether physical or virtual) into AWS. The goal is to provide minimal downtime and data loss in the event of disaster — whether it’s ransomware, hardware failure, natural disaster, or user error.

It’s the next-gen replacement for **CloudEndure**.

This service enables you to recover full systems into EC2 in **minutes** with up-to-date replicas, tested failovers, and ongoing monitoring.

---

## Why It Matters for Security

DRS is essential for **business continuity** and **ransomware resilience**. It allows:

- Rapid restoration of critical workloads without waiting on cold backups  
- Secure, immutable failover environments in AWS  
- Regular testing of DR runbooks without production impact  
- Automated protection of network, disk, and OS config  
- Encrypted, deduplicated, compressed transfer + storage  

Instead of "backup and pray", you have **live replication** and **instant launch capacity**, giving security teams a fallback that actually works.

---

## Cybersecurity Analogy

Think of **Elastic DRS** like a **bunker clone** of your entire infrastructure, constantly syncing data block-by-block, waiting to spring into action.  
If ransomware wipes out the original — the bunker clone is ready, clean, and bootable.

## Real-World Use Case

Let’s say Snowy’s org has a **mission-critical billing system** running on-prem in a data center in Seattle. They install DRS agents, replicate to AWS Oregon (`us-west-2`), and configure recovery templates.

- A regional outage or ransomware attack hits  
- RDS and S3 are fine (native AWS), but billing app is down  
- Snowy clicks **“Launch Recovery Instance”**  
- EC2 boots within minutes, with same IPs and app config  
- DNS/Route 53 points users to the DR instance  
- **Business resumes before customers even notice**

---

## How It Works

**Install Agent**  

- You install the AWS DRS agent on each source machine — whether it’s a VMware VM, physical server, Hyper-V, or cloud VM.

**Continuous Block-Level Replication**  

- The agent continuously replicates the disk blocks to a staging area in AWS (low-cost EBS volumes + EC2 instance).  
- This doesn’t require app downtime or snapshots.

**Failover to EC2**  
When disaster hits (or for testing), you click **“Launch Recovery Instance”** — and AWS spins up an EC2 instance with the same:

- OS, disks, and config  
- Network settings (VPC, IPs, etc.)  
- IAM roles, tags, metadata

**Failback (Optional)**  

- After disaster ends, you can replicate the EC2 instance back to the original location.

---

## Key Concepts

| **Term**                | **Description**                                                           |
|--------------------------|---------------------------------------------------------------------------|
| Staging Area            | Low-cost holding zone in AWS for block-level replicas                     |
| Recovery Instance       | An EC2 instance launched from the replicated server                       |
| Recovery Launch Template| Blueprint used to launch EC2 with custom instance type, security groups   |
| Point-in-Time Recovery  | Choose recent sync point for recovery (like RPO snapshot)                 |
| RPO (Recovery Point Objective) | Time between last sync and failure (often seconds–minutes)       |
| RTO (Recovery Time Objective) | Time to get the system running again (minutes)                    |

---

## Security Considerations

| **Concern**           | **How DRS Addresses It**                                |
|------------------------|----------------------------------------------------------|
| Data in transit        | Encrypted using TLS                                     |
| Data at rest           | EBS volumes encrypted via KMS                           |
| Ransomware fallback    | You can roll back to known-good replica                 |
| Testing DR plans       | Fully isolated test launches with zero prod impact      |
| IAM control            | Recovery role permissions tightly scoped                |
| Audit trails           | All actions logged via CloudTrail                       |
| Least privilege        | DRS roles and templates follow IAM best practices       |

---

## Integration with Other AWS Services

| **AWS Service** | **Purpose**                                                      |
|------------------|------------------------------------------------------------------|
| CloudWatch       | Monitor replication status and instance health                  |
| CloudTrail       | Logs all failover actions, agent installs, template edits       |
| KMS              | Encrypts EBS volumes in staging and recovery                    |
| IAM              | Scoped access for DR administrators                             |
| Organizations    | Deploy DRS agents and DR plans across accounts                  |

---

## Pricing Model

You’re billed for:

- **Staging resources** (cheap EC2 + EBS volumes)  
- **Storage** (EBS used to replicate source disks)  
- **Data transfer** (replication data inbound is free; failback out of AWS is charged)  
- **Recovery instances** (standard EC2 pricing during failover or test)

> **Tip**: You only pay **full EC2 prices** during **actual failover** or **DR testing**. Otherwise, staging area is low-cost.

---

## Final Thoughts

**Elastic Disaster Recovery** is your parachute, not just a screenshot of the cockpit.  
It’s what lets you say to leadership:  
> “We can lose our datacenter and still keep working.”

If your workload can’t afford **hours or days of outage**, and you need **security + speed** — **DRS is the AWS-native answer**.
