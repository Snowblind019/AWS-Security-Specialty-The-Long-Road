# Client-Side Encryption With KMS (Client-Side CMK)

## What Is It

Client-side encryption means you encrypt the data locally, before uploading it to S3 (or any storage service). The key point here is that AWS never sees the unencrypted data — and KMS is only used as a key provider, not an encryption engine.

The flow uses KMS to generate Data Encryption Keys (DEKs), but you handle:

- The actual encryption  
- The secure storage of ciphertext  
- The full responsibility for key rotation, wrapping, and re-encryption  

This is completely separate from SSE-KMS, where AWS handles encryption for you. Here, **you’re the one doing the cryptography.**

---

## Cybersecurity Analogy

Imagine **Snowy** wants to store secret notes in a bank vault (S3). She goes to AWS KMS and asks, “Hey, can I get a key to encrypt this note?”

- KMS hands her a DEK and its encrypted form  
- Snowy encrypts her note locally, using the DEK  
- She uploads the encrypted note to S3  
- AWS stores only the ciphertext and the wrapped DEK  

**AWS never sees the original note.** If someone breaks into S3, they get scrambled nonsense — and without KMS + Snowy’s permissions, they’re stuck.

## Real-World Analogy

You go to a safe manufacturer (AWS KMS) and ask them to give you a padlock and a backup key. You then lock your briefcase yourself at home and store it in a public locker (S3). The locker facility never sees what’s inside the briefcase or how you locked it — they just hold it.

This makes you fully responsible for:

- Using the right padlock  
- Securing the backup key  
- Knowing how to unlock it later  

---

## How It Works — Envelope Encryption

**Envelope encryption** is the backbone of client-side KMS encryption.

Instead of using your long-term KMS CMK to encrypt everything (which would be slow, expensive, and limited), you do this:

### 1. Call `GenerateDataKey`

- You ask KMS to generate a fresh Data Encryption Key (DEK)  
- You get back:  
  - **Plaintext DEK** (used immediately)  
  - **Encrypted DEK** (wrapped with your KMS CMK)  

### 2. Encrypt the Data Locally

- Use the plaintext DEK to encrypt your data with AES-256-GCM (or similar)  
- Discard the plaintext DEK from memory (securely)  

### 3. Upload to S3

- Upload the encrypted data blob  
- Store the encrypted DEK alongside the blob (e.g., as metadata or separate file)  

### 4. To Decrypt Later

- Retrieve encrypted blob + encrypted DEK  
- Send encrypted DEK to KMS → get back plaintext DEK  
- Decrypt data locally using the DEK  

---

## Why This Is Used

## CloudTrail and IAM Visibility

Since you’re using KMS via API (`GenerateDataKey`, `Decrypt`), these actions are **logged in CloudTrail** and can be:

- Tracked by IAM policy conditions  
- Audited by security teams  

- Scoped with encryption context (e.g., “only allow DEKs for finance uploads”)  

This gives you:  

- Visibility  
- Least-privilege enforcement  
- Auditability  

But remember: **data access itself (S3 GET)** won’t hit KMS unless you’re decrypting the DEK — so **design accordingly.**

---

## Plaintext DEK Handling Tips

Since the plaintext DEK is the most sensitive thing in the workflow:

- Only keep it in memory for the few milliseconds it takes to encrypt/decrypt  
- Use in-memory buffers instead of disk  
- Zero the buffer once done  
- Use secure libraries (e.g. `cryptography` in Python, AWS Encryption SDK)  
- Never log it, cache it, or transmit it unencrypted  

> **Think of the plaintext DEK like a lit match. Use it quickly, and then extinguish it.**

---

## AWS SDK Support

Most major AWS SDKs and encryption tools support this model, including:

- AWS Encryption SDK  
- AWS Java SDK CryptoModule  
- Third-party libraries with KMS integration  
- Custom envelope encryption tools using `GenerateDataKey`  

You can customize:

- Encryption context  
- Key specs (AES-128, AES-256)  
- Use per-object DEKs or shared DEKs for batch performance  

---

## KMS Pricing Implications

| KMS API Call       | Cost Impact                      |
|--------------------|-----------------------------------|
| `GenerateDataKey`  | ✔️ Charged per call                |

| `Decrypt`          | ✔️ Charged each time used          |
| `Encrypt`          | ✖️ Not used (you do it yourself)  |

High-volume use of `GenerateDataKey` or `Decrypt` can result in **thousands of calls**, so cache encrypted DEKs carefully.

---

## Comparison Table

| Feature                   | SSE-KMS             | Client-Side KMS CMK      |
|---------------------------|---------------------|---------------------------|
| Encryption Location       | AWS (S3)            | Customer side (local app) |
| Who Sees Plaintext Data   | AWS (briefly)       | Never AWS                 |
| DEK Handling              | Handled by AWS      | Handled by you            |
| Envelope Encryption?      | Yes                 | Yes                       |
| KMS Involved?             | Yes                 | Yes                       |
| CloudTrail Logs?          | Yes                 | Yes (via API)             |
| S3 Bucket Policy Support  | Yes                 | ✖️ No                     |
| Requires Custom Code      | No                  | Yes (or AWS SDK)          |
| Use Case                  | Simpler workloads   | Advanced compliance       |

---

## Real-Life Snowy Scenario

Snowy works at an **international bank** handling mortgage loan data. Their legal team says:  
> “Data must be encrypted before it leaves our premises, and AWS can never hold the key.”

**Snowy’s team:**

- Uses a local Java microservice  
- Calls `GenerateDataKey` for each object  
- Encrypts data locally with AES-GCM  
- Uploads encrypted data + encrypted DEK to S3  
- Stores metadata about key use in DynamoDB for rotation/audit  

Later, a user requests their mortgage file. The app:

- Pulls down the encrypted blob  
- Calls `Decrypt` on the encrypted DEK  
- Decrypts locally, returns data  

**The team gains:**  
- Regulatory compliance  
- Full control  
- KMS-based audit trails  

**But they also manage:**  
- Code maintenance  
- Memory hygiene  
- Rotation tooling  

---

## Final Thoughts

Client-side encryption with KMS is **powerful**, but **not plug-and-play**. It’s for teams who:

- Know how to manage encryption locally  
- Want zero trust in AWS access to plaintext  
- Need regulatory separation of storage and key ownership  

It brings visibility and control — but demands **security engineering** to do right.

> If SSE-KMS is a **guardrail**, then Client-Side CMK is a **racecar** — fast, sleek, and fully manual.  
> But you’d better know how to drive.
