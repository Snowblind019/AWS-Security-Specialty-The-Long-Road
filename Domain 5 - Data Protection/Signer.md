# AWS Signer

AWS Signer is a managed code-signing service that cryptographically signs software artifacts (Lambda deployment packages, container images, IoT firmware, generic binaries) so their authenticity, integrity, and provenance can be verified before deployment or execution. It answers who published the code, whether it has been altered since signing, and whether it is allowed to run. The most exam-relevant use is Lambda code signing: a signing profile plus a Code Signing Configuration on the function means Lambda rejects any package that is unsigned, tampered with, or signed by an untrusted profile, enforcing trust at deploy time. The thing to hold onto: Signer plus a Lambda Code Signing Configuration is how you enforce that only signed, trusted code runs, it is managed (KMS-backed keys, validity periods, CloudTrail audit) unlike hand-rolled GPG/OpenSSL, and an S3 ETag or a bare hash is not a substitute because it provides no authenticity or runtime enforcement.

## How it works

- **Create a signing profile.** The profile defines the signing platform (Lambda, container, generic), the signing material, and the signature validity period. It is a reusable signing template that ties signatures to a known publisher identity.
- **Sign the artifact.** Via CLI, SDK, or a CodePipeline signing stage, the artifact is hashed and signed, and the signature is attached or stored as a signed object. This typically lives post-build, pre-deploy in the pipeline.
- **Enforce at deploy/runtime.** For Lambda, a Code Signing Configuration attached to the function specifies which signing profiles are trusted and whether to warn or reject on failure. Lambda then validates the signature, the hash, the expiry, and the profile before accepting the code.
- **Reject on any failure.** Unsigned, modified (hash mismatch), expired, or wrong-profile artifacts are blocked. This is the "nothing unknown runs" guarantee.
- **Audit through CloudTrail.** Signing jobs and enforcement decisions log to CloudTrail, and IAM controls who can create profiles, sign, and configure enforcement, so the whole chain is auditable and access-controlled.

## Signer vs alternatives

| Feature | AWS Signer | Manual GPG/OpenSSL | Hash-only (S3 ETag) |
|---|---|---|---|
| **Managed** | Yes | No | No |
| **Authenticity (who signed)** | Yes | Yes, if built | No |
| **Runtime/deploy enforcement** | Yes (Lambda CSC) | No | No |
| **Validity/expiration** | Yes | No | No |
| **Audit trail** | Yes (CloudTrail) | Only if built | No |

## What gets tested

- **Enforce trusted code with Signer plus a Code Signing Configuration.** "Only signed, trusted deployment packages may run" for Lambda is a signing profile plus a CSC set to reject on failure. IAM restricting who can update the function is not the same control.
- **Signer vs a bare hash or ETag.** A hash or S3 ETag detects change but proves nothing about who produced the artifact and enforces nothing at runtime. Supply-chain trust needs Signer's signature and enforcement.
- **Warn vs enforce mode.** A Code Signing Configuration can warn or reject. For hard enforcement, the config must be set to reject unsigned or untrusted code, not just warn.
- **Signature validity and expiry.** Signatures have a validity period, so an expired signature is rejected, which matters for long-lived artifacts and re-signing cadence.
- **Supply-chain and CI/CD security.** Adding a Signer stage post-build protects against tampering between build and deploy, a common exam framing for pipeline integrity.
- **KMS-backed and auditable.** Signing keys are managed with KMS and every operation is logged, which is what distinguishes Signer from ad-hoc signing scripts.

## Limitations

- Enforcement coverage is service-specific. Lambda has native Code Signing Configuration enforcement, while other artifact types rely on the consuming system to verify, so Signer only blocks execution where the platform enforces it.
- A Code Signing Configuration set to warn rather than reject does not actually block untrusted code, so misconfiguring the mode defeats the control.
- Signatures expire, so long-lived artifacts need re-signing, and an expired signature will be rejected even if the code is legitimate.
- Signer proves authenticity and integrity, not that the code is safe. Signed malware from a trusted-but-compromised pipeline still verifies, so signing complements, not replaces, scanning and secure build practices.
- Trust rests on the signing key and profile. A compromised signing identity produces valid signatures on malicious artifacts, so key custody (KMS) and IAM scoping around who can sign are critical.
- It secures the artifact's provenance, not runtime behavior after it starts, so it pairs with least-privilege execution roles and monitoring rather than standing alone.