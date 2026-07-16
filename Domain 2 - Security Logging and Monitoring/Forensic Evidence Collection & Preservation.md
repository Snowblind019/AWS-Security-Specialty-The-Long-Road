# Forensic Evidence Collection & Preservation

The incident-response discipline of capturing evidence in a reliable, untampered, admissible way and preserving it with integrity and chain of custody, before any analysis. In AWS this is a specific sequence: isolate the affected resource without destroying it, capture volatile data before non-volatile, snapshot EBS, and lock the evidence away in a dedicated forensics account. This is Domain 1 (Incident Response) territory, and the exam tests the AWS-specific mechanics and the ordering, not generic DFIR prose.

The governing rules are preserve first and analyze later, order of volatility (RAM before disk), and chain of custody. In AWS that translates to a sequence: **isolate the instance without stopping it, revoke its credentials, capture memory, snapshot EBS, then move copies to an isolated forensics account** for analysis. Terminating, stopping, or rebooting destroys volatile evidence, so the order is not optional.

## How it works

- **Preserve first, automate**: drive collection with **SSM Automation runbooks** or Lambda rather than logging into the host, because every manual command alters state (overwrites RAM, rotates logs, changes timestamps). Automation also makes the process repeatable and preserves chain of custody.
- **Isolate, do not terminate**: enable **termination protection**, attach a **deny-all forensic security group**, **detach the instance from its Auto Scaling group** (or set it to Standby) so it is not replaced or terminated, and **revoke the instance role's sessions** (a deny policy on tokens issued before now) because the role's temporary credentials may already be exfiltrated. Do not stop, reboot, or patch yet.
- **Order of volatility, memory first**: capture **RAM before disk**, because stopping the instance loses memory and any instance-store volumes (EBS persists). Acquire memory on the live host via **SSM Run Command** with an acquisition tool (**LiME** or **AVML** on Linux, **WinPmem** on Windows). Memory can hold decryption keys, tokens, network state, and in-memory malware.
- **Disk**: take **EBS snapshots** for a bit-for-bit copy. Copy or share the snapshot to a **dedicated forensics account**. If the volume is KMS-encrypted, the forensics account needs a **grant on the KMS key** (or the snapshot must be re-encrypted with a shared key) or it cannot read it. Create a volume from the snapshot and attach it read-only to a forensic workstation. Analyze copies, never originals.
- **Metadata and context**: capture instance ID, tags, AMI, the IAM role and its policies at the time, security group and NACL rules, and Auto Scaling activity. This is what lets you reconstruct the resource and reason about whether it was misconfigured, drifted, or changed by hand.
- **Logs with integrity**: pull from centralized stores (CloudTrail, VPC Flow Logs, S3 access logs, application logs), **SHA-256 hash** every artifact, and store in an **immutable S3 bucket (Object Lock compliance mode plus versioning)** in the forensics account.
- **Chain of custody**: maintain an evidence log of who collected what, when, and where it is stored, tag snapshots with the incident ID, let CloudTrail record actions taken on the evidence, keep hash records tamper-proof, and analyze only copies.

## Collect in order of volatility

| Order | Evidence | Where it lives | How to collect | Lost if you |
|---|---|---|---|---|
| 1 | Memory (RAM) | Volatile, in the running instance | SSM Run Command with LiME, AVML, or WinPmem | Stop, reboot, or terminate |
| 2 | Network and session state | Volatile | Capture with memory, plus VPC Flow Logs | Stop or reboot |
| 3 | Disk | EBS (persists), instance store (volatile) | EBS snapshot, copy to forensics account | Terminate (loses instance store) |
| 4 | Logs and metadata | Centralized (CloudTrail, S3, CloudWatch) | Pull, hash, store immutable | Let rotation or deletion run |

## What gets tested

- Isolate, do not terminate. For a compromised EC2 instance: termination protection on, a deny-all forensic security group, detach from the Auto Scaling group so it is not replaced, and revoke the instance role's credentials. Stopping or terminating destroys memory and instance-store data.
- Order of volatility: capture RAM before disk, because a stop or reboot loses volatile memory and instance-store volumes while EBS persists. Memory holds keys, tokens, and in-memory malware.
- The EBS snapshot is the disk-evidence primitive. Copy it to a dedicated forensics account, and if the volume is KMS-encrypted the forensics account needs a grant on the key (or a re-encrypt with a shared key). Always analyze a copy.
- Integrity and immutability are the chain-of-custody answer: SHA-256 hash every artifact and store it in S3 with Object Lock (compliance mode, WORM) and versioning.
- Automate collection with SSM Automation or Lambda to keep it consistent, avoid logging into the host, and preserve chain of custody.
- Distinguish acquisition tools (LiME, AVML, WinPmem, run on the live host) from analysis tools (Volatility, run later on the copy).
- Isolate evidence in a dedicated forensics or security account for separation of duties and a clean chain of custody.

## Limitations

- You get one shot at volatile data. A reboot, stop, or terminate loses memory and instance-store contents permanently.
- Encrypted EBS complicates cross-account evidence sharing. Without a KMS grant, the forensics account cannot read the snapshot.
- Memory acquisition still touches the live host slightly, so document exactly which tool ran, when, and its hash.
- Evidence quality is bounded by logging coverage. If CloudTrail data events or VPC Flow Logs were not enabled, the trail has gaps, which ties this back to your logging and scoping practices.
- Forensics is response, not prevention, and Object Lock retention in compliance mode cannot be shortened once set, so choose retention deliberately.