# AWS Resource Access Manager

AWS RAM shares specific resource types across account boundaries without duplicating them and without the consuming account assuming a role in the owning account. The resource stays owned, billed, and administered by one account, while principals in other accounts use it as though it were local. In a multi-account estate this is what makes centralized ownership viable: a networking account owns the VPC, the subnets, the Transit Gateway, and the Resolver rules, and application accounts consume them rather than each building a parallel copy that nobody reviews. From a security standpoint that centralization is the point, since one team owning the network means one place where routing, flow logs, and network controls are enforced. The corresponding risk is that RAM is a legitimate, low-friction path for data and infrastructure to leave the organization, so the interesting controls are the ones that constrain who may create a share. The thing to hold onto: RAM makes a resource available across accounts, it does not by itself grant anyone permission to use it, IAM in the consuming account still has to.

## How it works

**A resource share has three parts.** The resources being shared, the principals receiving them, and a RAM permission defining what the receiver may do. AWS managed permissions exist per resource type, and customer managed permissions allow narrowing beyond the default, which is the least-privilege answer when the managed permission is broader than needed.

**Principals can be accounts, OUs, the organization root, and in some cases IAM roles or users.** Sharing to an OU covers accounts added to that OU later, which is convenient and correspondingly easy to over-scope.

**Organization sharing must be enabled first.** Enabling sharing with AWS Organizations establishes trusted access, after which shares to principals inside the organization are accepted automatically with no invitation step. Shares to accounts outside the organization always require an explicit invitation and acceptance, and invitations expire.

**Access evaluation is layered.** The RAM permission sets what the share allows, the consuming account's IAM policies must still grant the action to the principal, and SCPs in both organizations still apply. A share alone gives nobody access.

**Shared VPC subnets have specific, tested participant boundaries.** Participants launch and manage their own resources in the shared subnet. They cannot modify or delete the VPC, subnets, or route tables, cannot view or modify resources belonging to other participants, and cannot re-share the subnet onward. The owner cannot delete a subnet while participant resources remain in it. Participants can create their own security groups and can reference security groups owned by the VPC owner. The owner sees the network interfaces and can enable VPC Flow Logs covering all participant traffic, which is the reason this pattern is good for centralized network visibility.

**Supported resource types are a defined list.** Common ones include VPC subnets, Transit Gateways, VPC IPAM pools, Route 53 Resolver rules and DNS Firewall rule groups, Network Firewall rule groups, License Manager configurations, EC2 Capacity Reservations and Dedicated Hosts, Cloud Map namespaces, Glue and Lake Formation catalog objects, Service Catalog portfolios, and Outposts. RAM exists largely for resource types that have no resource-based policy of their own.

**External sharing is controllable with condition keys.** The standard guardrail denies creating or updating shares that allow principals outside the organization.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "DenyExternalRAMSharing",
    "Effect": "Deny",
    "Action": ["ram:CreateResourceShare", "ram:UpdateResourceShare"],
    "Resource": "*",
    "Condition": {
      "Bool": { "ram:RequestedAllowsExternalPrincipals": "true" }
    }
  }]
}
```

**Revocation is a management action, not a data action.** Removing a principal or deleting the share ends access, but resources the participant already created in a shared subnet do not disappear, so revocation and cleanup are separate steps.

**Auditing runs through CloudTrail and the RAM console.** Share creation, principal association, and invitation acceptance are all API events, and both owner and participant views show current shares.

## Comparison

| Mechanism | What crosses the boundary | Requires role assumption | Resource duplicated | Typical resource types |
| --- | --- | --- | --- | --- |
| AWS RAM | The resource itself, usable in place | No | No | Subnets, Transit Gateway, Resolver rules, IPAM, catalogs |
| Resource-based policy | Access to a specific resource | No | No | S3, KMS, SQS, Secrets Manager, Lambda |
| Cross-account IAM role | A session in the owning account | Yes | No | Anything, but the principal acts as the other account |
| VPC peering or Transit Gateway attachment | Network reachability only | No | No | Network paths between separate VPCs |
| Copy or replicate | A second copy of the data or resource | No | Yes | AMIs, snapshots, S3 objects |

## What gets tested

- **Shared VPC participant limits.** Expect a question asking what a participant account can and cannot do in a shared subnet. Launch resources yes, modify the VPC or route tables no, see other participants' resources no.
- **Centralized network visibility.** VPC Flow Logs enabled by the VPC owner cover participant traffic, which is why shared VPC beats per-account VPCs when the requirement is one place to inspect network telemetry.
- **Blocking external sharing.** An SCP using `ram:RequestedAllowsExternalPrincipals` is the answer for preventing data or infrastructure from being shared outside the organization. Recognize the `ram:AllowsExternalPrincipals` counterpart for existing shares.
- **RAM versus resource-based policy.** If the resource type has no resource policy, RAM is the sharing mechanism. If a scenario is about S3 or KMS access, the answer is a resource policy plus condition keys, not RAM.
- **RAM versus cross-account roles.** RAM is correct when the requirement is that the consuming account uses the resource directly. A role is correct when the requirement is to perform actions in the owning account.
- **Auto-acceptance.** Shares within an organization with trusted access enabled are accepted automatically. Scenarios describing an unexpected pending invitation usually mean sharing with Organizations was never enabled, or the target is outside the organization.
- **Least privilege on the share.** Customer managed permissions are the answer when the AWS managed permission grants more than the receiver needs.
- **Cost.** RAM itself is free, and the owning account continues to pay for the underlying resource, which is often the stated reason for centralizing it.

## Limitations

- Only supported resource types can be shared, and support varies by resource, so RAM is never a general-purpose cross-account access answer.
- Sharing to an OU or the whole organization is broad and static in intent: accounts added later inherit the share automatically, which is a feature until it is an exposure.
- The consuming account's use of a shared resource is governed by that account's IAM, so the owner cannot fully control what participants do with what they receive beyond the RAM permission.
- Revoking a share does not remove resources participants already created, and in shared subnets those resources block subnet deletion.
- Blast radius is concentrated by design. A misconfiguration in the shared VPC or Transit Gateway affects every consuming account at once.
- Participants cannot re-share, which is correct security behavior but a real constraint in layered organizational structures.
- RAM provides no data-level controls. Sharing a Glue catalog or a subnet says nothing about who can read the underlying data, which remains an IAM, Lake Formation, or security group question.
- Cross-organization shares depend on invitation acceptance and trust in another organization's controls, which is a governance problem RAM cannot solve for you.