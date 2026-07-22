# Amazon S3 Pre-Signed URLs

A pre-signed URL is a time-limited, SigV4-signed link that grants a specific operation (`GET`, `PUT`, sometimes `DELETE`/`HEAD`) on one specific object, letting someone with no AWS credentials use it for a bounded window. It is one of the cleanest least-privilege delegation tools in AWS: instead of making a bucket public or handing out IAM credentials, you issue a signed ticket for one file, one action, that expires. The critical subtlety for the exam is that a pre-signed URL carries the permissions of whoever signed it and is only valid as long as that signer's credentials are, so a URL signed by a role's temporary credentials dies when the session expires, regardless of the requested expiry. The thing to hold onto: the URL inherits the signer's permissions and lifetime (temporary role credentials cap it well below the 7-day max), the receiver needs no IAM, and access is scoped to one object and one method, so security comes from short TTLs, HTTPS delivery, and least-privilege signing.

## How it works

- **The signer's backend generates it with IAM permissions.** A process with `s3:GetObject` or `s3:PutObject` uses the SDK to sign a URL over the bucket, object key, HTTP verb, and expiry using SigV4 (HMAC-SHA256) with the signer's credentials.
- **The URL carries the signature in query parameters.** `X-Amz-Algorithm`, `X-Amz-Credential`, `X-Amz-Signature`, `X-Amz-Expires`, and related params make it self-contained. Anyone holding the URL can perform exactly the signed operation.
- **The receiver uses it with no AWS credentials.** A valid signature within the time window returns the object (or accepts the upload). An invalid signature or an expired window returns 403.
- **It inherits the signer's permissions and credential lifetime.** The URL can never do more than the signer could, and it stops working when the signer's credentials expire. Signed with an IAM user's long-term key, the max expiry is 7 days. Signed with temporary STS/role credentials, it is capped by the remaining session duration, often far shorter than 7 days, even if you request longer.
- **Access is logged as the signer.** S3 data-event logging in CloudTrail records the operation under the signing identity, and generation of pre-signed URLs (the signing API activity) can be monitored, so usage is auditable.

## Pre-signed URL facts

| Aspect | Value / behavior |
|---|---|
| **Max expiry (IAM user key)** | 7 days (604800 s) |
| **Max expiry (temporary/role creds)** | Capped by session duration, often much less |
| **Signing** | SigV4, HMAC-SHA256 |
| **Methods** | `GET`, `PUT`, `DELETE`, `HEAD` (per SDK) |
| **Signer needs IAM** | Yes (`s3:GetObject`/`s3:PutObject`) |
| **Receiver needs IAM** | No |
| **Scope** | One object, one method |

## What gets tested

- **The URL inherits the signer's permissions and credential lifetime.** A pre-signed URL signed by a role's temporary credentials expires when those credentials do, so a 7-day expiry request is silently capped. This is the most tested pre-signed URL subtlety. For a genuinely long-lived URL you must sign with IAM user long-term credentials.
- **No IAM for the receiver, but the signer must have the permission.** The generator needs `s3:GetObject`/`s3:PutObject`. The receiver is anonymous. If a pre-signed URL fails, the signer lacked the permission or the credentials expired.
- **Least-privilege delegation.** Pre-signed URLs are the answer for giving a customer or device one-time file access without opening the bucket or issuing credentials, over making the object public or creating IAM users.
- **Short TTL and HTTPS.** Reducing exposure from a leaked link is a short expiry (seconds to minutes) and HTTPS-only delivery, since anyone with the URL can use it during its window.
- **Auditing.** Access is logged in S3 data events under the signer's identity, so CloudTrail data events are how you trace pre-signed URL usage.
- **Pre-signed URL vs bucket policy vs CloudFront signed URL.** Pre-signed URLs are per-object temporary S3 access. CloudFront signed URLs/cookies are the CDN-layer equivalent for distributing content at the edge.

## Limitations

- Anyone who obtains the URL during its validity window can use it, so a leaked link is live access until it expires. Short TTLs and HTTPS delivery are essential, and the full URL should never be logged in plaintext.
- The URL cannot exceed the signer's permissions or outlive the signer's credentials, so temporary-credential signing quietly shortens the effective lifetime below any requested expiry.
- It grants exactly the signed operation on the signed object, so broad or multi-object access needs multiple URLs, not wildcards.
- Pre-signed URLs do not add encryption or authorization beyond the signer's grant, so they complement, not replace, bucket policies, Block Public Access, and encryption.
- Revocation is awkward: you cannot easily invalidate an issued URL before its expiry short of rotating the signer's credentials or changing the object/permissions, which is why short TTLs matter.
- Because access logs attribute the action to the signer, distinguishing which downstream recipient used a shared URL requires application-level tracking, not S3 logs alone.