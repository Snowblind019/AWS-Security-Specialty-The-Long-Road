# AWS Control Tower

AWS Control Tower builds and maintains an opinionated multi-account landing zone on top of AWS Organizations, then keeps it enforced. It does not introduce new security primitives: everything it applies is an SCP, a Config rule, a CloudFormation Hook, an organization CloudTrail trail, or an IAM Identity Center assignment. What it contributes is that these are provisioned consistently, applied at the organizational unit rather than per account, extended automatically to every account created afterward, and monitored for tampering. The security argument is straightforward: in a multi-account estate the failure mode is not a missing control, it is a control that exists in eleven accounts and not the twelfth. Control Tower closes that gap by making the baseline a property of the OU rather than something an administrator remembers to repeat. The thing to hold onto: Control Tower governs the account boundary and the baseline, it does not secure what runs inside the accounts.

## How it works

**The landing zone is three account roles.** The management account owns Organizations and Control Tower itself. The Log Archive account receives the organization CloudTrail trail and Config history in centralized S3 buckets and is intended to be effectively write-only for everyone else. The Audit account holds cross-account read and notification access for security teams and is the natural delegated administrator for security services. Log Archive and Audit sit in a foundational Security OU that Control Tower creates and expects to keep.

**Controls come in three enforcement types.** Preventive controls are implemented as SCPs and deny the API call outright. Detective controls are implemented as AWS Config rules and report non-compliance after the fact. Proactive controls are implemented as CloudFormation Hooks and block a resource during stack provisioning before it exists. The mapping of type to implementation is exam material in itself.

**Controls also carry a behavior category.** Mandatory controls are always on and cannot be disabled. Strongly recommended controls are enabled by default and can be opted out. Elective controls are off until you enable them. Do not confuse the enforcement type with the behavior category; questions deliberately mix the two vocabularies.

**Controls apply to organizational units.** You enable a control against an OU and it covers every account in that OU, including accounts added later. This is the mechanism that makes new accounts governed on creation rather than after a review.

**Account Factory provisions governed accounts.** It is surfaced as an AWS Service Catalog product, so account creation can be delegated without granting Organizations permissions. Each provisioned account lands in the chosen OU, is enrolled in the organization trail and Config, receives the OU's controls, and gets Identity Center assignments. Account Factory Customization applies blueprints for additional baseline resources, and Account Factory for Terraform covers pipeline-driven provisioning.

**Provisioning depends on a privileged role.** Control Tower assumes `AWSControlTowerExecution` in each enrolled account. It is highly privileged by necessity, and protecting the ability to assume it is a real security consideration rather than a footnote.

**Region governance is explicit.** You choose a home Region and the Regions the landing zone governs. The Region deny control restricts activity outside the approved set, which is the standard answer for data residency scenarios.

**Drift is a first-class concept.** If someone edits a Control Tower SCP directly in Organizations, detaches a policy, moves an account between OUs, deletes a governed OU, or alters the log bucket policy, Control Tower reports landing zone drift. Remediation is the repair or update landing zone operation, not a manual fix in Organizations, because a manual fix leaves Control Tower's view inconsistent.

**Identity is centralized by default.** Control Tower configures IAM Identity Center with permission sets across accounts, and supports pointing at an external identity provider or running Identity Center self-managed.

## Comparison

| Option | What it delivers | Customization | Ongoing enforcement |
| --- | --- | --- | --- |
| AWS Control Tower | Prescriptive landing zone, OU-scoped controls, account vending, drift monitoring | Limited to supported controls and blueprints | Yes, with drift detection and repair |
| AWS Organizations alone | Account hierarchy, SCPs, RCPs, policy types | Complete | Only what you build |
| Landing Zone Accelerator | Highly configurable landing zone deployed as code for regulated workloads | Extensive | Yes, through the pipeline |
| Config conformance packs | Detective rule sets deployed org-wide | Rule level | Detective only, no account lifecycle |
| Security Hub | Aggregated posture findings against standards | Standard and control level | Reporting only |

## What gets tested

- **Which account for what.** Logs go to Log Archive. Cross-account security access and delegated administration go to Audit. Answers placing the trail bucket in the management account are wrong.
- **Control type mapping.** Preventive equals SCP, detective equals Config rule, proactive equals CloudFormation Hook. A requirement to block creation before the resource exists in a CloudFormation deployment path is proactive.
- **Mandatory versus strongly recommended versus elective.** When a scenario asks why a control cannot be turned off, the answer is that it is mandatory, not that permissions are missing.
- **Scope of application.** Controls attach to OUs. The answer to "ensure all future accounts inherit this" is enabling the control on the OU, not scripting it per account.
- **Drift scenarios.** Direct edits to Control Tower managed SCPs, accounts moved out of a governed OU, or modified log bucket policies produce landing zone drift. The fix is repair or update the landing zone.
- **Region restriction.** Data residency and approved-Region requirements point to the Region deny control plus governed Region selection.
- **Delegated administration.** GuardDuty, Security Hub, Macie, Detective, and Audit Manager delegate to the Audit account. The management account should not be the operational security account.
- **Account vending without broad permissions.** Delegating account creation through the Service Catalog product is the correct answer over granting `organizations:CreateAccount`.
- **Control Tower versus Landing Zone Accelerator.** When the scenario states requirements beyond what Control Tower's control set expresses, particularly in government or heavily regulated contexts, the answer moves to Landing Zone Accelerator.
- **Cost.** Control Tower has no charge of its own. Billing comes from Config, CloudTrail, S3, and any security services enabled, which matters because Config recording across every account is the usual cost driver.

## Limitations

- Opinionated by design. The landing zone structure, the foundational OU, and the account roles are largely fixed, and working around them produces drift rather than flexibility.
- Changes made directly in Organizations to Control Tower managed resources are drift, not customization. Custom governance still belongs in your own SCPs attached outside the managed set.
- Enrolling existing accounts has prerequisites. An account with an existing Config recorder or conflicting configuration, or without the required execution role, will fail enrollment until reconciled.
- Landing zone versions require deliberate updates, and controls enabled on an OU may require re-registration after an update before they take effect everywhere.
- Governs the account boundary and baseline only. It says nothing about application security, data classification, key management design, workload IAM, or anything inside an account beyond the enabled controls.
- Detective controls inherit Config's properties: post-hoc, evaluation latency, and per-evaluation cost across every account.
- Not available in every Region, and the home Region choice is not casually reversible.
- The `AWSControlTowerExecution` role is a high-value target. Control Tower creates the governance, it does not by itself protect the path into every account that governance depends on.