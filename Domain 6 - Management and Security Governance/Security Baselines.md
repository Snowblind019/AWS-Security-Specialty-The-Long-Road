# Security Baselines in AWS

A security baseline is the defined minimum set of controls every account and workload must meet, stated explicitly rather than assumed. It is what turns "we follow best practices" into a checkable claim: root has MFA or centralized root access management, CloudTrail is on in every Region with a tamper-resistant destination, Config and GuardDuty are enabled, encryption at rest and in transit is enforced, no security group exposes administrative ports to the internet, IMDSv2 is required, and secrets live in Secrets Manager rather than environment variables. The security value is not in the list, which is broadly the same everywhere, but in whether the list is expressed as enforceable controls, measured continuously, and evidenced on demand. A baseline that exists only in a wiki is a description of what somebody intended. The thing to hold onto: a baseline becomes real at the point it is expressed as a control, measured by a service, and provable to an auditor.

## How it works

**Baselines are sourced, not invented.** The AWS Security Reference Architecture defines the multi-account structure and where each security service belongs. The Well-Architected Security Pillar supplies design principles. CIS AWS Foundations Benchmark, AWS Foundational Security Best Practices, NIST 800-53, and PCI DSS supply the specific, testable controls. Starting from one of these and adding organization-specific requirements is faster and more defensible than writing controls from scratch.

**They apply in four layers, and each layer needs a different mechanism.**

- **Organization.** SCPs and RCPs for permission ceilings, declarative policies for pinned service configuration, tag and backup policies, Region restriction. This layer produces guarantees, because nothing inside the organization can bypass it.
- **Account.** Delivered at bootstrap: organization CloudTrail coverage, Config recorder, GuardDuty and Security Hub through delegated administrator auto-enable, account-level settings such as EBS encryption by default and S3 Block Public Access, baseline IAM roles and Identity Center permission sets.
- **Workload.** IaC modules, launch templates, Service Catalog products, and hardened AMIs built with EC2 Image Builder using CIS or STIG hardening components.
- **Runtime.** SSM Patch Manager with patch baselines and maintenance windows, Amazon Inspector for vulnerability findings, GuardDuty for behavior.

**Measurement runs through Security Hub and Config.** Security Hub enables standards such as FSBP, CIS, NIST 800-53, and PCI DSS, produces per-control status and a security score, and with central configuration applies standards and control settings to OUs from a delegated administrator rather than account by account. AWS Config conformance packs deploy rule sets organization-wide and are the right vehicle for custom rules that no standard covers.

**Enforcement is chosen per control, deliberately.** Some baseline items can be prevented outright, some can only be detected and remediated, and some are proactive checks in a deployment path. The mapping decision is the actual engineering work: prevent where a condition key exists, pin where a declarative policy covers the attribute, detect and auto-remediate where neither does.

**Remediation is part of the baseline, not a follow-up.** Config rules paired with SSM Automation documents, or EventBridge routing Security Hub findings to Lambda and Step Functions, are what make a detective control converge on compliance rather than accumulate findings.

**Exceptions are managed, time-bound, and visible.** Security Hub controls can be disabled per standard or per account, Config rules can scope out resources by tag, and both leave a record. An untracked exception is indistinguishable from a failure, so the exception register matters as much as the control list.

**Evidence closes the loop.** AWS Audit Manager collects Config and Security Hub verdicts, CloudTrail activity, and manual documents against framework controls and packages them into a signed report. AWS Artifact supplies the AWS side of the same picture. Together they answer the auditor without a screenshot exercise.

**Baselines are versioned and rolled out.** A new control is announced, monitored in detect-only mode, remediated for existing violations, then enforced preventively. Skipping the monitoring phase is how a baseline change becomes an outage.

## Comparison

| Source or standard | What it provides | Where it is enforced or measured | Typical use |
| --- | --- | --- | --- |
| AWS Security Reference Architecture | Multi-account structure and service placement | Design time | Deciding which account owns which security function |
| Well-Architected Security Pillar | Principles and review questions | Design and review | Architecture review, not scored compliance |
| AWS Foundational Security Best Practices | AWS-specific control set, broad service coverage | Security Hub standard | Default technical baseline for AWS-native estates |
| CIS AWS Foundations Benchmark | Externally recognized scored benchmark | Security Hub standard, Config conformance pack | Audits and customers who ask for CIS specifically |
| NIST 800-53 and PCI DSS | Regulatory control sets | Security Hub standard, Config conformance pack, Audit Manager framework | Regulated workloads and formal audits |
| Control Tower controls | Preventive, detective, and proactive controls per OU | Organizations, Config, CloudFormation Hooks | Governed landing zones |
| Custom Config rules | Organization-specific requirements | Config conformance pack | Anything no published standard covers |

## What gets tested

- **FSBP versus CIS.** FSBP is the broader AWS-specific default and covers more services. CIS is the externally recognized benchmark to enable when an auditor or customer names it. Enabling both is normal and produces overlapping findings, which consolidated control findings in Security Hub deduplicates.
- **Organization-wide standards.** Security Hub central configuration from a delegated administrator applies standards and control settings across OUs, including new accounts. Per-account enablement is the wrong answer at scale.
- **Conformance packs versus standards.** Custom or organization-specific rules go in a Config conformance pack deployed from the delegated administrator. Published benchmarks go through Security Hub standards.
- **Evidence versus posture.** Security Hub shows current posture. Audit Manager assembles the evidence package for an audit. Artifact supplies AWS's own attestations. Questions distinguish these three cleanly.
- **Preventive versus detective mapping.** "Must not be possible" resolves to SCP, RCP, declarative policy, or an account-level setting. "Must be identified and corrected" resolves to Config rules with SSM Automation remediation.
- **Hardened images.** EC2 Image Builder with hardening components and a pipeline is the answer for maintaining golden AMIs, not manual snapshots.
- **Patching as a baseline control.** SSM Patch Manager with patch baselines and maintenance windows, with compliance reported to Config and Security Hub. Inspector reports vulnerabilities, it does not patch them.
- **New accounts.** Baseline coverage for future accounts comes from OU-attached policies, StackSets automatic deployment, and delegated administrator auto-enable, never from a per-account checklist.
- **Exceptions.** Disabling a specific Security Hub control for a specific account is the supported answer when a control genuinely does not apply, rather than ignoring the finding.

## Limitations

- Standards overlap and conflict. Running FSBP, CIS, and PCI simultaneously produces duplicated and occasionally contradictory findings, and reconciling them is ongoing work.
- Control coverage is service-limited. New AWS services routinely appear in an estate before any standard has controls for them, leaving a gap that only custom rules fill.
- Detective controls report, they do not converge. Without remediation wired in, a baseline produces a growing findings backlog that eventually gets ignored, which is worse than no measurement.
- Cost scales with coverage. Config recording, Security Hub controls, GuardDuty, Inspector, and Audit Manager across every account and Region is a significant recurring expense, and scope reduction is where baselines quietly erode.
- Preventive controls only bind forward, so every baseline version change leaves an existing non-compliant population requiring separate, sometimes destructive, remediation.
- Exception processes tend to become permanent. A time-bound exception with no expiry mechanism is just a weaker baseline that still reports green.
- A baseline is a floor. Meeting it says nothing about threat modeling, application security, data classification, or incident response capability, and a fully compliant environment can still be architected badly.