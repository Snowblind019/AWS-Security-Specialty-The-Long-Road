# Integrity Checks

An integrity check verifies that data has not been altered, corrupted, or tampered with, whether by accident (bitrot, transfer errors) or maliciously (injection, unauthorized change). It is orthogonal to confidentiality: you are not asking what the data says, only whether it changed. The technique is a hash (SHA-256) computed over the data and compared later, sometimes strengthened with a secret (HMAC) or a private key (digital signature) to also prove authenticity. In AWS this shows up as CloudTrail log-file validation, S3 upload checksums and ETags, SigV4 payload hashing, and Lambda code hashes. The thing to hold onto: a bare hash detects accidental change but an attacker who can alter the data can recompute the hash, so tamper-evidence against a real adversary needs an HMAC (shared secret) or a digital signature (asymmetric), and the exam-critical AWS example is CloudTrail log-file validation using signed digests.

## How it works

- **Hash, store, recompute, compare.** Compute a hash of the file, packet, or response, store or send it alongside, then recompute later and compare. A match means intact, a mismatch means something changed. This alone catches corruption and accidental change.
- **HMAC adds a secret for tamper resistance.** A plain hash can be recomputed by anyone who alters the data. HMAC mixes in a shared secret, so only a party with the secret can produce a valid tag, which is what SigV4 and S3 pre-signed URLs use to bind a request to its signer.
- **Digital signatures add asymmetric authenticity.** Signing the hash with a private key lets anyone with the public key verify both integrity and origin, plus non-repudiation. This is what code signing, JWTs, and cert chains rely on.
- **S3 upload integrity.** A `Content-MD5` header (or the newer SHA-based checksum options like `x-amz-checksum-sha256`) makes S3 verify what it received against the hash and reject the upload on mismatch, catching corrupted or altered uploads in transit.
- **S3 ETag for consistency, not security.** The ETag is an object identifier (MD5 for single-part, a composite for multipart) useful for detecting whether content changed and for sync logic, but it is not a security control and should not be treated as tamper-proof.
- **CloudTrail log-file validation.** CloudTrail writes signed `.digest` files containing hashes of the log files, so you can verify with AWS's public key that logs were not altered or deleted. This is the forensic integrity control auditors expect.

## Hash vs HMAC vs signature

| Property | Checksum (CRC) | Hash (SHA-256) | HMAC | Digital signature |
|---|---|---|---|---|
| **Catches accidental change** | Yes | Yes | Yes | Yes |
| **Resists a deliberate attacker** | No | No (attacker recomputes) | Yes (needs secret) | Yes (needs private key) |
| **Proves origin / authenticity** | No | No | Shared-secret only | Yes, publicly verifiable |
| **Non-repudiation** | No | No | No | Yes |
| **AWS example** | Legacy error checks | File comparison, finding hashes | SigV4, pre-signed URLs | Code signing, JWT, CloudTrail digest signing |

## What gets tested

- **A bare hash is not tamper-proof against an attacker.** If an adversary can modify the data, they can recompute a plain hash. Real tamper-evidence needs an HMAC (shared secret) or a signature (asymmetric key). This distinction is the core of most integrity questions.
- **CloudTrail log-file validation for audit integrity.** Proving logs were not altered is CloudTrail's signed digest files verified with AWS's public key, a distinct control from encrypting the logs.
- **S3 upload integrity is Content-MD5 or a checksum algorithm.** Ensuring an object arrived uncorrupted uses the checksum on PUT, and S3 rejects mismatches.
- **ETag is not a security control.** Using ETag to prove tamper-resistance is wrong. It signals content change for sync, not adversarial integrity.
- **SigV4 protects request integrity in transit.** The signed payload hash prevents modification and replay of API requests, an HMAC-based integrity guarantee.
- **Integrity vs confidentiality.** Integrity controls detect change, they do not hide data. A question about keeping data secret is encryption, not hashing.

## Limitations

- A plain hash only detects change, it does not prevent it, and it provides no defense against an attacker who can also rewrite the stored hash.
- Checksums like CRC and hashes like MD5 are weak against deliberate tampering (collisions, easy recomputation), so they are for error detection, not adversarial integrity.
- HMAC gives tamper resistance but not non-repudiation, since both parties share the secret and either could have produced the tag.
- ETag semantics vary between single-part and multipart uploads, so it is unreliable as an integrity proof and is not a security feature.
- Integrity checks say nothing about confidentiality. Data can be intact and still fully exposed, so hashing must pair with encryption where secrecy matters.
- Verification is only as trustworthy as the key distribution behind it. A signature or digest check that trusts the wrong public key validates malicious data cleanly.