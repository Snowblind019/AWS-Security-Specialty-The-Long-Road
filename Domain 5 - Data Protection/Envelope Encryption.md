# Envelope Encryption

## What Is Envelope Encryption

Envelope Encryption is a **cryptographic design pattern** used by AWS and many modern security systems to securely encrypt large amounts of data **without directly using your main (master) key** on the data itself.

Instead of encrypting sensitive files with your **CMK** (Customer Master Key), the process goes like this:

1. Generate a one-time, random **Data Encryption Key (DEK)**  
2. Use that DEK to encrypt the data  
3. Encrypt the DEK itself using a **Key Encryption Key (KEK)** — usually your CMK in KMS  
4. Store the ciphertext of the data + the encrypted DEK together  

This results in a **layered, scalable encryption strategy** where your main key never touches the plaintext data.

---

## Cybersecurity Analogy

Imagine Snowy is a castle queen with a sacred treasure (data) that needs to be locked up.  
Instead of using the **master key** to lock every chest (file), she:

- Creates a random key (**DEK**) for each chest  
- Locks the chest with that DEK  
- Then locks that DEK inside a vault (**KMS**) with her **master key**

Now:

- She can rotate the master key without re-locking every chest  
- If someone finds a chest, they still need the DEK *and* the master key  
- The system scales beautifully across thousands of chests (files)

> This is envelope encryption: you don’t expose your vault key to every file — you **wrap the data key** and keep it separate.

## Real-World Analogy

Think of it like **gift wrapping**:

- The data is your present  
- The DEK is the wrapping paper  
- The master key (CMK) is the lockbox you keep the wrapping paper in  

You can:

- Tear off the wrapping (decrypt) if you have both  
- Replace the lockbox (rotate master keys) without touching the gift  

It’s a model that **balances performance, security, and management flexibility**.

---

## Why AWS Uses It Everywhere

You’ll see envelope encryption across AWS:

| Service | How It Uses Envelope Encryption |
|---------|----------------------------------|
| **KMS** | `GenerateDataKey` creates DEKs that are locally used to encrypt |
| **S3** | SSE-KMS uses DEKs to encrypt objects, then wraps them with CMKs |
| **RDS** | Encrypts snapshots and data files with DEKs |
| **Lambda** | Encrypts environment variables with DEKs |
| **EBS** | Volumes are encrypted with DEKs stored and wrapped by CMKs |

> In almost all of these cases, AWS **never uses your CMK to encrypt the actual data** — just to wrap the DEK.

---

## How It Works (Technical Breakdown)

### Encryption Flow

- Call `GenerateDataKey` from AWS KMS  
- Returns:
  - A **plaintext DEK** (used immediately to encrypt your data)  
  - A **ciphertext DEK** (the same DEK, but encrypted with your CMK)  
- Use the plaintext DEK to encrypt your data (e.g., AES-GCM)  
- Store:
  - The **encrypted data blob**
  - The **encrypted DEK** (alongside or within the object’s metadata)

---

### Decryption Flow

1. Extract the **encrypted DEK**  
2. Call `Decrypt` in AWS KMS to get the **plaintext DEK**  
3. Use that DEK to decrypt the data

---

## Why Not Just Use the CMK Directly?

CMKs in KMS are:

- Expensive to invoke at scale  
- Rate-limited (to protect misuse)  
- Heavily logged in CloudTrail  

If you used your CMK for every encrypt/decrypt call, you’d:

- Hit API throttles  
- Create massive latency  
- Risk exposure of your core key material  

Instead, AWS says: **generate a secure DEK**, use it once, **wrap it with the CMK**.

You now get:

- **Speed** (DEK operations are local)  
- **Safety** (CMK never exposed)  
- **Auditability** (CMK used only to wrap/unwrap)

---

## Security Properties

| Property            | Explanation                                               |
|---------------------|-----------------------------------------------------------|
| **Key separation**   | CMK never touches data directly — isolation of key usage |
| **Auditability**     | Every use of the CMK is logged in CloudTrail             |
| **Scalability**      | One CMK can protect millions of DEKs                     |
| **Rotation flexibility** | CMK can be rotated; old encrypted DEKs remain decryptable |
| **Performance efficiency** | Local data encryption with DEK is fast             |

---

## Common Attack Paths and Defenses

| Threat                    | Defense Mechanism                                      |
|---------------------------|--------------------------------------------------------|
| **CMK exposure**           | CMK stays in HSM-backed KMS; never leaves AWS infra    |
| **DEK leakage in memory**  | You must protect the plaintext DEK on your side        |
| **Replay attacks**         | Use encryption context, authenticated encryption       |
| **Key reuse across services** | Use different CMKs per app or tenant               |
| **Loss of wrapped DEKs**   | Store encrypted DEKs with encrypted data reliably      |

---

## Envelope Encryption With AWS KMS

When using **KMS**, the envelope model becomes very clean:

### Encryption

```plaintext
kms: GenerateDataKey → returns plaintext + encrypted DEK
App: Use plaintext DEK to encrypt data
App: Store ciphertext + encrypted DEK
```

### Decryption

```plaintext
App: Load encrypted DEK → call kms:Decrypt → get plaintext DEK
App: Use DEK to decrypt ciphertext
```

> All encryption and decryption happens **locally**.  
> The only thing **KMS sees is the DEK** — not your actual data.

---

## Encryption Context (Optional, But Powerful)

You can pass a **key-value map** (encryption context) when generating and decrypting the DEK:

```json
{
  "app": "snowy-ecommerce",
  "tenant": "blizzard",
  "env": "prod"
}
```

KMS **requires that same context** on decryption.

This:

- Prevents misuse of encrypted DEKs outside their intended context  
- Helps enforce data integrity and origin binding  
- Adds an extra layer of logical access control

---

## Use Cases for Envelope Encryption

| Use Case                       | Why Envelope Encryption Works Well                          |
|--------------------------------|--------------------------------------------------------------|
| Encrypting millions of S3 objects | Each gets a unique DEK, but all use one CMK               |
| Multi-tenant SaaS platforms     | One CMK per tenant; DEKs per object                        |
| Database record-level encryption | Per-record DEKs for fine-grained crypto control           |
| Lambda environment secrets      | Small sensitive blobs; DEKs avoid CMK overuse             |
| Cross-account data sharing      | Wrap DEKs with recipient's CMK                            |

---

## Final Thoughts

**Envelope encryption** is the cryptographic scaffolding behind nearly all modern encryption at scale.

It lets you:

- Encrypt large data securely and quickly  
- Isolate your master key from raw data  
- Log and monitor every sensitive key operation  
- Build trust boundaries between keys, services, and users  

If you're touching **KMS, S3, RDS, EBS**, or any security-focused service in AWS — you're **already using envelope encryption**, even if you didn’t know it.

But now you do — and now you understand how to use it intentionally, securely, and at enterprise scale.
