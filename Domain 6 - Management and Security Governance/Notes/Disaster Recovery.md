# Disaster Recovery (DR) in AWS

## What Is Disaster Recovery

**Disaster Recovery (DR)** is the set of strategies, tools, and practices used to **restore systems and data after a major failure**, such as:

- Hardware failure  
- Natural disaster  
- Data corruption  
- Human error  
- Ransomware or malicious breach  
- Regional AWS outage  

In AWS, **DR is not just backup**. It’s a **whole-systems strategy** involving:

- Cross-region replication  
- Immutable backups  
- Infrastructure-as-Code (IaC) redeployment  
- Orchestration tools (CloudFormation, AWS Backup, custom scripts)  
- TLS encryption + KMS key sharing  
- Security and compliance restoration  

> **Why it matters:**  
> It’s not about *if* you’ll fail — it’s about **how fast you recover and how much you lose**.

---

## Cybersecurity Analogy

Think of DR like a **fire evacuation plan for your house**:

- **Backups** are the fire extinguishers (they stop the burn)  
- **Redundant regions** are the second home (you keep living)  
- **IaC** is your blueprint to rebuild the house  
- **DR runbooks** are the emergency plan taped to your fridge  

**Without all of them, you might survive — but you won’t recover fast, or securely.**

---

## Real-World Analogy

Imagine **Snowy** runs a regional pizza chain with a digital ordering platform.  
One night, the **US-East data center is hit by a tornado**.

If Snowy only stored data in `us-east-1`, everything goes down:  
- Orders stop  
- Customers are angry  
- Revenue plummets  
- Compliance is violated  

But if Snowy had:

- Cross-region replicas  
- Route 53 failover  
- Backups in Glacier  
- CloudFormation templates  

Then Snowy could **failover to `us-west-2` in minutes** — with full encryption, access controls, and logs intact.

---

## Key DR Objectives

| **Metric** | **What It Means**              | **Example**                         |
|------------|--------------------------------|-------------------------------------|
| RPO        | Max acceptable data loss       | “We can afford to lose 5 minutes”   |
| RTO        | Max acceptable downtime        | “We must restore in under 2 hours”  |

Different DR strategies aim for different **RTO/RPO thresholds** — based on:

- Business criticality  
- Compliance requirements  
- Cost tolerance  

---

## The Four AWS DR Strategies

| **Strategy**        | **Description**                                                                 | **When to Use**                         |
|---------------------|----------------------------------------------------------------------------------|-----------------------------------------|
| **Backup & Restore**| ✔️ Cheapest, slowest. S3/Glacier + IaC rehydration                              | Cost matters more than speed            |
| **Pilot Light**     | Minimal services running; scale on failover                                     | Faster than restore, lower standby cost |
| **Warm Standby**    | Scaled-down live environment in another region                                  | RTO < 30 minutes                        |
| **Multi-Site (Hot)**| Fully active infra in multiple regions; near-zero RTO with routing failover     | Zero downtime accepted (RTO ≈ 0)        |

---

## Core AWS Services Used in DR

**Amazon Route 53**  
Failover routing based on health checks

**AWS Backup**  
Supports EC2, EFS, RDS, DynamoDB, S3  
Point-in-time restore, lifecycle rules, vaulting

**Amazon S3 & Glacier**  
Cross-Region Replication (CRR)  
S3 Object Lock for immutability  
Deep Archive for low-cost cold storage

**CloudFormation / Terraform**  
Redeploy infra via IaC  
Store in versioned S3/CodeCommit

**KMS Multi-Region Keys**  
Encrypt backups across regions  
Primary → replica key linking

**Amazon RDS / Aurora**  
Cross-region read replicas  
Aurora Global DB: <1s replication lag

**AWS Systems Manager (SSM)**  
Runbooks and automation documents for failover

**AWS Organizations + SCPs**  
Govern permissions in DR environments  
Prevent failover misconfigurations

---

## Security-Specific DR Considerations

| **Control**              | **Details**                                                                 |
|--------------------------|------------------------------------------------------------------------------|
| Encrypted Backups        | Use SSE-KMS; replicate keys to failover region                              |
| Access Control           | Pre-provision least privilege roles; enforce permission boundaries          |
| Logging Continuity       | CloudTrail → CRR to central S3; enable digest validation                    |
| Secrets Recovery         | AWS Secrets Manager + KMS multi-region; enable auto-rotation                |
| Network Security         | Pre-create VPCs, SGs, and NACLs; use TLS over internal comms (ALB, App Mesh)|

---

## Compliance & Governance

Frameworks like **NIST, ISO 27001, PCI-DSS** require:

- Regular DR testing  
- Durable + encrypted backups  
- Documented RTO/RPO targets  

AWS tools like **Audit Manager** help map DR to compliance controls.

---

## Real-Life Example: SnowySecure Compliance Stack

Snowy runs a **health data platform in `us-east-1`**. To meet **HIPAA + NIST 800-53**, Snowy:

- Uses **DynamoDB PITR + CRR to `us-west-2`**  
- Deploys **Aurora Global DB** for sub-second failover  
- Uses **CloudFormation + SSM Automation Documents**  
- Protects east-west traffic with **App Mesh + PrivateLink + TLS**  
- Locks down failover accounts with **SCPs**  

**Quarterly DR Test:**  
- Trigger failover  
- Validate logs via CloudTrail digests  
- Generate audit proof with Audit Manager  

Snowy knows:

- RTO: how long recovery took  
- RPO: how much (if any) data was lost  
- Encryption and IAM stayed intact  

---

## Final Thoughts

**Disaster Recovery in AWS is not a single feature — it’s a discipline.**

You’re not just copying data.  
You’re preserving:

- Security  
- Compliance  
- Access control  
- Operational continuity  

When done right, DR becomes:

- Repeatable  
- Auditable  
- Automated  
- Zero-trust aligned  

And when disaster hits — **you won’t panic**.  
**You'll run the playbook, monitor recovery, and resume business — securely.**
