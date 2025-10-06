# AWS Snowball Edge

## What Is the Service

AWS Snowball Edge is a rugged, physical edge device used for offline data migration and edge computing in harsh, bandwidth-constrained, or disconnected environments. It’s part of the AWS Snow family — purpose-built for situations where cloud connectivity is limited or where large-scale data transfer over network just isn’t viable.

There are two main variants:

- **Snowball Edge Storage Optimized** – for large-scale, petabyte-level data transfer and backup
- **Snowball Edge Compute Optimized** – for running EC2 instances, Lambda functions, or machine learning models at the edge

It’s basically a secure, portable AWS mini-data center that shows up in a suitcase — with tamper-resistant hardware, built-in encryption, and the ability to either migrate data to AWS or act as a remote compute node for disconnected edge operations.

**Snowy uses Snowball Edge when:**

- They need to transfer 100+ TB of log data from a remote POP with slow uplink
- They’re deploying EC2-based sensor processing in an oil field, military base, or ship at sea
- They need an air-gapped forensic archive temporarily processed and then uploaded to S3

---

## Cybersecurity Analogy

Think of Snowball Edge like a **locked armored briefcase with a full incident response lab inside**. Not only can it hold sensitive logs securely while in transit, but it can also analyze them on location — without needing internet access or exposing anything to a central SIEM.

It’s the equivalent of deploying a **mini SOC** into the field, letting it run localized detections or scans, then returning with a sealed chain-of-custody trail.

If S3 is your vault and EC2 is your brain, Snowball Edge is your **mobile brain-in-a-box**, hardened for rough environments and disconnected security workflows.

## Real-World Analogy

Imagine a security team working for a **telco** provider — they operate cell towers in rural areas with no fiber, poor backhaul, and highly sensitive subscriber metadata.

Once a month, a Snowball Edge device gets shipped out to the site:

- It ingests router logs, VPC mirrors, and access metadata from local gear
- Runs a pre-configured EC2 intrusion detection engine
- Flags anomalies
- Encrypts and stores the result
- Ships back to the main AWS Region
- AWS decrypts the data and loads it directly into S3

> No wide-area transfer. No need for full-time network connectivity. **Security and observability delivered without touching the internet.**

---

## How It Works

### Step-by-Step Flow:

1. **Order from AWS Console**
   - Choose between **Storage Optimized** (up to 80 TB usable) or **Compute Optimized** (for EC2/Lambda)

2. **Configure & Encrypt**
   - Define S3 buckets to preload or transfer to
   - Choose a **KMS** key (or use the default)
   - Data is encrypted **before** it hits the device

3. **AWS Ships the Device**
   - Tamper-evident, ruggedized chassis
   - LCD for tracking + USB management port

4. **Local Usage**
   - Connect via RJ45 or 10GbE to your network
   - Use **Snowball client** or **NFS interface** to upload/download data
   - If **Compute-Optimized**: deploy EC2 AMIs, run ML inference, stream logs, etc.

5. **Ship It Back**
   - Use provided shipping label
   - Once AWS receives it, they:
     - **Verify integrity**
     - **Decrypt with KMS**
     - **Load into designated S3 bucket**
     - **Securely wipe the device**

6. **Audit Logs**
   - All transfers are logged and available in **CloudTrail**
   - You can track chain-of-custody and full audit trail

---

## Security and Compliance Relevance

Snowball Edge is **built for secure environments by design**, with multiple layers of protection:

| **Feature**              | **Description**                                                  |
|--------------------------|------------------------------------------------------------------|
| **End-to-End Encryption**| All data is encrypted using **KMS** before transfer; device has **no plaintext access** |
| **Tamper-Evident Seals** | Physical security and tamper-proof hardware                      |
| **TPM (Trusted Platform Module)** | Protects encryption keys locally                        |
| **Chain of Custody**     | Full shipping, access, and erase logs                            |
| **Secure Erase**         | **NIST** 800-88 wipe after AWS ingestion                         |
| **IAM Access Control**   | Only authorized roles can load data to/from Snowball             |
| **FIPS Validated Crypto**| Meets common compliance frameworks (**FedRAMP**, **HIPAA**, etc.)|

> It’s one of the **few AWS services built for disconnected zones** with a security posture equivalent to cloud-native services.

---

## Pricing Model

**Snowball Edge pricing includes:**

- **Per-job fee**: Flat cost per device ordered
- **Data transfer time**: Additional cost if held >10 days
- **Shipping**: Paid by AWS (in most regions)
- **Optional compute cost**: EC2 or Lambda usage billed if used

> There are **no per-GB data transfer costs** like with internet-based uploads.

---

## Real-Life Example

**Snowy’s IR team** received a report of a **compromised SCADA system** in a hydroelectric facility deep in the mountains. There was no stable uplink, no cross-connect, and no chance of forwarding logs in real time.

They deployed a **Snowball Edge Compute Optimized** unit:

- Preloaded with forensic scripts, **YARA** rules, and a hardened EC2 instance
- Connected it to the local **SCADA** network via isolated switch
- Pulled logs, ran scans, and flagged firmware tampering
- Saved all results to the device
- Shipped it back to the SOC

Upon return, the data was decrypted, uploaded to a private **S3** bucket with **Object Lock**, and reviewed via **Athena**. A full incident report was generated using findings collected **entirely offline**, with full audit traceability and **zero cloud exposure** during the live forensics.

---

## Final Thoughts

**Snowball Edge is not just a “big USB drive”** — it’s a **battle-hardened field unit** that brings AWS security and compute to the farthest edges of your infrastructure.

In high-risk environments where network connectivity is poor, or compliance demands **physical isolation**, Snowball Edge offers:

- Secure, encrypted, auditable data migration
- Localized EC2 and Lambda processing
- Seamless integration with S3 and **KMS**
- Full alignment with security and compliance frameworks

> Whether you’re evacuating a POP, collecting logs from an **air-gapped** network, or running anomaly detection in a disaster zone —
> **Snowball Edge is what you ship when your cloud can’t reach the ground.**
