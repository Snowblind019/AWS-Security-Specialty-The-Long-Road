# Disaster Recovery (DR) in AWS

The strategies and tooling to restore systems and data after a major failure: hardware loss, natural disaster, data corruption, human error, ransomware, or a Regional AWS outage. In AWS, DR is measured by two numbers and realized through four strategies that trade cost against recovery speed. For the security exam, DR is where availability meets security: through a failover, backups must stay **encrypted, immutable, access-controlled, and auditable**, or the recovery itself fails.

The mental model is two numbers driving four strategies. **RPO** is how much data you can afford to lose (it drives replication frequency), and **RTO** is how long you can be down (it drives how ready the standby must be). The four strategies run from cheapest and slowest to most expensive and near-instant: **Backup and Restore, Pilot Light, Warm Standby, and Multi-Site (active-active)**. You pick by matching RTO and RPO targets to business criticality, compliance, and cost.

## How it works

- **RPO vs RTO**: RPO is the maximum acceptable data-loss window, RTO the maximum acceptable downtime. Every strategy and service choice is really a bid on these two.
- **The four strategies**: see the table below. Cost and recovery speed move in opposite directions.
- **Data-layer replication**: S3 **Cross-Region Replication**, RDS cross-Region read replicas, **Aurora Global Database** (sub-second cross-Region lag), DynamoDB global tables and point-in-time recovery.
- **Backup**: **AWS Backup** centralizes EC2, EBS, EFS, RDS, DynamoDB, and S3 backups with lifecycle rules and **cross-Region and cross-account copy**. A copy in a separate account limits blast radius if the primary account is compromised.
- **Server replication**: **AWS Elastic Disaster Recovery (DRS)** continuously replicates EC2 or on-premises servers at the block level for low RTO and RPO, distinct from AWS Backup's point-in-time snapshots.
- **Immutability**: **S3 Object Lock** and **AWS Backup Vault Lock** (compliance mode is WORM, undeletable even by root) protect backups from deletion or encryption by an attacker.
- **Infrastructure rebuild and orchestration**: CloudFormation or other IaC to redeploy, **ARC Region switch** or **SSM Automation** runbooks to coordinate failover, and Route 53 failover routing for DNS.
- **Encryption continuity**: **KMS multi-Region keys** so the replica Region can decrypt replicated backups. A single-Region key cannot decrypt in the failover Region.
- **Security continuity**: pre-provisioned least-privilege IAM roles and permission boundaries in the recovery Region, CloudTrail logging that continues (central S3 with replication and log-file validation), Secrets Manager multi-Region replicas, and pre-created VPCs, security groups, and NACLs. Governance via Organizations and SCPs to prevent failover misconfiguration.

## The four DR strategies

| Strategy | Standby footprint | RTO / RPO | Cost | When to use |
|---|---|---|---|---|
| Backup and Restore | None running, restore from backup and IaC | Hours / hours | Lowest | Cost matters more than speed |
| Pilot Light | Core data replicated, minimal always-on, scale up on failover | Tens of minutes / minutes | Low | Faster than restore, low standby cost |
| Warm Standby | Scaled-down live copy always running, scale up on failover | Minutes | Medium | RTO under roughly 30 minutes |
| Multi-Site (active-active) | Full capacity in multiple Regions | Near zero / near zero | Highest | Zero downtime accepted |

## What gets tested

- The four strategies order cost against speed. Backup and Restore is cheapest with no standby but the slowest. Pilot Light keeps data replicated and core services minimal, scaling up on failover. Warm Standby runs a scaled-down live copy. Multi-Site runs full active-active for near-zero RTO. Match the scenario's RTO and RPO to the cheapest strategy that meets them.
- RPO is the data-loss window (drives replication), RTO is the downtime window (drives standby readiness). Do not swap them.
- Security continuity is the exam's real angle. Backups must be encrypted with multi-Region KMS keys so the replica Region can decrypt them, IAM roles and boundaries must be pre-provisioned in the recovery Region, CloudTrail must keep logging (central S3 plus validation), and Secrets Manager must be replicated. A recovery that cannot decrypt its data or has no roles is a failed DR.
- Immutability against ransomware is heavily tested. S3 Object Lock and AWS Backup Vault Lock (compliance mode, WORM) keep an attacker, or a compromised root, from deleting or encrypting backups.
- AWS Backup supports cross-Region and cross-account copy. A backup copy in a separate, locked-down account is a standard ransomware and account-compromise defense.
- AWS Elastic Disaster Recovery (DRS) is the low-RTO/RPO server-replication answer (continuous block-level) for EC2 and on-premises, versus AWS Backup for point-in-time snapshots. Different tools for different needs.
- Orchestration is ARC Region switch or SSM Automation runbooks, with Route 53 for DNS failover. Aurora Global Database, DynamoDB global tables, and S3 CRR are the data-layer replication choices.

## Limitations

- DR is a discipline, not a single service. Untested, it rots: roles drift, keys go un-replicated, capacity falls short. Regular game-day tests are the point, and several compliance frameworks require them.
- Cost climbs steeply toward active-active. Most workloads do not need an RTO near zero, so over-provisioning standby is a common waste.
- Cross-Region encryption depends on multi-Region KMS keys (or per-Region keys planned ahead). A single-Region key will not decrypt in the replica Region, silently breaking a failover.
- Immutable backups in Vault Lock compliance mode cannot be shortened or deleted by design, so set retention deliberately before locking.
- App Mesh, historically suggested for east-west mTLS in a recovery stack, is being retired. Use a current service mesh or native TLS for internal encryption.