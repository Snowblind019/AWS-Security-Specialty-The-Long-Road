# Resource Control Policies

A resource control policy is an AWS Organizations policy type that sets the maximum access anyone can be granted to resources in your member accounts. Where a service control policy caps what your principals may do, an RCP caps what your resources may hand out, and it applies no matter who the caller is: a principal in the same account, a principal in another account in your organization, a principal in a completely unrelated AWS account, or an anonymous request. This is what makes it the enforcement mechanism for a data perimeter. Before RCPs, guaranteeing that no S3 bucket anywhere in the organization could be read by an outside identity meant auditing every bucket policy forever, because a single team could undo the guarantee with one resource policy. An RCP attached at the root makes that guarantee structural rather than aspirational. The thing to hold onto: an SCP protects you from your principals doing something wrong, an RCP protects your resources from being reached by the wrong principal.

## How it works

**It is an authorization policy, enabled per organization.** All features must be enabled and the `RESOURCE_CONTROL_POLICY` type must be enabled from the management account before any RCP can be created or attached. Attachment points are root, OU, or account.

**`RCPFullAWSAccess` is attached by default and must stay.** Like `FullAWSAccess` for SCPs, it is the baseline allow. An RCP evaluation requires an allow at every level from root to account, so detaching the default without replacing it denies everything to the resources in scope.

**Evaluation adds a step, it never adds permission.** A request succeeds only if the identity policy or resource policy grants it, no SCP denies it, and the RCP chain allows it with no explicit deny. RCPs cannot grant access, cannot make a resource policy more permissive, and cannot substitute for one.

**Coverage is a defined service list.** Amazon S3, AWS STS, AWS KMS, Amazon SQS, and AWS Secrets Manager were the initial supported services, with coverage expanding over time. Resources of unsupported services are unaffected regardless of what the policy says, which makes the supported list worth knowing rather than assuming.

**It applies to every caller, including principals in the same account.** This is the property that separates it from an SCP and the property most often misjudged. An RCP restricting access to organization principals also governs requests made by identities inside the owning account, so the conditions have to be written to accommodate legitimate internal access.

**Two exemptions carry over from SCPs.** Resources in the management account are not affected, and service-linked roles are not affected. The management account exemption is another reason to keep workloads and data out of it.

**The canonical policy is an organization-only perimeter with AWS service exceptions.**

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "EnforceOrgIdentityPerimeter",
    "Effect": "Deny",
    "Principal": "*",
    "Action": ["s3:*", "sts:AssumeRole", "kms:*", "sqs:*", "secretsmanager:*"],
    "Resource": "*",
    "Condition": {
      "StringNotEqualsIfExists": { "aws:PrincipalOrgID": "o-exampleorgid" },
      "BoolIfExists": { "aws:PrincipalIsAWSService": "false" }
    }
  }]
}
```

**Condition key choice is the whole design.** `aws:PrincipalOrgID` restricts to identities in your organization. `aws:PrincipalIsAWSService` prevents the policy from breaking AWS services that access your resources on your behalf, such as CloudTrail or Config writing to a log bucket. `aws:SourceOrgID` and `aws:SourceAccount` handle the service-as-intermediary case where an AWS service calls on behalf of a specific account. `aws:SecureTransport` lets one RCP enforce TLS across every supported resource in the organization instead of a statement in every bucket policy. Using the `IfExists` variants matters, since a missing key otherwise evaluates in ways that break legitimate access.

**Rollout should be evidence-driven.** IAM Access Analyzer external access findings identify which resources are currently reachable from outside the trust boundary, and CloudTrail shows which external principals actually use them. Attaching a perimeter RCP without that inventory is how a production integration with a partner account breaks.

## Comparison

| Control | Side constrained | Can grant | Covers same-account callers | Management account | Scope |
| --- | --- | --- | --- | --- | --- |
| Resource control policy | The resource being accessed | No | Yes | Exempt | Organization, supported services only |
| Service control policy | Principals in member accounts | No | Yes, for those principals | Exempt | Organization, all services |
| Resource-based policy | One specific resource | Yes | Yes | Applies | Single resource |
| VPC endpoint policy | Requests traversing that endpoint | No | Yes | Applies | Single endpoint |
| Permissions boundary | One identity's maximum permissions | No | Not applicable | Applies | Single principal |
| IAM identity policy | The principal | Yes | Yes | Applies | Single principal |

## What gets tested

- **RCP versus SCP.** "Prevent anyone outside our organization from accessing our S3 data, even if a bucket policy allows it" is an RCP. "Prevent our developers from using service X" is an SCP. Distractors regularly offer an SCP for the first case, which cannot work because the external principal is not in your organization.
- **RCPs cannot grant.** A scenario where access still fails after attaching a permissive RCP resolves to a missing identity or resource policy grant.
- **The default policy.** Detaching `RCPFullAWSAccess` without an equivalent allow denies everything. Expect this as the cause in a broken-access scenario.
- **Supported services.** If the resource in question is outside the supported list, the RCP is not the answer and per-resource policies still carry the burden.
- **Breaking AWS services.** A perimeter RCP that omits `aws:PrincipalIsAWSService` or the source-org conditions will block CloudTrail, Config, or replication from writing to a bucket. Correct answers include the service exception.
- **TLS enforcement at scale.** One RCP with `aws:SecureTransport` set to false denied is the scalable answer over adding a deny statement to every bucket policy.
- **Management account exemption.** Resources in the management account are not protected by RCPs, which is why the log archive and data accounts are member accounts.
- **Confused deputy scenarios.** `aws:SourceArn`, `aws:SourceAccount`, and `aws:SourceOrgID` appear when an AWS service is the intermediary. Recognize which key belongs to the principal and which to the calling service.
- **Cost.** RCPs are free, like all Organizations policy types.

## Limitations

- Supported service coverage is partial, so an RCP alone is not a complete data perimeter and does not remove the need for well-written resource policies.
- Deny-only. It cannot grant, cannot remediate an over-permissive resource policy, and cannot make a resource accessible.
- Resources in the management account are outside its reach entirely.
- Service-linked roles bypass it, which is intended but is a genuine exception when reasoning about guarantees.
- Applies to same-account access as well as cross-account, so an overly aggressive condition breaks internal workloads, not just external ones.
- Blast radius on misconfiguration is organization-wide and immediate. There is no gradual rollout mechanism built in, which is why the Access Analyzer and CloudTrail inventory step is effectively mandatory.
- Standard Organizations quotas apply: limited policies per entity and a size cap per policy, which forces consolidation in large perimeters.
- Governs authorization only. It says nothing about encryption, logging, network path, or what an authorized principal does with the data once retrieved.