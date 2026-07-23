# IaC Security Best Practices

Infrastructure as code turns every provisioning decision into a reviewable, versioned artifact, which is the single biggest improvement available to cloud security governance. It also turns every mistake into a repeatable one. A wildcard IAM policy written once and committed to a shared module is deployed into forty accounts by a pipeline that never questions it, and a hardcoded credential in a template is now in Git history permanently. The security work is therefore not "review the infrastructure" but "build the path that infrastructure travels down," with checks at authoring, at merge, at deployment, and after deployment, and with an organization-level backstop for everything the earlier stages miss. The thing to hold onto: securing IaC means securing the pipeline and the identities that run it, not just the templates.

## How it works

**Static analysis at authoring and pull request.** Linting with `cfn-lint` catches malformed templates. Policy-as-code scanning with CloudFormation Guard, cfn_nag, Checkov, Trivy, or KICS catches insecure patterns such as unrestricted ingress, unencrypted volumes, and wildcard actions. Amazon CodeGuru Security and Amazon Inspector code scanning cover the application and IaC files in the same repository. The control that matters is not owning a scanner, it is a branch protection rule that refuses the merge when the scan fails.

**Permission changes get a dedicated check.** IAM Access Analyzer custom policy checks belong in the pipeline as a distinct gate: `ValidatePolicy` for correctness and best practice findings, `CheckNoNewAccess` to fail a change that grants access the previous version did not, `CheckAccessNotGranted` to fail a change that grants a specific prohibited action, and `CheckNoPublicAccess` for resource policies. Generic IaC scanners do not perform this comparison.

**Secrets are referenced, never embedded.** CloudFormation dynamic references resolve at deployment without the value entering the template: `{{resolve:secretsmanager:MySecret:SecretString:password}}` and `{{resolve:ssm-secure:MyParam:1}}`. `NoEcho` on a parameter masks console display but is not encryption and does not protect the value everywhere it travels. Repository-side scanning with git-secrets, trufflehog, or provider-native secret scanning is the compensating control for what slips through.

**Terraform state is a credential store.** State files contain resource attributes in plaintext, including generated passwords and keys. Remote state belongs in an S3 bucket with KMS encryption, versioning, Block Public Access, a restrictive bucket policy, and state locking. Treat read access to state as equivalent to read access to the secrets inside it.

**The deployment identity is scoped separately from the pipeline identity.** A CloudFormation service role passed with `--role-arn` lets CloudFormation act with permissions the pipeline principal does not itself hold, so a compromised pipeline cannot use those permissions directly. Apply a permissions boundary to deployment roles. For external CI systems, federate with IAM roles through OIDC rather than issuing long-lived access keys, and constrain the trust policy by repository, branch, and environment.

**Pre-deployment approval is structural, not procedural.** CloudFormation change sets show the diff, including replacements, before an update executes. Stack policies restrict which resources an update may modify. Termination protection blocks stack deletion. These are the CloudFormation-native equivalents of a plan review and a protected branch.

**Proactive enforcement sits between the pipeline and the resource.** CloudFormation Hooks evaluate a stack operation and can block provisioning outright. AWS Config proactive rules evaluate a proposed configuration before creation. Control Tower proactive controls package Hooks per organizational unit. AWS Service Catalog restricts teams to pre-approved, parameterized products. These hold even when someone deploys outside the sanctioned pipeline.

**Organization guardrails are the backstop.** SCPs and RCPs deny the API call, and declarative policies pin service configuration durably. They exist precisely because scanning covers only the templates that go through scanning, and no pipeline covers the console.

**Post-deployment closes the loop.** Config rules and conformance packs evaluate live state, CloudFormation drift detection compares live state to the template, Security Hub aggregates the findings, and CloudTrail attributes the change. Without drift detection the repository becomes a description of what was once true.

## Comparison

| Layer | When it acts | Bypassable by | Best at |
| --- | --- | --- | --- |
| Linting and policy-as-code scan | Authoring and pull request | Deploying outside the pipeline | Catching insecure patterns cheaply, with fast feedback |
| Access Analyzer policy checks | Pull request | Deploying outside the pipeline | Detecting permission expansion specifically |
| CloudFormation Hooks and proactive Config rules | Stack operation, pre-provision | Non-CloudFormation deployment paths | Blocking creation with full resource context |
| Service Catalog | Provisioning request | Direct API access if not denied | Constraining teams to approved patterns |
| SCP, RCP, declarative policy | Every API call | Nothing inside the organization | Absolute guarantees, no exceptions |
| Config rules and drift detection | After creation | Nothing, but it is post-hoc | Continuous assurance and audit evidence |

## What gets tested

- **Secrets in templates.** The correct answer is a dynamic reference to Secrets Manager or an SSM SecureString parameter. `NoEcho` is a distractor: it hides display, it does not protect the value.
- **Least privilege for deployments.** Passing a CloudFormation service role so the pipeline principal need not hold the underlying resource permissions is the intended answer, often paired with a permissions boundary.
- **External CI credentials.** IAM roles with OIDC federation and a trust policy scoped to the repository and branch, never an IAM user with long-lived keys.
- **Preventing permission escalation in a pipeline.** IAM Access Analyzer custom policy checks, specifically `CheckNoNewAccess` and `CheckAccessNotGranted`. A generic template scanner is the weaker distractor.
- **Blocking at provisioning rather than at merge.** CloudFormation Hooks, Config proactive rules, or Control Tower proactive controls, chosen when the requirement says the deployment itself must fail rather than the pipeline.
- **Guaranteeing enforcement regardless of deployment path.** SCPs or declarative policies. Any answer relying on pipeline scanning fails the "regardless of how it is deployed" wording.
- **Reviewing before an update.** Change sets. Protecting specific resources during an update is stack policies, which is a different control and a common swap in distractors.
- **Terraform state exposure.** Encrypted S3 backend with KMS, restricted bucket policy, versioning, and locking. State is the answer whenever a scenario mentions plaintext credentials outside the template.
- **Drift.** Manual console changes after deployment are found with CloudFormation drift detection or Config, and attributed with CloudTrail. The template repository proves nothing on its own.
- **Approved patterns for self-service.** Service Catalog is the answer when teams must provision independently but only from vetted configurations.

## Limitations

- Every pipeline control is bypassed by anyone with console or CLI access to the target account. Without an organization-level denial, the pipeline is a convention rather than a control.
- Scanners find known patterns. Business logic flaws, wrong trust boundaries, and correct-looking but overly broad policies pass cleanly.
- Policy-as-code rule sets require ongoing maintenance and generate false positives that erode enforcement discipline once teams start requesting exceptions.
- Proactive controls are path-specific. CloudFormation Hooks do not see Terraform, and Config proactive rules cover a limited resource set.
- Deployment roles tend to accumulate permissions because a single role deploys everything. This is frequently the most privileged identity in the account and rarely the most scrutinized.
- Drift detection reports divergence, it does not revert it, and re-applying a template to correct drift is itself a change with its own risk.
- Git history is permanent. A secret committed and later removed remains recoverable, so remediation always means rotating the credential, not deleting the commit.
- None of this addresses runtime security. Correctly provisioned infrastructure still needs GuardDuty, Inspector, logging, and incident response.