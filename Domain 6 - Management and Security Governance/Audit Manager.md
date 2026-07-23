# AWS Audit Manager

AWS Audit Manager continuously collects and organizes evidence from your AWS environment, maps it to the controls of a compliance framework, and packages the result into a signed assessment report an auditor will accept. It is the customer half of the shared responsibility model made auditable: where Artifact proves AWS meets a standard, Audit Manager proves your workloads do. Critically, it is a collector and not an evaluator. It does not judge whether a resource is compliant, it does not remediate, and it does not generate its own findings. It reaches into Config, Security Hub, CloudTrail, and service describe APIs, pulls what those systems already know, timestamps it, and files it under the control it satisfies. The thing to hold onto: Audit Manager answers "show me the proof," while Config and Security Hub answer "is this compliant right now."

## How it works

**An assessment is the working unit.** You create one by choosing a framework, defining the scope in accounts and AWS services, naming audit owners, and specifying the S3 bucket that receives assessment reports. The assessment then runs continuously until you stop it.

**Frameworks are prebuilt or custom.** AWS ships frameworks for CIS AWS Foundations Benchmark, NIST 800-53, NIST CSF, PCI DSS, SOC 2, ISO/IEC 27001, HIPAA, GDPR, FedRAMP, and others. Custom frameworks let you define your own control sets, either by copying and editing a prebuilt one or by authoring custom controls with your own evidence mappings and collection cadence.

**There are exactly four automated evidence sources, plus manual.** This list is the substance of the service and worth memorizing.

- **Compliance check.** Pulled from AWS Config rule evaluations and AWS Security Hub findings. This is the only source that carries a pass or fail verdict, and it exists only because Config and Security Hub already produced it.
- **Configuration snapshot.** Read-only describe and list API calls against services in scope, capturing resource state such as bucket encryption settings or RDS snapshot encryption. Collected on a daily cadence.
- **User activity.** CloudTrail events, capturing who did what, including root API usage and policy changes. Collected continuously as events arrive.
- **Manual evidence.** Documents you supply for controls no API can prove: business continuity plans, signed attestations, vendor contracts, screenshots. Uploaded per control with a per-file size cap.

**Evidence is immutable once collected.** It carries a timestamp, the source, and the control it maps to, and it is stored encrypted with a KMS key you can specify. Assessment reports are delivered to S3 with a SHA-256 checksum file so the auditor can validate the package has not been altered.

**Organizations integration runs through a delegated administrator.** You register a member account as the Audit Manager delegated admin from the management account, and that account then scopes assessments across member accounts. The management account itself cannot serve as the delegated administrator.

**Assessments are Regional.** An assessment collects evidence in the Region where it was created. Covering a multi-Region footprint means an assessment per Region, which is a frequent gap in exam scenarios describing incomplete evidence.

**Evidence finder queries the evidence store.** It supports searching across collected evidence and generating a report directly from search results, and it is backed by CloudTrail Lake. Note the enrollment change: CloudTrail Lake closed to new customers on May 31, 2026, so treat evidence finder availability as dependent on existing Lake access rather than assuming it in a greenfield design.

## Comparison

| Service | Core question answered | Produces verdicts | Scope |
| --- | --- | --- | --- |
| AWS Audit Manager | Where is the evidence for this control | No, it collects verdicts made elsewhere | Your workloads, per Region, per assessment |
| AWS Artifact | Does AWS itself meet this standard | Not applicable, publishes auditor reports | AWS infrastructure only |
| AWS Config | Is this resource in a compliant configuration | Yes, per rule evaluation | Your resources, per Region |
| Security Hub | What is my aggregated security posture | Yes, findings scored against standards | Your accounts, aggregatable cross-Region |
| AWS Control Tower | Are guardrails enforced across the landing zone | Yes, preventive and detective controls | Organization landing zone |

## What gets tested

- **Audit Manager versus Artifact.** Evidence about your environment is Audit Manager. Evidence about AWS is Artifact. A HIPAA scenario often needs both: the BAA and SOC report from Artifact, the workload control evidence from Audit Manager.
- **Audit Manager versus Config and Security Hub.** If the requirement is detect and remediate non-compliant resources, the answer is Config with remediation, or Security Hub. If the requirement is assemble and hand over an evidence package, the answer is Audit Manager. Distractors will offer Audit Manager for remediation scenarios; it remediates nothing.
- **The dependency trap.** Audit Manager does not enable Config or Security Hub. If a scenario reports empty or sparse compliance check evidence, the cause is that the upstream service is not enabled or the relevant rules and standards are not turned on.
- **Delegated administrator.** For multi-account collection, register a delegated admin from the management account. The management account cannot be the delegated admin, and member account owners cannot self-enroll.
- **Regional scope.** Incomplete evidence across a multi-Region deployment points to a missing per-Region assessment, not a permissions problem.
- **Report integrity.** When the question asks how an auditor verifies the package was not tampered with, the answer is the SHA-256 checksum file delivered alongside the report, not CloudTrail log file validation and not S3 Object Lock, though Object Lock is a valid complementary answer for retention.
- **Custom controls.** When a scenario describes an internal policy with no matching prebuilt framework, the answer is a custom framework with custom controls and defined evidence mappings.
- **Framework updates.** AWS updating a prebuilt framework does not retroactively change assessments already running against the prior version.

## Limitations

- Collects evidence, does not evaluate it. Every pass or fail verdict originates in Config or Security Hub, so coverage is capped by what those services assess.
- No remediation, no prevention, no alerting on drift. It is an evidence layer, not a control layer.
- Regional service with per-Region assessments. Global coverage requires deliberate duplication.
- Prebuilt framework coverage is partial. Meaningful audits still require manual evidence for policy, personnel, and process controls that no API exposes.
- Cost scales with the volume of evidence collected and the number of resources assessed, and the upstream services generating that evidence, CloudTrail, Config, Security Hub, bill separately. Broad scope on a large organization is not cheap.
- Evidence is retained on a fixed schedule inside the service, so long-term retention beyond that window depends on the S3 copies you control.
- Deregistering the service can delete collected evidence. Export before decommissioning.
- Produces no legal standing. It documents controls, it does not create the contractual coverage that agreements in Artifact provide.