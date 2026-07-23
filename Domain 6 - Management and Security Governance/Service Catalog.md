# AWS Service Catalog

AWS Service Catalog publishes vetted infrastructure templates as products that end users can launch without holding the permissions to create the underlying resources. That last clause is the whole security proposition. A developer who needs an encrypted, tagged, hardened EC2 stack does not get `ec2:RunInstances` and `iam:PassRole`; they get permission to launch one specific product, and Service Catalog assumes a launch role to build it on their behalf. The result is self-service provisioning where the only configurations reachable are the ones a security team authored and versioned, with parameter values constrained, tagging enforced, and every provisioning action recorded in CloudTrail. It is the practical answer to the tension between developer autonomy and least privilege, which is otherwise resolved badly in both directions. The thing to hold onto: Service Catalog moves the permission from the person to the product, so the approved path becomes the only path a low-privileged user has.

## How it works

**Products are versioned templates.** A product wraps a CloudFormation template, or a Terraform configuration using the Terraform product types, with version history. Versions can be deprecated so existing deployments keep running while new launches move to the current one.

**Portfolios group products and carry permissions.** Access is granted to IAM users, groups, and roles at the portfolio level, so entitlement is managed by collection rather than per product.

**The launch constraint is the security control.** It names an IAM role that Service Catalog assumes to provision the stack. The end user needs only Service Catalog permissions, typically the end-user managed policy, and never needs the underlying resource permissions. Without a launch constraint the user's own permissions are used, which discards most of the benefit.

**Other constraints narrow the product further.** Template constraints restrict parameter values with rules, so a user cannot pick an unapproved instance type or disable encryption through a parameter. TagOptions enforce required tag keys and permitted values. Notification constraints publish stack events to SNS for approval and alerting workflows. Resource update constraints control whether users may change tags on provisioned resources. StackSet constraints let a single launch deploy across accounts and Regions.

**Portfolio sharing scales it across the organization.** Sharing through AWS Organizations distributes a portfolio to an OU or the whole organization without per-account invitations, and shared portfolios remain owned and updated centrally, so a template fix propagates rather than being copied. Principal sharing lets the sharing account define which principal names in receiving accounts get access.

**Provisioned products are the deployed instances.** Users see and manage only their own, can update to a newer product version, and can terminate. Drift detection compares a provisioned product to its template.

**Service actions cover day-two operations.** Defined as SSM Automation documents, they let a user restart an instance, rotate something, or run a maintenance task against their provisioned product without holding the underlying API permissions or console access.

**Control Tower Account Factory is built on it.** Account provisioning is surfaced as a Service Catalog product, which is why account creation can be delegated to teams that hold no Organizations permissions.

**It is only mandatory if the alternative is denied.** Service Catalog constrains what a low-privileged user can do. Making it the sole provisioning path requires IAM and SCPs that deny direct resource creation, otherwise it is an option rather than a control.

## Comparison

| Mechanism | Consumer needs resource permissions | Constrains parameter values | Central update propagation | Cross-account deployment |
| --- | --- | --- | --- | --- |
| Service Catalog product | No, with a launch constraint | Yes, template constraints | Yes, via shared portfolios | Yes, with StackSet constraints |
| Direct CloudFormation | Yes, or via a stack service role | Only by template design | No | No |
| CloudFormation StackSets | Not applicable, administratively deployed | Not applicable | Yes | Yes |
| Shared Terraform module | Yes | Only by module design | Only on version upgrade | No |
| AWS Proton | No, platform team owns templates | Yes, via schema | Yes | Environment dependent |
| Raw console access | Yes, fully | No | No | No |

## What gets tested

- **Self-service without permissions.** The signature scenario: developers must provision approved infrastructure but must not be able to create those resources directly. The answer is a Service Catalog product with a launch constraint, and the distractors are IAM policies that grant the resource permissions anyway.
- **Constraining choices.** Preventing a user from selecting an unapproved instance type, Region, or unencrypted option is a template constraint, not a Config rule and not an SCP.
- **Enforced tagging.** TagOptions apply required tags at provisioning. Tag policies in Organizations are the org-level counterpart, and questions sometimes contrast them.
- **Multi-account distribution.** Share the portfolio through AWS Organizations rather than recreating products per account, so updates propagate from one owner.
- **Making it the only path.** Any question phrased as "ensure they cannot provision any other way" requires an SCP or IAM denial alongside Service Catalog. Service Catalog alone is a convenience, not a guarantee.
- **Day-two operations.** Service actions backed by SSM Automation are the answer for letting users operate their resources without console or API permissions.
- **Account vending.** Control Tower Account Factory is a Service Catalog product, which is how account creation is delegated safely.
- **Least privilege on the launch role.** The launch role should be scoped to what the product actually creates. A launch role with administrative permissions turns a constrained product into a privilege escalation path.
- **Cost.** Service Catalog itself is free, so cost is never the objection.

## Limitations

- Only as good as the templates. A product with an insecure template distributes that insecurity efficiently, which makes template review and scanning a prerequisite rather than an optimization.
- The launch role is a privileged identity that anyone entitled to the product can indirectly exercise. Over-scoping it is the most common way this pattern is undermined.
- Not self-enforcing. Users who retain direct API access will bypass it, so it depends on denial controls elsewhere.
- Template maintenance is real work. Products need version updates, deprecations, and communication, and stale products push teams toward building their own.
- Provisioned resources can still be modified afterward by anyone with permissions on those resources, so drift detection and Config remain necessary.
- The catalog covers provisioning only. It says nothing about runtime security, data handling, or how the deployed workload is operated.
- Parameter-driven flexibility fights standardization. Every additional parameter added to satisfy a team is another dimension where the approved product can produce an unapproved result.