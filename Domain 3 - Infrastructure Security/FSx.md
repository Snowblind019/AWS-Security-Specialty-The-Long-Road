# Amazon FSx

## What Is the Service

Amazon FSx is a family of fully managed file systems built for specific workloads, offering shared file storage over standard protocols like SMB (for Windows), NFS (for Lustre/OpenZFS), and HPC-optimized solutions. You get familiar file storage, fully integrated with AWS networking, identity, encryption, and backup tools.  
But this isn’t just “storage”—it’s stateful, multi-tenant, and network-exposed. That makes it a key piece of data governance, network access control, and encryption strategy in cloud security architecture.

---

## Supported FSx Variants (With Security Context)

| FSx Variant             | Protocol      | Workload Focus                                  | Security Notes                                       |
|-------------------------|---------------|--------------------------------------------------|------------------------------------------------------|
| FSx for Windows File Server | SMB           | Windows-based apps, AD integration               | Heavy IAM/AD integration; audit logging              |
| FSx for Lustre          | NFS           | High-performance computing (HPC), AI/ML         | Often used with S3; no AD; security = VPC + encryption |
| FSx for NetApp ONTAP    | NFS/SMB/iSCSI | Enterprise hybrid storage, SnapMirror           | Advanced features like snapshotting, volume-level access |
| FSx for OpenZFS         | NFS           | Linux-based apps needing ZFS                    | Fine-grained control; ZFS ACLs; integrated backups   |

> Each of these has encryption at rest, in-transit, VPC placement, and optionally KMS CMK integration.

---

## Cybersecurity & Real-World Analogy

Imagine Snowy’s company runs a shared corporate file drive:

- **Windows FSx** is like your on-prem “S:\ Drive” — user home directories, project folders, and permissions tied to Active Directory.
- **Lustre FSx** is your ultra-fast scratch pad for temp data, ML models, or batch analytics — not for long-term sensitive storage.

Now imagine attackers get a foothold in the VPC or EC2 instance that’s mapped to the FSx volume. If you didn’t:

- Lock down the SMB/NFS access  
- Enable encryption in transit  
- Use IAM or AD-based access control  

…then they’re roaming through your file shares like it’s 2003.

---

## Security Controls by FSx Type

| Feature              | Windows FSx | Lustre FSx | NetApp FSx | OpenZFS |
|----------------------|-------------|------------|------------|---------|
| VPC Deployment       | ✔️          | ✔️         | ✔️         | ✔️      |
| Encryption at Rest   | ✔️ (KMS)    | ✔️ (KMS)   | ✔️ (KMS)   | ✔️ (KMS) |
| Encryption in Transit| ✔️ SMB TLS | ✔️ NFS TLS | ✔️         | ✔️      |
| AD Integration       | ✔️ AWS Managed AD, Self-Managed AD | ❌ | ✔️ | ❌ |
| IAM/ACL Control      | ✔️ AD Group Policies | N/A | ✔️ NFS/SMB ACLs | ✔️ ZFS ACLs |
| Audit Logging        | ✔️ CloudWatch (via Windows logs) | N/A | ✔️ | N/A |

---

## Access Control

### FSx for Windows:

- Requires Active Directory integration (either AWS Managed AD or your own)  
- Permissions are defined via NTFS ACLs  
- Tied directly to AD users and groups  

### FSx for Lustre:

- Access controlled via Linux permissions  
- Can integrate with S3 for ingest/output data  
- Focused more on data plane isolation than fine-grained identity control  

### All FSx Types:

- Must be deployed in private subnets  
- Access restricted by security groups + NACLs  
- No public access options (good)

---

## Encryption Strategy

All FSx file systems support:

- **Encryption at rest** using AWS KMS  
  - You can use AWS-managed keys or customer-managed CMKs  
- **Encryption in transit** using:
  - SMB 3.0+ TLS for Windows FSx  
  - TLS for NFS (if clients support it)  

Keys can be rotated, but care must be taken with long-term access clients.  
This is critical if you're storing:

- PII  
- Logs  
- Business-critical documents  
- Large ML datasets with compliance implications

---

## Logging & Monitoring

| Source           | Description                                                 |
|------------------|-------------------------------------------------------------|
| CloudTrail       | Management events (create/delete FSx volumes)               |
| CloudWatch Logs  | FSx for Windows writes Windows event logs to CloudWatch     |
| VPC Flow Logs    | Monitor SMB/NFS network access to FSx                       |
| AWS Config       | Can track configuration drift (e.g., encryption settings, subnet placement) |

You can also enable **Data Deduplication**, **Shadow Copies**, and **Snapshots** for rollback and versioning, especially in Windows FSx.

---

## Backup and Recovery

- FSx automatically integrates with **AWS Backup**  
- Snapshots can be scheduled, retained, and stored encrypted  
- For **NetApp/Windows FSx**: restore individual files/folders via volume mount  

> **Security tip:** Do not store backups in the same AZ as the FSx volume.

---

## Misconfig Risk Examples

| Misconfiguration                | What Could Happen                                     |
|--------------------------------|--------------------------------------------------------|
| ✖️ No encryption in transit     | Session hijack, replay of file access                 |
| ✖️ Public AD + no ACLs          | Any domain user can access every folder              |
| ✖️ Shared Windows AD secrets    | One compromised AD credential = full FSx access      |
| ✖️ Security group allows all VPC traffic | Any compromised EC2 can mount file share     |
| ✖️ No snapshot recovery policy  | Ransomware = permanent loss                          |
| ✖️ Lustre FSx not purged after ML job | Sensitive data sits in cleartext NFS with no controls |

---

## Snowy’s Real-World Scenario

Snowy’s security team launches FSx for Windows File Server for a new internal reporting dashboard:

- Active Directory tied to AWS Managed Microsoft AD  
- File access permissioned via NTFS ACLs mapped to security groups  
- CloudWatch logs enabled for access monitoring  
- KMS CMK created with limited IAM permissions to rotate  
- All EC2 app servers that access the share live in isolated private subnets behind NACLs  
- Weekly snapshots scheduled via AWS Backup  

A junior engineer accidentally mapped **Everyone** to a shared folder.  
**AWS Config caught the ACL drift**, and Snowy got paged via EventBridge alarm tied to a Config rule.

---

## Final Thoughts

FSx can feel “boring” — just shared files, right?  
But the reality is: it’s stateful, persistent, accessible over the network, and often tied into identity systems (AD).

- Encrypt it  
- Lock it down  
- Audit access  
- Use snapshots  
- Rotate credentials  

It’s not just about performance — it’s about **not letting your company’s file share become the attacker’s buffet.**
