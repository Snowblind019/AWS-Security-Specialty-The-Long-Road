# Enforcing HTTPS on Amazon S3

S3 endpoints accept both HTTP and HTTPS, and S3 will not refuse a plaintext request unless you tell it to. SDKs and the CLI default to HTTPS, but that default is client-side and overridable, so "we use the SDK" is not enforcement. The one authoritative control is a bucket policy that denies any request where `aws:SecureTransport` is false, which applies uniformly to the console, CLI, SDKs, signed URLs, scripts, and anonymous callers. The thing to hold onto: enforcing HTTPS on S3 is a bucket-policy deny on `aws:SecureTransport=false`, security groups and network controls do not apply to S3, and this control secures the wire only, so it pairs with Block Public Access (exposure), SSE (at rest), and IAM (authorization) rather than replacing any of them.

## How it works

- **The `aws:SecureTransport` deny is the golden control.** A bucket policy statement with `Effect: Deny`, `Action: s3:*`, `Principal: *`, and `Condition: Bool aws:SecureTransport=false` rejects every non-TLS request to the bucket and its objects with a 403. Because it is server-side, it cannot be bypassed by a client that chooses HTTP.
- **Violations are denied and logged.** An `http://` request returns 403 Access Denied, and with CloudTrail data events or S3 access logging enabled, the attempt is recorded, giving you a signal that something is trying to reach the bucket insecurely.
- **CloudFront in front adds edge enforcement.** Fronting the bucket with CloudFront lets you set a viewer protocol policy of redirect-to-HTTPS or HTTPS-only, terminate TLS at the edge with an ACM cert, lock the origin with Origin Access Control, and optionally attach WAF. This is the pattern for websites and public asset distribution.
- **Pre-signed URLs must be generated as HTTPS.** Pre-signed URLs grant temporary access and should always be `https://` with short expirations. They do not replace the `aws:SecureTransport` policy, which still blocks any other insecure path.
- **Block Public Access complements it.** BPA prevents anonymous exposure and is a different axis from transit encryption, but together they close both "readable by anyone" and "readable over plaintext." Enabling all four BPA settings is the standard companion control.

## The S3 HTTPS enforcement stack

| Control | What it does | What it does not do |
|---|---|---|
| **`aws:SecureTransport` deny** | Rejects all non-TLS requests at the bucket | Not at rest, not authorization, not exposure |
| **CloudFront HTTPS viewer policy** | Enforces TLS at the edge, adds CDN/WAF | Origin still needs OAC + the bucket policy |
| **Pre-signed HTTPS URLs** | Temporary encrypted access | Needs the deny policy to block other access |
| **Block Public Access** | Stops anonymous exposure | Nothing about encryption in transit |
| **SSE (S3/KMS)** | Encrypts objects at rest | Nothing about the wire |

## What gets tested

- **The answer is `aws:SecureTransport`.** For "require encryption in transit to a bucket," the correct control is a bucket policy denying `aws:SecureTransport=false`, not a security group (which does not apply to S3), not a NACL, and not trusting the SDK default.
- **Client defaults are not enforcement.** SDKs and the CLI default to HTTPS, but that is overridable client-side. Only the bucket policy guarantees it server-side.
- **Transit vs at rest vs exposure are separate.** `aws:SecureTransport` covers the wire, SSE-S3/SSE-KMS covers at rest, and Block Public Access covers anonymous exposure. A question asking for one should not be answered with another.
- **CloudFront plus OAC for public web content.** Serving S3 content over HTTPS to the world with the origin locked down is CloudFront with an HTTPS viewer policy and OAC, and the bucket policy still enforces TLS on the origin hop.
- **Pre-signed URLs are HTTPS and short-lived.** Insecure pre-signed URLs leak the signature and data in plaintext, so they must be HTTPS with short expiry, backed by the deny policy.

## Limitations

- The control secures transport only. It does nothing for at-rest encryption, authorization, or public exposure, so it must be layered with SSE, IAM, and Block Public Access.
- Security groups, NACLs, and other network controls do not apply to S3's public API endpoints, so transit enforcement must be policy-based, not network-based.
- Relying on client behavior (SDK HTTPS defaults) is not enforcement, since a client can be configured to use HTTP unless the bucket policy denies it.
- A missing or overly narrow policy (wrong resource ARNs, missing the `/*` object ARN) leaves gaps, so the deny must cover both the bucket and its objects.
- Enforcement generates 403s that must be monitored to be useful, otherwise attempted insecure access goes unnoticed even though it is blocked.
- CloudFront fronting adds enforcement at the edge but does not remove the need for the origin bucket policy, since a direct-to-S3 request must still be blocked.