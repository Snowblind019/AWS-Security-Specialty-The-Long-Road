# Avoiding Insecure Configurations

An insecure configuration is a resource deployed with unsafe defaults, excessive permissions, or a missing control, where nothing errors, no quota is breached, and no pipeline fails. The deployment succeeds and quietly adds an attack path. This is the dominant cause of cloud compromise, well ahead of exploited vulnerabilities: a bucket left publicly readable, a security group open to 0.0.0.0/0 on 22 or 3389, a policy granting `*` on `*`, an instance still answering IMDSv1, an RDS instance marked publicly accessible. The security discipline is not detection alone, it is layering controls so the insecure state cannot be created, is caught before deployment if it can be, is detected within minutes if it is, and is remediated automatically. The thing to hold onto: a preventive control makes the API call fail, a detective control tells you it succeeded, and the exam almost always wants the preventive one first.

## How it works

**Preventive at the permissions layer.** Service control policies and resource control policies cap what any principal in the organization can do, regardless of IAM grants. Condition keys make them precise rather than blunt: deny `rds:CreateDBInstance` unless `rds:StorageEncrypted` is true, deny `s3:PutObject` without the expected encryption header, deny `ec2:RunInstances` when `ec2:MetadataHttpTokens` is not `required`, deny principals outside the org on resource policies. SCPs never grant, they only set the ceiling, and they do not apply to the management account.

**Preventive at the service layer.** Some controls are account-wide switches rather than policies. S3 Block Public Access set at the account level overrides any bucket-level or ACL-level attempt to go public. EBS encryption by default is a per-Region account setting. IMDSv2 can be made the account default for new instances. These are stronger than a policy because there is no condition to get wrong.

**Preventive across accounts for network objects.** AWS Firewall Manager applies security group policies, WAF rules, Network Firewall, and DNS Firewall centrally across an organization, and can audit and auto-remediate non-compliant security groups. This is the answer when a scenario says "across all accounts and any new account" for network exposure.

**Proactive before deployment.** IaC scanning catches the pattern in the template rather than the resource. Static analysis with cfn-lint, CloudFormation Guard, or third-party scanners runs in the pipeline. CloudFormation Hooks evaluate a stack operation before provisioning and can block it. AWS Config proactive rules evaluate a proposed resource configuration before it is created. IAM Access Analyzer custom policy checks (`CheckNoNewAccess`, `CheckAccessNotGranted`, `ValidatePolicy`) belong in the same pipeline stage to fail a merge that would widen permissions.

**Detective at runtime.** AWS Config rules evaluate live resource state against managed or custom rules, packaged as conformance packs for CIS, PCI DSS, NIST, and similar. Security Hub aggregates those evaluations into scored standards. GuardDuty and Inspector cover behavior and vulnerabilities rather than configuration, so they complement rather than replace this layer.

**Responsive.** Config remediation actions invoke SSM Automation documents to fix a resource on detection. EventBridge on Config compliance change events or Security Hub findings drives Lambda or Step Functions for anything Automation cannot express.

**Governed centrally.** AWS Control Tower expresses all three modes as controls: preventive controls implemented as SCPs, detective controls implemented as Config rules, and proactive controls implemented as CloudFormation Hooks, applied per organizational unit. Organizations declarative policies enforce persistent service configuration such as EC2 metadata defaults and blocking public AMI sharing, and they survive attempts to change the setting rather than merely denying the call.

**Drift closes the loop.** Perfect IaC does not survive console access. AWS Config tracks configuration history and compliance over time, CloudFormation drift detection compares live stacks to their templates, and Terraform plan compares actual to intended state. Without a drift mechanism, a temporary manual change becomes a permanent one.

## Comparison

| Control | Timing | Enforcement point | Failure mode when used alone |
| --- | --- | --- | --- |
| SCP and RCP | Preventive, at the API call | Organizations permission ceiling | No coverage of the management account, no visibility into attempts unless logged |
| Declarative policy | Preventive, persistent setting | Organizations service configuration | Limited to supported services and attributes |
| IaC scanning and CFN Hooks | Proactive, pre-deployment | Pipeline or stack operation | Blind to console and CLI changes made outside the pipeline |
| Config rules | Detective, post-creation | Resource configuration evaluation | The insecure resource existed before it was flagged |
| Firewall Manager | Preventive and remediating | Org-wide network objects | Scoped to network and WAF constructs only |
| Security Hub | Detective, aggregation | Findings across accounts | Reports posture, changes nothing |

## What gets tested

- **Prevent versus detect.** Wording matters. "Ensure it cannot be created" or "must not be possible" means SCP, RCP, account-level setting, or declarative policy. "Identify," "report," or "alert on" means Config rules and Security Hub. "Automatically fix" means Config remediation with SSM Automation.
- **Account-level S3 Block Public Access.** When a scenario says a bucket policy or ACL keeps re-enabling public access, the answer is account-level BPA, which overrides both, not a Config rule that merely reports it.
- **Firewall Manager for security groups.** Any scenario requiring uniform security group enforcement across every existing and future account points to Firewall Manager, not to per-account Config rules.
- **IMDSv2.** Enforce with the instance metadata account default, a launch template setting, or an SCP with the `ec2:MetadataHttpTokens` condition. Reporting existing offenders is a Config rule.
- **Least privilege in a pipeline.** IAM Access Analyzer custom policy checks are the correct answer for blocking a policy change that grants new access at merge time. Access Analyzer external access findings are the detective counterpart for unintended cross-account exposure.
- **Proactive Config rules and CloudFormation Hooks.** These appear as the answer when the requirement is to block during provisioning but the deployment path is CloudFormation rather than the organization boundary.
- **Control Tower control types.** Know that preventive maps to SCP, detective maps to Config, proactive maps to Hooks. Questions test the mapping directly.
- **Conformance packs.** The right answer for deploying a full CIS or PCI rule set across an organization in one operation rather than rule by rule.

## Limitations

- SCPs do not apply to the management account, so an organization relying solely on them has an uncovered account by design.
- SCPs and RCPs deny only. They cannot grant, cannot fix an existing resource, and cannot express requirements that have no condition key.
- Condition-key coverage is uneven. Many attributes simply cannot be constrained at the API call, which is why account-level settings and proactive checks exist.
- Config is detective and evaluation is not instantaneous. There is a window in which the insecure resource is live, so Config alone is unsuitable for anything catastrophic on creation.
- Config cost scales with rule evaluations and configuration items recorded. Broad recording across a large organization is a real line item, and it is the usual reason a scenario describes partial coverage.
- IaC scanning is only as good as the deployment discipline. Console and CLI changes bypass it entirely, which is why drift detection is mandatory rather than optional.
- Drift detection reports differences, it does not revert them. Reverting requires a pipeline re-apply or an automated remediation.
- None of these layers address application-level flaws, credential theft, or misuse by a correctly permissioned principal. Configuration hardening reduces the attack surface, it does not cover behavior.