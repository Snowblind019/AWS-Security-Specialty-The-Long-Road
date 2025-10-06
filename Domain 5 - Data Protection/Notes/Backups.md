# AWS Backups
## What Is the Service

Backups in AWS are about **resilience**. Disasters happen — hardware dies, humans click wrong buttons, ransomware encrypts everything, or attackers purge resources. The only thing standing between you and total data loss is whether you’ve got **backups configured properly and recoverable**.

While each AWS service has its own backup mechanism (like RDS snapshots, EBS snapshots, S3 versioning), AWS also provides a **centralized service**: **AWS Backup**.

**AWS Backup** is a **policy-based, centralized backup manager** for automating backups across AWS services. It gives you:
- Backup plans (daily, weekly, monthly, retention policies)  
- Vaults (with encryption, access control, and immutability options)  
- Compliance tracking (Backup Audit Manager)  
- Cross-Region / cross-account backup copies  

Instead of scripting per-service snapshots or setting manual reminders, **AWS Backup becomes your cloud-wide data protection authority.**

---

## Cybersecurity Analogy

Backups are like **write-once black boxes** on an airplane.  
You hope you never need them.  
But when disaster strikes — when systems crash, when breaches occur — those backups are your **only shot at reconstruction and recovery**.

And **AWS Backup Vault Lock**?  
That’s like **encasing the black box in tamper-proof titanium** and sealing it with a **digital signature**. Not even the **pilot (root account)** can delete the logs once they’re locked.

## Real-World Analogy

Imagine your house is filled with **precious photos, documents, and collectibles**.

- Manually backing up each room = creating snapshots manually for every service  
- Setting up a rotating cloud backup that handles everything = **AWS Backup**  
- Creating a backup that can’t be deleted even if someone breaks in = **Vault Lock**  
- Keeping one copy in a fireproof safe across town = **Cross-Region backup**  
- Logging every access to that safe = **AWS CloudTrail + Backup Audit Manager**

---

## How It Works

### Core Components

| **Component**       | **What It Does**                                                     |
|---------------------|----------------------------------------------------------------------|
| Backup Plan         | Policy that defines frequency (daily/weekly/monthly), lifecycle, retention, and tags |
| Backup Vault        | Logical container for backups; controls encryption and access        |
| Vault Lock          | Immutability (WORM) — can't delete backups once locked               |
| Recovery Point      | The actual backup instance (snapshot, copy, etc.)                    |
| Backup Selection    | Filters which resources get backed up (via tags or ARNs)             |

---

### Flow Example

1. You create a backup plan (e.g. daily at midnight, retain for 30 days).  
2. You define a vault (with KMS key + Vault Lock enabled).  
3. You assign resources to the plan (via tag-based selection or explicit ARNs).  
4. AWS automatically backs up supported services:

   - EBS  
   - RDS  
   - DynamoDB  
   - EFS  
   - FSx  
   - Storage Gateway  
   - EC2 (via EBS)

5. You can optionally copy backups to **another region/account** for DR.  
6. All activity is logged via **CloudTrail**, and tracked by **Backup Audit Manager**.

---

## Which Services Support AWS Backup?

| **Service**       | **Native Backup** | **AWS Backup Support** | **Notes**                            |
|-------------------|-------------------|--------------------------|--------------------------------------|
| EBS               | Snapshots         | ✔️                        | Block-level backup                   |
| RDS               | Snapshots         | ✔️                        | Point-in-time restore                |
| Aurora            | Snapshots         | ✔️                        | Cluster-level recovery               |
| DynamoDB          | PITR + Export     | ✔️                        | Continuous backup                    |
| EFS               | Automatic         | ✔️                        | File system-level                    |
| S3                | Versioning        | ✖️ (native only)          | Use S3 Object Lock, lifecycle        |
| EC2 Instances     | AMIs + EBS        | ✔️ (via EBS)              | Not direct backup of EC2 metadata    |
| FSx               | Snapshots         | ✔️                        | Windows/File Gateway                 |
| Storage Gateway   | Snapshots         | ✔️                        | For tape and volume backups          |

---

## Pricing Model

- Charged **per GB-month** of backup storage  
- (Different price for warm vs cold storage)  
- **Backup restore operations** cost extra  
- **Cross-Region copy** incurs data transfer + storage fees  
- **Vault Lock** and **Audit Manager** are free, but logs go to CloudWatch/CloudTrail (which may cost extra)

---

## Security & Compliance Features

| **Feature**           | **What It Does**                                                 |
|------------------------|------------------------------------------------------------------|
| Vault Lock             | Enforces WORM backups — cannot delete before retention ends     |
| KMS Encryption         | All backups are encrypted at rest (your key or AWS key)         |
| Access Policies        | IAM permissions on vaults, plans, recovery points               |

| Backup Audit Manager   | Compliance tracking — lets you verify backup activity vs controls |
| Cross-Account Backup   | Store backups in a separate AWS account for isolation           |

You can enforce **least privilege** by restricting who can delete or modify recovery points, and **monitor access via CloudTrail**.

---

## Real-Life Example (Snowy Scenario)

**Blizzard**, the cloud security engineer at **SnowyCorp**, is tasked with ensuring they can recover critical financial and inventory data during a ransomware event.

Here’s what he does:

- Tags all production databases and EBS volumes with `Backup=true`
- Creates an AWS Backup Plan with:
  - **Daily backups**
  - **35-day retention**

  - **Copies to another region**
- Configures a **Vault Lock** with WORM enforcement and a custom **KMS key**
- Enables **Backup Audit Manager** to track if backup jobs are skipped or deleted
- Runs **restore tests quarterly** and stores results in **Security Hub** as findings

This lets SnowyCorp:
- Prove compliance to auditors  
- Enforce **separation of duties** (vault access ≠ resource ownership)  
- And confidently say: **yes, we can recover from anything**

---

## Final Thoughts

Backups aren't sexy — **until you need them**.  
Then they’re the **difference between a minor incident and total disaster**.

In AWS, building a secure, automated, testable backup strategy means combining:
- Service-level snapshot tools  
- AWS Backup for orchestration and compliance  
- Vault Lock for immutability  
- KMS for encryption  
- CloudTrail + Audit Manager for visibility  

Make **backups central** to your security posture — not just your DR playbook.  
**Backups are part of your data protection perimeter.**

