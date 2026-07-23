# AWS Organizations

AWS Organizations arranges multiple AWS accounts into a hierarchy of a root, organizational units, and member accounts, and gives you policy types that apply across that hierarchy. Its security significance is that the account is the strongest isolation boundary AWS offers, stronger than IAM within a single account, and Organizations is what makes running many accounts operationally viable. It supplies the permission ceiling that no IAM policy in a member account can exceed, the trusted access and delegated administration model that lets security services operate organization-wide, and the org-level CloudTrail trail that member accounts cannot disable. Consolidated billing is the least interesting thing about it. The thing to hold onto: IAM decides what a principal is allowed to do, Organizations decides the maximum any principal in that account could ever be allowed to do.

## How it works

**Structure is root, OUs, accounts.** The root is a container, not the management account. OUs nest several levels deep and are the normal attachment point for policies, because attaching to an OU covers accounts added later. Accounts are created directly or invited in, and can be moved between OUs.

**Feature sets matter.** Consolidated billing only gives you shared billing and nothing else. All features enabled is required for every policy type, and this prerequisite is the cause of most "the policy cannot be created" scenarios.

**Policy types are distinct tools.** Service control policies and resource control policies are permission ceilings. Tag policies standardize tagging. Backup policies distribute AWS Backup plans. AI services opt-out policies govern AWS's use of your content. Declarative policies pin service configuration durably. Each must be enabled individually before use.

**SCPs cap what your principals can do.** They set maximum permissions and never grant anything. Effective permissions are the intersection of the SCP allow and the IAM allow, so an action must be permitted at every level from the root down to the account and also granted in IAM. `FullAWSAccess` is attached by default, and replacing it with an allow list is how deny-by-default organizations are built.

**SCPs have three important exclusions.** They do not apply to the management account at all, including its root user. They do not apply to service-linked roles. They do not apply to AWS service principals acting on your behalf. The management account exemption is the reason best practice is to run no workloads there.

**RCPs cap what your resources can grant.** Where an SCP constrains the principal side, an RCP constrains the resource side, limiting the access that resource-based policies in member accounts can hand out, including to identities outside the organization. Coverage is a defined subset of services rather than everything, and `RCPFullAWSAccess` is the default equivalent. Together with condition keys such as `aws:PrincipalOrgID`, `aws:ResourceOrgID`, `aws:SourceOrgID`, and `aws:PrincipalIsAWSService`, this is the mechanism behind a data perimeter.

**Region restriction is a standard pattern with a standard gotcha.** Denying by `aws:RequestedRegion` must exempt global endpoints, or you break IAM, Organizations, Route 53, CloudFront, STS, and Support.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "DenyUnapprovedRegions",
    "Effect": "Deny",
    "NotAction": [
      "iam:*", "organizations:*", "route53:*", "cloudfront:*",
      "sts:*", "support:*", "budgets:*", "waf:*"
    ],
    "Resource": "*",
    "Condition": {
      "StringNotEquals": { "aws:RequestedRegion": ["us-west-2", "us-east-1"] }
    }
  }]
}
```

**Trusted access then delegated administration.** Enabling trusted access lets a service operate across the organization. Registering a delegated administrator moves day-to-day operation out of the management account into a security account. GuardDuty, Security Hub, Macie, Inspector, Detective, IAM Access Analyzer, Config, Audit Manager, Firewall Manager, Backup, and Systems Manager all follow this pattern.

**Organization CloudTrail trails are created centrally and are not editable by members.** A member account cannot stop logging, modify the trail, or delete the events, which is the property that makes the trail admissible as evidence.

**Root credentials can be centralized.** Centralized root access management removes root user credentials from member accounts entirely and performs the few genuinely root-only tasks from the management account through privileged sessions. This eliminates the historical problem of hundreds of dormant root credentials with no MFA.

## Comparison

| Control | Side of the request | Can grant | Applies to management account | Typical use |
| --- | --- | --- | --- | --- |
| Service control policy | Principals in member accounts | No | No | Organization-wide guardrails, Region and service restriction |
| Resource control policy | Resources in member accounts | No | No | Data perimeter, blocking external principals |
| IAM identity policy | The principal | Yes | Yes | Actual permission grants |
| Resource-based policy | The resource | Yes | Yes | Cross-account access, service access |
| Permissions boundary | A specific identity | No | Yes | Safe delegation of IAM administration |
| Session policy | A single session | No | Yes | Further narrowing at assume-role time |

## What gets tested

- **The management account exemption.** An SCP at the root does not restrict the management account. Scenarios describing an action that succeeded despite an SCP usually resolve here, or to a service-linked role.
- **SCPs do not grant.** Removing `FullAWSAccess` and attaching an allow-list SCP does not give anyone permissions; IAM must still grant them. The intersection rule is tested directly.
- **SCP versus RCP.** "Prevent our principals from using service X" is an SCP. "Prevent anyone outside the organization from accessing our S3 buckets, even if a bucket policy allows it" is an RCP. Distractors offer SCPs for the second case.
- **Region deny and global services.** The correct answer uses `NotAction` to exempt global endpoints. An answer denying all actions outside approved Regions breaks IAM and STS.
- **All features required.** Any policy type question where the organization is in consolidated billing mode has that as the blocker.
- **Delegated administration.** Security services should be operated from a dedicated security account, not the management account, and trusted access must be enabled first.
- **Organization trail immutability.** When the requirement is that member account administrators cannot tamper with logging, the answer is an organization trail delivered to a separate log archive account, with S3 Object Lock or a restrictive bucket policy for retention.
- **Root user hygiene.** Centralized root access management is the modern answer for removing member account root credentials. An SCP denying root is the older, partial answer and does not remove the credential itself.
- **Data perimeter condition keys.** Recognize `aws:PrincipalOrgID` for restricting to your own principals, `aws:ResourceOrgID` for restricting to your own resources, and `aws:PrincipalIsAWSService` for not breaking legitimate AWS service access.
- **Cost.** Organizations itself is free, so cost is never the reason to avoid it.

## Limitations

- The management account cannot be constrained by SCPs or RCPs, so it is a permanent exception that must be protected by other means: no workloads, minimal principals, strong root controls.
- SCPs and RCPs deny only. They cannot grant, cannot remediate existing resources, and cannot express requirements that lack a condition key.
- Service-linked roles bypass SCPs by design, which is correct behavior but a real gap in reasoning about guarantees.
- RCP service coverage is partial, so a data perimeter built on RCPs alone leaves uncovered services that still need resource policy discipline.
- Policy quotas are real: limited policies per entity, a size cap per policy, and a nesting depth limit. Large organizations hit these and must consolidate.
- Deny-list SCPs grow unmaintainable, and allow-list SCPs break workloads when new services are adopted. Both failure modes appear in practice.
- Organizations governs the account boundary and permission ceilings. It provides no detection, no logging by itself beyond enabling org trails, and nothing about what happens inside an account within the ceiling.
- The structure is not trivially reversible. OU design, account placement, and which account is the management account are decisions that are expensive to change later.