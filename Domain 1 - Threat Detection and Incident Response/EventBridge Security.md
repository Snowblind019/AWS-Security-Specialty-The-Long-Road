# EventBridge Security

EventBridge is the event bus that routes events from AWS services, custom apps, and SaaS partners to targets (Lambda, Step Functions, SQS/SNS, and more). In SCS it plays two roles: it is the detection-to-remediation backbone (route GuardDuty/Security Hub/Config/CloudTrail events to automated response), and it is an attack surface in its own right (anyone who can publish events or edit rules can spoof findings, trigger targets, or break detection).

Two angles to hold: using EventBridge as a security control (event-driven remediation) and securing EventBridge itself. The sensitive primitive is the ability to publish (`events:PutEvents`) and to change routing (`PutRule` / `PutTargets`); guard those, match events strictly, and keep targets least-privileged so a spoofed event cannot trigger anything dangerous.

## How it works (and what to secure)

- **Bus types**: default (receives AWS service events), custom (your apps), partner (SaaS). Use **resource policies** on custom/central buses to control who can publish, and scope cross-account access to specific account IDs/principals — never `Principal: *`.
- **Sensitive permissions**: `events:PutEvents` injects events; `events:PutRule` / `events:PutTargets` change routing; `events:DeleteRule` / `events:RemoveTargets` can disable detection. Scope `PutEvents` to the specific bus ARN and use condition keys (`events:source`, `events:detail-type`, `events:EventBusName`).
- **Strict pattern matching**: match on `source`, `account`, `region`, and known `detail` fields so a spoofed or overly broad event does not reach a target. Validate the payload again at the target (e.g. in Lambda code).
- **Least-privilege targets**: both the EventBridge invocation role and the target's own permissions should be minimal — an overprivileged target turns a triggered event into privilege escalation or lateral movement.
- **Monitoring**: EventBridge does not log every event by default. Use CloudTrail for the API calls (`PutEvents`, `PutRule`, `PutTargets`), CloudWatch metrics (`Invocations`, `FailedInvocations`, `MatchedEvents`, `ThrottledRules`), and target-level logs. Alarm on new or modified rules in prod and on `PutEvents` from unexpected principals. Event bus logging to CloudWatch/S3/Firehose is also available.
- **Encryption**: encrypted at rest by default with an AWS owned key (AES-256); you can specify a **customer-managed KMS key** for custom and partner events on a bus (also Pipes and archives). AWS service events always use an AWS owned key. TLS in transit. Event **metadata is not encrypted** — never put secrets in metadata or free-form fields; only the `detail` element is encrypted.

## EventBridge in the security pipeline

| Role | Example |
|---|---|
| Detection routing | GuardDuty/Security Hub finding → Lambda/SSM remediation |
| Config remediation | Config NON_COMPLIANT → SSM Automation |
| Audit-driven response | CloudTrail event pattern (e.g. `PutBucketPolicy`) → alert/quarantine |
| Attack surface | `PutEvents` or rule edits abused to spoof findings or disable detection |

## What gets tested

- EventBridge is the glue for event-driven remediation: route a finding or a specific API call to Lambda/SSM/Step Functions for automated response. This is the EventBridge half of the alarms-vs-EventBridge distinction (alarms watch metric thresholds; EventBridge matches event patterns).
- `events:PutEvents` is the dangerous permission — it lets a principal inject events, including spoofed GuardDuty findings to bury real ones. Scope it tightly and match events strictly.
- Cross-account event flow (e.g. into a central security account) is controlled by the event bus resource policy; restrict to specific accounts and deny by default.
- Deleting or modifying rules and targets is a detection-evasion technique; monitor `DeleteRule` / `RemoveTargets` via CloudTrail.
- Encryption at rest is on by default; use a customer-managed KMS key when you must control or audit the key. Metadata is not encrypted, so keep secrets out of it.
- Targets must be least-privilege so a triggered event cannot be leveraged for escalation.

## Limitations

- No native per-event log; you assemble visibility from CloudTrail, metrics, target logs, and optional event-bus logging.
- Customer-managed KMS keys cover custom and partner events only (AWS service events use an AWS owned key), and disable schema discovery on that bus.
- Event metadata is never encrypted.
- Strict patterns and target validation are on you; broad rules are an injection risk.