# SSE-C (Server-Side Encryption with Customer-Provided Keys)

SSE-C is the S3 server-side encryption mode where you supply the raw AES-256 key in the HTTPS request headers on every PUT and GET, AWS uses it to encrypt or decrypt the object server-side, and then discards the key immediately without ever storing it. You get AWS's encryption machinery but own the entire key lifecycle: generation, storage, rotation, and the total risk that comes with it. Because KMS is not involved, there is no CloudTrail record of key usage, no IAM/key-policy control over decryption, no encryption context, and no recovery if you lose the key. The thing to hold onto: SSE-C means AWS never holds or logs the key, so it is the near-opposite of SSE-KMS on auditability and safety, it requires HTTPS (S3 rejects SSE-C over HTTP), and it is rarely the right answer, because a mandate to keep keys out of AWS is usually better served by client-side encryption or an external key store (XKS).

## How it works

- **You generate and hold the key.** A 256-bit AES key you create, format, and store. AWS provides no entropy, storage, or backup for it.
- **The key travels in headers on every request.** PUT and GET include `x-amz-server-side-encryption-customer-algorithm: AES256`, the base64 key, and an MD5 of the key for integrity. S3 uses it, encrypts or decrypts server-side, and discards it.
- **HTTPS is mandatory.** Because the raw key is in the request, S3 rejects SSE-C requests over plaintext HTTP. Unlike SSE-S3 and SSE-KMS, SSE-C cannot be used without TLS.
- **The exact key is required to read back.** GET must present the identical key. A missing, wrong, or rotated key yields failure, and there is no recovery path if the key is lost.
- **No KMS means no KMS features.** No CloudTrail decrypt logging, no IAM `kms:Decrypt` scoping, no grants, no encryption context, and no revocation. Rotation means re-uploading objects under a new key.

## SSE-C vs SSE-S3 vs SSE-KMS

| Feature | SSE-S3 | SSE-KMS | SSE-C |
|---|---|---|---|
| **Who holds the key** | AWS | AWS KMS (CMK) | You (raw key, per request) |
| **Key stored in AWS** | Yes | Yes | Never |
| **CloudTrail on key use** | No | Yes | No |
| **IAM/policy control of decrypt** | No | Yes | No |
| **Encryption context** | No | Yes | No |
| **HTTPS required** | No | No | Yes |
| **Rotation** | Automatic | Optional (CMK) | Manual, re-upload |
| **Data-loss risk** | Low | Low | High (lose key, lose data) |

## What gets tested

- **SSE-C means AWS never stores or logs the key.** If a scenario requires AWS to never hold the key but still use server-side encryption, SSE-C fits mechanically, but the exam usually steers to client-side or XKS for the audit and safety SSE-C lacks. Recognize SSE-C as the "you pass the key every request, no KMS" mode.
- **No CloudTrail visibility.** SSE-C gives no key-usage audit, so if the requirement is auditing who decrypted what, SSE-C is wrong and SSE-KMS is right.
- **HTTPS is required for SSE-C.** A distinguishing fact: SSE-C requests must be over TLS, whereas SSE-S3/SSE-KMS do not have that hard requirement at the encryption-mode level.
- **Lose the key, lose the data.** There is no AWS recovery, so a scenario emphasizing recoverability argues against SSE-C.
- **No IAM/KMS conditions.** You cannot enforce access with `kms:Decrypt`, encryption context, or grants under SSE-C, so requirements for policy-based key control point to SSE-KMS.
- **SSE-C vs client-side vs XKS for external key custody.** A "keys must never be in AWS" mandate is better met by client-side encryption or XKS (which keep KMS-style workflows and, for XKS, CloudTrail), so SSE-C is rarely the intended answer even though it technically keeps the key out of AWS.

## Limitations

- No key backup or recovery. A lost or mistyped key permanently loses the data, since AWS never had it.
- No CloudTrail visibility into encryption/decryption, making detection engineering and forensics nearly impossible for these objects.
- No IAM or KMS policy control, no grants, and no encryption context, so all the KMS access-control advantages are forfeited.
- No revocation or clean rotation. Changing keys means re-uploading every affected object under the new key.
- HTTPS is mandatory and the key rides in the request, so any handling mistake or interception risk around the header is significant, and a compromised key silently decrypts everything with no audit trail.
- It shifts total operational and security burden to you while giving less observability than any other S3 mode, which is why AWS and the exam favor SSE-KMS, client-side, or XKS for nearly all real requirements.