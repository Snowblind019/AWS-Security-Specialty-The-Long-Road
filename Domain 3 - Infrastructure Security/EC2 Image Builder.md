# Amazon EC2 Security

Amazon EC2 gives you virtual machines: pick an AMI, an instance type, and a VPC, and AWS boots the instance. The security consequence is the shared-responsibility line. AWS owns the hypervisor, hardware, and facility; you own everything inside the guest, the OS and patches, the IAM role it carries, the keys, the firewall rules, the software, and the logging. Nothing inside the instance is secured for you by default. The thing to hold onto: an EC2 instance is a bundle of an identity (its role), a network position (its ENIs and security groups), and a metadata endpoint, and almost every EC2 exam scenario is really asking you to shrink the blast radius of one of those three when the box is compromised.

## How it works

- **Instance role and profile.** An instance assumes an IAM role at boot via an **instance profile**. Least privilege per purpose, never `s3:*`/`kms:*`/`ec2:*`, always resource-scoped. Restrict `iam:PassRole` so pipelines cannot attach an over-broad role, and watch role-credential retrieval in CloudTrail.
- **IMDSv2.** The instance metadata service hands out the role's credentials. IMDSv1 is a plain GET, so an **SSRF** flaw lets an attacker fetch those credentials (the Capital One 2019 pattern). **IMDSv2** requires a session token via PUT and honors a hop limit. Enforce `http_tokens=required`, set **hop limit = 1** so a container cannot reach the host's metadata, and set the **account-level IMDS default** (per Region) so new launches are IMDSv2-only. Enforce it org-wide and non-overridable with an Organizations **declarative policy** (`http_tokens_enforced`). Watch the `MetadataNoTokenRejected` CloudWatch metric for lingering IMDSv1 callers.
- **Host access.** Prefer **SSM Session Manager**: no inbound port 22, IAM-based auth, full session logging to CloudWatch/S3, CloudTrail auditing. Otherwise EC2 Instance Connect with ephemeral keys. Remove standing `authorized_keys`, restrict source IPs, and lock the **EC2 Serial Console** (a bare-metal/Nitro troubleshooting path abused to bypass network monitoring).
- **Network.** **Security groups** are stateful, allow-only, applied at the ENI; default egress is open. **NACLs** are stateless, allow and deny, ordered, applied at the subnet. Scope SGs per workload, reference other SGs instead of CIDRs, deny broad inbound, restrict egress to required destinations, alert on any `0.0.0.0/0` ingress or egress.
- **AMI hygiene.** Launch from hardened golden AMIs (CIS/Inspector-scanned, no embedded secrets, root SSH login off), build them from version-controlled Packer/Ansible, tag with owner and patch status, and restrict which AMIs can be used with the **Allowed Images** declarative policy.
- **Encryption.** Enable **EBS encryption by default** at the account/Region level so every new volume and snapshot copy is encrypted regardless of the source AMI or automation. Block public EBS snapshot sharing (declarative policy).
- **Monitoring.** Instances are a black box until you add the **CloudWatch Agent** (metrics and OS logs like `/var/log/secure`), **SSM Agent** (commands, patching, sessions), **Inspector** (OS and app CVE scanning), and **GuardDuty** (crypto-mining, port scans, credential exfiltration, anomalous traffic). These are opt-in.
- **Patching.** EC2 is not patched for you. **SSM Patch Manager** with patch baselines, `PatchGroup` tags, and maintenance windows, tracked on the SSM compliance dashboard.

## Security groups vs NACLs (the recurring EC2 network split)

| | Security group | Network ACL |
|---|---|---|
| State | Stateful (return traffic auto-allowed) | Stateless (must allow both directions) |
| Rules | Allow only | Allow and deny |
| Scope | ENI / instance | Subnet |
| Evaluation | All rules, most-permissive | Numbered order, first match |
| Default egress | Open | Allow all (default NACL) |
| Best for | Per-workload allow-listing | Coarse subnet-wide deny (e.g. block a CIDR) |

## What gets tested

- **IMDSv2 defeats SSRF credential theft.** "App was tricked into fetching its own role credentials" or any Capital-One-style SSRF is answered by enforcing IMDSv2 and hop limit 1, not by tightening the security group. Know that the account default plus a declarative policy makes it non-overridable org-wide.
- **Session Manager over SSH/bastion.** "Shell access with no inbound ports, no key management, and an audit trail" is SSM Session Manager. A bastion + SSH still needs an open port and does not log keystrokes by default.
- **Instance profile scope is the blast radius.** A compromised instance can do exactly what its role allows. The fix for over-reach is a scoped role plus `iam:PassRole` control, not a network change.
- **SG vs NACL selection.** Per-instance allow-listing and SG-to-SG references are security groups. "Block this specific malicious CIDR across a whole subnet" is a NACL deny rule, which SGs cannot express.
- **EBS default encryption is preventative.** Enforcing at rest for all new volumes is the account/Region **encryption by default** setting (and Config `encrypted-volumes` to detect drift), which also covers volumes from an unencrypted source AMI.
- **Declarative policies for durable EC2 posture.** IMDSv2 default, blocked public snapshots, allowed images, serial console, and VPC block-public-access are enforced as non-overridable org defaults via declarative policies, distinct from an SCP that denies an API call. Recognize declarative policy as the "stays enforced even as new accounts/instances appear" answer.
- **Detection is opt-in.** A "no alarm fired" scenario usually means CloudWatch Agent, Inspector, and GuardDuty were never enabled. The remediation is enabling them, since EC2 emits almost nothing security-relevant on its own.

## Limitations

- The account-level IMDS default and instance-launch settings can be overridden per instance; only the Organizations **declarative policy** makes IMDSv2 truly non-overridable. An account default alone is not fully preventative.
- Security groups cannot deny. If the requirement is an explicit block (a bad CIDR, a compromised range), that is a NACL or a firewall, not an SG.
- GuardDuty and Inspector detect, they do not prevent. They shorten time-to-detection but the exploit still runs; prevention is hardening, least privilege, and IMDSv2.
- Patch Manager and the CloudWatch/SSM agents must be installed and scheduled before an incident. Absent agents mean no patch compliance and no forensics, and none of it is on by default.
- EBS default encryption applies only to new volumes and snapshot copies, not existing ones. Turning it on does not retroactively encrypt what is already there.
- Immutable replacement (destroy and rebuild from a golden AMI in an ASG) is the containment pattern for a compromised instance, but it assumes state is externalized; a stateful box loses data if simply rebuilt.