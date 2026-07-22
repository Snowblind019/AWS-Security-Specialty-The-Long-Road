# Client-Side Encryption With KMS (Client-Side CMK)

Client-side KMS encryption means your application encrypts the data locally, before it ever reaches S3, using KMS purely as a key provider rather than an encryption engine. KMS mints data keys, your code does the actual AES encryption, and AWS only ever stores ciphertext plus a wrapped data key. This is the deliberate opposite of SSE-KMS: there, AWS encrypts server-side and briefly handles your plaintext; here, AWS never sees the plaintext at all, and you own the DEK handling, rotation, and re-encryption. The thing to hold onto: the CMK still lives in AWS KMS (so you keep CloudTrail logging and IAM condition control), which is exactly what separates this from the custom-HSM model, and it means client-side KMS satisfies "AWS never sees my data" but not "AWS never holds my key."

## How it works (envelope encryption)

- **Call `GenerateDataKey`.** You ask KMS for a fresh data encryption key and get back two things: the plaintext DEK for immediate use and the encrypted DEK wrapped under your CMK. Using a per-object DEK avoids sending bulk data through KMS.
- **Encrypt locally, then destroy the plaintext DEK.** Your app encrypts the data with the plaintext DEK (AES-256-GCM or similar) and securely zeroes that DEK from memory the moment it is done. Treat the plaintext DEK like a lit match: use it fast, then extinguish it.
- **Store ciphertext plus the wrapped DEK.** Upload the encrypted blob to S3 and keep the encrypted DEK alongside it (object metadata or a companion record). S3 sees only opaque binary.
- **Decrypt by unwrapping the DEK first.** To read the data later, retrieve the blob and the encrypted DEK, call KMS `Decrypt` on the wrapped DEK to get the plaintext DEK back, then decrypt the data locally.
- **Encryption context scopes and audits key use.** Passing an encryption context (for example a purpose or tenant) binds the DEK to that context and lets you enforce and audit it in IAM conditions and CloudTrail, so a DEK issued for one workload cannot be silently reused for another.
- **The AWS Encryption SDK standardizes the plumbing.** It handles envelope format, encryption context, keyrings, and DEK caching, so you are not hand-rolling serialization. It also lets you cache DEKs to cut KMS call volume on high-throughput workloads.

## Client-side KMS vs the alternatives

| Feature | SSE-KMS | Client-side KMS CMK | Client-side custom HSM |
|---|---|---|---|
| **Encryption location** | AWS server-side | Your app | Your app |
| **AWS sees plaintext** | Briefly | Never | Never |
| **Who holds the key** | AWS KMS | AWS KMS | You only |
| **CloudTrail on key use** | Yes | Yes (`GenerateDataKey`, `Decrypt`) | No (unless your HSM logs it) |
| **IAM condition control** | Yes | Yes | No |
| **S3 bucket policy enforceable** | Yes | No | No |
| **Custom code required** | No | Yes | Yes |

## What gets tested

- **"AWS never sees the plaintext" vs "AWS never holds the key."** Client-side KMS CMK satisfies the first: data is encrypted before upload. It does not satisfy the second, because the CMK is in AWS KMS. A requirement that AWS cannot hold or access the key forces the custom/external HSM model, not this one. This distinction is a classic distractor.
- **Client-side KMS vs SSE-KMS.** If the data must be encrypted before it leaves your premises, that is client-side. If server-side AWS encryption is acceptable and you want it simple and policy-enforceable, that is SSE-KMS.
- **You keep CloudTrail and IAM conditions.** Choosing client-side KMS over a custom HSM is often about retaining auditability and encryption-context enforcement while still doing the crypto yourself.
- **S3 bucket policies cannot require client-side encryption.** Because the encryption happens in your app, there is no server-side header for a bucket policy to check, unlike SSE-KMS which you can mandate via policy.
- **DEK hygiene and cost.** Per-object DEKs are cleaner but multiply `GenerateDataKey` and `Decrypt` calls. DEK caching via the Encryption SDK trades a little key isolation for large cost and latency savings on high volume.

## Limitations

- The CMK lives in AWS KMS, so this model does not meet sovereignty mandates that require AWS to have no access to key material. That is the custom-HSM or external-key-store territory.
- You own the code, the DEK memory hygiene, and the rotation/re-encryption tooling. It is not plug-and-play like SSE-KMS.
- No S3 bucket-policy enforcement of the encryption, since there is no server-side encryption header to validate.
- High-volume workloads generate large numbers of KMS calls unless you cache DEKs, which has real cost implications.
- A plaintext DEK mishandled (logged, cached to disk, not zeroed) undermines the whole scheme, so runtime security engineering is as important as the KMS setup.
- S3 GETs do not hit KMS unless you are unwrapping a DEK, so your audit picture of "who read the data" depends on your app logging the decrypt path, not on KMS alone.