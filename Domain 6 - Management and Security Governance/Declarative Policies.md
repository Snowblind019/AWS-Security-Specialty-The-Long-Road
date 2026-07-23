# Declarative Policies

A declarative policy is an AWS Organizations policy type that states the configuration a service must hold across your accounts, and has the service itself enforce that state permanently. Instead of denying a list of API actions the way a service control policy does, you declare an outcome, for example that instance metadata must require IMDSv2, that AMIs may only come from approved providers, or that VPCs must block internet gateway traffic, and the service refuses any request that would move it away from that state. The security value is durability. An SCP is only as complete as the actions and condition keys it enumerates, so a newly launched API or a new console path can leave a gap that nobody notices until an audit or an incident. A declarative policy is expressed against the service attribute rather than the API surface, so it continues to hold as the service evolves. The thing to hold onto: an SCP blocks the calls you thought to name, a declarative policy pins the setting regardless of how someone tries to change it.

## How it works

**It is a management policy type, disabled by default.** The organization must have all features enabled, and the policy type must be enabled from the management account before use. Delegated administration for Organizations policies applies. Like other management policies and unlike SCPs, a declarative policy attached to the root does affect the management account.

**Enforcement lives in the service control plane.** The check happens inside the service, not in the IAM evaluation of a named action, so it applies uniformly across the console, CLI, SDK, CloudFormation, Terraform, and any future entry point. A principal with full administrative IAM permissions still cannot move the setting.

**Coverage is per service attribute.** Amazon EC2 was the first supported service, with attributes including instance metadata defaults such as requiring IMDSv2 and setting the hop limit, allowed images settings restricting AMI sources to Amazon, Marketplace, or named accounts, serial console access, snapshot and image public access blocking, and VPC Block Public Access mode. Coverage expands over time, so treat the attribute list as service-defined rather than fixed.

**Syntax uses inheritance operators, not statements.** There is no Effect, Action, or Resource. You assign values per attribute and control whether descendants may override, with `@@assign` for scalars and append or remove semantics for lists.

```json
{
  "ec2_attributes": {
    "instance_metadata_defaults": {
      "http_tokens": { "@@assign": "required" },
      "http_put_response_hop_limit": { "@@assign": "2" }
    },
    "vpc_block_public_access": {
      "internet_gateway_block": {
        "mode": { "@@assign": "block-bidirectional" },
        "exclusions_allowed": { "@@assign": "disabled" }
      }
    }
  }
}
```

**Attachment and inheritance follow the org tree.** Root, OU, or account, with child policies merged according to the operators the parent permits. Locking descendants out of override is the same pattern used by other management policies.

**Account status reports show blast radius before enforcement.** You can generate a report of the current value of a given attribute across every account and Region in the organization, which is how you find the workloads that will break before you attach the policy rather than after.

**Custom error messages are configurable.** When an action is refused, you can return your own message with an internal contact or runbook link instead of a generic denial, which materially reduces the support load of an org-wide control.

**Effective policy is queryable.** `DescribeEffectivePolicy` with the declarative policy type returns the merged result actually in force for an account, which is the correct way to prove coverage rather than reading attached policies and inferring.

**Enforcement is forward looking for existing resources.** Pinning a metadata default governs launches from that point; instances already running with IMDSv1 are not rewritten. Remediating the existing fleet is a Config plus Systems Manager problem.

## Comparison

| Control | Expressed as | Survives new APIs and features | Applies to management account | Fixes existing resources |
| --- | --- | --- | --- | --- |
| Declarative policy | Desired service configuration state | Yes | Yes | No |
| Service control policy | Deny or allow on named actions with conditions | No, gaps appear as services change | No | No |
| Resource control policy | Ceiling on resource-based policy grants | No | No | No |
| Config rule | Evaluation of live resource state | Rule dependent | Yes, if the account is recorded | Only with remediation actions |
| Control Tower proactive control | CloudFormation Hook at stack operation | No, and only on the CloudFormation path | Yes | No |
| Account-level service setting | Per-account, per-Region toggle | Yes | Yes | No |

## What gets tested

- **Durability wording.** Phrases like "must remain enforced as the service adds new capabilities," "cannot be circumvented by any means," or "regardless of how the request is made" point to a declarative policy over an SCP.
- **Declarative policy versus SCP.** If the requirement is to stop an entire service or action from being used, that is an SCP. If the requirement is that a service remain configured a particular way while still being usable, that is a declarative policy.
- **Management account coverage.** Choose the answer noting the management account is included, in contrast to SCP behavior. This is a recurring discriminator across all management policy types.
- **The EC2 attribute set.** IMDSv2 enforcement, allowed AMI providers, VPC Block Public Access, serial console access, and public snapshot or image blocking are the canonical examples. A scenario about S3 or RDS configuration is probably not this policy type.
- **Assessing impact first.** When a scenario worries about breaking existing workloads, the correct step is generating the account status report before attaching, not attaching and monitoring for failures.
- **Existing non-compliant resources.** Declarative policies do not remediate. The complete answer pairs the policy for future state with Config rules and SSM Automation for the current fleet.
- **Prerequisites.** All features enabled plus the policy type enabled in the management account. A scenario where the policy cannot be created usually points at one of these.
- **User experience.** The custom error message capability is the answer when a question asks how to direct blocked users to an internal exception process.

## Limitations

- Supported services and attributes are a short, AWS-defined list. Anything outside it needs SCPs, RCPs, Config, or account settings instead.
- No retroactive remediation. Existing resources keep their current configuration until something else changes them.
- No denial event to alert on in the usual IAM sense, so drift monitoring and coverage proof come from effective policy queries and Config rather than from `AccessDenied` patterns.
- Requires AWS Organizations with all features. Standalone accounts cannot use it and must rely on per-account settings.
- Permissive child operators undermine the control. A root policy that allows descendants to reassign is a policy that an OU can quietly weaken.
- Blunt by nature. Because it pins a configuration rather than scoping by principal or resource, exceptions are awkward, and legitimate workloads that need the excluded behavior must be moved to a differently governed OU.
- Governs configuration only. It does nothing about credentials, data protection, network traffic content, or workload behavior.