# AWS Encryption SDK

## What Is It

The AWS Encryption SDK is a client-side encryption library designed for developers who want to encrypt data before sending it to AWS — without writing all the cryptographic plumbing from scratch.

It:

- Automatically handles envelope encryption  
- Supports multiple master keys (multi-MK)  
- Works with AWS KMS, CloudHSM, or external key managers (like HashiCorp Vault)  
- Operates in languages like Java, Python, JavaScript, C, and .NET  

Instead of figuring out:

- How to generate data keys (DEKs)  
- How to securely wrap them  
- What encryption algorithms to use  
- How to store metadata with ciphertext  

You can call a simple function like:

```python
ciphertext = encryptor.encrypt(plaintext, master_key_provider)
```
And all of that happens under the hood, securely, and consistently.

This is the encryption abstraction layer for apps that need client-side security at scale — especially when you need multi-region, multi-key, or external HSM support.

---

## Cybersecurity Analogy

Imagine you're Snowy, tasked with writing an app that encrypts sensitive billing data before storing it in S3. You know envelope encryption is the right pattern (generate random DEK, encrypt data, wrap DEK with CMK) — but you don't want to hand-craft it with pycryptodome, KMS API calls, and JSON wrappers.


The Encryption SDK is your encryption butler:

- It answers: “How do I pick a strong DEK?” ✅  
- It handles: “How do I wrap and store keys safely?” ✅  
- It builds: “A consistent ciphertext format with metadata.” ✅  

- It even lets you say: “Encrypt this file using both my KMS key and my HSM key.” ✅  

You stay focused on your app — not cryptographic edge cases.

## Real-World Analogy

Think of the Encryption SDK as the Amazon Prime of encryption. You don’t build the trucks, the warehouses, or even choose the shipping carrier — you just say, “Ship this securely and get it there fast.”

Instead of reinventing key generation, wrapping, envelope formats, or integrity checks — you let the SDK handle it.

It’s the logistics stack for cryptography — but for your apps.

---

## How It Works

When you call the SDK’s `encrypt()` method, here’s what happens:

- Generate a DEK — using secure random entropy  
- Encrypt the plaintext data with that DEK  
  - Usually AES-GCM (authenticated encryption)  
- Wrap (encrypt) the DEK with one or more Master Keys (MKs)  
  - Using AWS KMS, CloudHSM, Vault, or a custom interface  
- Attach metadata to the ciphertext:  
  - Encryption algorithm  
  - Key info (ARNs, IDs)  
  - Encryption context  
  - Wrapped DEKs  
- Return ciphertext — a complete, self-describing blob  

When you decrypt:

- The SDK extracts the metadata  

- It fetches and unwraps the DEK using the configured master key provider  
- It uses the DEK to decrypt the data and returns plaintext  

This means the ciphertext can be:

- Stored anywhere (S3, RDS, on disk)  
- Read later by any system with access to the key material  
- Portable across regions and clouds  

---

## Key Features and Design Principles

| Feature                | Description                                                                 |
|------------------------|-----------------------------------------------------------------------------|
| Envelope encryption    | Securely wraps data keys (DEKs) with master keys (CMKs, HSMs, etc.)         |
| Multi-key support      | Encrypts the same DEK with multiple master keys                             |
| Language SDKs          | Available for Python, Java, JavaScript, C, .NET                             |
| Key providers          | Support for KMS, HSMs, or custom plugins (e.g., HashiCorp, Thales)          |
| Encryption context     | Optional key-value metadata for added integrity validation                  |
| Streaming support      | Handles large files without loading them fully into memory                  |
| Format standardization | Provides consistent ciphertext format with headers, metadata, versioning    |
| Authentication included| Uses authenticated encryption (typically AES-GCM) to protect data integrity |

---

## When To Use It

| Use Case                               | Why Encryption SDK Helps                                         |
|----------------------------------------|------------------------------------------------------------------|
| Client-side encryption before uploading to S3 | Handles envelope encryption cleanly                 |
| Multi-region workloads                 | Support for multiple CMKs (one per region)                       |
| Compliance-driven key separation       | Encrypt with both KMS and an HSM or Vault                        |
| Large file encryption with streaming   | Built-in support without loading full file into memory           |
| BYOK/External HSM workflows            | Plug in custom master key providers                              |
| Custom encryption in apps that don’t want SSE/S3-KMS | Maintain control without relying on AWS services     |

---

## Encryption Context

You can attach a key-value pair metadata object called an **encryption context** during encryption.

During decryption, that context must exactly match — or the operation fails.

This is great for:

- Ensuring the ciphertext wasn’t tampered with  
- Binding the encryption to a specific user, tenant, or application  
- Preventing misuse of the key in unintended contexts  

**Example:**

```json
{
  "service": "billing",
  "tenant": "SnowCorp",
  "env": "prod"
}
```

---

## AWS KMS + Encryption SDK Together

This is a very common and powerful combo:

- The SDK calls `GenerateDataKey` to get a DEK  
- It encrypts locally with that DEK (not on AWS)  
- It uses `Encrypt` to wrap the DEK with a KMS CMK  
- It stores the encrypted blob somewhere (S3, EFS, database)  

Then later:

- Decryption extracts metadata and calls KMS to unwrap the DEK  
- The decrypted DEK is used locally to decrypt the file  

**Why this is awesome:**

- Minimal KMS calls  
- Strong audit trail (CloudTrail logs for DEK usage)  
- Local control of plaintext  
- Zero AWS access to your data at rest  

---

## Security Caveats

| Risk                      | Explanation                                                                 |
|---------------------------|-----------------------------------------------------------------------------|
| DEK exposure in memory    | You are responsible for protecting plaintext DEKs in RAM                    |
| Custom key providers      | You must secure and validate access to external Vaults or HSMs              |
| Application compromise    | If your app is compromised, the encryption SDK can be used to decrypt too  |
| Misuse of multi-MK        | Accidentally encrypting data with the wrong combination of master keys      |
| Missing encryption context| If you skip it, integrity checks are weaker                                |

---

## Real-Life Snowy Scenario

Snowy is building a SaaS platform where every customer’s invoices must be encrypted client-side before uploading to S3.

But she also needs to:

- Encrypt using both KMS (for backup decryption) and Vault (for on-prem key use)  
- Allow customers to re-encrypt invoices if they rotate their keys  
- Audit every decrypt event via CloudTrail  
- Handle 50 GB CSVs from batch billing jobs  

She integrates the Encryption SDK with:

- A custom `MultiKeyProvider` plugin for KMS + Vault  
- Streaming file I/O  
- An encryption context per customer  

Each encrypted invoice:

- Is wrapped with two master keys  
- Can be decrypted by either KMS or Vault  
- Is stored in S3, unreadable to AWS  

The app is now resilient, compliant, and built for scale — with none of the crypto complexity in her own codebase.


