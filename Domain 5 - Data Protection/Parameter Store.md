# AWS Systems Manager Parameter Store

Parameter Store (part of AWS Systems Manager) is a managed store for configuration data and secrets, holding values as plaintext String and StringList parameters or as KMS-encrypted SecureString parameters. It is the low-cost, natively integrated place to keep database endpoints, feature flags, API keys, and small secrets, retrievable by IAM-scoped principals and injectable into ECS tasks, Lambda, EC2, and CloudFormation. Its security model is straightforward but has a specific split: SecureString encrypts the value at rest with a KMS key, and reading it back requires both `ssm:GetParameter` in IAM and `kms:Decrypt` on the key. The thing to hold onto: SecureString plus a customer-managed KMS key is how you store secrets here, retrieval is a two-permission gate (SSM and KMS), and Parameter Store is the cheaper, simpler sibling to Secrets Manager, which you pick over it when you need automatic rotation, cross-account sharing, or generated secrets.

## How it works

- **Three parameter types.** String and StringList are plaintext. SecureString encrypts the value with KMS (the `aws/ssm` managed key or a CMK). Only SecureString is encrypted, so secrets must use it, not String.
- **Retrieval is a two-permission gate.** Reading a SecureString needs `ssm:GetParameter` (or `GetParameters`/`GetParametersByPath`) in IAM and, because the value is KMS-encrypted, `kms:Decrypt` on the key. `WithDecryption=true` triggers the decrypt. Denying the role on the CMK blocks the read even if SSM permission is granted.
- **Hierarchies and path-based access.** Parameters are named as paths (`/prod/db/password`), so you can scope IAM to a prefix (`/prod/*`) and fetch a whole branch with `GetParametersByPath`. This is the clean way to separate environments.
- **Standard vs advanced tier.** Standard parameters are free with a 4 KB value limit. Advanced parameters allow larger values (up to 8 KB), more parameters, and parameter policies (like expiration and no-change notifications), at a per-parameter cost.
- **Integration and injection.** ECS task definitions and Lambda reference SecureString parameters so values inject at runtime rather than being baked into images or plaintext env vars, and CloudFormation and other services resolve parameters at deploy time.
- **Auditing and change tracking.** Parameter access and changes log to CloudTrail, parameters keep version history, and EventBridge can react to changes, giving you an audit trail of who read or modified a secret.

## Parameter Store vs Secrets Manager

| Dimension | Parameter Store (SecureString) | Secrets Manager |
|---|---|---|
| **Cost** | Free standard tier | Per-secret monthly + API cost |
| **Encryption at rest** | KMS (SecureString only) | KMS (always) |
| **Automatic rotation** | No native rotation | Built-in rotation (Lambda) |
| **Generate secrets** | No | Yes (random password generation) |
| **Cross-account sharing** | No | Yes (resource policy) |
| **Best for** | Config + simple secrets, low cost | Rotating DB creds, generated secrets |

## What gets tested

- **SecureString plus KMS for secrets.** Storing a secret in Parameter Store means a SecureString backed by a KMS key (a CMK for scoped access and CloudTrail auditing). A plaintext String parameter for a secret is the wrong answer.
- **Retrieval needs both SSM and KMS permissions.** A principal that can call `GetParameter` but cannot decrypt gets denied on a SecureString. The fix for a failed secret read is often a `kms:Decrypt` grant on the key, not an SSM permission change.
- **Parameter Store vs Secrets Manager.** If the requirement is automatic rotation, generated secrets, or cross-account secret sharing, that is Secrets Manager. If it is low-cost config and simple secrets without rotation, Parameter Store is the economical choice. This is the most tested distinction.
- **Path-based IAM scoping.** Restricting access by parameter hierarchy (`/prod/*` vs `/dev/*`) is the clean least-privilege pattern and a common correct answer.
- **Injection over baking.** Referencing SecureString parameters in ECS/Lambda so secrets inject at runtime beats embedding them in images or plaintext environment variables.
- **CMK for cross-account and audit.** Sharing or auditing decrypts requires a customer-managed key, since the default `aws/ssm` key cannot be shared cross-account and gives less control.

## Limitations

- No native automatic rotation. Rotating a secret in Parameter Store is a process you build, whereas Secrets Manager rotates via a managed Lambda. This is the main reason to choose Secrets Manager for credentials.
- No secret generation. Parameter Store stores what you put in it, it does not generate random passwords like Secrets Manager.
- No cross-account sharing of parameters, so multi-account secret distribution needs Secrets Manager (or a CMK-based workaround) rather than Parameter Store.
- Only SecureString is encrypted. A secret accidentally stored as a String parameter is plaintext, so type discipline matters.
- Value size and feature limits split across tiers, so larger values and parameter policies require the paid advanced tier.
- Retrieval depends on KMS availability and the two-permission gate, so a missing `kms:Decrypt` grant silently blocks secret reads even when SSM access looks correct.