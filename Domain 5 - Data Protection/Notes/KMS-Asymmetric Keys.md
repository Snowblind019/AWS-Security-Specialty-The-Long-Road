# AWS KMS: Asymmetric Keys  

## What Are Asymmetric KMS Keys

**Asymmetric KMS keys** are public/private key pairs managed by AWS KMS that you can use for:

- **Encryption/Decryption**
- **Digital Signing/Verification**

Unlike **symmetric keys** (where a single secret key is used for both encryption and decryption), asymmetric keys use:

- A **public key** to **encrypt** or **verify** data  
- A **private key** to **decrypt** or **sign** data  

And most importantly:

- The **private key stays in AWS KMS** and is **never exported**  
- The **public key** can be downloaded, shared, embedded in apps, or distributed to clients  

This unlocks workflows where:

- Clients **encrypt data before uploading to AWS**  
- You **verify signed data** from remote services  
- You **rotate keys centrally** without rebuilding client logic  

---

## Cybersecurity Analogy

Think of symmetric keys like a **master keycard** — whoever holds it can open and close the vault.

Asymmetric keys are like:

- A **public dropbox** (anyone can drop in a message)  
- That **only Snowy can unlock** with the private key stored in KMS  

- Snowy **signs** a document using her **private key**  
- Anyone with the **public key** can **verify it’s authentic** — but no one else can fake it  

> It’s **trust with directional boundaries**, enforced cryptographically.

## Real-World Analogy

Picture this:

You run a **health records app**.  
Mobile clients (phones, tablets) need to **encrypt sensitive patient data** before it ever reaches S3.

You **don’t want to hand out KMS permissions** to every phone.  
So instead:

- You generate an **asymmetric KMS key**
- Clients **download the public key** and **encrypt on-device**

- The **server (in AWS)** decrypts using the **private key stored in KMS**

No private keys stored on EC2
AWS handles key rotation, logging, and security

---

## Key Usage Types

When you create an asymmetric KMS key, you pick its **key spec** and **usage type**:

| **Usage Type**     | **Description**                                        |
|--------------------|--------------------------------------------------------|
| `ENCRYPT_DECRYPT`  | For public encryption and private decryption           |
| `SIGN_VERIFY`      | For private signing and public signature verification  |

---

## Key Operations (Per Type)

### For `ENCRYPT_DECRYPT`:

| **Operation**   | **Description**                           |
|------------------|--------------------------------------------|
| `GetPublicKey`   | Download the public key                   |
| `Encrypt`        | Encrypt plaintext with the public key     |
| `Decrypt`        | Decrypt ciphertext with the private key   |

---

### For `SIGN_VERIFY`:

| **Operation**   | **Description**                            |
|------------------|---------------------------------------------|
| `Sign`           | Sign data using the private key            |
| `Verify`         | Verify signature using the public key      |
| `GetPublicKey`   | Download the public key                    |

> **Note:** Encryption limits apply (e.g., RSA has strict plaintext size caps).  
> For large payloads, use **envelope encryption** with `GenerateDataKeyPair`.

---

## How Access Works

Permissions are **IAM-scoped** the same way as symmetric keys — but **only KMS performs private key operations**.

- Clients can **download the public key** without needing decryption access  
- To **sign or decrypt**, the caller must have `kms:Sign` or `kms:Decrypt`  
- All usage is **logged via CloudTrail**  

- Grants, conditions, and encryption context can wrap around access  

---

## Security Benefits

| **Feature**                    | **Benefit**                                                     |
|--------------------------------|------------------------------------------------------------------|
| Private key never leaves AWS   | No key export = safer key management                            |
| Client-side encryption         | Encrypt without calling AWS at all                              |
| Public verification            | Audit signatures without needing decryption access              |
| Grant-based delegation         | Short-lived usage for Lambda, external partners                 |
| Built-in rotation              | Supports rotation policies like symmetric keys                  |

---

## Key Differences: Symmetric vs Asymmetric

| **Feature**              | **Symmetric**                        | **Asymmetric**                                           |
|--------------------------|--------------------------------------|----------------------------------------------------------|
| **Key Type**             | AES-256                              | RSA or ECC (public/private pair)                         |
| **Exportable**           | ✖️ No                                | ✔️ Public key only                                       |
| **Use Case**             | AWS service encryption, DEK wrapping | Client-side encryption, digital signatures               |
| **Performance**          | Very fast                            | Slower (especially RSA)                                  |
| **Supported Operations** | Encrypt, Decrypt, GenerateDataKey    | Encrypt, Decrypt, Sign, Verify                           |
| **Envelope Encryption?** | ✔️ Yes                               | ✔️ Yes (via `GenerateDataKeyPair`)                        |
| **Typical Use**          | EBS, S3, RDS encryption              | PKI, API message signing, external apps                  |

---

## Common Use Cases

| **Use Case**                          | **Asymmetric Key?** |
|---------------------------------------|----------------------|
| Encrypting data outside AWS           | ✔️ Yes               |
| Verifying a document signature        | ✔️ Yes               |
| Issuing digital certificates          | ✔️ Yes               |
| Encrypting Lambda logs in S3          | ✖️ Use symmetric     |
| Internal service-to-service TLS       | ✖️ Use ACM/ECS       |
| Signing software packages             | ✔️ Yes               |
| Verifying license keys                | ✔️ Yes               |
| High-throughput envelope encryption   | ✖️ Too slow          |

---

## Security Risks and Misuse

- Public key leakage isn’t dangerous — but granting `kms:Decrypt` too broadly **is**  
- Always **scope roles** with tag-based access or encryption context  
- **Monitor `GetPublicKey` and `Sign` requests** for unusual patterns  
- Use **CloudTrail + KMS key usage metrics** to spot spikes in `Decrypt` or `Sign`

---

## Real-Life Snowy Scenario

Your team maintains a **REST API** that signs responses for **external customers** to verify.

You:

1. Create a **KMS asymmetric key** with `SIGN_VERIFY`  
2. Configure **API Gateway** to call `kms:Sign` on each response payload  
3. Distribute the **public key** to customers for local `Verify`  

- You rotate the key annually using built-in KMS rotation  
- No one touches the private key  
- Customers have full verification trust — **without internal access**  
- Every use of `kms:Sign` is **logged and auditable**

---

## Final Thoughts

**Asymmetric KMS keys** are perfect for situations where **public trust meets private enforcement**.

They’re **not** the default choice for bulk encryption — but they’re ideal for:

- **Cryptographic identity**  
- **External data protection**  
- **Digital integrity verification**  

Used correctly, they:

- Eliminate **homegrown crypto**  
- Centralize **key auditability**  
- Provide **secure, non-interactive encryption** across trust domains

