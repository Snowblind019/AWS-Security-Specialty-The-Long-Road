# IAM Permissions: Console vs CLI vs API

Every AWS action is ultimately an API call, and IAM evaluates the same policy the same way no matter how the call arrives. What changes across the console, the CLI/SDKs, and raw API requests is not the evaluation logic but two things around it: how many calls a single action fans out into, and what request context those calls carry. The console turns one button click into many API calls and needs supporting read permissions just to render its screens, so a policy that looks correct can behave differently depending on the entry point. On the SCS exam this shows up as "works in one path, fails in another," as privilege-escalation paths that hinge on context keys, and as attributing activity in CloudTrail by how it was invoked. The thing to hold onto: the permission does not change by path, but the set of calls and the request context do, and that difference is where both bugs and abuse live.

## How the three paths differ

- **Console** is a web UI that fans a single user action into many API calls. Launching an EC2 instance can be a dozen calls, and the screens need `List*`, `Describe*`, and `Get*` permissions to populate. A policy granting only the one write action may throw errors in the console because it cannot render, even though the write itself is allowed.
- **CLI and SDKs** map roughly one-to-one to API actions. You call exactly the action you name, which is the least surprising path: `aws s3 cp` is `s3:GetObject`/`s3:PutObject` and little else.
- **Raw API** is SigV4-signed HTTPS to the service endpoint, the ground truth beneath the other two. It is the most direct, the most scriptable, and the path most used in automation and in credential-theft abuse.

## Comparison

| Dimension | Console | CLI / SDK | Raw API |
|---|---|---|---|
| Relationship to API | Fans out into many calls | ~1:1 with API actions | The API itself |
| Extra permissions to work | Often needs `List`/`Describe`/`Get` to render | Rarely | None beyond the action |
| Request context | Federated/session context, may carry MFA and session tags | Whatever the profile/creds supply | Whatever the signer injects |
| Error messages | Human-readable | Minimal | None; raw response codes |
| Typical abuse use | Uncommon | Common | Very common |
| CloudTrail fingerprint | `userAgent` like `signin.amazonaws.com` | `aws-cli/2.x` | SDK string or arbitrary/spoofed |

## What gets tested

- **The console needs supporting read permissions.** A frequent "works in CLI, fails in console" cause is a policy that grants the action but not the `Describe`/`List`/`Get` calls the console uses to draw the page. The action is allowed; the UI just cannot render. This is the accurate version of the confusion, and it is often the reverse of what people assume.
- **Context keys differ by path, and that drives allow/deny.** `aws:MultiFactorAuthPresent`, `aws:PrincipalTag` (ABAC), source IP, and `aws:ViaAWSService` may be present in a federated console session but absent in a raw key-based CLI call. A condition satisfied one way and not the other is why the same identity succeeds in one path and gets AccessDenied in another.
- **`iam:PassRole` must be resource-scoped.** The console hides it behind a role dropdown; the CLI requires the exact role ARN. Either way, a `PassRole` without a resource condition lets a principal hand a powerful role to a service and escalate. Scope it to specific role ARNs.
- **Attribute activity with CloudTrail fields.** `eventSource`, `userAgent`, and `userIdentity.sessionContext` tell you whether a call came from the console, a specific SDK, or an internal service, which is the detection answer for "where did this action originate."
- **`userAgent` is a signal, not proof.** A raw signed request can set any `userAgent` string it wants, so it can be forged. Use it to spot patterns, never as an authoritative security control.
- **Everything resolves to an API call.** Presigned URLs and STS sessions carry the signer's authority: a presigned S3 URL works without further authentication until it expires, and STS credentials act with the assumed role's permissions. Policy conditions are what constrain these paths.
- **Scope API paths with explicit deny and conditions.** Where a path should be blocked (no MFA, wrong source, wrong tag), an explicit deny with the right condition key is the enforcement, since it beats any allow.

## Limitations

- **CloudTrail does not narrate the console perfectly.** A single console action appears as many events, and some console-only helper calls are easy to miss or show up under unexpected event sources, creating detection blind spots.
- **`userAgent` and client strings are spoofable.** Attribution by client fingerprint is best-effort; a determined caller controls that field on raw requests.
- **The console masks which permission is load-bearing.** Because it quietly calls helpers you may already be allowed, it is hard to tell from the console alone which single permission a workflow actually depends on, which complicates least-privilege design.
- **Some console features have no clean CLI equivalent.** Certain console-supporting actions exist only to power the UI, so testing a role in one path does not guarantee the others behave the same. Test roles in every path you intend to support.
- **Source-note correction.** The claim that granting `iam:CreateUser` works in the console but fails in the CLI is not how it behaves; `CreateUser` is a direct one-to-one API action that works identically in both. The real path-dependent failures come from missing supporting read permissions and from context-key conditions, not from the write action itself.