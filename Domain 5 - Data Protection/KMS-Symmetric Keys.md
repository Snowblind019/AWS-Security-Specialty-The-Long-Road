# AWS KMS: Symmetric Keys

A symmetric KMS key is a single AES-256 key used for both encryption and decryption, created once and held in KMS where it is never exportable and only ever used by reference. It is the default and by far the most common KMS key type, backing SSE-KMS on S3, EBS, RDS, DynamoDB, Lambda, and virtually every AWS-integrated encryption feature, and it is the key type behind envelope encryption via `GenerateDataKey`. The CMK never touches your data directly, it wraps the data keys that encrypt your data. The thing to hold onto: symmetric keys are the right choice for essentially all bulk and service encryption and DEK wrapping (asymmetric is only for signing or cross-boundary public-key use), they support automatic rotation, and the real security work is scoping access with IAM, key policy, encryption context, and grants, plus watching `Decrypt` usage in CloudTrail.

## How it works

- **One key, two directions.** The same key encrypts and decrypts. `Encrypt`, `Decrypt`, `GenerateDataKey`, `GenerateDataKeyWithoutPlaintext`, and `ReEncrypt` are the core operations, and `ReEncrypt` moves ciphertext from one CMK to another without ever exposing plaintext.
- **Envelope encryption is the standard flow.** A service or app calls `GenerateDataKey`, gets a plaintext DEK plus the DEK wrapped under the CMK, encrypts data locally with the plaintext DEK, discards it, and stores the wrapped DEK with the ciphertext. Reading calls `Decrypt` on the wrapped DEK. Bulk data never streams through KMS.
- **Access is a layered decision.** KMS allows an operation if the key policy, an IAM policy, or a valid grant permits it, and any encryption-context condition matches. The key policy is the foundational gate, IAM and grants add scoped access on top.
- **Encryption context scopes and audits use.** A key-value context passed on encrypt must match on decrypt, which prevents cross-purpose misuse and replay and shows up in CloudTrail. You can condition IAM and key policies on `kms:EncryptionContext:...` to bind a key's use to a project or tenant.
- **Rotation is supported and cheap.** Automatic rotation (historically annual, now with a configurable period) rotates the backing key material while keeping the same key ID, and old ciphertext stays decryptable because KMS retains prior versions. Rotation does not require re-encrypting data.
- **Everything is logged.** `Encrypt`, `Decrypt`, `GenerateDataKey`, `CreateGrant`/`RevokeGrant`, `PutKeyPolicy`, and `ScheduleKeyDeletion` all land in CloudTrail, which is how you detect abnormal decrypt volume, use from unexpected roles or Regions, or shadow data export via `GenerateDataKeyWithoutPlaintext`.

## Symmetric vs asymmetric KMS keys

| Requirement | Symmetric | Asymmetric |
|---|---|---|
| **General data / service encryption** | Yes | No |
| **DEK wrapping / envelope encryption** | Yes | Rarely (via data key pair) |
| **Digital signatures / verification** | No | Yes |
| **Public-key exchange with external clients** | No | Yes |
| **High-throughput bulk operations** | Yes (fast) | No (slow, size-limited) |
| **Automatic rotation** | Yes | No, manual |

## What gets tested

- **Symmetric is the default and the answer for bulk/service encryption.** Encrypting AWS service data, wrapping DEKs, and high-throughput encryption all use symmetric keys. Asymmetric is only for signing/verification or giving external parties a public key.
- **Least privilege on KMS.** Never `kms:*` on `*`. The intended answer scopes to specific keys and actions, often with an encryption-context condition, and uses grants for short-lived delegation instead of bloating the key policy.
- **Encryption context prevents misuse.** Binding a key's use to a context that must match on decrypt is the mechanism to stop a DEK from being reused in the wrong place and to enforce logical access control.
- **Rotation keeps the key ID and does not re-encrypt data.** Enabling automatic rotation is transparent to existing ciphertext, a commonly tested subtlety.
- **Detection via CloudTrail.** Spikes in `Decrypt`, use from new roles or unexpected Regions, and unusual `GenerateDataKeyWithoutPlaintext` are the signals, since KMS logs usage (not content).
- **Key policy plus IAM plus grants.** Access can come from any of the three, so reasoning about who can use a key must consider all of them, not IAM alone.

## Limitations

- Symmetric keys cannot sign or verify and cannot give an external party a public key, so cross-boundary trust and signatures require asymmetric keys.
- The CMK is never exportable, so any requirement to run the raw key outside KMS needs a different model (CloudHSM, or keys held outside AWS via XKS).
- Access can be granted three ways (key policy, IAM, grants), so an over-broad grant or IAM statement is a silent path that key-policy review alone misses.
- Without encryption-context scoping, a key delegated for one purpose can be used for another, weakening least privilege.
- KMS request volume has real cost and rate limits, so latency-sensitive or high-throughput workloads must lean on local DEKs (envelope encryption) rather than per-item KMS calls.
- Encryption protects confidentiality, not authorization. A principal with legitimate `Decrypt` access, or a compromised role that has it, reads the data, so monitoring and tight scoping remain essential.