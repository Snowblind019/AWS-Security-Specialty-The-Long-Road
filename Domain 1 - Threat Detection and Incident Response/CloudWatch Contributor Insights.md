# CloudWatch Contributor Insights

A CloudWatch feature that ranks the top-N contributors to a pattern in your logs or metrics — the source IPs, users, or API calls responsible for the most of something (failed logins, errors, traffic) over time. It analyzes data you already have; it does not collect anything new.

The one thing to hold onto: it answers "who is doing the most of X right now." It surfaces the heavy hitter behind a spike so you can alarm on it. It is not a detector and does not decide what is malicious — you define the pattern and the threshold.

## How it works

- You write a **rule** (JSON) pointing at CloudWatch Logs (or metrics): the log group(s), a filter, the **contribution keys** to group by (e.g. `$.sourceIP`), and the value to count.
- It aggregates roughly every minute and renders a **top-N time series** of contributors.
- Attach a **CloudWatch alarm** to a contributor metric to fire when the top contributor crosses a threshold (e.g. one IP > 1,000 failed logins in 5 minutes); embed the rule in dashboards.
- AWS provides built-in rules for some services. **DynamoDB Contributor Insights** is a related, separate feature that surfaces most-accessed and most-throttled keys.

Example — top IPs causing failed logins:

```json
{
  "logGroupNames": ["/aws/lambda/AuthFunction"],
  "filter": "{ $.status = \"FAILED_LOGIN\" }",
  "contribution": { "keys": ["$.sourceIP"], "value": "$.status" }
}
```

## Contributor Insights vs neighbors

| Tool | Role |
|---|---|
| Contributor Insights | Ranks top-N contributors to a pattern, continuously |
| CloudWatch Logs Insights | Ad-hoc query language over log groups |
| GuardDuty | Managed threat detection; decides what is suspicious |

## What gets tested

- It identifies the top contributors to a pattern from CloudWatch Logs/metrics — e.g. the source IP behind the most failed logins. The "who's the heavy hitter" tool.
- Rule-based and near-real-time (~1 min); can drive alarms when a top contributor crosses a threshold.
- Distinguish it from CloudWatch Logs Insights (ad-hoc queries) and GuardDuty (managed detection). Contributor Insights ranks; it does not judge intent.
- Security fits: brute force / credential stuffing (top failing IPs), API key abuse or throttling (top callers), data exfiltration (top pullers), DDoS contributor analysis.

## Limitations

- Not a detector — you define the pattern and what counts as bad.
- Needs logs already in CloudWatch Logs, ideally structured (JSON) so keys are extractable.
- Per-event analysis cost on top of normal CloudWatch charges.
- Narrow feature; recognition-level for the exam rather than a major topic.