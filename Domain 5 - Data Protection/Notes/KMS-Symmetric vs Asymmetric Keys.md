# KMS: Symmetric vs Asymmetric Keys  

## What Are These

KMS supports two main types of keys:

- **Symmetric Keys** – one key to encrypt and decrypt  
- **Asymmetric Keys** – public/private key pair where each side has a distinct role

At first glance, they seem interchangeable. Both are managed in KMS. Both are used for cryptographic operations. Both support IAM policies, grants, CloudTrail logging, and optional key rotation.

But how you use them, who uses them, and what trust boundaries they enforce are completely different.

Choosing the wrong key type:

- Can break your use case  
- Waste cost and performance  
- Expose surface area unintentionally  
- Or just fail silently in production

---

## Cybersecurity Analogy

Imagine you run a secure vault.

- **Symmetric key** = You and your team all share one access card. Whoever has it can both lock and unlock the vault.  
- **Asymmetric key** = You install a dropbox with a public lock anyone can use, but only you can unlock the contents from the inside.

This means asymmetric keys are about *one-way access* or *verifiable identity*, while symmetric keys are about *internal speed* and *control*.

---

## Side-by-Side Comparison


| **Feature / Trait**        | **Symmetric Key**                                      | **Asymmetric Key**                                             |
|---------------------------|--------------------------------------------------------|----------------------------------------------------------------|
| **Key Type**              | AES-256                                                | RSA / ECC Public-Private Key Pair                              |
| **Use Cases**             | Encrypt/decrypt internal AWS data                     | Digital signatures, client-side encryption                     |

| **Default in AWS Services** | Yes (EBS, S3, RDS, Lambda, etc.)                      | No                                                             |
| **Key Exportability**     | ❌ Not exportable                                      | ✅ Public key exportable                                       |
| **Private Key Visibility** | Managed by AWS, never exposed                         | Private key stays in KMS, never exportable                     |

| **Public Key Usage**      | N/A                                                    | Encrypt data outside AWS, verify signatures                    |
| **Performance**           | Fast, efficient for high-throughput ops               | Slower (especially RSA decryption/signing)                     |

| **Envelope Encryption**   | Common (via GenerateDataKey)                          | Yes, via GenerateDataKeyPair                                   |
| **Primary Operations**    | Encrypt, Decrypt, GenerateDataKey                     | Encrypt, Decrypt, Sign, Verify                                 |
| **Common Algorithms**     | AES-256-GCM                                            | RSA-2048/3072/4096, ECC NIST curves                            |
| **CloudTrail Support**    | Yes                                                    | Yes                                                            |
| **Rotation Support**      | Yes (automated or manual)                             | Yes (manual for asymmetric)                                    |
| **Use in IAM Policies**   | Yes                                                    | Yes                                                            |
| **Trust Model**           | Shared key trust — both sides use same key            | One-way trust — separate encrypt/decrypt keys                 |
| **AWS SDK Integration**   | Fully integrated                                       | Some SDKs require additional crypto libs                       |
| **Max Payload Size**      | 4 KB (post base64 encoding)                            | Depends (e.g., RSA-2048 ≈ 245 bytes max)                       |

---

## When to Use Symmetric Keys

- Encrypting AWS service resources (S3, EBS, RDS, Lambda)  
- Doing high-throughput or high-speed encrypt/decrypt  
- Managing large payloads (via envelope encryption)  
- You want a secure, simple, internal-only encryption layer  
- The client calling KMS is allowed to use IAM or STS roles

**Examples:**

- S3 Server-Side Encryption (SSE-KMS)  
- Encrypting secrets for Lambda to decrypt at runtime  
- Centralized data lake encryption  
- Audit logs encryption with condition keys (e.g., GuardDuty → S3)

---

## When to Use Asymmetric Keys

- Clients outside AWS need to encrypt before upload  
- You need digital signatures (i.e., Sign / Verify)  
- You want to distribute trust via public keys  
- You need to prove non-repudiation or integrity  
- KMS must hold the private key, but you share the public one

**Examples:**

- On-device encryption from mobile clients (offline first)  
- API response signing (e.g., API Gateway using KMS to sign payloads)  
- External identity validation (e.g., IoT, license verification)  
- Secure ingest pipelines where clients encrypt, but AWS holds keys

---

## Misconceptions and Pitfalls

| **Myth**                                                      | **Reality**                                                                 |
|---------------------------------------------------------------|------------------------------------------------------------------------------|
| “I can use asymmetric keys for S3 like symmetric ones.”       | ✖️ No. S3 only supports symmetric CMKs for server-side encryption.           |
| “Asymmetric is more secure.”                                  | ✖️ Not always — it’s about trust boundaries, not strength. AES-256 is strong. |
| “I can just encrypt all files using KMS directly.”            | ✖️ KMS is not a storage engine. Use envelope encryption with S3, RDS, etc.   |
| “Symmetric keys are for basic stuff only.”                    | ✖️ Wrong. Symmetric KMS powers most of AWS's own encryption.                 |
| “Asymmetric keys auto-rotate like symmetric.”                 | ✖️ They support rotation, but only manual, and require extra planning.       |

---

## Real-Life Snowy Scenario #1: S3 + Mobile App

Snowy builds a mobile client where users upload documents to S3.  
You don’t want client apps to have KMS IAM permissions — and the data must be encrypted *before* it even hits AWS.

**Solution:**

- Generate an asymmetric KMS keypair  
- Distribute the public key to client apps  
- Clients encrypt payloads locally  
- Your backend uses `kms:Decrypt` to decrypt the payload and forward to S3  
- Private key never leaves AWS

---

## Real-Life Snowy Scenario #2: Verifiable API Responses

Snowy’s billing API must prove every invoice response is authentic.

You:

- Create a `SIGN_VERIFY` asymmetric key in KMS  
- Grant your API Gateway role `kms:Sign`  
- Sign every response payload  
- Clients verify signatures using the downloaded public key  
- You never expose secrets or manage key storage manually

---

## Security Guidance

- Use symmetric keys for service-to-service encryption  
- Use asymmetric when trust is split between AWS and external clients  
- Always scope IAM to `kms:Decrypt` or `kms:Sign` per role  
- Monitor `GetPublicKey`, `Decrypt`, and `Sign` in CloudTrail  
- Set alarms for unexpected asymmetric key usage from unusual principals

---

## Final Thoughts

Symmetric and asymmetric KMS keys are two sides of the same encryption coin — but they serve fundamentally different trust models.

- If you’re protecting data *inside AWS*, start with **symmetric keys**.  
- If you’re exchanging data with the *outside world*, **asymmetric** is your go-to.

They’re not competitors.  

