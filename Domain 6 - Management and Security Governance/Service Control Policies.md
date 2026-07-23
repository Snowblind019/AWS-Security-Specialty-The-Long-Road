# Service Control Policies

A service control policy is an AWS Organizations policy that defines the maximum permissions available to principals in member accounts. It grants nothing. An action succeeds only if IAM allows it and the SCP chain also allows it, which makes the SCP a ceiling that no administrator inside the account can raise, including that account's root user. This is the only mechanism in AWS that constrains an account from outside the account, which is why it carries the weight in multi-account governance: Region restriction, blocking services that have no business being used, preventing tampering with logging and security services, and stopping privilege escalation paths that IAM alone cannot close because the account admin can always rewrite IAM. The thing to hold onto: an SCP filters what principals in your accounts may do, it never decides who may reach your resources.

## How it works

**Prerequisites and attachment.** AWS Organizations with all features enabled, the SCP policy type enabled, and attachment to the root, an OU, or an individual account. OU attachment is normal because it covers accounts added later.

**Evaluation is an intersection with deny precedence.** An allow must be present at every level from the root down to the account, and IAM must independently grant the action. An explicit deny anywhere in the chain ends the evaluation. SCPs contain no `Principal` element, since they apply to every principal in scope by definition.

**Two strategies, chosen deliberately.** A deny list keeps the default `FullAWSAccess` attached and adds targeted denies, which is maintainable and the common choice. An allow list removes `FullAWSAccess` and enumerates permitted services, which is stronger and breaks the first time a team adopts a service nobody listed.

**Three exclusions, all heavily tested.** SCPs do not apply to the management account at all, including its root user. They do not apply to service-linked roles. They do not apply to AWS service principals acting on your behalf. Anything relying on an SCP for an absolute guarantee has to account for these.

**Region restriction needs global service exemptions.**

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "DenyUnapprovedRegions",
    "Effect": "Deny",
    "NotAction": [
      "iam:*", "organizations:*", "sts:*", "route53:*",
      "cloudfront:*", "support:*", "budgets:*", "health:*"
    ],
    "Resource": "*",
    "Condition": {
      "StringNotEquals": { "aws:RequestedRegion": ["us-west-2"] }
    }
  }]
}
```

**Restricting member account root uses the principal ARN.**

```json
{
  "Effect": "Deny",
  "Action": "*",
  "Resource": "*",
  "Condition": {
    "StringLike": { "aws:PrincipalArn": "arn:aws:iam::*:root" }
  }
}
```

**Protecting security controls is a core pattern.** Deny `cloudtrail:StopLogging` and `cloudtrail:DeleteTrail`, `guardduty:DeleteDetector` and `guardduty:DisassociateFromMasterAccount`, `config:DeleteConfigurationRecorder` and `config:StopConfigurationRecorder`, and deletion of the organization's log bucket, typically with an exception for a named security role via `aws:PrincipalArn`.

**Enforcing configuration uses request-time condition keys.** Deny `rds:CreateDBInstance` when `rds:StorageEncrypted` is false, deny `ec2:RunInstances` when `ec2:MetadataHttpTokens` is not `required`, deny `s3:PutObject` without the expected encryption header, deny resource creation when a required tag is absent using `aws:RequestTag`. Coverage depends entirely on whether the service publishes a usable condition key.

**Watch the escape hatches in conditions.** `aws:ViaAWSService` distinguishes a call made directly from one made by an AWS service on the principal's behalf, and omitting it breaks legitimate service-mediated access. Conditions on MFA are risky in SCPs because automation and service roles do not carry MFA context. `StringNotEqualsIfExists` and the other `IfExists` variants matter because a request without the key otherwise fails the comparison in the wrong direction.

**Diagnosis runs through CloudTrail.** A denial caused by an SCP appears in the CloudTrail error message as an explicit deny in a service control policy, which distinguishes it from an IAM denial. There is no dry-run mode, so rollout means attaching to a non-production OU first and reading CloudTrail.

## Comparison

| Control | Constrains | Can grant | Restricts member account root | Applies to external principals reaching your resources |
| --- | --- | --- | --- | --- |
| Service control policy | Principals in member accounts | No | Yes | No |
| Resource control policy | Access to resources in member accounts | No | Yes, as a caller | Yes |
| IAM identity policy | One principal | Yes | No | No |
| Permissions boundary | One identity's maximum | No | No | No |
| Session policy | One session | No | Not applicable | No |
| Resource-based policy | One resource | Yes | Applies to the caller | Yes |

## What gets tested

- **The management account exemption.** An SCP at the root does not restrict the management account. A scenario where a prohibited action succeeded almost always resolves here or to a service-linked role.
- **SCPs do not grant.** Attaching an allow-list SCP gives nobody permissions. IAM must still grant the action, and the effective permission is the intersection.
- **SCP versus RCP.** Preventing an outside account from reading your S3 bucket is an RCP, because the external principal is not in your organization and your SCP never evaluates for them.
- **Region deny and global services.** The correct answer exempts global endpoints. Denying everything outside a Region breaks IAM, STS, Route 53, and CloudFront.
- **Protecting logging.** Denying CloudTrail and Config mutation APIs, with an exception for a named break-glass or security role, is the standard answer for tamper resistance, alongside an organization trail in a separate account.
- **Root user handling.** The principal ARN pattern restricts member account root. For removing root credentials entirely, the modern answer is centralized root access management, not an SCP.
- **Allow list versus deny list.** Sandbox and highly regulated OUs get allow lists. General workload OUs get deny lists. Questions describing a broken deployment after a new service launch point at an allow list.
- **Service-linked roles.** Expect a scenario where an AWS service continued operating despite an SCP. This is by design.
- **Quotas.** Limited policies per entity and a size cap per policy force consolidation, which is why large organizations run a small number of large SCPs.
- **Testing approach.** Attach to a non-production OU, monitor CloudTrail for explicit denies, then promote. There is no simulator that fully evaluates SCPs.

## Limitations

- The management account is permanently outside SCP control, which is the strongest argument for running no workloads and storing no data there.
- Service-linked roles bypass SCPs, so "nothing in this account can do X" is never quite true.
- Deny-only. SCPs cannot grant, cannot remediate existing resources, and cannot express any requirement without a supporting condition key.
- Condition key coverage is uneven across services, and the keys that exist are not always evaluated at the moment you need them, which is why declarative policies were introduced for configuration state.
- Blast radius on error is organization-wide and immediate, with no dry run, no staged rollout mechanism, and denials that surface as confusing failures in unrelated systems.
- Deny lists grow indefinitely and are never provably complete. Allow lists are provably complete and break constantly.
- SCPs govern the principal side only. Data perimeters, external access, and resource exposure need RCPs and resource policies.
- They provide no detection. Attempted violations are visible only if someone is reading CloudTrail for explicit denies.