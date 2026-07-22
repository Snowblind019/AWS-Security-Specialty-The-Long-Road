# AMI Hardening

An Amazon Machine Image (AMI) is the template an EC2 instance is cloned from: OS, installed software, configuration, and baked-in packages. Because every instance inherits the image, an insecure AMI is a scaling vector: one unpatched CVE, one open port, one permissive user, replicated across the whole fleet from first boot. Hardening means locking the image down before it is used, so anything launched from it starts in a secure, production-grade posture instead of being patched into compliance afterward. The thing to hold onto: hardening is a build-time control, not a runtime one. You are securing the mold, not each stamped part, and the exam almost always wants the golden-image pipeline over per-instance remediation.

## How it works

- **Start from a trusted base.** Amazon Linux 2023, Ubuntu LTS, RHEL, or a Marketplace CIS pre-hardened base image. Not random community AMIs, which are an unvetted supply-chain risk.
- **Apply the hardening layer.** Disable unused services, ports, and users; enforce file permissions, auditd/journald logging, and SELinux or AppArmor. In a pipeline this is an AWSTOE component (a YAML build step), or an AWS-managed **CIS Level 1** or **STIG** hardening component so you are not maintaining custom scripts.
- **Patch during the build.** `dnf update` / `apt upgrade`, strip stale packages, refresh monitoring agents. The image is patched once; instances launch already current.
- **Bake in the security tooling.** SSM Agent (so you can drop SSH entirely), CloudWatch Agent, and the config for GuardDuty and Inspector coverage. Agent presence is a build-time guarantee, not a per-instance hope.
- **Enforce the instance-metadata and disk controls.** IMDSv2-only in the launch template, EBS encryption on by default with a CMK, root login disabled.
- **Scan before you publish.** Run **Amazon Inspector** (or OpenSCAP / CIS-CAT) against the build instance. The pipeline distributes only if the scan passes; a Critical or High finding halts it.
- **Create and tag the image.** `aws ec2 create-image` for one-offs, **EC2 Image Builder** for a repeatable pipeline. Tag `hardened=true`, `cis_level=1`, stage, and version.
- **Scope and rotate.** Keep AMIs private or account-scoped, rebuild on a cadence, and store the current image ID in **SSM Parameter Store** so launch templates resolve "latest hardened" instead of a pinned stale ID.

## AMI hardening vs the rest of the compute-image stack

| | EC2 Image Builder | Manual AMI (`create-image`) | Packer (self-managed) | SSM Patch Manager |
|---|---|---|---|---|
| Model | Automated golden-image pipeline | One-off snapshot | Automated, you run it | Patches running instances |
| Repeatable / versioned | Yes, semantic versions | No | Yes | N/A |
| Built-in hardening + CVE scan | CIS / STIG components plus Inspector | No | You script it | Patches, does not harden |
| Distribution | Multi-account, multi-Region | Manual copy | You script it | In place |
| Best for | Immutable, compliant image supply chain | Quick throwaway | Multi-cloud builds | Keeping live fleets current |

## What gets tested

- **Golden image over per-instance work.** When a scenario has a fleet needing a consistent secure baseline, pick EC2 Image Builder, not "SSH in and patch each one" and not "SSM Patch Manager." Patch Manager keeps *running* instances current; it does not produce a hardened image.
- **CIS vs STIG components.** Both are AWS-managed hardening components. STIG components are free. CIS hardening runs through a Marketplace CIS subscription (there is a cost), and CIS pre-hardened base images / components are AMI-only, not container recipes.
- **Where the CVE scan lives.** Inspector is the assessment step inside the build and the continuous scanner on running instances. It is not the thing that hardens; it is the gate that proves hardening worked.
- **The remediation loop.** Inspector High/Critical finding fires an EventBridge rule that reruns the Image Builder pipeline and republishes a fresh image. Recognize this as the "how do we keep images from drifting" answer.
- **IMDSv2 and SSM as distractors.** Enforcing IMDSv2 and replacing SSH with Session Manager are hardening measures set at build time, frequently the "more correct" option versus a security-group or NACL change that only narrows the blast radius.
- **Sharing scope.** Hardened AMIs stay private or account-scoped, shared cross-account with explicit launch permissions or RAM. "Make the AMI public" is always wrong in a compliance scenario.

## Limitations

- Hardening secures the image at build time only. Configuration drift, runtime compromise, and new CVEs published after the build are not covered, which is why Inspector on running instances and a rotation cadence are mandatory, not optional.
- AWS-managed STIG components are fixed with no parameters. If they break an application you cannot disable a single finding ID; you clone the component and scope it down yourself.
- STIG and CIS components scan and remediate against a baseline, but AWS does not warrant that the resulting image is certified compliant. Final sign-off is your compliance team's, not the pipeline's.
- Image Builder automates AMIs and container images but does not patch already-running fleets. Pairing it with SSM Patch Manager (or immutable redeploys) covers the gap between rebuilds.
- The pipeline itself is attack surface. Build in an isolated subnet with a scoped instance profile, or the build environment becomes the weak link in the image supply chain.