# SSE-C

## What Is SSE-C

SSE-C stands for Server-Side Encryption with Customer-provided keys, and it's exactly what it sounds like:

- You (the customer) generate and manage the encryption key
- Every time you upload or download an object, you include the raw key in the HTTPS request headers
- AWS uses that key to perform server-side encryption/decryption — but never stores the key, not even temporarily

This means AWS handles the encryption algorithm and storage, but not the key lifecycle.
**No KMS. No CloudTrail audit. No backups.**
It’s like borrowing AWS’s encryption machinery — but refusing to give them the keys.

---

## Cybersecurity Analogy

Imagine Snowy walks into a datacenter with a USB stick that holds a private key. Every time she gives AWS an object to store, she unlocks it with her key, and then locks it back. But once she walks away, AWS has no idea what key she used — and they have no way to decrypt that object unless she shows up again with the same exact key.
This puts 100% of the risk on Snowy.
Lose the key? Data's gone.
Mistype a byte? Decryption fails.
Key compromised? No revocation.

## Real-World Analogy

Let’s say Blizzard brings a secure safe to a public vault. He locks the safe using his own combination and asks the vault operator to store it. The vault has no clue what the combination is — they’ll never open it.
If Blizzard forgets the combo, the contents are permanently inaccessible, even if physically intact.
**This is SSE-C.** You keep the combo. AWS holds the safe.

---

## How SSE-C Works

### Upload Flow (PutObject):

1. You generate a 256-bit AES key (you’re responsible for entropy, format, and storage)
2. You Base64-encode the key and include it in the HTTPS headers:

  - x-amz-server-side-encryption-customer-algorithm: AES256
  - x-amz-server-side-encryption-customer-key: <your base64 key>
  - x-amz-server-side-encryption-customer-key-MD5: <md5 hash of key>

3. AWS:

- Uses the key to encrypt the object
- Stores the encrypted object in S3
- **Discards the key immediately**

### Download Flow (GetObject):

You must include the same headers, with the **exact same key**, so S3 can decrypt the object.
> ❗If the key is missing, rotated, or wrong — you get back an **unusable blob**.

---

## Key Characteristics

| Feature          | SSE-C                     |
|------------------|---------------------------|
| Key Generation   | Customer                  |
| Key Storage      | Customer                  |
| Key Rotation     | Manual, external          |
| Encryption Type  | Server-side AES-256       |
| KMS Involved?    | ✖️ No                     |
| CloudTrail Logging? | ✖️ No KMS logs        |
| Auditability     | Minimal                   |
| Common Use Case  | Regulated workloads w/ external crypto mandates |

---

## Why Use SSE-C? (It’s So Dangerous!)

Most customers should avoid SSE-C, but there are a few legit reasons someone might need it:

**External Compliance Demands**
Some regulations (esp. in banking or defense) require external key ownership
SSE-C allows you to use your on-prem HSM or key store

**Transitional Architectures**
Organizations migrating off legacy encrypted systems might use SSE-C as a stopgap
It lets them retain key parity while testing AWS

But even then, **AWS strongly recommends KMS-based or client-side encryption instead.**

---

## Risks and Limitations

| Limitation                  | Why It Matters                                                                 |
|-----------------------------|--------------------------------------------------------------------------------|
| No key backup               | If you lose the key, AWS can’t help. Data is permanently lost.                |
| No key revocation or rotation | You have to re-upload everything if keys change                           |
| No CloudTrail               | KMS is not involved, so no logging for Decrypt or GenerateDataKey             |
| No IAM-level control        | You can't scope access based on kms:Decrypt or tags                           |
| No grants, no context       | You lose all KMS advantages like encryption context enforcement               |
| HTTPS Required              | Must use HTTPS at all times or AWS will reject the request                    |
| Compromised key = full breach | Anyone with the key can decrypt the data, undetected                      |

---

## Security Monitoring Caveats

There is **no native CloudTrail visibility** on encryption operations with SSE-C.
You can:

- Track `PutObject` / `GetObject` in **S3 Data Events** if enabled
- Log network activity via **VPC Flow Logs**
- But you will **not see anything equivalent to** `kms:Decrypt` or `kms:GenerateDataKey`

This makes detection engineering and forensic auditing **nearly impossible.**
It’s the **black hole** of server-side encryption models.

---

## SSE-C vs SSE-KMS vs SSE-S3 Comparison

| Feature                     | SSE-S3         | SSE-KMS                        | SSE-C                  |
|----------------------------|----------------|--------------------------------|-------------------------|
| Who Manages Key?           | AWS            | AWS or Customer (CMK)          | Customer (raw key)      |
| CloudTrail Logging         | ✖️ None        | ✔️ Yes (KMS APIs)             | ✖️ None (no KMS)       |
| Key Rotation               | Automatic      | Optional (CMK-based)           | Manual, external        |
| IAM/KMS Condition Enforcement | ✖️ No       | ✔️ Yes                        | ✖️ No                  |
| Encryption Context         | ✖️ No          | ✔️ Yes                        | ✖️ No                  |
| HTTPS Required?            | ✖️ No             | ✖️ No                             | ✔️ Yes                 |
| Key Stored in AWS?         | ✔️ Yes         | ✔️ Yes                         | ✖️ Never               |
| Revocation/Policy Control  | ✖️ No          | ✔️ Yes (KMS policy)           | ✖️ No                  |
| Forensic Visibility        | ✖️ Minimal     | ✔️ Excellent                   | ✖️ Black box           |
| Risk of Data Loss?         | Low            | Low                            | High                    |

---

## Real-Life Snowy Scenario

Snowy’s company signs a contract with a **European defense contractor**.
Their compliance policy demands that data encryption keys **never be stored or visible to AWS**, even in wrapped form.

- Snowy’s team builds a secure enclave that generates AES256 keys per object
- Keys are passed to S3 using HTTPS headers
- Keys are stored securely in a hardware device in Germany (external HSM)
- Access is wrapped with audit controls and human review
- Every object must be uploaded/downloaded with the same key

But Snowy is nervous:

- If a developer messes up the key headers, the object is **unrecoverable**
- There's no **CloudTrail evidence** of access
- There's **no way to revoke** key usage post-upload

Eventually, the team migrates to **client-side envelope encryption + KMS** with external XKS integration, gaining control and audit.

---

## Final Thoughts

SSE-C is the **sharpest encryption knife** AWS gives you — and like any sharp object, it's easy to get hurt.

It offers:

- Absolute control
- Absolute detachment
- Absolute risk

It’s for:

- Power users with regulatory constraints
- Legacy compatibility
- Short-term compliance wins

But for everyone else, **SSE-KMS or client-side KMS encryption** is safer, easier, and far more observable.
**If you're not 100% sure you need SSE-C — you don't.**
