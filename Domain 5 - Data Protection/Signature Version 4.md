# AWS Signature Version 4 (SigV4)

SigV4 is the signing process AWS uses to authenticate API requests and guarantee their integrity. Every CLI command, SDK call, and pre-signed S3 URL is a SigV4-signed request, binding the caller's IAM identity, the request contents, a timestamp, and the target region and service into a signature AWS can independently recompute and verify. It is HMAC-based (symmetric): the signature is derived from your secret access key through a chain of HMAC-SHA256 operations, and crucially the secret itself is never transmitted, only the derived signature. This is not public-key cryptography, there is no public key involved, AWS holds the same secret and recomputes the signature to compare. The thing to hold onto: SigV4 gives authentication, integrity, and replay protection from a shared-secret HMAC (not a digital signature), the signature is scoped to a specific date, region, and service so it cannot be reused elsewhere, and a `SignatureDoesNotMatch` is a signing problem while `AccessDenied` is an IAM authorization problem, which are different failure classes.

## How it works

- **Canonical request.** The client normalizes the HTTP request (method, URI, sorted query string, canonical and signed headers, hashed payload) into a deterministic form. Ordering, casing, trimming, and header selection all matter, because any difference changes the hash.
- **String to sign.** The client builds a string containing `AWS4-HMAC-SHA256`, the timestamp, the credential scope (`YYYYMMDD/region/service/aws4_request`), and the SHA-256 of the canonical request. The credential scope is what binds the signature to a date, region, and service.
- **Derive the signing key (the HMAC chain).** Starting from `AWS4` + secret access key, HMAC-SHA256 is applied in sequence over the date, then region, then service, then `aws4_request`, producing a signing key locked to all four. The signature is HMAC of the string-to-sign under that key. The secret never leaves the client.
- **Attach the signature.** It goes in the `Authorization` header for normal requests, or in the query string for pre-signed URLs (`X-Amz-Signature`, `X-Amz-Credential`, `X-Amz-Date`, `X-Amz-Expires`).
- **AWS verifies by recomputation.** AWS rebuilds the canonical request and string-to-sign, derives the same signing key from its copy of your secret, recomputes the signature, and compares. A mismatch is rejected. This is symmetric verification, not public-key.

## What SigV4 provides

| Property | How SigV4 delivers it |
|---|---|
| **Authentication** | Signature ties the request to the IAM identity's secret key |
| **Integrity** | Hashed canonical request breaks the signature on any change |
| **Replay protection** | Timestamp plus short expiry limits reuse |
| **Scoping** | Credential scope binds signature to date/region/service |
| **Secret never sent** | Only the derived signature travels, not the key |

## What gets tested

- **SigV4 is HMAC, not a public-key signature.** It provides authentication and integrity from a shared secret, so it does not give non-repudiation the way an asymmetric digital signature would. Treating SigV4 as public-key crypto is a mistake the exam probes.
- **`SignatureDoesNotMatch` vs `AccessDenied`.** A signature mismatch means the canonical request, headers, hash, region, service, or clock is wrong (a signing problem). `AccessDenied` means the signature verified but IAM does not permit the action (an authorization problem). Diagnosing which is which is tested.
- **Scope binding.** The signature is locked to a specific date, region, and service, so it cannot be replayed against a different region or service. This is why credential scope exists.
- **Replay protection via timestamp and expiry.** `RequestExpired` comes from clock skew or an expired pre-signed URL, so time synchronization matters, and short TTLs limit the replay window.
- **Pre-signed URLs put the signature in the query string.** For pre-signed URLs, SigV4 parameters travel as query params rather than an Authorization header, and the URL inherits the signer's permissions and credential lifetime.
- **The secret is never transmitted.** SigV4 proves possession of the secret without sending it, which is why intercepting a request does not reveal the key.

## Limitations

- SigV4 is symmetric HMAC, so it does not provide non-repudiation, since AWS holds the same secret and could in principle produce the same signature. It authenticates and integrity-checks, it is not a legal digital signature.
- It is exact and unforgiving: a single difference in header casing, ordering, trimming, or payload hashing breaks the signature, which makes manual signing error-prone (the SDK/CLI handle it for a reason).
- It depends on clock accuracy. Excessive clock skew produces `RequestExpired` or signature failures, so time sync is required.
- The signature proves who signed and that the request is intact, but not that the action is permitted. IAM authorization is a separate layer, so a valid signature can still be denied.
- Signature security rests on the secret key's confidentiality. A leaked secret access key lets an attacker sign valid requests, so key protection and rotation remain essential.
- Scoping limits a signature to one date, region, and service, but within that scope and validity window a captured pre-signed URL is usable, so short expiries and HTTPS delivery still matter.