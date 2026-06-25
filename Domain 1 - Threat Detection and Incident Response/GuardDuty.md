# GuardDuty

AWS's managed threat detection service. It continuously analyzes AWS-native telemetry and emits findings about active misuse — credential compromise, C2 traffic, recon, data exfiltration. It taps its foundational sources directly, so there are no agents to deploy for the core detections and no logs you have to enable first.

The one-line role: GuardDuty detects active threats and generates findings. It is not prevention, not vulnerability scanning, not data classification, and not investigation — those are other services. Its foundational sources (CloudTrail management events, VPC Flow Logs, DNS query logs) are always-on and read independently; everything else is an opt-in protection plan.

## How it works

- **Foundational sources** (always on, no separate setup): CloudTrail management events, VPC Flow Logs, and DNS query logs. GuardDuty reads these directly — you do not need a trail or Flow Logs enabled, and an attacker disabling them does not blind it.
- **Protection plans** (opt-in, extra cost): S3 Protection (CloudTrail S3 data events), EKS Protection (audit logs), Malware Protection (agentless EBS scans, plus Malware Protection for S3), RDS login activity, Lambda network activity, and Runtime Monitoring agents for EC2/ECS/EKS.
- **Findings** carry a type (e.g. `UnauthorizedAccess:EC2/SSHBruteForce`, `Exfiltration:S3/ObjectRead`), severity, the implicated resource, and evidence (IP, geo, ASO, timeline). Route to **EventBridge**, **Security Hub**, **Detective**, SNS, or a SIEM.
- **Extended Threat Detection (ETD)**: correlates signals across sources and time (24-hour rolling window) into multi-stage **attack-sequence findings** of **Critical** severity, mapped to MITRE ATT&CK with remediation steps. On by default at no extra cost. S3-related sequences require S3 Protection to be enabled separately, and ETD ignores archived/suppressed findings.
- **Org-wide**: a delegated administrator auto-enrolls member accounts; central view of coverage and findings.
- **Suppression rules** mute known-benign patterns (but note they remove those findings from ETD correlation).

## GuardDuty vs the rest of the detection stack

| Service | Job |
|---|---|
| GuardDuty | Detects active threats, generates findings |
| Inspector | Scans for software vulnerabilities (CVEs) and unintended exposure |
| Macie | Discovers and classifies sensitive data in S3 |
| Detective | Investigates and scopes a finding |
| Security Hub | Aggregates findings, posture scoring |

## What gets tested

- GuardDuty is the "detect active misuse / threats" answer and the source of findings. Distinguish it from Inspector (vulnerabilities/CVEs), Macie (sensitive-data discovery), Detective (investigation), and Security Hub (aggregation). This distinction is heavily tested — match the verb in the question.
- Foundational sources are tapped directly: GuardDuty uses CloudTrail/VPC Flow/DNS without you enabling those logs, so stopping a trail does not stop GuardDuty.
- Protection plans (S3 data events, EKS, RDS, Lambda, Malware, Runtime) are opt-in and cost extra; enable per need.
- Findings drive automated response via EventBridge to SSM Automation/Lambda; "Investigate in Detective" is the scoping pivot; Security Hub centralizes.
- Extended Threat Detection produces correlated Critical attack-sequence findings and is on by default — but S3 attack sequences need S3 Protection enabled, and suppressed findings are excluded from correlation.
- Malware Protection scans EBS volumes (agentless) tied to suspicious findings; Malware Protection for S3 scans uploaded objects.
- Org-wide enablement uses delegated admin and auto-enroll.

## Limitations

- Detection, not prevention — it does not block; wire findings to EventBridge/SSM for containment.
- Reads AWS-native sources only; it is not a SIEM for arbitrary or custom logs.
- Protection plans are opt-in and add cost.
- Findings are signals, not proof — confirm in Detective before destructive action.