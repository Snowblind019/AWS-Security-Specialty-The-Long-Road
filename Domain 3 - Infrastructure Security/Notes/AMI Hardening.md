# AMI Hardening

## What Is the Service

An **Amazon Machine Image (AMI)** is a preconfigured template used to launch EC2 instances.  
It includes the operating system, installed software, custom configurations, and environment-specific packages.  
Basically, it’s the blueprint from which your servers are cloned.

But here’s the catch:  
If your AMI is **insecure**, every instance launched from it **inherits those vulnerabilities** — misconfigurations, old libraries, unpatched exploits, open ports, permissive users. This becomes a **scaling vector for risk**.

**Hardening an AMI** means locking it down before it's used, so any EC2 launched from it starts life with a **secure, production-grade posture**.  
It’s especially critical in:

- Production environments  
- Regulated workloads (PCI, HIPAA, FedRAMP, etc.)  
- Multi-account or CI/CD-driven infrastructure  
- Zero-trust networks  

This makes AMI Hardening a **baseline security control**, not a nice-to-have.  
It’s *“secure by design.”*

---

## Cybersecurity Analogy

Think of AMIs like **manufacturing molds**.  
If you’re stamping out hundreds of machines using a **flawed mold** — every product is compromised from the jump.

Hardening your AMI is like reinforcing that mold with:

- strict quality control  
- tamper-proofing  
- anti-defect guidelines  

Now every product you create starts **secure**.

## Real-World Analogy

Imagine Blizzard is spinning up **300 EC2s** to power an upcoming **multiplayer event**.

Instead of patching each one individually, **Snowy** bakes a secure, hardened AMI:

- All unnecessary packages stripped out  
- Only port 443 open  
- SSH disabled; SSM only  
- CloudWatch and GuardDuty agents installed  
- Audit logging enabled  
- IMDSv2 enforced  

**Result?**  
Every server is consistent, monitored, encrypted, and compliant — from the first boot.

---

## How It Works (What You Do)

Hardening an AMI involves several steps, typically **automated in a pipeline**:

### 1. Start with a secure base image

- Prefer **Amazon Linux 2/2023**, **Ubuntu LTS**, **RHEL**, etc.  
- Avoid random Marketplace or community images.

### 2. Apply security configurations

- Disable unused services, ports, users  
- Enforce file permissions, logging, SELinux/AppArmor

### 3. Update and patch

- Run `yum update` or `apt upgrade`  
- Remove stale packages, update antivirus/monitoring agents

### 4. Install monitoring + security tooling

- SSM agent, GuardDuty detectors, CloudWatch logs  
- CIS benchmark scripts or Inspector scans

### 5. Cleanup

- Remove `.bash_history`, temporary credentials  
- Ensure no secrets are baked in

### 6. Scan the hardened instance

- Run **Amazon Inspector** or **CIS-CAT**  
- Confirm zero critical vulnerabilities

### 7. Create the hardened AMI

- Use `aws ec2 create-image` or **EC2 Image Builder**  
- Tag it:  
  - `hardened=true`  
  - `cis_level=1`  
  - `owner=snowy`

### 8. Restrict access

- Keep AMIs **private** or **scoped by account**  
- Don’t share hardened AMIs publicly unless absolutely necessary

### 9. Version and rotate

- Rebuild AMIs on a regular cadence (weekly/monthly)  
- Use **SSM Parameter Store** to store “latest hardened AMI ID”

---

## Pricing Models

AMI hardening has **no direct cost**, but related services include:

| Service              | Cost Factor                                |
|----------------------|---------------------------------------------|
| EC2 Image Builder    | No cost for the service itself              |
| EC2 Instance (build) | Normal EC2 pricing during build             |
| Amazon Inspector     | Per-resource scanning fee                   |
| CloudWatch/SSM       | Charges for logs, metrics, etc.             |

---

## Other Key Details

| Area             | Best Practice Example                                                       |
|------------------|------------------------------------------------------------------------------|
| IMDS             | Enforce **IMDSv2 only** in launch template                                   |
| Root Login       | Disable root login and use non-root users                                    |
| SSH              | Remove SSH entirely if using Session Manager                                 |
| Unused Packages  | Strip out FTP, Telnet, NFS, rpcbind, netcat, etc.                            |
| Logging          | Pre-configure auditd, journald, and ship logs to CloudWatch                  |
| EBS Encryption   | Enable by default with CMK or AWS-managed key                                |
| Marketplace      | Use **vetted, verified hardening partners only** (CIS, STIG, etc.)           |
| Vulnerability Scan | Amazon Inspector or OpenSCAP                                               |
| Lifecycle Control | Tag AMIs by version, stage (dev, prod), and expiration timestamp            |

---

## Real-Life Example

**Snowy** works on a **regulated healthcare workload (HIPAA)**.  
EC2s must be:

- Log-monitored  
- Agent-backed  
- No direct shell access  
- Disk-encrypted  
- Network-restricted  

Instead of doing this per-instance, Snowy automates a **secure AMI pipeline** using **EC2 Image Builder**.

Weekly, it:

1. Spins up base **Amazon Linux 2023**  
2. Applies **Ansible scripts**  
3. Runs **Amazon Inspector**  

- If it **passes** → AMI is versioned and published  
- If it **fails** → pipeline halts  

Now dev teams just use the `blizzard-prod-ami` and launch secure instances **without thinking about security** — because it’s **baked in**.

---

## Final Thoughts

Hardening AMIs isn’t optional anymore.  
It’s **table stakes** for secure cloud infrastructure.

If your EC2 fleet is running on:

✖️ Default images  
✖️ Community builds  
✖️ Manual patching  

...you’re flying blind.

**Hardened AMIs** are how you scale **compliance**, **visibility**, and **secure defaults** from Day 0.  
It’s not about **perfection** — it’s about **predictable, audit-ready baselines**.

