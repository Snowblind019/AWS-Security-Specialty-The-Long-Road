# AWS Fault Injection Service

AWS Fault Injection Service (AWS FIS), formerly Fault Injection Simulator, is a managed chaos-engineering service that injects real faults into real AWS resources so you can watch how your system responds and fix the weaknesses you find. You describe an experiment in a template (actions, targets, stop conditions, and an IAM experiment role), then run it. FIS ships preconfigured actions such as stopping EC2 instances, throttling API calls, stressing CPU or memory, disrupting network paths, failing over a database, and interrupting an Availability Zone, with no agents to install. It is part of AWS Resilience Hub.

FIS is mostly a resilience tool, but it earns a place in security thinking two ways. First, it acts on your workloads under an IAM role you hand it, so that experiment role is the blast radius, and a loose FIS setup is a clean path to stopping or throttling your own production. Second, it is how you prove incident response actually works: inject the fault, then check that the alarms fire, the detections trigger, and the failover and runbooks do what the architecture diagram promises. The thing to hold onto: the safety of FIS lives in three places, the scoped experiment role, tag-based targeting, and CloudWatch stop conditions. Get those right and it is controlled; get them wrong and it is a self-inflicted outage.

## How it works

- **Experiment template**: the blueprint. It holds the actions, targets, stop conditions, the experiment role ARN, and optional report configuration and options.
- **Actions**: preconfigured fault activities (aws:ec2:stop-instances, API throttling, CPU or memory stress via SSM, network disruption, RDS or Aurora failover, Kinesis throughput exception, EKS pod stress, AZ power interruption). They run in a set order or simultaneously.
- **Targets**: the resources an action hits, chosen by resource type, tags, and filters, with a selection mode (ALL, a COUNT, or a PERCENT). Tag scoping is the primary blast-radius control, for example 10 percent of instances tagged env=prod.
- **Stop conditions**: one or more CloudWatch alarms. If any of them fires during the run, FIS halts the experiment automatically. This is the emergency brake.
- **Experiment role (roleArn)**: the IAM role FIS assumes to perform the actions. FIS can do only what this role allows, so it is the security boundary. Creating and running experiments also needs fis: permissions and iam:PassRole for that role.
- **No agents**: fully managed actions install nothing. Actions that run through SSM documents (some stress and network faults) do require the target instances to be managed by Systems Manager with the SSM Agent and an instance profile.
- **Scenario Library and scheduling**: prebuilt scenarios such as an AZ availability interruption, plus recurring scheduled experiments for a regular game-day cadence.

## AWS FIS vs sibling options

| | AWS FIS | AWS Resilience Hub | SSM Automation | Third-party chaos (Gremlin, Chaos Monkey) |
|---|---|---|---|---|
| Role | Inject real faults with guardrails | Assess and track resilience posture | Run operational and remediation runbooks | Inject faults, self-managed |
| Injects faults? | Yes, managed actions | No, it assesses (can invoke FIS) | Only if you script it | Yes |
| Safety controls | Stop conditions, tag targeting, scoped role | N/A | You build them | Vendor-specific |
| Best for | Controlled chaos and IR game days | Measuring RTO / RPO over time | Ops automation and remediation | Multi-cloud or custom chaos |

## What gets tested

- FIS is chaos engineering: an experiment template (actions, targets, stop conditions, experiment role) injects real faults into real resources to test resilience. It is mostly a resilience and operations topic and only lightly SCS.
- The security-relevant piece is the experiment role. FIS acts under an IAM role you pass, so that role is the blast radius. Least-privilege it, and control iam:PassRole and fis:StartExperiment tightly, because a loose FIS setup is a way to stop or throttle production.
- Stop conditions are CloudWatch alarms that auto-halt the experiment, and tag-based targeting scopes which resources are hit. Together they are the guardrails that keep fault injection from becoming a self-inflicted denial of service.
- The strongest SCS use of FIS is incident-response game days: inject a fault, then confirm alarms fire, detections such as GuardDuty and Security Hub trigger, failover works, and runbooks execute. It validates the respond phase of an incident.
- Some actions run through SSM documents and require the targets to be managed by Systems Manager, with the SSM Agent and an instance profile.

## Limitations

- It runs real actions on real resources and can cause a real outage if targeting or stop conditions are wrong. Plan first and run in pre-production before production.
- It is not a security-testing tool by itself. It tests resilience and response, not vulnerabilities (that is Inspector) or misconfiguration (that is Config and Security Hub).
- SSM-based actions need instances managed by Systems Manager, so unmanaged instances are out of reach for those faults.
- Stop conditions are only as good as your CloudWatch alarms. No alarm means no automatic halt.
- The experiment role and iam:PassRole are sensitive. Over-permissioning turns a resilience tool into an availability risk, so treat FIS permissions as segregation-of-duties material.