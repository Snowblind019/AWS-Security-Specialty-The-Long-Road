# Digital Signatures

## What Is a Signature

A digital signature is a cryptographic proof of authenticity and integrity. It lets you confirm:

- Who sent a message (authentication)  
- That it hasn’t been altered in transit (integrity)  
- That the sender can’t deny having sent it (non-repudiation)  

It's like the digital equivalent of signing a contract — except way more tamper-proof and verifiable by anyone with the right public key.

Signatures are essential for secure systems, especially in the cloud:

- Signing IAM requests (AWS Signature Version 4)  
- Signing Lambda deployment packages  
- Signing software binaries  
- Signing SSL/TLS certificates  
- Verifying JWT tokens in Cognito or STS  
- Code signing for Lambda, ECS, IoT, etc.  

**Digital signatures are built on top of asymmetric cryptography: one key to sign, one to verify.**

---

## Cybersecurity and Real-World Analogy

### Cybersecurity Analogy

Imagine you’re Snowy sending Blizzard an important letter.  
Instead of just trusting the envelope, you:

- Write the letter  
- Seal it with wax  
- Press your unique ring into the wax  

When Blizzard gets the letter, he sees the seal. If it’s broken or fake, he knows something’s wrong.  
**That seal? That’s your signature — unforgeable, verifiable, and unique to you.**

### Real-World Analogy

Think of signing a contract with a pen:

- You use your private signature  
- Anyone can compare it with the one they know is yours  
- You can't later say, “That wasn’t me” if the signature matches  

**In crypto, the private key signs, and the public key verifies.**

---

## How It Works (Under the Hood)

Here’s the step-by-step simplified:

1. You take your original message (e.g., file, API request, JSON)  
2. You hash it (e.g., SHA-256)  
3. You encrypt the hash with your private key → this becomes the signature  
4. You send the message + signature  

On the other side:

1. The recipient hashes the message again (same algorithm)  
2. Then uses your public key to decrypt your signature  
3. If the decrypted hash matches their hash — ✅ the message is valid and untampered  
4. If anything changed — even a comma — the hashes won't match.

**Hashing + Asymmetric Encryption = Signature**

| **Component** | **Role**                              |
|---------------|----------------------------------------|
| Hashing       | Reduces input to fixed-size fingerprint |
| Private Key   | Encrypts the hash (signs it)            |
| Public Key    | Decrypts the hash (verifies it)         |

---

## Key Properties of Signatures

| **Property**         | **Explanation**                                      |
|----------------------|------------------------------------------------------|
| Authentication       | You know who signed it (because only they had the private key) |
| Integrity            | You know it wasn’t altered (hash mismatch = tampered data)     |
| Non-Repudiation      | The signer can’t deny having signed it                        |
| Public Verifiability | Anyone with the public key can verify it — no secrets needed  |

---

## Common Signature Algorithms

| **Algorithm** | **Type**     | **Used In**                                   |
|---------------|--------------|-----------------------------------------------|
| RSA           | Asymmetric   | SSL certs, S/MIME, JWTs, OpenSSH              |
| ECDSA         | Asymmetric   | Modern TLS certs, Bitcoin, AWS SigV4          |
| HMAC-SHA256   | Symmetric (MAC) | AWS API signing, S3 presigned URLs         |

> Note: HMACs aren’t true digital signatures (they use shared secrets), but they provide similar guarantees and are faster — used a lot in cloud APIs.

---

## Where You’ll See It in AWS

### IAM API Requests (Signature Version 4)

- You sign each AWS API request with your secret access key  
- AWS uses HMAC-SHA256 with timestamp and payload hash  
- Prevents tampering, spoofing, or replay attacks  

### Lambda Code Signing

- AWS lets you enforce that only signed deployment packages can run  
- Uses a signed hash digest and trusted signing profile (AWS Signer)  

### JWT Token Verification (Cognito, STS)

- Tokens are signed using RS256 (asymmetric)  
- Clients verify token signatures using well-known public keys (JWKS)  

### ACM Certificate Signatures

- ACM issues certs signed by Amazon's CA (RSA/ECDSA)  
- The signature on the certificate proves it’s valid and trusted  

### CodeArtifact and ECR

- Signed artifacts and container images to prove trust and integrity  

---

## Signature vs HMAC vs Encryption — Quick Comparison

| **Purpose**         | **Signature**                         | **HMAC**                         | **Encryption**                    |
|---------------------|----------------------------------------|----------------------------------|-----------------------------------|
| **Key Type**        | Asymmetric (priv/pub)                  | Symmetric (shared secret)        | Symmetric or Asymmetric           |
| **Used For**        | Integrity + Auth + Non-repudiation     | Integrity + Auth                 | Confidentiality                   |
| **Reversible?**     | Only for verification                  | No                               | Yes (decryptable)                 |
| **Public Verify?**  | ✔️ Yes                                 | ✖️ No                            | ✖️ Not verifiable publicly        |

---

## Real-Life Example

Winterday is deploying a Lambda function that controls sensitive admin APIs. Snowy enforces code signing using AWS Signer. Here’s what happens:

- Winterday signs the ZIP package with their private key  
- AWS verifies the signature with the public key in a Signing Profile  
- Lambda will refuse to run any function that isn't signed and trusted  

Later, Snowy’s API Gateway receives a request from an external service. It uses **SigV4**:

- Snowy inspects the `Authorization` header  
- It contains a signature hash (HMAC)  
- Snowy re-hashes the payload and checks the timestamp  

If everything matches — the request is valid  
No secrets are exposed. No trust assumptions made. Just signatures doing their job.

---

## Final Thoughts

Signatures are your **cryptographic truth detector**.  
They're the way we say, “I sent this” and “nothing changed it” — and have the math to prove it.

In a zero-trust cloud world, where messages fly across APIs, services, regions, and identities, **signatures are the glue that holds trust together**.  
Whether it's a Lambda function, a signed API call, or a JWT token — **no signature means no trust.**
