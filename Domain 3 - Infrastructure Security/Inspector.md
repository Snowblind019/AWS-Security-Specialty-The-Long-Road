# Inspector

A managed, continuous vulnerability scanner for compute: EC2 instances, ECR container images, and Lambda functions/layers. It finds known software vulnerabilities (CVEs) in your packages and prioritizes them by exploitability and exposure. Turn it on and it keeps scanning as images, instances, and functions change.

The one-line role: Inspector scans compute for known vulnerabilities (CVEs). That is its lane — not threat detection (GuardDuty), not data classification (Macie), not config compliance (Config). It is continuous and event-driven: it re-scans automatically when a new CVE is published, so a "clean" resource can light up later without any change on your side.

## How it works

- **EC2**: scans OS packages and language libraries via the **SSM Agent** (the instance must be SSM-managed); an **agentless** mode (EBS-snapshot based) covers instances without the agent.
- **ECR**: scans image layers on **push**, then **re-scans** existing images when new CVEs are published (continuous), within a configurable scan duration.
- **Lambda**: scans function code and layers on publish/update and when new CVEs land.
- **Findings** include the CVE, affected package/version, path or layer, severity, and remediation (the fixed version). Delivered to **Security Hub** (ASFF) and **EventBridge**.
- **Prioritization** uses an Inspector score combining vulnerability severity with **exploit intel** and **network exposure** (is the EC2 instance internet-reachable). High-and-now usually means actively exploitable plus exposed.
- **Auto-close**: findings resolve automatically once the vulnerable version is gone (patched, rebuilt, layer bumped).

## Inspector vs the rest of the detection stack

| Service | Job |
|---|---|
| Inspector | Scans compute (EC2/ECR/Lambda) for CVEs |
| GuardDuty | Detects active threats from telemetry |
| Macie | Discovers sensitive data in S3 |
| Config | Resource configuration compliance |
| Security Hub | Aggregates findings, posture scoring |

## What gets tested

- Inspector is the "scan for vulnerabilities / CVEs / outdated packages" answer, across EC2, ECR images, and Lambda. Match the verb: vulnerability scanning is Inspector, not GuardDuty (threats), Macie (data), or Config (configuration).
- EC2 scanning depends on the SSM Agent and the instance being SSM-managed; "Inspector isn't covering my EC2" usually means SSM is not set up (or use agentless mode).
- It is continuous and event-driven — it re-scans automatically when new CVEs are published, not a point-in-time scan.
- Findings route to Security Hub and EventBridge; wire High findings to SSM Patch Manager/Automation, image rebuilds, or layer bumps. Inspector auto-closes findings when the vuln is remediated.
- Network exposure feeds the priority score (internet-reachable vulns rank higher). The old standalone Inspector "network reachability assessment" is deprioritized in C03.
- Shift-left: integrate with CI/CD to block deploys on High/Critical container or Lambda findings.

## Limitations

- Covers EC2, ECR, and Lambda only — not arbitrary on-prem or unsupported resources.
- EC2 agent-based scanning needs SSM; gaps appear where SSM is not deployed (mitigated by agentless mode).
- Finds known CVEs in packages; it is not a SAST/DAST analyzer for your own application logic.
- Detection of vulnerabilities, not remediation — pair with SSM/CI to fix.