# Envelope Encryption

Envelope encryption is the design pattern behind nearly all encryption at scale in AWS: instead of encrypting data directly with your master key (CMK), you generate a random data encryption key (DEK), encrypt the data locally with the DEK, then encrypt (wrap) the DEK with the CMK and store the wrapped DEK next to the ciphertext. The master key never touches the plaintext data and never leaves KMS, it is used only to wrap and unwrap DEKs. This is why S3, EBS, RDS, DynamoDB, and Lambda can encrypt at massive scale while KMS stays fast, cheap, and auditable. The thing to hold onto: the CMK wraps the DEK and the DEK encrypts the data, so `GenerateDataKey` (one call returning both a plaintext and a wrapped DEK) is the mechanism, `Decrypt` unwraps, and bulk data never streams through KMS, which is exactly why direct CMK encryption is limited to small payloads.

## How it works

- **Encryption is one KMS call plus local work.** `GenerateDataKey` returns a plaintext DEK and the same DEK wrapped under the CMK. You encrypt the data locally with the plaintext DEK (AES-GCM), discard the plaintext DEK from memory, and store the ciphertext together with the wrapped DEK.
- **Decryption unwraps then decrypts locally.** You read the wrapped DEK, call KMS `Decrypt` to get the plaintext DEK back, then decrypt the data locally. KMS only ever sees the DEK, never your data.
- **Why not use the CMK directly.** KMS `Encrypt`/`Decrypt` on raw data is capped at small payloads (a few KB), rate-limited, and every call is logged and adds latency. Envelope encryption moves the bulk crypto local, so one CMK protects millions of objects without throttling.
- **The CMK stays in the HSM-backed boundary.** The master key never leaves KMS (or CloudHSM behind a custom key store), so wrapping and unwrapping happen inside that boundary and the key material is never exposed to your application.
- **Encryption context binds and audits.** Passing a key-value encryption context on `GenerateDataKey` requires the same context on `Decrypt`, which prevents a wrapped DEK from being unwrapped in the wrong context, and it appears in CloudTrail so you can audit and condition key policies on it.
- **Rotation stays cheap.** Rotating the CMK does not require re-encrypting data. Old wrapped DEKs remain decryptable under the prior key version that KMS still tracks, so rotation is a key-layer operation, not a data-layer one.

## Direct CMK vs envelope encryption

| Aspect | Direct CMK encrypt | Envelope encryption |
|---|---|---|
| **Payload size** | Small (KB-scale limit) | Any size (data encrypted locally) |
| **KMS calls** | One per encrypt/decrypt of data | One per DEK, reused for the data |
| **Throughput** | Rate-limited, latency per call | Local, fast, scales to millions |
| **Master key exposure** | Still never leaves KMS | Never leaves KMS, only wraps DEKs |
| **Rotation** | Re-encrypt affected data | Rotate CMK, wrapped DEKs still valid |

## What gets tested

- **CMK wraps, DEK encrypts.** The exam expects you to know the master key encrypts the data key, not the data, and that `GenerateDataKey` returns both plaintext and wrapped DEK in one call.
- **Direct KMS encryption is size-limited.** If a scenario needs to encrypt large objects, the answer is envelope encryption (a DEK), because direct KMS `Encrypt` is capped at a few KB. This is a common distractor.
- **Rotation does not re-encrypt data.** Rotating a CMK leaves existing wrapped DEKs decryptable, so "rotate the key" does not mean "re-encrypt everything." That is a frequently tested subtlety.
- **Encryption context for scoping and integrity.** Binding a wrapped DEK to a context (tenant, app, env) that must match on decrypt is the mechanism to prevent cross-context misuse and to enforce logical access control auditable in CloudTrail.
- **Per-tenant CMK, per-object DEK.** Multi-tenant isolation uses one CMK per tenant with per-object DEKs, giving both blast-radius separation and scale.
- **KMS sees the DEK, not the data.** In client-side and SDK flows, the plaintext data never reaches AWS, only the DEK does, which is the basis for "AWS never sees my data" claims.

## Limitations

- You are responsible for the plaintext DEK in memory. A DEK that is logged, cached to disk, or left in memory undermines the whole scheme, since it decrypts the data without KMS.
- The wrapped DEK must be stored reliably with the ciphertext. Lose the wrapped DEK and the data is unrecoverable, even though the CMK is intact.
- Application compromise still exposes data, because a compromised app holds the credentials to call `Decrypt` and unwrap DEKs legitimately.
- Reusing one CMK across unrelated services or tenants collapses the blast radius, so key separation is a deliberate design choice envelope encryption enables but does not enforce.
- Skipping encryption context forfeits the context-binding integrity and misuse protection, weakening the guarantees the pattern can provide.
- Envelope encryption solves confidentiality and scale, not authorization. IAM and the CMK key policy still decide who can unwrap a DEK, so misconfigured access defeats it regardless of the crypto.