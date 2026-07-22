# SSE-S3 (Server-Side Encryption with S3-Managed Keys)

SSE-S3 is the simplest S3 encryption mode: AWS encrypts objects at rest with AES-256 using keys it fully generates, rotates, and protects, with no KMS, no key management, and no cost to you. It is also now the default, S3 applies SSE-S3 to all new objects automatically, so "encrypted at rest" is baseline. The trade is that all control, visibility, and accountability stay with AWS: there is no CloudTrail record of key usage, no IAM or key-policy gate on decryption, no encryption context, and no revocation. Access is governed purely by S3 object permissions, so anyone with S3 read access can read the object. The thing to hold onto: SSE-S3 is encryption without governance, it satisfies "must be encrypted at rest" cheaply and simply, but the moment you need to audit who decrypted what, scope key access, or revoke, you need SSE-KMS with a customer-managed key instead.

## How it works

- **Envelope encryption, fully AWS-managed.** On PUT, S3 encrypts the object with a unique data key and wraps that key with an S3-managed master key. On GET, S3 decrypts transparently. You never see or manage any key.
- **It is the default.** New objects are encrypted with SSE-S3 by default, so an object is not stored unencrypted unless a different mode is chosen. The header value is `AES256`.
- **Enable and enforce.** You can rely on the default, set it explicitly per object (`x-amz-server-side-encryption: AES256`), or set bucket default encryption. A bucket policy can deny PUTs where the encryption header is not `AES256` to force this specific mode.
- **No KMS means no KMS features.** No CloudTrail on key use, no `kms:Decrypt` scoping, no grants, no encryption context, no revocation. Access is only S3 object permissions.
- **Default encryption is not retroactive.** Setting bucket default encryption covers new objects only, not existing ones, and without a bucket policy a client can still specify a different valid mode.

## SSE-S3 vs SSE-KMS

| Feature | SSE-S3 | SSE-KMS |
|---|---|---|
| **Key management** | AWS only | AWS-managed key or your CMK |
| **CloudTrail on key use** | No | Yes |
| **Decrypt gated by KMS permission** | No | Yes (`kms:Decrypt`) |
| **Encryption context** | No | Yes |
| **Revocation** | No | Yes (key policy) |
| **Cost** | Free | CMK + KMS requests |
| **Access control** | S3 object permissions only | S3 + KMS two-permission model |

## What gets tested

- **SSE-S3 for simple, cheap at-rest encryption.** When the requirement is only "encrypted at rest" with no audit or key-control need (public datasets, low-sensitivity logs), SSE-S3 is the simple, free answer.
- **SSE-S3 vs SSE-KMS on governance.** If the requirement is auditing decrypts, scoping key access, encryption context, revocation, or cross-account key ownership, SSE-S3 cannot do it and SSE-KMS with a CMK is required. Recognizing this boundary is the core tested distinction.
- **Access is only S3 permissions.** Under SSE-S3, anyone with S3 read access can read the object, because there is no separate KMS gate. A scenario where a broad S3 role could read sensitive logs undetected points at the SSE-S3 limitation and argues for SSE-KMS.
- **Enforce the mode with a bucket policy.** Requiring SSE-S3 specifically is a bucket policy denying uploads without the `AES256` header, since default encryption alone can be overridden per request.
- **Default is on but not retroactive.** New objects are encrypted by default, but existing objects and mode-overriding requests are not covered without policy, a common nuance.

## Limitations

- No CloudTrail visibility into key usage, so you cannot prove who decrypted an object or when, which rules SSE-S3 out for regulated or forensic requirements.
- No KMS-level access control: decryption is not gated by a key permission, so any principal with S3 read access reads the object, with no second gate.
- No encryption context, grants, or revocation, so all the conditional and delegation controls of KMS are unavailable.
- No customer control over key rotation or retirement, since AWS manages the keys silently.
- Default encryption is not retroactive and does not by itself prevent a client from choosing a different mode, so enforcing SSE-S3 specifically still needs a bucket policy.
- It provides confidentiality at rest only, not authorization, transit protection, or exposure control, so it pairs with IAM, `aws:SecureTransport`, and Block Public Access rather than standing alone.