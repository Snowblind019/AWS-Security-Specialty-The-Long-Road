# Secure Bootstrapping of New AWS Accounts

Bootstrapping is everything that happens to a new AWS account between creation and the moment a human is given access to it. A freshly created account has no CloudTrail trail of its own, no Config recorder, no detection services, no baseline roles, a default VPC in every Region, and a root user. If an engineer receives credentials before the baseline lands, there is a window in which activity is unlogged and uncontrolled, and that window is the actual security problem, not the eventual configuration. Mature bootstrapping therefore inverts the order: the account is placed into a governed OU so guardrails bind immediately, organization-level services extend to it automatically, the account baseline deploys through automation with no human in the path, and only then is access handed over. The thing to hold onto: the goal is not that a new account eventually becomes compliant, it is that there is never a moment when it is not.

## How it works

**Placement into the right OU is the first control, not the last.** SCPs, RCPs, and declarative policies attached to an OU apply the instant the account lands there. An account created into a governed OU is constrained before any resource exists in it, which is why the OU choice at creation time carries more weight than any subsequent step.

**Organization-level services extend automatically, and this is usually the correct answer.** An organization CloudTrail trail covers new accounts with no action. GuardDuty, Security Hub, Macie, Inspector, IAM Access Analyzer, and Config all support auto-enable or central configuration from a delegated administrator, so new accounts inherit detection without custom code. Reaching for Lambda to enable GuardDuty in a new account is a distractor when the auto-enable setting exists.

**The cross-account role differs by creation path.** An account created through the Organizations API or console gets `OrganizationAccountAccessRole` automatically, trusted by the management account. An existing account invited into the organization does not, and the role must be created manually before automation can reach in. Control Tower uses `AWSControlTowerExecution` for the same purpose. This distinction is a recurring exam item and a common real-world failure.

**Control Tower Account Factory is the prescriptive path.** It creates the account, places it in the chosen OU, enrolls it in the organization trail and Config, applies the OU's controls, and configures IAM Identity Center permission sets. Account Factory Customization applies blueprints for additional baseline resources, Customizations for Control Tower layers a CloudFormation and SCP pipeline on top, and Account Factory for Terraform covers pipeline-driven provisioning for teams standardized on Terraform.

**StackSets with service-managed permissions and automatic deployment cover the account baseline.** Targeted at an OU, a StackSet deploys its stack into every account already in that OU and into every account added afterward, with no trigger to write. This is the standard mechanism for baseline IAM roles, log destinations, budgets, alarms, and per-account settings.

**Event-driven automation covers what StackSets cannot express.** An EventBridge rule on `CreateAccountResult` invokes a Lambda that assumes the cross-account role and performs setup requiring imperative logic. Note that Organizations is a global service homed in us-east-1, so the event fires there regardless of where the rest of the workload runs.

**Account-level defaults get pinned rather than scripted.** EBS encryption by default, S3 Block Public Access at the account level, instance metadata defaults requiring IMDSv2, allowed AMI sources, and VPC Block Public Access are all better expressed as declarative policies at the OU than as bootstrap scripts, because a policy cannot be skipped and does not drift.

**Root user handling is part of the baseline.** Centralized root access management removes root credentials from member accounts entirely and performs the few root-only tasks from the management account. Where that is not in use, the baseline must include securing root with MFA and monitoring root usage through CloudTrail and an EventBridge alarm.

**Access comes last.** Baseline IAM roles and Identity Center permission sets, including a documented break-glass path, are provisioned by automation, not created ad hoc by the first engineer to log in.

## Comparison

| Mechanism | Covers new accounts automatically | Best for | Requires custom code |
| --- | --- | --- | --- |
| SCP, RCP, declarative policy on an OU | Yes, immediately on placement | Guardrails and pinned configuration | No |
| Organization CloudTrail trail | Yes | Tamper-resistant audit logging | No |
| Security service auto-enable from delegated admin | Yes | GuardDuty, Security Hub, Macie, Inspector, Config, Access Analyzer | No |
| CloudFormation StackSets, service-managed, auto-deploy | Yes, for accounts in target OUs | Declarative account baseline resources | No |
| Control Tower Account Factory | Yes, at provisioning | Full landing zone provisioning and enrollment | No, blueprints optional |
| EventBridge on CreateAccountResult plus Lambda | Yes, if the rule exists first | Imperative steps nothing else covers | Yes |

## What gets tested

- **Order of operations.** Guardrails and logging before access. Scenarios describing an unlogged window in a new account resolve to placing the account in a governed OU and relying on organization-level services rather than post-creation scripting.
- **The cross-account role gap.** Automation failing against an invited account points to the missing `OrganizationAccountAccessRole`, which is created only for accounts provisioned through Organizations.
- **Auto-enable over automation.** When the requirement is that every new account has GuardDuty or Security Hub, the answer is the auto-enable setting in the delegated administrator account, not a Lambda function.
- **StackSets automatic deployment.** For deploying a baseline stack to all current and future accounts in an OU, choose service-managed StackSets with automatic deployment over per-account stack creation.
- **Organization trail coverage.** New accounts are covered by an existing organization trail with no action, and member administrators cannot disable it.
- **Configuration defaults.** IMDSv2, EBS encryption by default, and account-level S3 Block Public Access are stronger as declarative policies or account settings than as bootstrap steps, because they persist and cannot be skipped.
- **Root user.** Centralized root access management is the modern answer for eliminating member account root credentials. Detecting root usage is a CloudTrail plus EventBridge alarm.
- **Event location.** Organizations events are emitted in us-east-1, so an EventBridge rule created in the workload Region will never fire.
- **Self-service without excess permissions.** Account Factory surfaced through Service Catalog lets teams request accounts without holding `organizations:CreateAccount`.
- **Delegated administration.** Security tooling operates from a dedicated security account, and trusted access must be enabled before a delegated administrator can be registered.

## Limitations

- Automation cannot fully eliminate the creation window. There is always a short interval between account creation and baseline completion, which is why OU-level policy, which binds first, matters more than the stack that lands second.
- Imperative bootstrap code becomes a privileged, poorly reviewed control path. The Lambda that can assume an administrative role in every account is among the most valuable targets in the organization.
- StackSets and blueprints drift like any deployed resource. Without drift detection and Config, the baseline is a claim about the past.
- Invited accounts arrive with existing history, existing IAM principals, existing resources, and possibly existing compromise. Bootstrapping standardizes them going forward, it does not clean them.
- Auto-enable settings for security services vary in behavior and coverage between services, so "enable everywhere" is several distinct configurations rather than one switch.
- The baseline is a floor, not a security program. It guarantees logging, detection, and guardrails exist; it says nothing about workload architecture, data classification, or how the account is used afterward.
- Cost scales with the baseline. Config recording, GuardDuty, Security Hub, and detection services in every account across every governed Region is a meaningful line item, and scoping decisions made at bootstrap time are what determine it.