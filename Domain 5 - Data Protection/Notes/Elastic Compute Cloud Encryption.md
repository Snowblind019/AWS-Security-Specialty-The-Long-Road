# EC2 Encryption

## What Are We Talking About When We Say “EC2 Encryption”?

When someone says “EC2 is encrypted,” they’re usually wrong.  

**There is no single setting that encrypts “EC2.”**  
What you’re actually encrypting is:

- **EBS volumes** (your virtual hard drives)  
- **Instance store volumes** (ephemeral SSD, not always available)  
- **Snapshots** (**EBS** backups)  
- **AMIs** (images created from encrypted volumes)  
- **Traffic** in/out of the instance (handled by **TLS**, not EC2 itself)  
- **Metadata and logs** (stored in **CloudWatch**, S3, etc.)

> **CPU registers, RAM, and network buffers are NOT encrypted** — and encryption-in-use is a separate category altogether.

---

## Cybersecurity Analogy

Think of EC2 like a rental office space.

- **EBS** encryption is **locking the filing cabinets** inside.  
- **Network encryption** is **locking the door and encrypting your emails**.

If you don’t encrypt your cabinets and someone breaks in or reuses the space after you, **they might find old contracts or invoices**.

Encryption at rest protects your data **when disks are decommissioned, backed up, or snapshotted** — not while it’s running in memory.

## Real-World Analogy

**BlizzardTech** builds a batch data processing EC2 instance.  
They launch it from an AMI that came from a third-party.  
It stores intermediate results on a non-encrypted **EBS** volume.  
When done, they terminate the instance — but **forget to delete the volume**.

Six months later:

- A junior **dev** restores the volume from a snapshot  
- Notices some leftover logs containing user data  
- Files a ticket asking if that’s sensitive  

Turns out: it’s **GDPR-regulated customer data that was never encrypted.**

No alert. No audit. No encryption. No compliance.

---

## 1. EBS Volume Encryption

This is the **main layer** of EC2 encryption.

**EBS** volumes are **encrypted at rest using AWS KMS**:

- You can use the default AWS-managed key (`aws/ebs`)  
- Or a **customer-managed CMK** (`alias/blizzard-prod-ebs`)  
- Encryption is **AES-256**, handled transparently by the EBS service

**When encrypted:**

- Data, snapshots, and backups are encrypted  
- You can’t convert encrypted → unencrypted, or vice versa, without creating a copy  
- Performance is not meaningfully impacted (hardware acceleration is used)

**To encrypt:**

- Check the box at volume creation  
- Or copy an unencrypted snapshot to a new **encrypted** one  

Use **IAM + KMS** key policies to control **who can create volumes using your CMKs**.

## 2. Snapshot Encryption

Snapshots inherit encryption from the volume.

- If your volume was encrypted with `aws/ebs`, the snapshot will be too.  
- If you copy a snapshot and specify a **different CMK**, it’ll use that.

**Why this matters:**

- Anyone with `ec2:CreateVolume` + access to your snapshot can spin up a new EC2 with that data  
- **KMS key access is your last line of defense**

**Best practice:**

- Store snapshots in a **different account or separate encrypted bucket** (if exporting to S3)  
- Monitor `ec2:CopySnapshot` in **CloudTrail**  
- Disable **public snapshot sharing** (this can cause public leaks)

## 3. AMI Encryption

When you create an AMI from an encrypted **EBS** root volume:

- The AMI will also be encrypted  
- You must share both the AMI + **KMS** key if you want someone else to launch it

> **You can’t share encrypted AMIs publicly**  
> They must be shared to specific AWS account IDs  
> **KMS** keys must also allow `kms:Decrypt` from those accounts

This is how you enforce **multi-tenant isolation** when building secure image pipelines.

## 4. Instance Store (Ephemeral) Disks

Not all instance types support **instance store volumes** — but when they do, here’s the problem:

These are **physically attached disks** (**NVMe**, **SSD**) that **disappear on termination**.  
By default, they are **NOT encrypted unless your instance type supports it** (and it’s not consistent).

**To enable encryption:**

- You need **Nitro-based instances** (newer generations)  
- You need to use the `nvme-cli` **inside the instance** to verify encryption  

This is mostly useful when you need high-speed temp storage, not for persistent data.

## 5. Encryption in Transit

AWS does **not encrypt traffic between EC2 instances** by default.

You must use:

- **TLS 1.2+**  
- **OpenVPN**, **WireGuard**, or **SSH tunneling**  
- **mTLS**, especially in service mesh or **gRPC** environments  
- **EFS with TLS**, **RDS with SSL** enabled, etc.

**To enforce:**

- Use **Security Groups** to block ports you don’t trust  
- Use **PrivateLink** or **VPC Peering + SGs**  
- Add **IAM Conditions** like `aws:SecureTransport = true` for API endpoints  
- Use **CloudFront** or **ALB with HTTPS enforcement** in front of EC2 web services  

## 6. KMS Key Management for EC2

Most EC2 encryption relies on **AWS KMS**.

**Common keys:**

- `aws/ebs` *(default)*  
- `alias/blizzard-prod-ebs` *(custom)*  
- `alias/snapshot-kms-prod`

You must manage:

- **IAM** permissions (`kms:CreateGrant`, `kms:Decrypt`)  
- Key rotation policies  
- Alias naming conventions  
- Monitoring via **CloudTrail**

**Best Practice:**

- Use **CMKs** for high-sensitivity data  
- Rotate keys annually  
- Attach key policies that limit usage by tag or principal  
- Enable key usage logging  
- Disable old keys after migration

## 7. Logging and Monitoring

You won’t get visibility into EC2 encryption **unless you ask for it.**

**Tools:**

- **CloudTrail** for **KMS** usage events (`CreateVolume`, `AttachVolume`, `CopySnapshot`)  
- **AWS Config** to detect unencrypted volumes  
- **Inspector** can flag unencrypted storage  
- **Security Hub** surfaces **misconfigurations**  
- **Trusted Advisor** warns on unencrypted **EBS** if using Business or Enterprise support

**Custom Controls:**

- Lambda auto-encrypt snapshots  
- **SCPs** to deny unencrypted volume creation  
- **EventBridge** rules for `ec2:CreateVolume` without encryption

---

## Pricing Model (Encryption Overhead)

| Component                  | Notes                                                  |
|---------------------------|--------------------------------------------------------|
| **EBS encryption**         | No extra charge                                        |
| **KMS CMK usage**          | $1/month per **CMK** + $0.03 per 10K requests         |
| **Snapshots**              | Charged per GB-month                                   |
| **CloudTrail/KMS logging** | Charged by log ingestion                               |
| **Inspector scans**        | Charged per resource scanned                           |

> So yeah, encryption is mostly **cheap** — but key management isn’t free.

---

## Snowy Real-World Use Case

**Winterday’s** SOC receives an alert about a terminated EC2 instance from an older analytics workload.

They investigate:

- The volume was left behind (still live in `us-east-1a`)  
- It was **unencrypted**  
- A junior **dev** took a snapshot to preserve logs  
- Then shared it with their personal AWS account to “keep a backup”  

That’s a **compliance incident**, and could’ve been a **breach** if the **dev** was malicious.

**Fixes:**

- Add **SCP** to deny volume creation unless encryption enabled  
- Enforce **CMK** usage per environment  
- Block snapshot sharing unless explicitly whitelisted  
- Build automation to check for unencrypted snapshots and notify

---

## Final Thoughts

Encryption on EC2 isn’t a toggle. It’s a mindset.

You don’t get automatic safety unless you **explicitly ask for it**.  
Encrypt your volumes.  
Manage your **KMS** keys.  
Audit your snapshots.  
Block unencrypted activity by default.  
Tag everything.

And remember — if it’s not encrypted, it’s as good as public.

> Don’t be the one explaining in your post-incident report that “we thought AWS encrypted that automatically.”
