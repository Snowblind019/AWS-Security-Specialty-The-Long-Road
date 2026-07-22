# Secrets Management

Secrets management is the practice of storing, accessing, rotating, and auditing credentials (DB passwords, API keys, tokens, certificates) so they are never hardcoded and every use is controlled and logged. In AWS the two native stores are Secrets Manager and SSM Parameter Store SecureString, both KMS-encrypted and IAM-gated, and the choice between them is the recurring exam decision. The threat that drives all of it: a leaked secret is often the keys to the kingdom, and attackers actively scan public repos, images, and logs for them, so secrets must be fetched at runtime rather than baked into env vars, code, or Dockerfiles. The thing to hold onto: Secrets Manager is the answer when you need automatic rotation, generated secrets, or cross-account sharing, Parameter Store SecureString is the cheaper choice for config and simple secrets without rotation, and retrieving a secret is always a two-permission gate (the store's Get action plus `kms:Decrypt` on the key).

## How it works

- **Secrets Manager: managed storage plus rotation.** Stores KMS-encrypted secrets, supports automatic rotation via a Lambda (scheduled, for example every 30 days), has native integration for RDS/Aurora/Redshift/DocumentDB credential rotation, and supports resource policies for cross-account access. Apps fetch at runtime via the SDK.
- **Parameter Store SecureString: lightweight and cheaper.** KMS-encrypted parameters for config and small secrets, IAM-controlled, hierarchical paths, but no native rotation and no secret generation. Chosen to avoid Secrets Manager's per-secret cost when rotation is not needed.
- **Retrieval is a two-permission gate.** Reading a secret needs the store's read action (`secretsmanager:GetSecretValue` or `ssm:GetParameter` with decryption) and `kms:Decrypt` on the encrypting key. If the secret uses a CMK, denying the role on that key blocks the read even with the store permission granted.
- **IAM scoping is the core control.** Grant `GetSecretValue` on the specific secret ARN, not `*`, and tighten with conditions (`secretsmanager:SecretId`, `VersionStage`, `aws:SourceVpc`). Use Lambda execution roles or IRSA on EKS to scope per workload.
- **Rotation reduces the exposure window.** Secrets Manager's rotation Lambda changes the credential, updates the secret, and can test the new value, so a leaked secret is short-lived. Parameter Store has no native rotation, so you build it.
- **Auditing is native.** CloudTrail logs `GetSecretValue`/`PutSecretValue` and KMS decrypts, CloudWatch captures rotation Lambda logs, Config tracks changes, and GuardDuty or custom alarms flag unusual access (new IPs, off-hours, anomalous volume).

## Secrets Manager vs Parameter Store SecureString

| Dimension | Secrets Manager | Parameter Store SecureString |
|---|---|---|
| **Automatic rotation** | Yes (Lambda, native for RDS/Aurora/etc.) | No, build it yourself |
| **Generate secrets** | Yes | No |
| **Cross-account sharing** | Yes (resource policy) | No |
| **Cost** | Per secret per month + API | Free standard tier (SecureString advanced tier paid) |
| **Encryption** | KMS (CMK or `aws/secretsmanager`) | KMS (CMK or `aws/ssm`) |
| **Best for** | Rotating creds, generated secrets, cross-account | Config and simple secrets, low cost |

## What gets tested

- **Secrets Manager vs Parameter Store.** Automatic rotation, generated passwords, or cross-account secret sharing point to Secrets Manager. Low-cost config and simple secrets without rotation point to Parameter Store SecureString. This is the most tested distinction.
- **Native RDS rotation.** Rotating database credentials with minimal custom code uses Secrets Manager's built-in rotation for RDS/Aurora, over a hand-built Parameter Store solution.
- **Two-permission retrieval.** A denied secret read despite the Get permission usually means a missing `kms:Decrypt` grant on the CMK. Both permissions are required.
- **Least-privilege on the secret ARN.** The correct IAM answer scopes to the specific secret (and conditions), never `secretsmanager:GetSecretValue` on `*`.
- **Fetch at runtime, never hardcode.** The secure pattern retrieves the secret at runtime and avoids env vars, code, and images, so a dumped Lambda does not expose it.
- **CMK for cross-account and audit.** Sharing secrets across accounts or auditing decrypts uses a customer-managed key, since the default `aws/secretsmanager` key cannot be shared cross-account.
- **Rotate before key deletion.** Deleting or disabling a KMS key without rotating the secret breaks retrieval, so key lifecycle must be coordinated with the secret.

## Limitations

- Parameter Store has no native rotation or secret generation, so credential rotation and generated passwords require Secrets Manager or custom tooling.
- Retrieval depends on KMS, so a missing `kms:Decrypt` grant silently blocks reads even when the store permission looks correct.
- Secrets fetched at runtime still land in the process memory or environment, so a compromised workload or one that logs its inputs can expose them despite encryption at rest.
- Cross-account sharing requires a CMK and resource policies, since AWS-managed keys cannot cross accounts.
- Secrets Manager cost scales per secret and per API call, so high secret counts and frequent fetches (without caching) add up.
- Deleting a KMS key before rotating dependent secrets breaks retrieval, so key and secret lifecycles are coupled and must be managed together.