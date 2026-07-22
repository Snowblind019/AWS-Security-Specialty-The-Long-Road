# Amazon S3 Encryption

S3 encryption protects objects at rest so that data stolen through public exposure, a misconfigured policy, or compromised credentials is unreadable without the key. Since S3 buckets are one of the most common AWS breach points, this is a first-order control, and it is now baseline: S3 applies SSE-S3 encryption by default to all new objects, so there is no unencrypted-at-rest default anymore. The real decisions are which encryption mode to use and how to enforce a stricter one. The thing to hold onto: the four modes are SSE-S3 (AWS keys, default), SSE-KMS (your CMK, auditable and policy-controlled), SSE-C (you supply the raw key), and client-side, you enforce a specific mode with a bucket policy condition, and for SSE-KMS at scale you turn on S3 Bucket Keys to cut KMS costs.

## How it works

- **SSE-S3 is the default.** AWS encrypts every new object with AES-256 using keys it fully manages, free, transparent, and now on by default. This satisfies "encrypted at rest" but gives no CloudTrail key-usage visibility or custom policy.
- **SSE-KMS adds control and audit.** Each object is encrypted with a data key wrapped by your KMS key (AWS-managed `aws/s3` or a CMK). A CMK gives CloudTrail decrypt logging, IAM/key-policy scoping, grants, and rotation. This is the mode for fine-grained control and auditability.
- **S3 Bucket Keys cut SSE-KMS cost.** With Bucket Keys enabled, S3 uses a short-lived bucket-level key to reduce calls to KMS `GenerateDataKey`, dramatically lowering KMS request costs and throttling on high-volume buckets. This is the answer to the "SSE-KMS is expensive at scale" problem.
- **SSE-C means you supply the key per request.** AWS encrypts/decrypts with a key you pass and never stores, so losing it means unrecoverable data, and it is not logged in CloudTrail. Niche and operationally heavy.
- **Client-side encryption keeps AWS out of the crypto.** You encrypt before upload (often via the Encryption SDK), giving maximum control at high operational burden. AWS never sees the plaintext.
- **DSSE-KMS for dual-layer requirements.** Dual-layer server-side encryption applies two independent layers of KMS encryption for regimes (like certain federal standards) that mandate it.
- **Enforcement is a bucket policy condition.** Default encryption sets the baseline, and a bucket policy can require a specific mode by denying uploads whose `s3:x-amz-server-side-encryption` header does not match (for example requiring `aws:kms`), so a client cannot downgrade to a weaker mode.

## S3 encryption modes

| Mode | Key custody | CloudTrail on key use | Enforce/audit control | Use when |
|---|---|---|---|---|
| **SSE-S3** | AWS | No | Default, simplest | Baseline at-rest, no audit need |
| **SSE-KMS** | AWS KMS (your CMK) | Yes | Policy-scoped, auditable | Fine-grained control, compliance |
| **SSE-C** | You supply per request | No | You manage entirely | Rare, external key custody |
| **Client-side** | You (outside AWS) | No (app-side only) | Maximum control | AWS must never see plaintext |
| **DSSE-KMS** | AWS KMS, two layers | Yes | Dual-layer mandates | Federal/dual-layer requirements |

## What gets tested

- **Enforce a mode with a bucket policy, not just default encryption.** Requiring SSE-KMS specifically is a bucket policy denying uploads where the encryption header is not `aws:kms`. Default encryption sets a baseline but a request can specify a different valid mode unless the policy pins it.
- **SSE-KMS for audit and scoped access.** "Who decrypted what and when," per-role key access, and compliance point to SSE-KMS with a CMK. SSE-S3 gives no key-usage audit.
- **S3 Bucket Keys for KMS cost at scale.** High PUT/GET volume with SSE-KMS driving up KMS costs is solved by enabling S3 Bucket Keys, which reduces `GenerateDataKey` calls.
- **Transit vs at rest.** S3 encryption modes are at-rest only. Encryption in transit is `aws:SecureTransport`, a separate control.
- **Default encryption is now on.** New objects are encrypted by default (SSE-S3), so "the object was stored unencrypted" is no longer a default outcome, though a bucket policy is still needed to force a stronger specific mode.
- **Cross-Region with multi-Region keys.** Replicating SSE-KMS objects across Regions uses multi-Region keys so the destination can decrypt with the same logical key.

## Limitations

- SSE-S3 gives no CloudTrail key-usage visibility or custom key policy, so audit and scoped access require SSE-KMS with a CMK.
- SSE-KMS at high volume incurs KMS request costs and can hit throttling unless S3 Bucket Keys are enabled.
- SSE-C puts full key custody, availability, and rotation on you with no KMS safety net and no CloudTrail logging, making it rarely the right choice.
- Encryption protects object contents, not object key names, bucket names, or access logs, so metadata and naming can still leak information.
- Default encryption ensures a baseline but does not enforce a specific mode, so a bucket policy is still required to mandate SSE-KMS and prevent weaker choices.
- At-rest encryption does not authorize access or secure the wire, so it must pair with Block Public Access, IAM/bucket policies, and `aws:SecureTransport` for a complete posture.