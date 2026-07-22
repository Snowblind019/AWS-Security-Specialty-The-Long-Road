# Digital Signatures

A digital signature is cryptographic proof of who produced a message and that it has not changed, giving you authentication, integrity, and non-repudiation in one primitive. It is built on asymmetric keys: the holder of the private key signs, and anyone with the matching public key can verify, no shared secret required. In AWS this shows up everywhere trust has to be established without a password on the wire: SigV4 request signing, Lambda code signing via AWS Signer, JWT verification in Cognito and STS, certificate signatures from ACM, and KMS asymmetric sign/verify. The thing to hold onto: a true digital signature uses asymmetric keys and gives non-repudiation and public verifiability, while an HMAC (which SigV4 actually uses) gives integrity and authentication from a shared secret but not non-repudiation, and that difference is exactly what exam questions pit against each other.

## How it works

- **Hash, then sign the hash.** The signer hashes the message (SHA-256), then produces a signature over that digest with the private key. Sending message plus signature lets a verifier recompute the hash and check it against the signature using the public key. Any change, even one byte, breaks the match.
- **Sign and verify, not encrypt and decrypt.** The RSA intuition of "encrypt the hash with the private key" works for RSA specifically, but the correct general framing is sign/verify. ECDSA, for example, is a signature scheme, not encryption, so treating signing as "private-key encryption" is a simplification that does not generalize.
- **The properties come from key asymmetry.** Only the private-key holder could have produced the signature (authentication and non-repudiation), the hash binding proves the content is intact (integrity), and because verification needs only the public key, anyone can check it without a secret (public verifiability).
- **AWS SigV4 is HMAC, not asymmetric.** Each AWS API request is signed with a key derived from your secret access key using HMAC-SHA256 over a canonical request plus timestamp and payload hash. This stops tampering, spoofing, and replay, but because it is a shared-secret MAC it does not provide non-repudiation.
- **AWS surfaces that use real signatures.** Lambda code signing (AWS Signer verifies a signing profile's public key and Lambda refuses unsigned or untrusted packages), JWTs from Cognito/STS (RS256, verified against a published JWKS), ACM certs (signed by Amazon's CA), and signed artifacts in ECR and CodeArtifact. KMS asymmetric keys can sign and verify directly, with the private key never leaving KMS.

## Signature vs HMAC vs encryption

| Property | Digital signature | HMAC | Encryption |
|---|---|---|---|
| **Key type** | Asymmetric (private signs, public verifies) | Symmetric shared secret | Symmetric or asymmetric |
| **Gives you** | Integrity, authentication, non-repudiation | Integrity, authentication | Confidentiality |
| **Publicly verifiable** | Yes, anyone with the public key | No, verifier needs the secret | No |
| **Non-repudiation** | Yes | No (either party could have signed) | No |
| **AWS example** | Lambda code signing, JWT RS256, KMS sign | SigV4 request signing, S3 presigned URLs | KMS encrypt, SSE |

## What gets tested

- **Signature vs HMAC on non-repudiation.** If the requirement is proving a specific party signed something in a way they cannot later deny, that needs an asymmetric digital signature. An HMAC cannot give non-repudiation because both sides share the secret. SigV4 is HMAC.
- **What SigV4 actually is.** SigV4 uses HMAC-SHA256 derived from the secret access key, provides integrity and replay protection via timestamp, and is not an asymmetric signature. Questions like to test whether you know it is a MAC.
- **Enforcing trusted code.** "Only signed, trusted deployment packages may run" is Lambda code signing with AWS Signer and a signing profile, not IAM policy alone.
- **JWT verification.** Cognito/STS tokens are asymmetric (RS256) and verified against a public JWKS endpoint, so clients need no secret to validate them.
- **KMS asymmetric sign/verify.** When the requirement is signing where the private key must never leave a managed boundary, KMS asymmetric keys sign and verify without exposing the private key.
- **Signature proves integrity and origin, not confidentiality.** A signed message is not a secret message. If the data must also be hidden, you need encryption in addition to the signature.

## Limitations

- A signature protects integrity and origin, not confidentiality. Signed data is still readable unless separately encrypted.
- HMAC-based schemes like SigV4 give no non-repudiation, since the shared secret means either holder could have produced the tag.
- Signatures are only as trustworthy as the key distribution behind them. If a verifier trusts the wrong public key or a compromised signing profile, the math still checks out on malicious content.
- Private-key compromise is catastrophic: an attacker can forge signatures that verify cleanly, which is why KMS and Signer keep private keys inside a managed boundary.
- The "private-key encryption" mental model does not generalize past RSA, so reasoning about ECDSA or EdDSA as encryption leads to wrong conclusions.
- Verification cost and key rotation still need managing. Rotating a signing key means re-establishing trust in the new public key (new JWKS entry, new signing profile version), which is operational work, not automatic.