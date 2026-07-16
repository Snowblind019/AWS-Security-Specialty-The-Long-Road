# Incident Response Lifecycle

The structured process to prepare for, detect, contain, eradicate, recover from, and learn from security incidents, so response is controlled and repeatable rather than improvised. AWS aligns its **Security Incident Response Guide** to the **NIST SP 800-61** lifecycle. In the exam this is the backbone of the Incident Response domain, and the high-value skill is mapping each phase to the specific AWS services that carry it out.

The canonical model is NIST 800-61's four phases: **Preparation; Detection and Analysis; Containment, Eradication, and Recovery; and Post-Incident Activity**. Operators often split the middle into three, which is the SANS PICERL six-step view (the difference is grouping, not substance). NIST 800-61 Revision 3 (2025) remapped these onto the CSF 2.0 functions (Govern, Identify, Protect, Detect, Respond, Recover), but the phase model is still how AWS frames IR. Preparation is the only phase entirely before an incident. The rest run as a loop, with lessons feeding back into preparation.

## How it works (by phase)

- **Preparation**: build the plan, roles, and playbooks, turn on detection (GuardDuty, CloudTrail, Config, Security Hub, Macie, Inspector), pre-provision least-privilege IR roles and break-glass access, write SSM Automation runbooks, onboard AWS Security Incident Response, and run tabletop and game-day exercises. Under-preparation is the classic wrong-answer setup.
- **Detection and Analysis**: findings arrive from GuardDuty, Security Hub, and third-party tools via Security Hub. You triage (true or false positive), scope the blast radius, and set severity using Detective, CloudTrail, VPC Flow Logs, and Athena, with EventBridge routing alerts. This is the Finding Validation and Scoping work.
- **Containment**: stop the spread. **Short-term** actions isolate an EC2 instance with a deny-all forensic security group, detach it from its Auto Scaling group, revoke the instance role's sessions, disable or rotate credentials, and block IPs via WAF or NACLs. **Long-term** actions are segmentation and patching that let you keep operating while you eradicate. Preserve evidence before anything destroys it.
- **Eradication**: remove the foothold: backdoors, rogue IAM users or roles, persistence Lambdas, and malware. Patch the exploited vulnerability, rotate every potentially exposed credential, and hunt indicators of compromise across the environment with Detective finding groups and Athena.
- **Recovery**: restore from known-good state (a hardened AMI, AWS Backup, or DRS point-in-time), reintroduce traffic in stages (Route 53 or ARC), and keep heightened monitoring for about 30 days to catch re-entry.
- **Post-Incident Activity**: produce a root-cause analysis and lessons-learned, tune detections (GuardDuty suppression rules, Security Hub automation rules), update playbooks, and harden controls (SCPs, MFA). This is the most-skipped phase, and its output feeds the next Preparation.
- **AWS Security Incident Response (managed service)**: launched at re:Invent 2024, it monitors and triages findings from GuardDuty and Security Hub CSPM (and third-party tools through Security Hub), automatically filtering over 99 percent and opening cases only for the critical few, with 24/7 access to the AWS Customer Incident Response Team (CIRT), coordinated communication, and containment actions. It aligns to NIST 800-61 and requires AWS Organizations with all features enabled. It is not a detection service and not an alert aggregator, it ingests and triages what your detectors produce. The **CIRT** does log-based and control-plane investigation, not host or memory forensics, for which AWS points to a DFIR partner.

## Phases mapped to AWS services

| Phase | Goal | Key AWS services |
|---|---|---|
| Preparation | Be ready before it happens | GuardDuty, CloudTrail, Config, Security Hub, SSM runbooks, IR roles, Security Incident Response onboarding |
| Detection and Analysis | Confirm it is real and scope it | GuardDuty, Security Hub, Detective, CloudTrail, VPC Flow Logs, Athena, EventBridge |
| Containment | Stop the spread | SSM Automation, forensic security group, revoke role sessions, WAF/NACL, IAM disable |
| Eradication | Remove the foothold | Detective finding groups, Athena, credential rotation, patching |
| Recovery | Restore with confidence | AWS Backup, Elastic Disaster Recovery, hardened AMIs, Route 53, ARC |
| Post-Incident Activity | Learn and improve | GuardDuty suppression rules, Security Hub automation rules, updated playbooks, SCPs |

## What gets tested

- The NIST 800-61 four phases (and the SANS six-step grouping) are the framework, and AWS aligns to NIST 800-61. Know the order, and that you never jump to recovery before eradication is complete.
- Each phase has its AWS services: detection is GuardDuty, Security Hub, and CloudTrail, investigation is Detective, containment is SSM plus a forensic security group and session revocation, recovery is AWS Backup and DRS, and tuning is suppression and automation rules.
- AWS Security Incident Response is the managed triage-and-response service. It ingests and triages GuardDuty and Security Hub CSPM findings, filters over 99 percent, opens cases for the critical few, and gives 24/7 CIRT access with containment and coordination. It is not detection (GuardDuty), not aggregation (Security Hub), and not investigation (Detective), and it needs Organizations with all features.
- Sequencing is testable: contain before eradicate before recover, and preserve evidence before containment can destroy it.
- Short-term versus long-term containment: isolate immediately, then segment and patch sustainably.
- Preparation determines everything downstream. Pre-provisioned roles, playbooks, and enabled logging are what make the later phases possible.
- The lifecycle is a loop. Post-incident tuning and playbook updates feed back into Preparation.

## Limitations

- The lifecycle is a loop, not a straight line. Post-incident outputs feed back into preparation, and treating it as linear is a common mistake.
- AWS Security Incident Response requires Organizations with all features and pre-deployed CloudFormation StackSets and IAM for automated containment. CIRT performs log-based investigation only, not host or memory forensics.
- Response quality is bounded by preparation and logging coverage. Weak logging or missing IR roles cripple the later phases, which ties this back to the logging, scoping, and forensics practices.
- It manages risk, it does not eliminate it, and rushing recovery before eradication is the most common failure mode.