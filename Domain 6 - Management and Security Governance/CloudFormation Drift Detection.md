# CloudFormation Drift Detection

Drift detection compares the resources a CloudFormation stack actually has in the account against the properties the stack's template declared, and reports where the two no longer agree. Infrastructure as code only delivers its security value if the code remains the source of truth, and it stops being the source of truth the moment someone opens a port in the console, edits an IAM policy by CLI, or disables versioning during an incident and never puts it back. Drift is how a hardened baseline silently decays into an insecure configuration while the template in Git still claims otherwise. Drift detection is the check that catches that divergence, and it is equally the evidence an auditor wants that deployed reality still matches approved design. The thing to hold onto: drift detection tells you what no longer matches the template, it does not tell you who changed it, when, or put it back.

## How it works

**Two scopes, both on demand.** Stack-level detection scans every supported resource in the stack. Resource-level detection scans one logical resource. Both are asynchronous: the call returns a detection ID and you poll for the result.

```bash
aws cloudformation detect-stack-drift --stack-name myAppStack
aws cloudformation describe-stack-drift-detection-status --stack-drift-detection-id <id>
aws cloudformation describe-stack-resource-drifts --stack-name myAppStack
aws cloudformation detect-stack-resource-drift --stack-name myAppStack --logical-resource-id MySecurityGroup
```

**Status values differ by level.** A stack is `DRIFTED`, `IN_SYNC`, `NOT_CHECKED`, or `UNKNOWN`. A resource is `MODIFIED`, `DELETED`, `IN_SYNC`, or `NOT_CHECKED`. A single drifted resource makes the whole stack `DRIFTED`.

**Results include the actual difference.** `DescribeStackResourceDrifts` returns property differences with the expected value, the actual value, and a difference type of `ADD`, `REMOVE`, or `NOT_EQUAL`. This is what makes the output usable as audit evidence rather than a bare boolean.

**Only declared properties are checked.** If a property was never specified in the template, CloudFormation has no declared intent for it and will not flag a change to it. A resource can be meaningfully altered and still report `IN_SYNC` when the altered property was left to its default. This is the single most consequential behavior of the feature.

**Only stack resources are checked.** A resource created outside the stack is invisible to drift detection, because drift is defined relative to the template. Detecting unmanaged resources is a different problem, solved by Config or resource inventory, not by this feature.

**Nested stacks and StackSets are supported.** Detection on a parent stack covers nested stacks as resources, and StackSets support drift detection across stack instances so a landing zone can be checked in one operation rather than account by account.

**Nothing runs it for you.** There is no continuous mode and no automatic event when drift occurs. Operationalizing it means either scheduling detection with EventBridge Scheduler plus Lambda, or using the AWS Config managed rule `cloudformation-stack-drift-detection-check`, which periodically evaluates stacks and produces a compliance finding that can route to Security Hub and EventBridge.

**Remediation is a separate decision.** Detection changes nothing. The three real responses are re-apply the template through a stack update to return managed properties to their declared values, amend the template if the change was intended and should become the new baseline, or investigate and revert manually. Choosing correctly requires knowing who made the change, which comes from CloudTrail.

## Comparison

| Mechanism | What it compares | Continuous | Covers resources outside the stack | Attribution |
| --- | --- | --- | --- | --- |
| CloudFormation drift detection | Live state against template-declared properties | No, on demand | No | No |
| AWS Config | Live state against rules, plus full configuration history | Yes | Yes | Links to the change, paired with CloudTrail |
| Config rule for stack drift | Stack drift status as a compliance verdict | Yes, periodic | No | No |
| CloudTrail | API calls made | Yes | Yes | Yes, identity and time |
| Terraform plan | Live state against declared configuration | No, on demand | Only what state tracks | No |
| Stack policies | Nothing, they gate stack update operations | Not applicable | No | Not applicable |

## What gets tested

- **Drift detection versus AWS Config.** Template-relative divergence is drift detection. Continuous evaluation, configuration timelines, and coverage of resources not managed by a stack is Config. When a scenario wants ongoing automatic checking, the answer usually pairs the two: the Config managed rule evaluating drift status, not drift detection alone.
- **Attribution.** If the question asks who changed the security group, the answer is CloudTrail. Drift detection never identifies a principal.
- **The unspecified property trap.** Expect a scenario where a resource was changed but reports `IN_SYNC`. The cause is that the property was not declared in the template.
- **Resources created outside the stack.** These are never reported as drift. The correct answer for unmanaged resource discovery is Config, resource import, or an inventory service.
- **Stack policies are misunderstood on purpose.** They restrict what a stack update operation may modify. They do not prevent anyone from changing a resource directly through the console or CLI. Preventing out-of-band change is an IAM or SCP problem.
- **Automating detection.** EventBridge Scheduler invoking Lambda that calls `detect-stack-drift` and evaluates results is the standard pattern, because CloudFormation emits no drift event on its own.
- **StackSets.** Multi-account landing zone drift checking points to StackSet drift detection rather than per-stack calls.
- **Cost.** Drift detection itself carries no charge, so cost is never a reason to reject it in a scenario.

## Limitations

- On demand only. Between runs, drift is undetected, and the window is whatever your schedule makes it.
- Blind to properties the template does not declare, which means a clean result is not proof the resource is unchanged.
- Blind to resources outside the stack entirely.
- Not all resource types are supported, and support for a type does not imply every property of that type is checked.
- No history. It reports expected against actual at the moment of the run, with no timeline of how the resource got there and no prior values beyond the template's.
- No attribution, so every drift finding requires a CloudTrail lookup before it can be triaged.
- No remediation. Nothing is reverted until a human or a pipeline acts, and a stack update to revert carries its own change risk.
- Detects divergence from intent, not insecurity. A template that was insecure from the start will report `IN_SYNC` forever, which is why drift detection sits alongside Config rules and IaC scanning rather than replacing either.