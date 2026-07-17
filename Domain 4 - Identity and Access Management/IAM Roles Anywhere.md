# IAM Policies: Inline vs AWS Managed vs Customer-Managed

These are the three flavors of identity-based policy, the JSON permission documents you attach to users, roles, and groups. They differ not in how IAM evaluates them, which is identical, but in who owns them, how they are stored, whether they can be reused and versioned, and how visible they are to auditing. AWS managed policies are authored and updated by AWS. Customer-managed policies are standalone objects you write and own. Inline policies are embedded directly into a single identity with no independent existence. On the SCS exam the type you pick drives blast radius, least-privilege quality, and detectability, and the recurring guidance is to default to customer-managed for anything real. The thing to hold onto: same evaluation, very different lifecycle and governance, and inline is the one that quietly becomes a shadow permission.

## How it works

- **All three share the same structure** of `Statement`, `Effect`, `Action`, `Resource`, and optional `Condition`, and all go through the same policy evaluation. The type never changes an allow or deny.
- **AWS managed policies** are authored by AWS, cannot be edited, are shared across every AWS customer, and are updated by AWS on their own schedule. They are convenient starting points and some service-linked roles require them, but they tend to be broad.
- **Customer-managed policies** are standalone objects in your account with their own ARN. You attach them to many identities, keep up to five stored versions with a settable default and rollback, and manage them through IaC and CI/CD. They appear in policy listings and in Access Analyzer.
- **Inline policies** are embedded one-to-one in a single user, role, or group. They have no separate ARN, are not reusable, carry no version history, are deleted automatically when the identity is deleted, and do not appear in the managed-policy list.
- **Quotas differ.** Managed policies cap at a document size and five versions, with a default limit on how many attach to one principal; inline policies have their own per-identity size limits and no versioning.

## Comparison

| Dimension | AWS managed | Customer-managed | Inline |
|---|---|---|---|
| Owner | AWS | You | You, bound to one identity |
| Editable | No | Yes | Yes |
| Reusable across identities | Yes | Yes | No, one-to-one |
| Versioning / rollback | AWS-controlled | Yes, up to 5 versions | None |
| Listed in policy namespace | Yes | Yes | No, only on the identity |
| Lifecycle | Updated by AWS silently | You manage | Deleted with the identity |
| Best fit | Quick starts, some service-linked roles | Production least privilege, governance | Strict one-to-one that must die with the identity |

## What gets tested

- **Customer-managed is the recommended default.** Reusable, versioned, auditable, and IaC-friendly, it is the answer for production least-privilege and governance scenarios.
- **AWS managed trades control for convenience.** AWS can broaden a managed policy without your review, so a role can silently gain permissions over time. They are often over-broad and cannot be scoped with your own tags or conditions unless wrapped by a permissions boundary or SCP. Fine for quick starts, risky as your production least-privilege layer. Note some service-linked roles mandate a specific AWS managed policy.
- **Inline means a lifecycle-bound one-to-one relationship.** It is the choice when a permission must exist only on one identity and disappear when that identity is deleted, such as break-glass or a tightly scoped exception. The cost is that it is invisible in policy lists and easy to orphan, so it is a poor fit at scale.
- **Only managed policies version.** Up to five versions with a default and rollback for customer-managed; inline has no version history at all. Questions about auditing "who changed this policy and when" favor managed.
- **Know the policy categories, not just these three.** These are identity-based policies. Resource-based policies (bucket, key policies) carry a `Principal` and attach to the resource; permissions boundaries cap the maximum permissions an identity can have without granting anything; SCPs and RCPs are org-wide guardrails. The exam mixes these and expects you to place each correctly.
- **Detection favors managed.** Customer-managed and AWS managed policies surface in `list-policies`, Access Analyzer, and Security Hub rollups; inline can be missed, which is a governance blind spot.

## Limitations

- **AWS managed policies drift outside your control.** You cannot pin a version, edit the content, or prevent AWS from adding permissions, and you cannot constrain them with your own conditions directly.
- **Inline policies resist auditing.** No versioning, no reuse, absent from managed-policy listings, and easy to lose track of when identities change, which is exactly how shadow permissions form.
- **Customer-managed still needs lifecycle work.** The five-version cap means you must delete old versions before adding new ones, and over-attaching one policy spreads privilege creep.
- **Managed policy limits apply.** Document size, the five-version ceiling, and the default cap on policies attached per principal all constrain large designs.
- **None of these are org guardrails.** They grant or scope at the identity level only. Capping permissions across an account or organization requires permissions boundaries and SCPs, not a choice among these three types.
- **Source-note correction.** PowerUserAccess is not "everything except IAM and billing"; it allows most services while denying IAM, Organizations, and account management actions. And AWS managed policies do have versions, AWS just controls them, so "no version control" means no control by you, not the absence of versions.