# AWS KMS Grants

A KMS grant is a way to delegate a scoped, temporary subset of key operations to a principal without editing the key policy or IAM. It lives as a separate object attached to the key, names a grantee (a role, service, or user) and the exact operations it may perform (`Encrypt`, `Decrypt`, `GenerateDataKey`, and so on), can be constrained by encryption context, and can be revoked instantly, mid-session, with no policy change. This is the mechanism AWS services themselves use behind the scenes: when S3, EBS, or RDS encrypt with your CMK, they create grants automatically. The thing to hold onto: a grant is programmatic, scoped, and instantly revocable delegation that works alongside the key policy (KMS authorizes if the key policy, an IAM policy, or a valid grant allows the action), which makes it ideal for short-lived and service-driven access but means grants are an access path you must monitor separately from IAM.

## How it works

- **A grant delegates specific operations to a grantee.** `CreateGrant` names the grantee principal, the allowed operations, optional constraints, and an optional retiring principal. The grant creator must be permitted by the key policy to create grants.
- **Grants are additive to the key policy and IAM.** KMS allows an operation if the key policy, an applicable IAM policy, or a valid grant permits it. So a principal with no `kms:Decrypt` in IAM can still decrypt if a grant allows it. Grants add access, they do not subtract it.
- **Encryption-context constraints scope usage.** A grant can require an exact encryption context (`EncryptionContextEquals`) or a subset, so it is only usable for requests carrying that context. This binds the delegated access to a specific purpose, tenant, or pipeline stage.
- **AWS services create grants for you.** When you encrypt an EBS volume or an S3 object with a CMK, the service creates a grant so it can use the key on your behalf, then retires it when done. This is why you see service-created grants you did not author.
- **Revoke and retire end access immediately.** `RevokeGrant` (admin or creator) forcibly removes it, `RetireGrant` (the grantee or retiring principal) voluntarily ends it. Either takes effect immediately, even mid-session, unlike a key-policy edit.
- **Grant tokens handle propagation delay.** `CreateGrant` returns a grant token the grantee can pass immediately to use the grant before it is fully eventually-consistent across KMS, useful for transient automation.

## Key policy vs grant

| Aspect | Key policy | KMS grant |
|---|---|---|
| **Nature** | Foundational, long-term | Scoped, temporary delegation |
| **Lives in** | Key metadata | Separate grant object |
| **Requires policy edit to change** | Yes | No |
| **Instant revocation** | No (edit and propagate) | Yes (`RevokeGrant`/`RetireGrant`) |
| **Visibility** | On the key | Only via `ListGrants` / CloudTrail |
| **Best for** | Admin and broad access rules | Services, sessions, short-lived scoped access |

## What gets tested

- **Grants for temporary, scoped, revocable delegation.** When a scenario needs to give a Lambda, a service, or a short-lived job just enough key access without editing the key policy, and to pull it back instantly, that is a grant, not an IAM change.
- **Grants are additive.** A principal can perform a KMS operation via a valid grant even with no matching IAM permission. Reasoning that "IAM denies it so it cannot happen" is wrong if a grant exists.
- **Encryption-context constraints.** Binding delegated access to a specific context so the key can only be used for the intended purpose is a grant constraint, a common least-privilege answer.
- **Service-created grants are normal.** Seeing grants you did not create is expected because EBS, S3, and RDS create them to use your CMK. This is not automatically suspicious.
- **Monitoring grants.** Grants are not obvious in the console, so `CreateGrant`, `RevokeGrant`, and `RetireGrant` in CloudTrail, plus `Decrypt`/`Encrypt` calls without matching IAM, are the events to watch. Grants are a delegation path that bypasses IAM visibility.
- **Instant revocation vs policy edit.** If the requirement is to cut access immediately, revoking a grant beats editing a key policy, which has to propagate.

## Limitations

- Grants add access outside IAM and the key policy, so an over-broad or forgotten grant is a silent privilege path that IAM review alone will not catch.
- Grants are not clearly surfaced in the console, so you must use `ListGrants` and CloudTrail to inventory them, which makes them easy to overlook during audits.
- Constraints are only as tight as you make them. A grant without an encryption-context constraint delegates the operation broadly, undermining least privilege.
- Grants delegate use of the key, not ownership. They cannot exceed what the key supports, and the key policy still governs who may create grants in the first place.
- Because services create and retire grants automatically, distinguishing legitimate service grants from a malicious one requires context, not just the presence of a grant.
- Revocation is immediate but relies on you knowing the grant exists. An attacker who created a grant for persistence is only removed once that grant is discovered.