# SSE-KMS (Server-Side Encryption with KMS Keys)

SSE-KMS is the S3 server-side encryption mode that uses a KMS key to protect objects, giving you the cryptographic control that SSE-S3 hides: CloudTrail logging of key use, IAM and key-policy scoping of decryption, encryption context, and revocation. The defining feature is the two-permission model: reading an SSE-KMS object needs both S3 permission (`s3:GetObject`) and KMS permission (`kms:Decrypt`) on the key, so the KMS key policy becomes a second authorization gate independent of S3. This is what enables data-egress control, cross-account key ownership, and object-level access auditing. The thing to hold onto: SSE-KMS ties every object read to a `kms:Decrypt` you can log, scope, and revoke, a customer-managed key is required for that control (the default `aws/s3` key gives less), and S3 Bucket Keys are how you keep the KMS request cost manageable at scale.

## How it works

- **Envelope encryption per object.** On PUT, S3 calls KMS `GenerateDataKey`, encrypts the object with the plaintext data key, and stores the object plus the wrapped data key. On GET, S3 sends the wrapped key to KMS `Decrypt` and decrypts. You never see the data key but control the CMK that wraps it.
- **Key choice: `aws/s3` or a CMK.** The AWS-managed `aws/s3` key is automatic and free but cannot be policy-scoped, shared cross-account, or audited the same way. A customer-managed CMK gives key policy, rotation, tagging, grants, and CloudTrail visibility.
- **Two-permission gate.** Access requires both S3 and KMS permissions. A principal with full S3 access still gets AccessDenied if the KMS key policy denies them, which is the core control SSE-KMS adds over SSE-S3.
- **CloudTrail logs every key use.** `GenerateDataKey` on PUT and `Decrypt` on GET appear in CloudTrail, so you can tie object access to a principal, correlate in a SIEM, and alert on decrypts from unexpected regions or identities.
- **Enforce via bucket policy and key policy.** A bucket policy can deny PUTs whose `s3:x-amz-server-side-encryption` is not `aws:kms` (or that omit a required key), and the KMS key policy scopes who can decrypt. Together they lock down both how objects are encrypted and who can read them.
- **S3 Bucket Keys cut cost.** Enabling S3 Bucket Keys uses a short-lived bucket-level key to reduce `GenerateDataKey` calls to KMS, dramatically lowering cost and throttling on high-volume buckets.

## SSE-S3 vs SSE-KMS

| Feature | SSE-S3 | SSE-KMS |
|---|---|---|
| **Key** | AWS-managed | AWS-managed `aws/s3` or CMK |
| **CloudTrail on key use** | No | Yes (`GenerateDataKey`, `Decrypt`) |
| **Two-permission (S3 + KMS)** | No | Yes |
| **Fine-grained access control** | No | Yes (IAM, key policy, grants) |
| **Revocation** | No | Yes (change key policy) |
| **Encryption context** | No | Yes |
| **Cross-account key ownership** | No | Yes |
| **Cost** | Free | CMK + KMS requests (mitigate with Bucket Keys) |

## What gets tested

- **The two-permission model.** Reading an SSE-KMS object needs `s3:GetObject` and `kms:Decrypt`. A user with full S3 access denied by the KMS key policy still cannot read the object. This is the most tested SSE-KMS fact and a common troubleshooting scenario (a GET fails, fix the KMS grant).
- **CMK for audit, cross-account, and control.** CloudTrail decrypt visibility, cross-account key ownership, encryption context, and revocation require a customer-managed key. The `aws/s3` key does not provide them.
- **Enforce SSE-KMS with a bucket policy.** Requiring objects to be encrypted with KMS (or a specific CMK) is a bucket policy denying PUTs without `s3:x-amz-server-side-encryption: aws:kms`, optionally pinning the key ID.
- **Org-wide enforcement with SCPs.** Blocking the default key, forcing a specific CMK, or preventing unencrypted uploads across an OU uses SCPs plus bucket/key policies, turning S3+KMS into a centralized encryption authority.
- **Egress and detection.** Tying `GetObject` to a `kms:Decrypt` event and alerting on anomalous decrypts (foreign region, unexpected principal) is a SSE-KMS capability SSE-S3 cannot provide.
- **S3 Bucket Keys for cost.** High-volume SSE-KMS driving KMS costs is solved by enabling S3 Bucket Keys.

## Limitations

- The two-permission model means a missing `kms:Decrypt` grant silently blocks reads even when S3 access is correct, a frequent source of confusing AccessDenied errors.
- The default `aws/s3` key gives none of the audit, cross-account, or scoping benefits, so realizing SSE-KMS's value requires a CMK and the management it entails.
- SSE-KMS at high request volume incurs KMS costs and can hit throttling unless S3 Bucket Keys are enabled.
- Encryption protects confidentiality, not authorization on its own. The KMS key policy and IAM still govern access, so misconfiguration there exposes data despite encryption.
- Cross-account access requires a CMK and grants or key-policy statements, since the AWS-managed key cannot be shared, adding key-management overhead.
- Revocation via key-policy change stops future decrypts but does not retroactively protect data already read, so it is a forward-looking control, not a recall.