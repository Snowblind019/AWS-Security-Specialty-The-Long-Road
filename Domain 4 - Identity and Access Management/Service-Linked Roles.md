# Service-Linked Roles (SLRs)

A service-linked role is a special IAM role that an AWS service predefines and manages so it can act on your behalf inside your account. AWS owns the whole definition: the trust policy is locked to that one service's principal, the permissions come from an AWS-managed policy, and the name follows a fixed `AWSServiceRoleFor*` pattern. You can see it, list it, and audit it, but you cannot rewire its trust, and in most cases you cannot edit its permissions either. It typically appears automatically the first time you enable a feature that needs it. On the SCS exam the role matters because it is part of your IAM surface, it behaves differently from a role you create, and it has some governance quirks (notably that SCPs do not restrict it). The thing to hold onto: an SLR is a role the service owns and assumes itself, scoped and named by AWS, which you monitor rather than modify.

## How it works

- **The trust policy is fixed to the service principal.** For example `elasticloadbalancing.amazonaws.com` with `sts:AssumeRole`, and you cannot edit it. Only that service can assume the role, which blocks it from being repurposed or abused by another principal.
- **Permissions come from an AWS-managed policy.** You can view and audit what the role is allowed to do, but you generally cannot change it; AWS maintains the policy and updates it as the service evolves.
- **Creation is usually automatic.** Enabling a feature often creates the SLR on first use, or you create it explicitly with `iam:CreateServiceLinkedRole`. Some services require the role to exist before the feature works.
- **Naming is predictable.** `AWSServiceRoleForElasticLoadBalancing`, `AWSServiceRoleForAutoScaling`, and so on. The name and the trust principal tell you which service owns it.
- **Deletion is guarded.** `iam:DeleteServiceLinkedRole` only succeeds when the service is no longer using it, AWS validates that asynchronously, and deleting one that is in use breaks the dependent feature.

## SLR vs service role vs regular role

| Feature | Service-linked role | Service role (you create) | Regular IAM role |
|---|---|---|---|
| Created and owned by | The AWS service | You, then pass to a service | You |
| Trust policy | Fixed to one service, not editable | You set it to the service principal | Fully customizable |
| Permissions | AWS-managed, usually not editable | You define and edit | You define and edit |
| Needs `iam:PassRole` | No, service assumes its own role | Yes, you pass it to the service | N/A |
| Name | `AWSServiceRoleFor*` | Anything | Anything |
| Lifecycle | Tied to the service | You manage | You manage |

## What gets tested

- **AWS owns the SLR end to end.** Created, trust-locked, and permission-managed by the service. This is the answer when a scenario describes a role that appeared on its own with a fixed trust to a service principal.
- **SLR versus a service role you create.** A service role (a Lambda execution role, an EC2 instance profile role) is one you build and hand to the service, which requires `iam:PassRole`. An SLR is owned by the service and needs no `PassRole`. The exam tests this distinction directly.
- **SCPs do not restrict service-linked roles.** You cannot use an SCP guardrail to constrain what a service does through its SLR, which is a real governance gap and a favorite exam nuance. It ties back to the general rule that SCPs have carve-outs.
- **Deleting an SLR can break production.** Because the feature depends on it, removal is validated and can disable logging, scaling, or certificate renewal. "Access logs stopped appearing" often traces to a deleted SLR.
- **You audit, not author.** Since you cannot edit the trust and usually cannot edit the permissions, the security work is monitoring creation and deletion in CloudTrail (`CreateServiceLinkedRole`, `DeleteServiceLinkedRole`) and periodically reviewing what the role can touch, including with Access Analyzer.

## Limitations

- **Minimal customer control.** The trust policy is not editable and the permissions are AWS-managed, so you cannot tighten or repurpose an SLR the way you can a role you own.
- **Deletion is blocked while in use and breaks the feature.** It is not safe to remove an SLR you think is unused without confirming no service depends on it.
- **SCP guardrails miss them.** Because SCPs do not apply to SLRs, org-wide guardrails cannot bound the actions a service takes via its service-linked role.
- **One service only.** An SLR cannot be reused for anything else; it is bound to the single service that owns it.
- **Not universally supported.** Services that do not offer an SLR use a regular service role you create and manage instead, so the pattern is not consistent across every service.
- **Source-note correction.** SLR permissions are AWS-managed, not customer-tuned; the earlier framing that "this is where you control the scope of what AWS services can do" is not accurate for SLRs. You review and audit that policy; you do not generally set it.