# Amazon EFS Encryption

## What Is Amazon EFS Encryption

Amazon **EFS** (Elastic File System) is AWS’s managed **NFS** file share that can be mounted across EC2 instances, containers, and Lambda functions. It’s great for use cases where multiple compute nodes need **shared, low-maintenance, POSIX-compliant file storage**.

But here's the problem: **data in shared filesystems is vulnerable** — especially when:

- You mount the same share on multiple machines  
- You rely on legacy **NFS** permissions  
- You operate across multiple **AZs**  

That's why **EFS Encryption** is critical. It protects the **entire lifecycle of data**:

- **At rest** — encrypted using AWS **KMS**  
- **In transit** — encrypted via **TLS** during **NFS** client communications  

When encryption is enabled, files are automatically encrypted with **256-bit AES keys**, and access control is enforced by **IAM policies**, **security groups**, and **POSIX permissions**.

It’s all invisible to the app — but vital to the security architect.

---

## Cybersecurity Analogy

Think of **EFS** like a **shared team drive in a corporate war room.** Everyone’s dropping docs, picking up files, editing configurations.

Now imagine if:

- That drive wasn’t locked in a safe (no encryption at rest)  
- Or if the hallway leading to it had no cameras (unencrypted transit)  
- Or if old users could still sneak in (no **IAM**)  

**EFS Encryption** is the combination of:

- **Locking the safe** (**KMS** encryption at rest)  
- **Watching the hallway** (**TLS** in-transit)  
- **Controlling access** to who can even enter the war room (**IAM** + security groups)  
Without all 3? Someone *will* walk in, pick up sensitive data, and leave — and you won’t even know they were there.

## Real-World Analogy

Let’s say **Winterday DevOps** mounts **EFS** to 10 EC2 instances spread across **3 AZs**. This shared volume holds:

- Bash scripts  
- Lambda layer files  
- JSON config with sensitive keys (bad idea, but it happens)  
- Application log files  

If **EFS encryption** isn’t enabled:

- Anyone gaining access to the EC2 instance could read the plaintext data off disk  
- Data replicated across **AZs** could be intercepted by rogue insiders (in a worst-case scenario)  
- Root-level compromise on one instance = full access to everything stored on **EFS**  

Now imagine a rogue container running in the same **VPC** — if it can mount the **EFS** volume (and there’s no **IAM** restriction), it can scrape sensitive files with `cat`.

**Winterday** enables:

- **EFS Encryption at Rest** using AWS **KMS CMK**  
- **TLS in-transit encryption** on all mount points  
- **IAM identity-based access control** using `efs:ClientMount` and `efs:ClientWrite`  
- **Security group boundaries** to allow **NFS** only between known EC2 **IPs**

> Result: even if someone gets onto an instance, they can’t scrape the contents, intercept the **NFS** stream, or mount the volume from elsewhere without **IAM** access.

---

## How It Works

### 1. Encryption at Rest

- Enabled when the file system is **created** (cannot be enabled later)  
- Uses **AWS KMS** (either AWS-managed key or customer-managed **CMK**)  
- Encrypts:  
  - File content  
  - Metadata  
  - Directory names  
  - Snapshots  

**EFS uses envelope encryption:**

- Generates a unique data key per object  
- Encrypts that key with the **KMS** key (**CMK**)  
- Stores the encrypted data + encrypted key together  
- Decryption happens on-the-fly when accessed

### 2. Encryption in Transit

- Uses **TLS 1.2** between client and **EFS** mount target  

- Requires mounting with the `-o tls` option:

```bash

sudo mount -t nfs4 -o tls fs-12345678.efs.us-west-2.amazonaws.com:/ efs
```

- Works only with **Amazon-provided NFS client** (`amazon-efs-utils`)  
- Protects against:  

  - MITM attacks  
  - Passive packet sniffing  
  - Credential/session leakage

### 3. Key Rotation

- If using a customer-managed **CMK** (vs. the default `aws/elasticfilesystem` key), you can:
  - Enable **automatic rotation**  
  - Re-encrypt files with a new **CMK** manually (not retroactive by default)  
- All key usage is logged in **CloudTrail**

---

## Pricing Models

Encryption itself is **free**, but you pay for:

- **AWS KMS requests**
  - Each encryption/decryption counts as a **KMS** operation  
  - You pay per 10,000 operations (unless using default key, which is free)

- **Storage costs**
  - **EFS** encrypted or not, storage pricing is the same (Standard/IA tiers)

- **Data transfer**
  - In-transit **TLS** encryption doesn’t cost extra, but **cross-AZ traffic still bills**

> If you’re using customer **CMKs** heavily (e.g., thousands of files read per second), **KMS** costs can add up — but for most orgs, it's negligible compared to the risk reduction.

---

## Other Explanations / Gotchas

- **You can’t turn on encryption after EFS is created.** You must:
  - Backup → recreate a new encrypted **EFS** → restore data

- **CloudTrail + KMS Logs:** always enable these for auditability  
  - You want visibility into who decrypted what and when

- **Data still readable by root:** encryption at rest prevents physical disk access attacks, not compromised OS users — always combine with **IAM** and OS-level security

- **POSIX permissions still apply:** encryption doesn’t override Linux-style file perms — use them properly

- **Don’t assume TLS is enabled by default** — you must mount with the correct client + flag

---

## Real-Life Example: SnowyCorp ML Cluster

**SnowyCorp** runs a **SageMaker** model training pipeline where:

- EC2 nodes process training data in real-time  
- Logs and checkpoints are written to **EFS** for durability and sharing  
- Shared **EFS** volume is mounted by 4 EC2s across **2 AZs**

**Security setup includes:**

- **EFS created with CMK** for encryption at rest  
- Mounted with `amazon-efs-utils` using **TLS**  
- EC2 **IAM** roles scoped to:  
  - `efs:ClientMount`  
  - `efs:ClientWrite`  
  - `kms:Decrypt` on **CMK**  
- Security group only allows **NFS** from specific EC2 instance **IPs**  
- **CloudTrail** logs every **KMS** decrypt operation  
- **GuardDuty** monitors for anomalous **NFS** port scanning in **VPC**

> If any EC2 is compromised, an attacker can’t:
> - Mount the volume from another machine (**IAM** blocked)  

> - Read files on disk (**KMS** protected)  
> - Sniff data in transit (**TLS** encrypted)  


**SnowyCorp sleeps better at night.**

---

## Final Thoughts

**EFS is simple. And that’s exactly why it can be dangerous.**

When you give multiple EC2s access to a shared filesystem, you're introducing a **horizontal attack surface**. One weak node = lateral read access to all your data.

- **Encryption at rest** protects your data if the volume is copied, stolen, or snapshots are shared.  
- **Encryption in transit** protects you from eavesdropping and **MITM** during active sessions.

But neither of those protect you from:

- Bad **IAM** policies  
- Open security groups  
- Malicious insiders with EC2 access  

Encryption is one layer. Don’t stop there. Use it in conjunction with:

- **IAM** policies (least privilege)  
- Logging (**CloudTrail + KMS + GuardDuty**)  
- Mount restrictions (**SGs** + **TLS-only** clients)  
- Filesystem permissions (**POSIX**)  
- Separation of data between environments (*dev vs. prod*)  

> **If you're serious about security, never deploy EFS without encryption at both ends.**  
> It's one checkbox — but it locks down a world of risks.

