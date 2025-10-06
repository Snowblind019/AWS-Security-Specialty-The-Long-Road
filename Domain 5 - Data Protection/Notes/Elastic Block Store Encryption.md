# EBS Encryption (Amazon Elastic Block Store)

## What Is It

Amazon **EBS** (Elastic Block Store) provides persistent block-level storage for EC2 instances — like a hard drive in the cloud.  
You can use it for OS volumes, application data, databases, and logs.

**EBS Encryption** enables automatic **encryption at rest** for:

- Boot volumes  
- Data volumes  
- Snapshots  
- Volume clones  
- Attached backups  
- Even the data in transit between EC2 and **EBS**

This ensures that even if someone:

- Copies your snapshot  
- Mounts your volume  
- Downloads your backup  
  - They get only **encrypted gibberish** unless they also have access to the **KMS** key.

---

## Cybersecurity Analogy

Imagine you’re using an external hard drive to store sensitive work documents. You keep it **password-protected and encrypted** — so even if someone steals it from your bag, they can’t open it.

**EBS** encryption works the same way.  
**No key = no access**, even if the volume is stolen, copied, or improperly shared.

---

## Real-World Analogy

Think of **EBS** encryption like putting a **safe inside your cloud server**.  
Your **EC2** might be running normally, but behind the scenes, the disk writes and reads **from an encrypted safe**.  
No user or attacker ever sees the raw disk unless their **IAM** role and the **KMS** key policy allow it.

## How EBS Encryption Works

- When you create an encrypted **EBS** volume, AWS uses **AES-256** encryption under the hood.
- Encryption and decryption are handled **transparently**:  
  - Your app doesn’t know it’s encrypted  
  - Your performance is unaffected  
- Keys are managed in **AWS Key Management Service (KMS)**
- You can use:  
  - **AWS-managed key** (alias: `aws/ebs`)  
  - **Customer-managed key (CMK)** for granular control  

All snapshots created from encrypted volumes remain encrypted.  
All new volumes from encrypted snapshots inherit the encryption.

Since 2020, **encryption by default** is supported — and highly recommended.

---

## SnowySec EBS Flow Example

**Snowy’s** production workloads run across 30 EC2 instances with encrypted **EBS** volumes. Here's how the workflow is hardened:

1. A custom **CMK** (`snowy-ebs-prod-key`) is created in **KMS**  
2. Default encryption for **EBS** is enabled account-wide using that **CMK**  
3. EC2 launch templates are configured to use encrypted volumes only  
4. **IAM** policies restrict EC2 roles from launching unencrypted volumes  
5. **EBS** snapshots are encrypted and stored with lifecycle policies in S3 Glacier  
6. **CloudTrail** monitors all `CreateVolume`, `CopySnapshot`, `AttachVolume` calls  
7. Config rules detect and alert if an unencrypted volume or snapshot is found  
8. Tagging policies enforce `Sensitive=True` for all encrypted resources  
9. **KMS** key usage is logged, and alerts are triggered for abnormal decryption events  

This means:  
If an attacker gains access to EC2 and copies a snapshot — they’ll need to also compromise the **CMK** and **IAM** role.  
No key? No breach.

---

## Security Use Cases

| Threat                               | **EBS Encryption Mitigation**                                             |
|--------------------------------------|---------------------------------------------------------------------------|
| Rogue admin copies snapshot          | Snapshot remains encrypted; requires **CMK** to decrypt                   |
| Volume attached to unauthorized EC2  | **CMK** access denied, volume won't decrypt or mount                      |
| Snapshot shared across accounts      | **KMS** prevents cross-account decrypt unless explicitly granted          |
| Insider exfiltrates **EBS** clone    | Encrypted volume unusable without matching key access                     |
| EC2 malware attempts disk readout    | Volume reads pass through encryption; unauthorized access fails           |

---

## Best Practices for EBS Encryption

- **Enable default encryption** for all Regions and accounts  
- Use **customer-managed CMKs** for separation of environments (prod vs dev)  
- Monitor and log all `KMS:Decrypt`, `CreateSnapshot`, and `AttachVolume` events  
- Apply **Config rules** to flag unencrypted volumes or snapshots  
- Use **lifecycle policies** to clean up unused encrypted snapshots  
- Rotate **CMKs** periodically and audit usage with **CloudTrail**  
- Use **resource-based policies and grants** for tight key access control  
- **Prevent cross-account snapshot sharing** unless absolutely necessary  

---

## Service Integrations That Matter

| Service      | Why It Matters                                                                 |
|--------------|---------------------------------------------------------------------------------|
| **KMS**      | Stores and manages keys, controls access, logs usage                           |
| **CloudTrail** | Audits all **EBS** and **KMS-related** API activity                         |
| **EC2**      | Attaches/detaches volumes, must honor encryption settings                      |
| **Config**   | Detects non-compliant volumes or snapshots                                     |
| **Security Hub** | Flags **misconfigurations** in encryption posture                        |
| **IAM**      | Controls who can launch, attach, or decrypt encrypted volumes                  |

---

## Pricing Overview

| Item             | Cost                                                                  |
|------------------|-----------------------------------------------------------------------|
| **EBS encryption** | **Free** — no extra cost for encryption itself                     |
| **KMS CMKs**     | ~$1/month per key                                                     |
| **KMS usage**    | ~$0.03 per 10,000 API calls (Encrypt/Decrypt)                         |
| **Snapshots**    | Priced by storage usage; remains encrypted                            |

---

## Common Misunderstandings

- Encryption adds performance overhead → **False** (*EBS encryption is optimized*)  
- You can decrypt **EBS** manually with a password → **False** (*only via IAM+KMS policies*)  
- Snapshots lose encryption → **False** (*they stay encrypted always*)  
- Default encryption applies to old volumes → **False** (*only future volumes*)  

---

## Final Thoughts

**EBS encryption is your zero-effort seatbelt.**  
You turn it on once — and forget it. But when something goes wrong, it’s the barrier that keeps your data sealed.

**It doesn’t prevent access.**  
But it ensures that **access doesn’t equal understanding**.  
Even a full volume dump is worthless without **KMS** keys and **IAM** permissions.

**In the world of cloud breaches, encryption isn’t the only layer — but it’s the last one that matters.**

**SnowySec** uses it for everything — boot, backup, batch jobs, even the bastion host.

Because *“unreadable data is unstealable data.”*
