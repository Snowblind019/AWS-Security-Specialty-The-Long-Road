# AWS IAM

IAM is the authorization control plane for AWS: it decides who (the principal) can take which actions on which resources, under which conditions, and for how long. It evaluates every API call, mints short-lived credentials through STS, and is where least privilege is actually enforced. If CloudTrail tells you what happened and Config tells you what changed, IAM is what decides whether an action was allowed to happen at all. Its whole value on the SCS exam is that access becomes a property of design: with the right evaluation logic, conditions, and explicit denies, entire classes of attack become impossible rather than merely discouraged. The thing to hold onto: IAM is the allow/deny decision layer beneath everything, deny always wins, and nothing is permitted unless something explicitly allows it.

## How it works

- **Principals and identities.** A principal is whoever calls an API (an IAM user, a role session, a service principal, or a federated identity). Identity-based policies attach to users (long-term, avoid access keys), roles (assumable, issue temporary STS credentials, preferred), and groups (RBAC-style collections). The root user sits outside this and is the most privileged identity in the account.
- **Credential types.** Console passwords, long-lived access keys (avoid), STS temporary credentials (best practice, auto-expiring), OIDC web identity (EKS IRSA, GitHub Actions), SAML federation (enterprise SSO), and IAM Roles Anywhere (X.509 for non-AWS workloads). Each is covered in its own note.
- **Policy types.** Identity-based (grant to a principal), resource-based (attached to the resource, carry a `Principal`, enable cross-account), permissions boundaries (cap an identity's maximum permissions), session policies (further limit an STS session), and SCPs/RCPs (Organizations guardrails evaluated as an outer fence). See the policy-types note for the tradeoffs.
- **Evaluation logic.** An explicit `Deny` in any applicable policy fails the request outright. Otherwise the request needs an `Allow` from identity or resource policy, and every applicable guardrail (SCP, RCP, permissions boundary, session policy) must also permit it. With no matching allow, the default is an implicit deny. Short version: deny beats allow, and no allow means deny.
- **Trust policy vs permissions policy.** A role's trust policy says who may assume it (`sts:AssumeRole`, `sts:AssumeRoleWithWebIdentity`, `sts:AssumeRoleWithSAML`, `sts:TagSession`); its permissions policy says what the assumed session may do. You need both.
- **Conditions and ABAC.** Condition keys gate an allow on context (MFA present, source IP, VPC endpoint, TLS, time, tags). ABAC matches a principal tag to a resource tag so one policy scales across many resources instead of an ever-growing list.

## Policy types compared

| Type | Attached to | Grants or limits | Cross-account | Typical use |
|---|---|---|---|---|
| Identity policy | User/group/role | Grants | Indirect (caller's account) | Day-to-day permissions for a principal |
| Resource policy | Resource (S3, KMS, SQS, Lambda) | Grants | Yes, via `Principal` | Share a resource, restrict to a VPC endpoint, allow a service |
| Permissions boundary | User/role | Limits (never grants) | N/A | Cap what a builder role can give itself |
| Session policy | STS session | Limits (never grants) | N/A | Further restrict a powerful role per use |
| SCP / RCP | Account/OU (Organizations) | Limits | Org-wide | Global guardrails outside IAM's grant path |

## What gets tested

- **Evaluation order is the single most tested concept.** Explicit deny anywhere wins; every guardrail (SCP, boundary, session policy) must allow; then an explicit allow is required; otherwise implicit deny. Boundaries and session policies intersect with identity policies, they never add permissions.
- **Cross-account needs an allow on both sides.** The target account grants via a resource policy or a role trust, and the caller's identity policy must also allow the action or the `sts:AssumeRole`. One side alone is not enough for the assume-role pattern.
- **Resource-based policies carry a `Principal`; identity-based do not.** That `Principal` element is what enables cross-account access and how you tell the two apart on sight.
- **Permissions boundaries cap, they do not grant.** Effective permissions are the intersection of the identity policy and the boundary. This is the mechanism for letting engineers create roles safely.
- **SCPs and RCPs are Organizations guardrails.** They only limit, never grant, and SCPs do not affect the management account or constrain service-linked roles. They set the outer boundary before IAM's own evaluation.
- **`iam:PassRole` is an escalation control.** Scope it to specific role ARNs; an unscoped `PassRole` lets a principal hand a powerful role to a service and escalate.
- **MFA conditions have a gotcha.** Enforce with a `Deny` on `aws:MultiFactorAuthPresent` false, and use `BoolIfExists` so that a context missing the key is handled correctly rather than silently bypassing the check.
- **Know the high-value condition keys** (see below), especially `aws:PrincipalOrgID` for org scoping, `aws:SourceIp` versus `aws:VpcSourceIp`, `aws:sourceVpce`, `aws:SecureTransport`, and `aws:SourceIdentity` for tracing federated callers.
- **STS session basics.** AssumeRole defaults to one hour and can go up to the role's max session duration (up to 12 hours), but role chaining is capped at one hour.

## Common condition keys

| Purpose | Key | Example value |
|---|---|---|
| Require MFA | `aws:MultiFactorAuthPresent` | `true` (guard with `BoolIfExists`) |
| Restrict source IP | `aws:SourceIp` | `203.0.113.0/24` |
| VPC endpoint only | `aws:sourceVpce` | `vpce-0123...` |
| Require TLS | `aws:SecureTransport` | `true` |
| ABAC tag match | `aws:PrincipalTag/Service` vs `aws:ResourceTag/Service` | equal |
| Restrict to org | `aws:PrincipalOrgID` | `o-abc123` |
| Enforce encryption on upload | `s3:x-amz-server-side-encryption` | `aws:kms` |

## Limitations

- **IAM is eventually consistent.** Policy and role changes propagate with a short delay, so a just-changed permission may not take effect instantly.
- **Guardrails only subtract.** Boundaries, session policies, and SCPs limit and never grant, so a design that relies on them to add access is broken, and it is easy to accidentally deny something you meant to allow.
- **SCP blind spots.** SCPs do not apply to the management account and do not restrict service-linked roles, so they are not a complete org-wide control on their own.
- **Cross-account resource policies are not self-sufficient for assume-role.** Even when a target resource policy names a principal, the assume-role pattern still needs the caller's identity policy to allow the action.
- **IAM is not a network control.** It can condition on network attributes, but it is an authorization layer, not a firewall; VPC endpoints, security groups, and TLS enforcement do the network job.
- **Long-lived access keys remain possible.** They are still supported, so without governance (prohibit, rotate, monitor via credential reports and Access Advisor) they stay a standing risk.

Related notes in this set: policy types, policy simulator, Access Advisor, Access Analyzer, credential reports, Identity Center, Roles Anywhere, and permissions across console, CLI, and API.