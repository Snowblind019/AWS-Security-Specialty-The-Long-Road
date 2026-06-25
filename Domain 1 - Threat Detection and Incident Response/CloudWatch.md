# CloudWatch

AWS's observability service: metrics over time, alarms that fire on thresholds or learned baselines, and actions that respond. For security, the load-bearing pattern is turning log activity into metrics and metrics into automated response: a metric filter spots a CloudTrail event (root login, unauthorized call), increments a metric, an alarm fires, and an action notifies or remediates. Log analysis itself is covered in the Logs Insights and Contributor Insights notes.

The security value is not the graphs, it is the detect-to-act loop. Two routing paths matter and get confused: CloudWatch alarms watch metric thresholds; EventBridge matches event patterns (specific API calls, GuardDuty/Security Hub findings, state changes). Threshold on a number points to an alarm; reacting to a specific event points to EventBridge.

## How it works

- **Metrics**: namespace + name + dimensions + value over time. AWS services publish many by default; add custom metrics via the agent or EMF. Standard 1-minute and high-resolution 1-second granularity.
- **Metric filters**: scan a CloudWatch Logs group for a pattern and emit a metric when it matches — e.g. count root-account usage, failed console logins, IAM policy changes, or security-group edits in CloudTrail logs. This is how log activity becomes alarmable.
- **Alarms**: watch a metric or metric-math expression (including anomaly bands). States are OK / ALARM / INSUFFICIENT_DATA. **Composite alarms** combine conditions to cut noise. **Anomaly detection** alerts on deviation from a learned baseline instead of a fixed threshold.
- **Alarm actions**: notify SNS / Incident Manager, trigger **SSM Automation** or Lambda for auto-remediation, scale via Auto Scaling, or hand off to EventBridge.
- **Metric Streams**: continuous near-real-time export of metrics to Firehose, then S3/lake/SIEM.
- **Cross-account observability**: a central monitoring account views metrics, logs, and dashboards across accounts.

## CloudWatch alarms vs EventBridge

| | CloudWatch alarm | EventBridge rule |
|---|---|---|
| Triggers on | Metric threshold / anomaly band | Event pattern (API call, finding, state change) |
| Best for | "Metric X crossed Y" | "Respond to this specific event" |
| Example | p95 latency high; > N failed logins | A GuardDuty finding; a `PutBucketPolicy` call |
| Action | SNS, SSM Automation, Auto Scaling, Lambda | Lambda, Step Functions, SSM, queues |

## What gets tested

- The canonical SCS pattern: a metric filter on CloudTrail logs → metric → alarm → SNS/action, for detecting root usage, unauthorized API calls, failed console logins, and IAM/security-group/NACL changes. The CIS AWS Foundations alarms are the textbook set.
- Alarm actions can remediate, not just notify — wire an alarm to SSM Automation or Lambda for automatic response.
- Alarms watch metrics; EventBridge matches event patterns. To react to a specific API call or a GuardDuty/Security Hub finding, use EventBridge, not an alarm.
- Composite alarms reduce alert noise; anomaly detection handles cyclical workloads where a fixed threshold would misfire.
- Metric Streams to Firehose is the near-real-time path for getting metrics into a SIEM or lake.
- Cross-account observability centralizes monitoring; a metric filter only sees logs already in CloudWatch Logs.

## Limitations

- Alarms act on metrics and thresholds, not arbitrary events — that is EventBridge's job.
- Metric filters only match patterns in logs already ingested into CloudWatch Logs.
- Standard metric resolution rolls up and coarsens for older data.
- Observability-heavy features (Synthetics, RUM, ServiceLens/X-Ray, Container Insights) are largely ops, not SCS material.