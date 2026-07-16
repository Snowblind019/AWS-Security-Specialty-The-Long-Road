# Detective

Detective is the investigation layer you reach for after an alert. It ingests CloudTrail, VPC Flow Logs, EKS audit logs, and GuardDuty findings and builds a behavior graph — linked entities (principals, IPs, instances, sessions) you pivot through to scope what happened and how far it spread. It verifies and scopes; it does not detect.

The line that anchors every Detective question: GuardDuty detects, Detective investigates. GuardDuty raises the finding; Detective is where you jump to reconstruct the actor's behavior, draw the blast radius, and confirm or disprove the threat with evidence. Detective generates no findings of its own.

## How it works

- Builds a **behavior graph** from CloudTrail, VPC Flow Logs, EKS audit logs, and GuardDuty findings — no per-source pipeline to wire up; it ingests automatically once enabled.
- **Entity profiles**: one page per principal/IP/instance/account showing activity volume, new geolocations, new user agents, and related findings — handholds for testing "has this role ever done this before?"
- **Timelines**: scrollable, filterable windows that line up API calls, network flows, and cluster events as one sequence.
- **Finding groups**: cluster related findings into a single incident, so you review one case, not twenty symptoms.
- **Detective Investigation**: prebuilt analyses (impossible travel, suspicious IAM activity, flagged IPs) that run ML and threat intel over the graph.
- **Admin/member model**: a delegated administrator account holds one graph across the org. Retains up to **12 months** of aggregated investigation data, not your raw logs.

## Detective vs the rest of the detection stack

| Service | Role |
|---|---|
| GuardDuty | Detects threats, raises findings |
| Detective | Investigates and scopes a finding (behavior graph) |
| Security Hub | Aggregates findings, posture scoring |
| CloudTrail Lake | Raw SQL log search, long retention |

## What gets tested

- Detective is post-alert investigation, root cause, and blast radius. It does not detect threats or generate findings — that is GuardDuty. "Investigate / scope / understand the incident" points to Detective; "detect" points to GuardDuty.
- Its four sources are fixed: CloudTrail, VPC Flow Logs, EKS audit logs, and GuardDuty findings, ingested automatically. You cannot feed it arbitrary logs.
- The "Investigate in Detective" pivot from a GuardDuty (or Security Hub) finding is the canonical workflow.
- Finding groups bundle related findings into one incident; entity profiles surface new geo, new user agent, and activity spikes as compromise tells.
- Up to 12 months of aggregated data means you can investigate even after raw logs in their native services have expired.
- Org-wide investigation uses the admin/member (delegated administrator) model, one graph.
- Detective does not remediate; hand confirmed incidents to EventBridge/SSM.

## Limitations

- Not a detector — it needs findings (GuardDuty) as entry points and produces none itself.
- Data sources are fixed; no custom log ingestion.
- No remediation actions.
- Per-GB-ingested cost; retains aggregates for about 12 months, not raw logs.