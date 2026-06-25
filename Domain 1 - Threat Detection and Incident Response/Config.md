# Config

Config records the configuration state of your AWS resources over time and evaluates that state against rules. It answers "what does this resource look like now, how did it change, and is it compliant." When something drifts out of policy it flags NON_COMPLIANT and can auto-remediate via SSM Automation.

The distinction that anchors most Config questions: Config tracks resource state and compliance over time; CloudTrail tracks who made the API call. "The S3 bucket is public" is a Config finding; "who ran PutBucketAcl" is a CloudTrail event. They are complementary, and Config is also the data source behind many Security Hub controls.

## How it works

- The **configuration recorder** captures create/update/delete changes as **Configuration Items (CIs)** and builds a per-resource timeline with property diffs and relationships. Delivered to S3 (the delivery channel), with optional SNS.
- **Rules** evaluate state: **managed** (prebuilt, e.g. `s3-bucket-public-read-prohibited`, `restricted-ssh`, `cloudtrail-enabled`, `ebs-encrypted-volume`, `iam-policy-no-statements-with-admin-access`) or **custom** (Lambda or Guard). Triggered on change or periodically. Output is COMPLIANT / NON_COMPLIANT.
- **Conformance packs** bundle rules plus remediation into a versioned baseline (Foundational Security Best Practices, CIS, NIST, PCI), deployable org-wide.
- **Remediation** ties a NON_COMPLIANT result to an **SSM Automation** document, automatic or approval-gated.
- **Aggregators** roll up compliance across accounts and Regions for a single org-wide view.
- **Advanced queries** run SQL over current recorded state (e.g. all unencrypted EBS volumes) for audit evidence.

## Config vs neighbors

| Service | Answers |
|---|---|
| Config | What the resource looks like, how it changed, whether it is compliant |
| CloudTrail | Who made the API call, when, from where |
| Security Hub | Aggregated posture and findings (many fed by Config rules) |

## What gets tested

- Config is resource state and compliance over time; CloudTrail is the API call. "Is the bucket public / is the volume encrypted / did the trail stop" is Config; "who changed it" is CloudTrail. Pair them.
- The detect-to-remediate loop: a Config rule marks NON_COMPLIANT, EventBridge catches it, SSM Automation fixes it. This is the canonical auto-remediation pattern (public S3, open SSH, unencrypted resources).
- Managed rules are the off-the-shelf misconfiguration checks; conformance packs are the repeatable org-wide baselines (FSBP/CIS/NIST/PCI).
- Config is the underlying data source for many Security Hub controls — they are linked, not redundant.
- Aggregators give org-wide compliance from one account; the recorder must be enabled per account/Region (protect it with an SCP).
- Config detects after the change; it is not prevention. SCPs and resource policies prevent; Config catches what slips through.
- Change-triggered rules evaluate on each change; periodic rules evaluate on a schedule.

## Limitations

- Records only supported resource types, and only while the recorder is on.
- Detection, and optional remediation, after the fact — not prevention.
- Per-CI and per-evaluation cost; broad recording in dev gets expensive.
- Remediation runbooks must be idempotent and safe; risky fixes should be approval-gated.