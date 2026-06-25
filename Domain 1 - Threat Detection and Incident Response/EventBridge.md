# EventBridge

A serverless event bus that routes events (JSON signals that something happened) from AWS services, SaaS partners, and custom apps to targets like Lambda, Step Functions, SNS, and SQS. It evolved from CloudWatch Events. In SCS it is the router that turns a detection into an action: a GuardDuty finding, a CloudTrail API call, or a Config compliance change becomes an automated response. Hardening EventBridge itself is in the EventBridge Security note.

EventBridge does not analyze or store anything — it matches event patterns and fires targets. Its exam role is event-driven response: pair a detection source with a remediation or notification target. It is the "react to a specific event" half of the response toolkit, as opposed to CloudWatch alarms, which react to metric thresholds.

## How it works

- **Components**: an **event bus** (default for AWS service events, custom for your apps, partner for SaaS), **events** (JSON), **rules** (event-pattern matchers, not SQL), and **targets** (Lambda, Step Functions, SNS, SQS, Kinesis, SSM Automation, ECS, and more).
- **Rules** match on fields like `source`, `detail-type`, and `detail`, with content filters (`prefix`, `numeric`, `anything-but`). Example: GuardDuty findings with `severity >= 7` and `type` starting with `UnauthorizedAccess`.
- **Common sources**: GuardDuty findings, Security Hub findings, Config compliance changes, CloudTrail API calls, IAM/EC2/S3 service events, AWS Health, and SaaS partners.
- **Archive & replay**: store events and replay them into a bus to test new rules or IR playbooks, or to re-run a past window for post-incident analysis.
- **Schema registry**: discovers event structure and generates code bindings.
- **Related**: EventBridge **Pipes** (point-to-point source-to-target with filtering and enrichment) and **Scheduler** (cron/rate-based invocations).

## Mechanism vs neighbors

| Mechanism | Reacts to | Use when |
|---|---|---|
| EventBridge rule | An event pattern (finding, API call, state change) | Respond to a specific event |
| CloudWatch alarm | A metric threshold / anomaly band | A number crossed a line |
| SNS | A published message (pub/sub fan-out) | Broadcast to many subscribers |

## What gets tested

- EventBridge matches event patterns and routes to targets — the standard way to wire GuardDuty/Security Hub/Config findings to automated remediation (Lambda, SSM Automation, Step Functions). It is the detection-to-response router.
- The alarms-vs-EventBridge fork: a metric threshold is a CloudWatch alarm; reacting to a specific API call or finding is an EventBridge rule.
- Rules use JSON event-pattern matching with content filters, not SQL or metric math.
- The default bus receives AWS service events automatically; custom and partner buses handle your apps and SaaS.
- Archive & replay is the answer for testing IR automation and replaying past events without new data.
- Securing the bus (PutEvents scoping, resource policies, encryption) is covered in the EventBridge Security note.

## Limitations

- Routes and triggers; it does not analyze or store logs — it is the reflex, not the brain.
- At-least-once delivery: possible duplicates and out-of-order events, so targets should be idempotent.
- Pattern matching only, no joins or SQL.
- Near-real-time, not a hard real-time guarantee.