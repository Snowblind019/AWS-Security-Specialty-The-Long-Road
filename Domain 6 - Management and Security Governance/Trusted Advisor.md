# AWS Trusted Advisor

Trusted Advisor evaluates an account against a fixed set of AWS-authored best practice checks across cost optimization, performance, security, fault tolerance, service limits, and operational excellence, and reports each as green, yellow, or red. For security work it is a narrow but genuinely useful instrument: it flags publicly accessible S3 buckets, security groups open to the internet on sensitive ports, public RDS and EBS snapshots, missing root MFA, weak IAM password policy, and absent CloudTrail logging, and it uniquely reports AWS access keys that have been detected exposed in public repositories. Its limits are equally clear. The check set is fixed and not extensible, the depth is shallow compared to Config or Security Hub, and the full set is gated behind a paid support plan. Treat it as a high-signal, low-effort second opinion rather than a compliance system. The thing to hold onto: Trusted Advisor tells you the obvious things quickly and for free-ish, Config and Security Hub tell you what your own standard requires.

## How it works

**Checks run per account and refresh on a cycle.** Results refresh automatically on a periodic schedule and can be refreshed manually per check, subject to a cooldown. There is no continuous evaluation and no per-change trigger, which is the structural difference from Config.

**Access depends on the support plan.** Basic and Developer support get a limited subset, covering service quota checks and a handful of core security checks. Business, Enterprise On-Ramp, and Enterprise support unlock the full check set and the API. Enterprise support adds Trusted Advisor Priority, which is curated and prioritized by the account team.

**Organizational view aggregates across accounts.** With AWS Organizations and a qualifying support plan, the management account or a delegated administrator sees findings across member accounts and can export reports. Without it, Trusted Advisor is an account-by-account console visit.

**Programmatic access runs through the API.** The AWS Support API and the Trusted Advisor API expose check definitions, results, and refresh operations, which is what makes automation possible. Both require a qualifying support plan.

**Eventing and metrics are homed in us-east-1.** Trusted Advisor publishes CloudWatch metrics and emits EventBridge events for check status changes in us-east-1 regardless of where the resources are. A rule created in the workload Region will never fire, which is the single most common automation mistake with this service.

**Security checks worth knowing by name.** S3 bucket permissions, security groups with unrestricted access on specific ports, IAM use and root MFA, IAM password policy, public RDS and EBS snapshots, exposed access keys, CloudTrail logging enabled, ELB listener and security group configuration, and Route 53 and CloudFront certificate expiry.

**Service limit checks are a security control, not just an operations one.** Approaching a quota is how availability fails silently, and unexpected consumption is a signal of both cost attacks and compromised credentials mining resources.

**Downstream integration is do-it-yourself.** Trusted Advisor is not one of Security Hub's native service integrations, so routing findings there means reading the API and calling `BatchImportFindings`, or reacting to EventBridge events with Lambda and SNS. Building auto-remediation on Trusted Advisor output is possible but is normally better served by Config rules with SSM Automation.

## Comparison

| Service | Check set | Continuous | Customizable | Remediation | Gating |
| --- | --- | --- | --- | --- | --- |
| Trusted Advisor | Fixed, AWS-authored, cross-pillar | No, periodic refresh | No | No, guidance only | Support plan |
| AWS Config | Managed and custom rules | Yes, on change and periodic | Yes, fully | Yes, via SSM Automation | Per-evaluation cost |
| Security Hub | Standards such as FSBP, CIS, NIST, PCI | Yes | Control level only | Via custom actions and EventBridge | Per-check cost |
| Well-Architected Tool | Structured review questionnaire | No, point in time | Custom lenses | No | Free |
| Compute Optimizer | Right-sizing recommendations | Periodic | No | No | Free |
| Service Quotas | Quota values and increase requests | On demand | Not applicable | Requests only | Free |

## What gets tested

- **Support plan gating.** Any scenario where the full check set or the API is required implies Business or Enterprise support. A Basic support account seeing only a few checks is the expected behavior, not a misconfiguration.
- **Trusted Advisor versus Config and Security Hub.** Continuous evaluation, custom rules, organization-wide standards, and automated remediation all point away from Trusted Advisor. It is the answer for quick best-practice guidance, service quota visibility, and the exposed access keys check.
- **Region for automation.** EventBridge rules and CloudWatch alarms on Trusted Advisor must be created in us-east-1.
- **Multi-account visibility.** Organizational view with a delegated administrator, not a script that logs into each account.
- **Exposed access keys.** This check is distinctive and appears in scenarios about leaked credentials. The correct response chain is deactivate and delete the key, rotate, review CloudTrail for use, and investigate the exposure source.
- **Service limits.** Approaching quotas surfaces in availability and incident scenarios, and Service Quotas is the service for requesting increases and setting CloudWatch alarms on utilization.
- **Guidance only.** Trusted Advisor never fixes anything. Any answer implying it remediates is wrong.
- **Not a compliance framework.** For CIS, PCI, or NIST evidence, the answer is Security Hub standards, Config conformance packs, and Audit Manager.

## Limitations

- The check set is fixed and cannot be extended, so organization-specific requirements have no expression here at all.
- Full functionality requires a paid support plan, which makes it unavailable as a baseline control in cost-constrained environments.
- Periodic refresh means findings are stale by design, and there is no evaluation at the moment of change.
- Coverage is shallow relative to Config and Security Hub, both in the number of resource types and in the specificity of what is checked.
- No remediation, no enforcement, and no prevention. It is advisory output that requires someone to act.
- No native Security Hub integration, so consolidating findings takes custom work.
- Automation is centralized in us-east-1, which is easy to miss and produces silently non-functional rules.
- Its breadth across cost, performance, and fault tolerance is useful operationally but means the security signal arrives mixed with recommendations that have no security relevance, which dilutes attention in practice.