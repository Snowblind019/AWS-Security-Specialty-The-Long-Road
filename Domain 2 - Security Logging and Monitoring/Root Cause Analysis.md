# Root Cause Analysis (RCA)

The Post-Incident Activity practice of determining not just what happened but **why**, and what will prevent recurrence, rather than patching the symptom and moving on. It is the learning phase of the incident response lifecycle. In AWS you build the RCA from the same log and configuration sources you used to scope the incident, and its output is a set of preventive controls that feed back into Preparation. The exam frames RCA as the step that turns an incident into hardening.

The mental split is symptom versus root cause. The symptom is what broke (a bucket went public, a key was abused). The root cause is why it was possible (no automated policy check, a committed secret, no ownership of secure defaults). RCA drills from one to the other, usually with the 5 Whys, and ends in action items that become controls. It is blameless on people and pointed on process.

## How it works

- **Reconstruct the timeline from AWS evidence**: **CloudTrail** for the who, what, and when of API calls, **VPC Flow Logs** for network activity, **AWS Config** for the configuration and change history that shows what changed and when the flaw was introduced, **Detective** to correlate the sequence and surface the root cause (finding groups map to MITRE ATT&CK, with up to a year of history), plus GuardDuty findings and Athena over the logs.
- **Drill to root cause**: use the **5 Whys** (or a fishbone or fault-tree analysis) to push past the proximate action to the systemic gap.
- **Structure the report**: incident summary, impact, a factual timeline (no blame), the root cause, contributing factors (logging gaps, noisy alerts, missing guardrails), the resolution, lessons learned, and action items with owners and due dates.
- **Stay blameless**: name process failures ("no required review on IAM changes," "rollback never tested," "no alert on logins from new geographies"), not individuals. Blame produces silence, and silence kills learning.
- **Feed Preparation**: the action items become preventive controls: **Config rules** for the misconfiguration class, **SCPs** and MFA enforcement, new CloudWatch alarms, detection tuning (GuardDuty suppression rules, Security Hub automation rules), and updated playbooks and runbooks.
- **AWS tooling for the RCA itself**: **Systems Manager Incident Manager** has a built-in post-incident analysis feature that generates a structured retrospective and action items from the incident, and **AWS Security Incident Response** case history and reports feed the analysis.

## Symptom vs root cause

| Symptom | Root cause |
|---|---|
| EC2 instance unreachable | Security group misconfiguration with no automated check |
| S3 bucket publicly accessible | No Config rule or guardrail enforcing secure bucket defaults |
| IAM key used by an attacker | A secret committed to a public repo, no secret scanning |
| Unauthorized login via API | No MFA, and a key reused from a prior breach |
| Lambda failing after a deploy | Upstream breaking change with no versioning or canary |

## What gets tested

- RCA is the Post-Incident Activity phase: why it happened plus prevention, not just the fix. It closes the incident-response loop back to Preparation.
- Reconstruct with CloudTrail (the identity and API timeline), Config (the configuration change history showing what changed and when), VPC Flow Logs, and Detective (the sequence and root cause, mapped to MITRE ATT&CK). Config is the workhorse for "what changed and when."
- The root cause is the systemic gap, not the proximate action. "Someone made the bucket public" is the symptom, "no automated policy check or secure-default guardrail" is the root cause.
- Action items become preventive controls: Config rules, SCPs, MFA, alarms, and detection tuning, all of which feed Preparation.
- Blameless RCA focuses on process, not people, because blame suppresses the reporting the analysis depends on.
- Systems Manager Incident Manager provides built-in post-incident analysis, tying RCA to the response-plan tooling.

## Limitations

- RCA quality is bounded by evidence. Gaps in CloudTrail, Config, or VPC Flow Logs leave the timeline incomplete, which ties this back to your logging, scoping, and forensics practices.
- It is the most-skipped phase. Exhausted teams move on, so RCA needs to be a required, owned deliverable, not an optional one.
- The 5 Whys can stop too early or chase a single line of causation. Combine it with a contributing-factors analysis for complex incidents.
- Action items without owners and due dates do not get done. An RCA that changes no controls is theater.
- RCA is learning, not response. It happens after containment and recovery, not during them.