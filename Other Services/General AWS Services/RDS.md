# Amazon RDS

## What Is Amazon RDS

Amazon RDS is AWS’s managed relational database service that takes care of provisioning, patching, backups, failover, and replication of popular SQL databases like:

- MySQL  
- PostgreSQL  
- MariaDB  
- Oracle  
- SQL Server  
- Amazon Aurora (AWS-native engine)  

RDS simplifies the operational overhead of running relational databases, while providing built-in security, scaling, monitoring, and high availability.

For security teams and architects, RDS matters because:

- It's a critical data layer that often contains PII, financial records, or sensitive business data  
- It must be hardened, encrypted, monitored, and isolated  
- Misconfiguration can lead to data breaches, SQL injection, or open exposure  

It’s not just about launching a DB — it’s about building a secure, resilient, auditable system.

---

## Cybersecurity Analogy

Think of your RDS instance as a vault. You don’t just care about the locks (authentication), but also:

- Where the vault is located (network isolation)  
- Who has the keys (IAM + DB credentials)  
- Whether the vault can alert you if tampered with (CloudWatch + audit logs)  
- And if the vault is copied elsewhere without you knowing (snapshots, data export)  

Database security is a layered defense model, and RDS provides many tools — but it’s up to you to assemble them correctly.

## Real-World Analogy

Let’s say **Blizzard** builds a backend for a global game. Millions of users' accounts, transactions, and play data are stored in RDS PostgreSQL.

Without proper controls, a developer could:

- Open port 5432 to the world  
- Reuse admin credentials across apps  
- Skip encryption and expose cleartext backups  

That’s a breach waiting to happen.

Instead, Blizzard:

- Places RDS inside a private VPC subnet  
- Enforces IAM-based access for developers  
- Enables encryption at rest and in transit  
- Monitors login attempts with CloudTrail and CloudWatch  
- Uses read replicas and multi-AZ for fault tolerance  

**Result**: a secure, scalable foundation that protects the game and its users.

---

## Security Architecture for RDS

Here’s how you build a strong security posture around RDS:

### 1. Network Isolation with VPC

- Launch RDS instances in private subnets  
- Use security groups to tightly control who can connect (by IP, port, protocol)  
- Block public access unless absolutely necessary  
- For bastion or app-layer access, use:
  - SSM Session Manager  
  - App running in same VPC/AZ  
  - VPN or Direct Connect  

> **Note**: Misconfigured public access is one of the top causes of data exposure in AWS.

### 2. Encryption at Rest and in Transit

- Enable KMS-based encryption when creating the instance (cannot be turned on later)  
  This encrypts:
  - Data on disk  
  - Automated backups and snapshots  
  - Read replicas  
  - Logs and temporary files  

- Use SSL/TLS for connections to encrypt data in transit  
  - Enforced via parameter groups  
  - Clients must use SSL libraries or drivers that support encryption  

> **Compliance Note**: For HIPAA, PCI-DSS, etc., both rest and transit encryption are non-negotiable.

### 3. IAM + Native DB Authentication

**IAM Authentication** (for MySQL, PostgreSQL, Aurora):

- Let users or apps authenticate via temporary AWS tokens instead of static DB passwords  
- Grant permissions via IAM roles  
- Reduces risk of long-lived credential exposure  

**Native Authentication**:

- Use strong password policies  
- Rotate credentials regularly  
- Never hardcode passwords in app configs — use Secrets Manager  

> Combine IAM and Secrets Manager for rotated, auditable, secure auth flows.

### 4. Backup and Snapshot Management

- Enable automated backups with a defined retention window  
- Store manual snapshots in encrypted form  

> **Snapshot Sharing Tips**:
> - Only share with trusted AWS accounts  
> - Never share unencrypted snapshots publicly (a known security incident pattern)  
> - Consider backup lifecycle policies and access controls on snapshots  

### 5. Monitoring, Logging, and Auditing

| Tool                  | What It Does                                                                             |
|-----------------------|------------------------------------------------------------------------------------------|
| **CloudWatch Logs**   | Collect PostgreSQL/MySQL slow query logs, error logs, general logs                      |
| **CloudTrail**        | Audit RDS-related API calls (start instance, snapshot, modify, delete)                  |
| **RDS Enhanced Monitoring** | Collect OS-level metrics and resource usage                                    |
| **Security Hub**      | Aggregate RDS misconfigurations from Inspector or Config                                |
| **Amazon GuardDuty**  | Detect suspicious behavior like unusual login patterns (when CloudTrail is integrated)  |

You should always know:

- Who accessed your DB  
- When it was accessed  
- From where  
- What actions were taken  

### 6. High Availability and Disaster Recovery

- Use Multi-AZ deployments for automatic failover  
  - Data is synchronously replicated to a standby in another AZ  
  - Failover is automatic with minimal downtime  

- Use **Read Replicas** for:
  - Offloading read queries  
  - Cross-region disaster recovery  
  - Promoting replicas to standalone DBs in DR scenarios  

- Use backups + snapshots for restore-based DR  

> **Best Practice**: Don't rely on one instance, one AZ, or one Region for critical workloads.

### 7. Patching and Maintenance

- AWS handles automated OS-level patching, but you define the maintenance window  
- You are responsible for application-level schema upgrades  

**Use blue/green deployments** (via RDS Blue/Green feature or replica promotion) to test upgrades safely  

> Never test patches on production systems. Use replicas or snapshots for staging.

---

## Snowy’s Example: Secure RDS PostgreSQL Setup

Snowy is building a secure logging backend that stores event data in RDS.

**Setup**:

- RDS PostgreSQL deployed in a private subnet in `us-west-2`  
- No public access, only accessible by app servers in same subnet  
- KMS encryption enabled at launch  

- Database credentials stored in **Secrets Manager**  
- All app access goes through **IAM roles** with token-based auth  
- Enhanced Monitoring and CloudWatch logging enabled  

- Snapshots are encrypted and shared only with backup accounts  
- A read replica is deployed in `us-east-1` for disaster recovery  
- **GuardDuty** + **Security Hub** monitor for unusual API calls or snapshot sharing  

> **Outcome**: This setup is resilient, encrypted, monitored, and least-privileged.

---

## Final Thoughts

Amazon RDS takes care of the infrastructure, but you’re still responsible for the configuration.

> **Most breaches** happen not because RDS failed — but because someone opened port 3306 to the world, shared a snapshot publicly, or skipped IAM controls.

**Use RDS when**:

- You need a managed SQL database without infrastructure overhead  
- You want built-in backups, HA, and scaling  
- You need compliance with encryption, audit logging, and IAM integration  

**Avoid RDS when**:

- You need full OS/root access (use EC2-hosted DB instead)  
- Your app uses a niche database not supported by RDS engines  
- You need fine-grained control over DB patches or extensions (Aurora may be better)  

> With the right settings, RDS becomes a secure, scalable, and production-grade data layer — especially when combined with IAM, Secrets Manager, encryption, logging, and isolation.

