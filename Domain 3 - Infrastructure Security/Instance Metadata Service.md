# Instance Metadata Service (IMDS)

## What Is the Service

The **Instance Metadata Service (IMDS)** is a local web service running at `http://169.254.169.254` on every EC2 instance. It allows the instance to query information about itself, including:

- **Instance ID, IP, AMI, availability zone**
- **IAM Role credentials** (temporary)
- **User data**
- **Tags** (if configured)
- **Network interfaces**
- **Instance store metadata**

This is crucial for bootstrapping and for **applications that need temporary AWS credentials** (e.g., when using an instance role instead of hardcoded secrets). It’s a key building block for “credential-less” access to AWS APIs from within EC2.

But here’s the catch: **IMDS also introduces serious security risks if left unprotected** — attackers can use **SSRF** (Server-Side Request Forgery) or malware to query the metadata endpoint and extract IAM role credentials, enabling privilege escalation or lateral movement.

---

## Cybersecurity Analogy

Think of **IMDS** as a *lockbox* bolted inside your EC2 instance. It contains your badge, your name tag, and a one-time-use credential card that expires every few hours. You don’t carry these credentials in your pocket — you ask the *lockbox* when you need them.

But if an attacker inside the app finds a way to pry open that *lockbox* (via **SSRF** or insecure code), they can impersonate your identity in AWS.

## Real-World Analogy

Imagine **Winterday** sets up an EC2 to run a web server. The server needs access to S3, so the instance is given an **IAM role**. Instead of **hardcoding** long-term credentials, the app reaches into `169.254.169.254` and grabs temporary tokens from the metadata endpoint.

Everything runs great… until a remote attacker exploits a bug in the web app that lets them make **arbitrary HTTP requests**.

They quietly query:

```bash
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/YourRole
```

Boom — they now have AWS credentials with full permissions. This isn’t theoretical — it’s how the **Capital One** breach happened.

---

## How It Works (IMDSv1 vs IMDSv2)

| Version  | Access Method                  | Vulnerability         | Protection Mechanism            |
|----------|--------------------------------|------------------------|----------------------------------|
| IMDSv1   | Simple HTTP GET request        | SSRF & no auth         | None                             |
| IMDSv2   | Two-step PUT-then-GET w/ token | Token required (TTL)   | Enforced hop limit, token TTL    |

### IMDSv2 Flow:

1. App sends a **PUT** request to **IMDS** asking for a token (adds a hop limit).
2. App includes that token in a **GET** request to fetch metadata (e.g., **IAM creds**).
3. The token expires after a set **TTL** (default 6 hours).

### Key Differences:

- **IMDSv2 uses session-based tokens**
- **Adds protection against SSRF attacks**
- **Can block metadata access from misbehaving processes**

---

## Security Risks of IMDSv1

| Risk Type           | Exploit Example                                                                |
|---------------------|---------------------------------------------------------------------------------|
| **SSRF Attacks**    | Web server with SSRF bug fetches **IAM** role **creds** from metadata endpoint |
✔️ Require IMDSv2 on all EC2s and launch templates
✔️ Use minimal **IAM roles** (least privilege)

✔️ Use **egress filtering** to block unknown IPs reaching `169.254.169.254`
✔️ Use host-based firewalls (`iptables`) to restrict metadata access to known processes
✔️ Use **EC2 Instance Profiles** instead of long-term creds
✔️ Scan for IMDSv1 use with **Inspector**, **Config**, or custom **Lambda** checks

---

## How to Enforce IMDSv2 (Examples)

### Via AWS CLI:

```bash
aws ec2 modify-instance-metadata-options \
--instance-id i-12345678 \
--http-endpoint enabled \
--http-tokens required
```

### Or in Launch Template (recommended):

- Set **Metadata Options**:
  - **Http tokens**: required
  - **Http endpoint**: enabled
  - **Http put response hop limit**: 1

---

## Pricing Models

**IMDS** itself is **free** — it’s part of EC2.
However, security tools like:

- **AWS Config Rules** (to detect IMDSv1)
- **Amazon Inspector** (to flag metadata risk)
- **AWS Systems Manager Compliance Scans**

...may have associated costs if enabled at scale.

---

## Real-Life Example

**Snowy** is managing 100 EC2s across 3 environments. After a **PenTest** report exposes one **dev** EC2 with **SSRF** and IMDSv1 enabled, **Snowy** rolls out:

- A script to update all launch templates to require IMDSv2
- An **AWS Config** rule to detect new instances allowing IMDSv1
- A scheduled **Lambda** to scan metadata access logs for suspicious usage

He also trains developers to use **boto3’s IMDSv2-compatible credential fetcher** so pipelines don’t break.

Within a week, they’ve enforced IMDSv2 across the fleet and reduced metadata surface risk to near-zero — all without downtime.

---

## Final Thoughts

The Instance Metadata Service is powerful — but also dangerous if left wide open.

**IMDSv2 is not just a recommendation — it’s your EC2 firewall for credentials.**

Leaving IMDSv1 enabled in 2025 is like running a Linux box with **Telnet** and no firewall. It only takes one **curl from inside the box** to lose your cloud.

✔️ Require IMDSv2
✔️ Use IAM roles with least privilege
✔️ Monitor access
✔️ Educate your team

**Security isn't about complexity. It's about defaults — and IMDSv2 should be yours.**
