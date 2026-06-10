# Amazon EBS — Deep Dive

## What Is the Service

Amazon **EBS (Elastic Block Store)** is block-level storage for **EC2 instances**. Think of it like virtual hard drives you can attach, detach, snapshot, encrypt, back up, and clone.

Each EBS volume is like a raw disk device — you mount it to an instance, format it with a file system (ext4, XFS, NTFS, etc.), and the instance reads/writes to it just like a physical disk.

### Why it matters:
- EBS volumes **persist beyond instance termination** (unless explicitly deleted)
- You can **create snapshots for disaster recovery** and replicate across **AZs or Regions**
- You can **encrypt at rest with KMS**, control access via **IAM**, and **tag volumes** for billing or automation
- It’s foundational for **compliance-driven workloads** that need reliable, auditable storage with encryption, backup, and access control

EBS is the **backbone of persistent storage** in AWS — and your threat surface if it’s not locked down properly.

---

## Cybersecurity Analogy

EBS is your **server’s internal drive** — meaning it contains sensitive data by design. But in the cloud, these drives are:

- **detachable**
- **cloneable**
- **restorable from snapshots**
- **shareable across accounts** (with some constraints)

If you don’t encrypt them, control snapshot access, or monitor detach/re-attach operations — **you’ve handed an attacker the ability to clone your disk and walk out the back door**.

## Real-World Analogy

Imagine you're managing laptops for a company. Every laptop has a hard drive. Now imagine that any employee could:

- Clone their drive to a USB stick
- Mail that USB to someone else
- Restore that USB into a brand-new laptop
- Do all of this silently unless you’ve set up logging, encryption, and access controls

That’s what happens if you don’t treat **EBS** as a **sensitive, regulated asset**.

---

## How It Works (Under the Hood)

EBS volumes live in an **Availability Zone** (not Region-wide) and can only be attached to EC2 instances in the same AZ.

### Each volume has the following core attributes:

| Attribute           | Description                                             |
|--------------------|---------------------------------------------------------|
| Type               | `gp3`, `gp2`, `io1`, `io2`, `st1`, `sc1`, etc.          |
| Size               | 1 GiB – 16 TiB per volume                              |
| Throughput & IOPS  | Configurable (especially for `gp3`, `io1`, `io2`)       |
| Encryption         | Optional at creation; uses **KMS**                     |
| Snapshots          | Point-in-time backups to S3                             |
| Multi-Attach       | Some volumes (like `io1/io2`) can attach to multiple EC2s simultaneously (risky for most apps) |

Volumes can be:
- Mounted to a single EC2
- Detached and moved
- Snapshotted and restored
- Copied across accounts or regions
- Encrypted or unencrypted (no in-place conversion)

---

## Security Considerations

EBS is deceptively simple — but there are many **attack surfaces** and **compliance requirements** you need to control:

| Concern                    | Mitigation                                                                 |
|---------------------------|----------------------------------------------------------------------------|
| Unencrypted volumes       | Enforce encryption by default via Launch Templates or **SCPs**             |
| Exposed snapshots         | Private by default — audit `CreateSnapshotPermission` and share policies |
| Snapshot cross-account copy | Use `kms:EncryptionContext` and deny `ec2:CopySnapshot` in IAM         |
| Snapshot theft            | Deny `ec2:ModifySnapshotAttribute` unless absolutely needed               |
| Detached volumes in prod  | Monitor via **EventBridge + CloudTrail** (`DetachVolume`, `AttachVolume`) |
| Uncontrolled restoration  | Watch for `CreateVolume`, `CreateVolumeFromSnapshot`                      |

Security is not about just encrypting — it’s about **controlling who can access volume contents, snapshots, and creation flows**.

---

## EBS Encryption

- At-rest encryption via **KMS**
- Encrypted snapshots → create encrypted volumes
- Can share encrypted snapshots across accounts (if **KMS** policy allows)
- Cannot encrypt existing unencrypted volumes (must create new encrypted copy)

### You can encrypt using:
- **AWS-managed keys** (`aws/ebs`)
- **Customer-managed CMKs** (for tighter control and cross-account security)

### Audit and restrict usage with:
- **KMS** key policies
- **IAM** policies using `kms:ViaService`, `kms:EncryptionContext`, `ec2:CreateVolume`
- **AWS Config** rules like `encrypted-volumes` and `encrypted-snapshots`

---

## Visibility and Monitoring

### Use **CloudTrail** to track:
- `CreateVolume`
- `AttachVolume`, `DetachVolume`
- `CreateSnapshot`, `DeleteSnapshot`, `ModifySnapshotAttribute`
- `CopySnapshot`, `ShareSnapshot`
- **KMS** decrypt events via **CloudTrail + CloudWatch Logs**

### Use **AWS Config** to track drift:
- Unencrypted volumes
- Unattached volumes
- Non-compliant snapshots
- Insecure snapshot permissions

### Use **CloudWatch** for performance metrics like:
- Volume throughput
- Queue depth
- Burst credits for `gp2`
- Latency spikes on I/O-intensive workloads

---

## Pricing Model

EBS pricing depends on:

| Component              | Example Price (varies by region)                    |
|------------------------|----------------------------------------------------|
| `gp3` volume storage   | $0.08 per GB-month                                 |
| IOPS (`gp3`)           | $0.005 per provisioned IOPS-month                  |
| Throughput (`gp3`)     | $0.04 per MB/s-month                               |
| Snapshots              | $0.05 per GB-month (deduplicated)                 |
| Cross-region copies    | Additional transfer and storage costs              |
| Encryption (CMK usage) | $1.00/month per CMK, $0.03 per 10k requests        |

### Pro tips:
- **Delete unused volumes** — they bill even if detached
- **Snapshots are incremental** — only deltas cost money
- Use **Data Lifecycle Manager (DLM)** to automate snapshot pruning

---

## Real-Life Example: Snowy’s Forensic Workflow

Let’s say an EC2 instance in `prod-analytics` crashes during an anomaly spike.

**Snowy’s** incident response playbook includes:
- Detach **EBS** volume from the EC2
- Create a **snapshot** for forensic imaging
- Use `CreateVolume` to restore a copy in an isolated “sandbox” **VPC**
- Mount it to a hardened EC2 instance with no internet access
- Run malware scans, log parsing, memory dump analysis
- Once reviewed, retain the snapshot for audit, and **encrypt with a CMK** before archiving

All access is **logged via CloudTrail**, **restricted by IAM**, and **tagged for compliance**.

---

## Final Thoughts

Amazon **EBS** is simple on the surface — just storage — but _every compromise starts at the disk_. If you don’t monitor snapshots, control encryption, or audit volume restores, you’ve left the keys to your kingdom lying on a detachable USB stick.

- Always encrypt
- Audit snapshot policies
- Monitor attach/detach activity
- Track **CMK** usage
- Use automation for lifecycle and compliance

**EBS is not just storage — it’s a potential data exfiltration path, compliance timebomb, and forensic goldmine. Treat it that way.**
