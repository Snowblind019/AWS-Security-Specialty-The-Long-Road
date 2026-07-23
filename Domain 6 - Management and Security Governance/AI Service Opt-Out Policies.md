# AI Services Opt-Out Policies

An AI services opt-out policy is an AWS Organizations policy type that controls whether AWS may store and use the content your accounts process through its AI and machine learning services for the purpose of improving those services. It is a data governance control rather than an access control: it does not deny a single API call, does not change IAM outcomes, and does not touch encryption. What it changes is AWS's own downstream handling of your customer content, including whether that content may be retained and whether it may be processed in a Region other than the one where the request originated. For workloads under HIPAA, GDPR, contractual data residency clauses, or a customer agreement forbidding secondary use, this policy is the mechanism that makes the commitment technically enforceable across every account in the organization rather than a promise made in a slide deck. The thing to hold onto: an SCP controls what your principals may do, an AI services opt-out policy controls what AWS may do with what they produce.

## How it works

**It is a policy type, and it starts disabled.** The organization must have all features enabled, not consolidated billing only, and the `AISERVICES_OPT_OUT_POLICY` type must be explicitly enabled from the management account before any policy can be created or attached. Delegated administration for Organizations policies is supported.

**Attachment follows the standard organization hierarchy.** Policies attach to the root, to an organizational unit, or to an individual account, and inherit downward. A policy at the root is the normal answer when the requirement is organization-wide and non-negotiable.

**It applies to the management account.** This is the sharp difference from service control policies. An SCP attached to the root never restricts the management account, but a management policy of this type does affect it, so the management account is not a hole in the coverage.

**Syntax is inheritance-operator based, not statement based.** There are no Effect, Action, or Resource elements. You assign a value per service, or use `default` to cover all covered services at once, and you control whether descendants may override with the child policy operators.

```json
{
  "services": {
    "@@operators_allowed_for_child_policies": ["@@none"],
    "default": {
      "@@operators_allowed_for_child_policies": ["@@none"],
      "opt_out_policy": {
        "@@operators_allowed_for_child_policies": ["@@none"],
        "@@assign": "optOut"
      }
    }
  }
}
```

**`@@none` is the lock.** Setting `@@operators_allowed_for_child_policies` to `@@none` prevents any OU or account beneath the attachment point from reassigning the value back to `optIn`. Without it, a child policy can undo the parent, which is exactly the misconfiguration a governance question will describe.

**Per-service override is possible.** You can set `default` to `optOut` and then selectively assign `optIn` for a named service such as `rekognition`, `textract`, `transcribe`, `comprehend`, `translate`, `lex`, `polly`, `codeguru_profiler`, `connect`, `kendra`, `personalize` or `sagemaker`, provided the parent policy allows the operator. The list of covered services is defined by AWS and grows over time, which is why `default` is the durable choice.

**Effect is forward looking.** Opting out stops future retention and use for service improvement. It does not retroactively delete content AWS already stored under a prior opt-in state; removing that requires a request to AWS Support.

**Accounts outside an organization cannot use it.** A standalone account has no Organizations policy engine, so the opt-out must be arranged through AWS Support, or the account must be brought into an organization.

## Comparison

| Policy type | What it governs | Applies to management account | Denies API calls |
| --- | --- | --- | --- |
| AI services opt-out policy | AWS's storage and use of your content for service improvement | Yes | No |
| Service control policy | Maximum permissions for principals in member accounts | No | Yes |
| Resource control policy | Maximum permissions granted by resource policies on org resources | No | Yes |
| Tag policy | Tag key and value standardization and compliance reporting | Yes | No |
| Backup policy | Centrally managed AWS Backup plans and schedules | Yes | No |
| Declarative policy | Persistent service configuration baselines such as EC2 defaults | Yes | Indirectly, by enforcing configuration |

## What gets tested

- **Opt-out versus SCP.** A requirement that customer content not be used to improve AWS services, or not leave the Region for that purpose, is an AI services opt-out policy. A requirement that a team be unable to call an AI service at all is an SCP. Distractors routinely offer a `Deny` on `rekognition:*` for a data-use requirement; it does not achieve the stated goal.
- **Prerequisites.** Expect a scenario where a policy cannot be created. The cause is either the organization is in consolidated billing only mode, or the policy type has not been enabled in the management account.
- **Management account coverage.** Choose the answer stating that the policy does cover the management account, in contrast to SCP behavior. This distinction is a favored discriminator.
- **Preventing override.** When the requirement is that no business unit can opt back in, the correct answer includes `@@operators_allowed_for_child_policies` set to `@@none` at the root, not merely an `optOut` assignment.
- **Scope of the assignment.** Use `default` when the requirement is "all AI services, including any added in future." Naming individual services is the wrong answer when the wording implies durability.
- **Who can act.** Only the management account or a delegated administrator can create and attach. Member account administrators cannot self-opt-out.
- **Existing data.** If the scenario asks about content already collected, the answer involves contacting AWS Support. The policy alone does not purge it.
- **Not a substitute for the rest of the stack.** It does not encrypt, does not log, does not restrict access. Expect it paired in correct answers with KMS, CloudTrail data events, and least-privilege IAM rather than replacing them.

## Limitations

- Covers only the AWS-defined set of AI and machine learning services. A service outside that list is unaffected regardless of how the policy is written.
- Governs service improvement use specifically. It does not stop the normal operational processing required for the service to return a result, and it does not stop abuse detection or legally required retention where those apply.
- No enforcement signal at call time. A principal calling a covered service sees identical behavior whether opted in or out, so there is no denial event to alert on and no CloudTrail `AccessDenied` to detect drift.
- Forward only. It creates no obligation on AWS to delete previously retained content without a separate request.
- Requires Organizations with all features. Single-account environments and consolidated-billing-only organizations cannot use it.
- Child policy operators are easy to leave permissive, producing a policy that looks compliant at the root while an OU quietly reassigns `optIn` beneath it.
- Provides no evidence artifact of its own. Demonstrating the control to an auditor means exporting the effective policy per account, not pointing at a report.