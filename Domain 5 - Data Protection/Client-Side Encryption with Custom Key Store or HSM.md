# Client-Side Encryption with Custom Key Store or HSM

## What Is It

This encryption model is entirely outside of AWS’s hands. You generate your encryption keys in **CloudHSM**, an on-prem **Hardware Security Module**, or a third-party KMS like **HashiCorp Vault**, **Thales**, **Fortanix**, or even a government-mandated crypto appliance — then **encrypt your data locally** before ever sending it to AWS.

- AWS does **not** see the key  
- AWS does **not** see the plaintext  
- No KMS, no SSE, no IAM control over encryption/decryption  
- All key management, encryption, rotation, logging — **it’s all you**  

This pattern is common in industries with strict data sovereignty or external compliance mandates (e.g., financial institutions, health care, government, military, etc.).

> If symmetric KMS is a middle ground, this is the **zero-trust extreme**.

---

## Cybersecurity Analogy

Think of it like this:

**Snowy** is storing sensitive government research notes. The compliance office says:

> “Nobody but you can touch the key — not AWS, not a cloud admin, not even by accident.”

So Snowy:

- Uses an HSM in a locked basement  
- Creates a key pair inside that HSM  
- Encrypts her notes locally using that key  
- Uploads only the ciphertext to S3  

If a rogue cloud admin, a misconfigured KMS, or a nation-state attacker tries to read it — they can’t.

> **AWS has no logs, no decryption path, no ability to help. And that’s by design.**

## Real-World Analogy

Imagine you're dropping off a briefcase in a bank’s safety deposit box.

But this time, you bring your **own custom-built biometric lock**, manufactured in your basement, powered by a battery only **you** know how to recharge.

The bank (AWS) stores your locked briefcase, but they:

- Can’t open it  
- Don’t know what locking mechanism you used  
- Don’t even know what’s inside  
- Can’t help if you forget your password  

> This is **maximum control, maximum responsibility**.

---

## How It Works

Here’s the typical encryption pipeline in this model:

1. **Generate the encryption key** in:
   - AWS **CloudHSM** cluster  
   - On-premise HSM  
   - External KMS/Vault (e.g., HashiCorp, CyberArk, Fortanix)  

2. **Encrypt your data locally** with that key using:
   - Your own crypto libraries  
   - AES-256-GCM or XTS  

3. **Upload encrypted blob** to S3 (or any AWS storage):
   - S3 doesn’t know it’s encrypted — it’s just binary data  
   - You can store encrypted metadata alongside if needed  

4. **Decryption happens off-AWS**, using your own systems:
   - Data is useless without your key infrastructure  
   - No AWS APIs involved in decryption  

---

## Integration Patterns

| System               | Purpose                                                |
|----------------------|--------------------------------------------------------|
| **CloudHSM**         | AWS-native HSM cluster you control                     |

| **External HSM**     | Physical device on-prem or colocation                  |
| **XKS**              | External Key Store — lets AWS KMS call out to your key store for decryption (used with SSE-KMS) |

| **AWS Encryption SDK** | Encrypts/decrypts locally using your chosen master key (KMS, HSM, etc.) |
| **HashiCorp Vault**  | Popular in zero-trust/DevSecOps pipelines              |

| **Thales CipherTrust** | Common in federal and high-assurance contexts       |

---

## Why It’s Used

| Use Case                      | Why It Fits                                               |
|-------------------------------|------------------------------------------------------------|
| Government classified workloads | Full key ownership required                             |
| Cross-border regulatory controls | Data must be encrypted before touching any foreign infra |
| Banks with crypto policy mandates | Keys must live in private cloud HSMs only             |
| Zero-trust or air-gapped systems | No external entity can be trusted with decryption       |
| BYOK with no trust in KMS        | Some orgs won't accept cloud-native encryption at all   |

---

## Security Trade-Offs

| Security Property     | Value                                                                 |
|------------------------|----------------------------------------------------------------------|
| ✔ Max control          | You own the full key lifecycle — generate, store, revoke             |
| ✔ Zero trust           | No AWS involvement; not even a chance for AWS to decrypt             |
| ✖ Zero visibility      | No CloudTrail logs for encryption/decryption                         |
| ✖ No native IAM controls | Can't restrict access using KMS condition keys                   |
| ✖ Manual rotation      | You must rotate and re-encrypt objects yourself                      |
| ✖ No policy enforcement | No S3 bucket policy support for external keys                     |
| ✖ No automatic backup  | If your HSM dies, so does your key — and your data                   |

> You gain **maximum assurance** — but you trade away all the “guardrails” AWS usually gives you.

---

## AWS Encryption SDK + External Keys

The **AWS Encryption SDK** helps bridge this complexity.

It can:

- Do envelope encryption with custom master keys  
- Encrypt/decrypt in your app with structured metadata  
- Support multi-master (e.g., HSM + backup KMS)  
- Rotate DEKs securely  

You still need to:

- Write integration logic with your vault  
- Manage availability of your HSM/KMS  
- Secure local runtime handling of DEKs  

But it helps **standardize** envelope encryption, metadata, and key wrapping formats.

---

## Comparison with Client-Side KMS CMK

| Feature                   | Client-Side KMS CMK     | Client-Side Custom HSM/KMS          |
|---------------------------|--------------------------|--------------------------------------|
| Key Source                | AWS KMS                  | CloudHSM, on-prem HSM, Vault         |
| Who Holds Key             | AWS (via CMK access)     | Customer only                        |
| Key Rotation              | Automatic via KMS        | Manual (unless scripted)             |
| CloudTrail Logging        | Yes (GenerateDataKey, Decrypt) | No (unless Vault/HSM logs it)  |
| IAM Condition Controls    | Yes                      | No                                   |
| S3 Bucket Policy Integration | No (client-side)     | No                                   |
| Compliance Scope          | Moderate–High            | Maximum (gov, defense, etc.)         |
| Complexity                | Medium                   | Very High                            |

---

## Real-Life Snowy Scenario

**Snowy** is working on a multi-national fintech platform that must comply with **European Schrems II** restrictions.

The legal team says:

> “We don’t trust any US cloud provider with unencrypted data or key custody.”

So Snowy:

- Deploys a CloudHSM cluster in **Frankfurt**  
- Connects encryption microservices to use CloudHSM APIs via **PKCS#11**  
- Writes a Go service to encrypt blobs with **AES-GCM** using HSM-backed keys  
- Uploads encrypted blobs to S3 in `eu-central-1`  
- Keys never leave the HSM; data is never readable outside their secure enclave  

✔ GDPR compliant  
✔ Crypto segregation  
✔ Cloud-native storage — all with **zero AWS key involvement**

---

## Final Thoughts

Client-side encryption with a **custom key store or HSM** is **not for the faint of heart** — but it’s the right choice when:

✔ You require external crypto trust boundaries  
✔ You must own your key lifecycle completely  
✔ Compliance dictates total cloud-provider isolation  

> It is powerful, opaque, and dangerous if mishandled.

If:

- **SSE-S3** is using a lock AWS built for you, and  
- **SSE-KMS** is asking AWS to use your lock, and  
- **Client-Side KMS** is AWS handing you the lock and letting you use it —  

Then **this model** is:

> **You forging your own lock, building your own vault, and trusting only yourself with the key.**

