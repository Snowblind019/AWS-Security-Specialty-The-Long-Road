# IAM Access Analyzer

IAM Access Analyzer uses automated reasoning, AWS's provable-security engine (Zelkova), to tell you what access your policies make possible, not what has been used. It mathematically evaluates resource and identity policies against a defined zone of trust and reports any path by which a resource could be reached from outside that zone: publicly, cross-account, or through federation. Because it reasons over policy logic rather than logs, it needs no past activity to reach a conclusion with certainty. Over time the service grew beyond that original external-access job to also flag unused access, validate policies as you write them, and run custom access checks in a pipeline. On the SCS exam it is the proactive, policy-intent counterpart to the reactive tools, and the constant trap is confusing it with Access Advisor. The thing to hold onto: Access Analyzer answers "what could be accessed from outside my trust boundary," using math over policies, before anyone tries.

## How it works

- **You create an analyzer with a zone of trust.** An account-level analyzer treats the account as trusted; an organization-level analyzer treats the whole org as trusted. Findings describe access from outside that boundary.
- **It monitors supported resource policies continuously.** A policy change triggers re-evaluation, and any external access it proves possible becomes a finding.
- **Automated reasoning does the work.** Zelkova evaluates every possible access path implied by the policy, so the result is "this is reachable," not "this was reached." No logs are involved.
- **You resolve each finding three ways:** fix the policy, archive it if the access is intentional (archive rules can auto-archive known-good patterns), or automate a response by routing findings to EventBridge and Security Hub.
- **Supported resources include** S3 buckets, IAM role trust policies, KMS keys, Lambda functions, SQS queues, SNS topics, Secrets Manager secrets, and a growing list of others. Unsupported resource types are simply not analyzed.

## The four things Access Analyzer does

| Capability | What it answers | Notes |
|---|---|---|
| External access findings | Can this resource be reached from outside my zone of trust (public, cross-account, federated) | The original feature; free |
| Unused access findings | Which roles, permissions, and credentials have gone unused | Least-privilege feature; priced per analyzed resource |
| Policy validation | Does this policy have errors, or violate best practices, as I author it | `ValidatePolicy`, used in the policy-writing loop |
| Custom policy checks | Does this policy grant more than a baseline, or grant a specific action | `CheckNoNewAccess`, `CheckAccessNotGranted`, for CI/CD gates |

## What gets tested

- **Access Analyzer is proactive and policy-based.** It reports what access is possible from configuration alone, which is the answer whenever a scenario wants to find unintended exposure before it is exploited. Contrast it with GuardDuty and CloudTrail, which react to activity that already happened.
- **Do not confuse it with Access Advisor.** Access Advisor shows what services an identity has used (usage history, for trimming). Access Analyzer shows what access a policy makes possible (reachability, for exposure). This swap is the classic exam trap.
- **Zone of trust defines the boundary.** An org-level analyzer treats cross-account access within the organization as trusted and only flags access from outside the org. An account-level analyzer flags cross-account access to other accounts, even ones in the same org.
- **Know the external finding types:** public (`Principal: "*"`), cross-account, and federated. A bucket or KMS key readable by an outside account or the internet is the canonical finding.
- **Unused access findings are the newer least-privilege angle.** Unused roles, unused permissions, and stale credentials surface here, and this is where the exam now overlaps Access Analyzer with least privilege. Remember it is the paid analyzer.
- **Custom policy checks belong in pipelines.** `CheckNoNewAccess` (does a proposed policy grant more than the current one) and `CheckAccessNotGranted` (does a policy grant a named action) are the automated-reasoning gates for CI/CD, and they are the answer for "block risky policy changes before deploy."
- **Remediation uses conditions.** Scoping with `aws:PrincipalOrgID` or `aws:SourceIp`, and archiving intentional exposures, are the expected fixes for external findings.

## Limitations

- **It proves possibility, not use.** A finding says access is reachable, not that anyone used it. Whether it was ever exercised or abused is a CloudTrail and GuardDuty question.
- **Supported resource types are finite.** The list is growing but bounded; a resource type not on it is not evaluated, so absence of findings is not proof of no exposure.
- **The zone of trust can hide intra-org risk.** An org-level analyzer will not flag unintended access between two accounts inside the org, because that access is within the trusted zone by definition.
- **Not entirely free.** External access findings, policy validation, and custom policy checks are free, but unused access analysis is billed per IAM role or user analyzed. The source's blanket "free" is only partly right.
- **Analyzers are regional.** External access analyzers operate per region, so coverage means creating them in each region you use.
- **No runtime context.** It reasons over policies, not sessions, so it does not tell you about tags, request conditions at call time, or which principal actually connected.