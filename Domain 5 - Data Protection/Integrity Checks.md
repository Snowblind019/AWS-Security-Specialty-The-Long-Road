# Integrity Checks

## What Are Integrity Checks

An **integrity check** is a way to verify that data has not been altered, corrupted, or tampered with — either accidentally (bitrot, transfer errors) or maliciously (injection, unauthorized changes).

In cybersecurity and cloud systems, integrity checks:

- Detect tampering  
- Prove that data is authentic and unchanged  
- Help build trust between systems  
- Act as the foundation for digital forensics and secure communications  

**Integrity ≠ confidentiality.** You don’t care what the data says — you care whether it’s been altered.

---

## Cybersecurity Analogy

Imagine you send a physical package to **Blizzard**. Before sending it, you:

- Wrap it with security tape  
- Add a numbered seal  
- Write down the exact weight on the shipping slip  

When **Blizzard** receives it, he checks:

- If the seal was broken  
- If the weight matches  
- If the tape is still intact  

If anything is off — possible tampering. That’s an integrity check.

## Real-World Analogy

Think of integrity checks like **tamper-evident seals** on a medication bottle:
- The seal doesn’t keep the bottle safe (that’s security)  
- It doesn’t hide what’s inside (that’s encryption)  
- It just tells you: “This has or hasn’t been opened.”  

Same with data. The integrity check can’t fix the data — but it will alert you if someone or something messed with it.

---

## How It Works (Under the Hood)

The core idea is simple:

- Take some input data (file, packet, API response)  
- Calculate its **hash** (e.g., SHA-256)  
- Send/store the hash alongside the data  

- Later, recalculate the hash and compare it to the original  

- If the hashes match — data is intact  

- If not — something changed  

Sometimes this is combined with **signatures or HMACs** to ensure both integrity and authenticity.

---

## Common Techniques for Integrity Checks

| Method                | Description                            | Example Use Case                     |
|-----------------------|----------------------------------------|--------------------------------------|
| **Hashing (SHA-256)** | Basic fingerprint of the data          | File uploads, package verification   |
| **Checksums (CRC32)** | Lightweight error detection            | Disk sectors, network packets        |
| **HMAC**              | Hash + secret key to prevent tampering | AWS SigV4, S3 pre-signed URLs         |
| **Digital Signatures**| Hash encrypted with a private key      | SSL certs, JWTs, software packages   |
| **Content-MD5 Header**| Base64-encoded MD5 hash in HTTP headers| S3 PUT object integrity validation   |
| **S3 ETag**           | Identifier that changes if object changes | S3 version control and sync logic |

---

## AWS Use Cases for Integrity Checks

### S3 Object Upload Integrity  
- Include a **Content-MD5** header when uploading to S3  
- S3 calculates the MD5 of what it received and compares  
- If it doesn’t match — upload fails  

Protects against:  
- Corrupted uploads  
- Man-in-the-middle alterations  
- Flaky network issues  

### S3 ETag  
- Automatically generated hash (often MD5 or multipart hash)  
- Compare to your local hash to verify content consistency  

### AWS Lambda Code Hash  
- Each Lambda version includes a hash of the deployment package  
- AWS uses this to detect unauthorized changes  

### CloudTrail Log File Validation  
- AWS provides a `.digest` file containing signed hashes of CloudTrail logs  
- Verify logs weren’t altered using public key + hash check  
- Required for forensic evidence and audit trails  

### AWS API SigV4  
- Includes hash of payload in the signed request  
- Ensures the request wasn’t tampered with in transit  
- Prevents replay or modification attacks  

### GuardDuty / Inspector Findings  
- Include SHA-256 hashes of suspicious files  
- Use these to search threat intel databases  

---

## Hash vs Checksum vs Signature

| Feature       | Checksum (CRC)           | Hash (SHA-256)             | Digital Signature             |
|---------------|--------------------------|----------------------------|------------------------------|
| **Speed**     | Fast                     | Moderate                   | Slower                       |
| **Tamper Proof** | ✖️ No (easily forged)  | 🟣 Somewhat (collisions possible) | ✔️ Yes (cryptographically strong) |
| **Use For**   | Bit errors               | File comparison            | Authenticated validation     |
| **Security**  | ✖️ Minimal                | 🟣 Medium                  | ✔️ High                      |

---

## Real-Life Example

Snowy is uploading a deployment archive (`build.zip`) to S3. Before uploading:

- He runs `sha256sum build.zip` and stores the result  
- Then uploads the file with a `--content-md5` header  
- S3 calculates the hash of what it received and compares it  

Later, he downloads it on a new server and reruns the hash:

- If the hash matches: file is clean and intact  
- If not: either the file was tampered with or corrupted during transit  

For **CloudTrail logs**, Snowy’s compliance team regularly validates the `.json.gz` log files using the `.digest` file and AWS’s public key — ensuring no one has silently modified the logs.

---

## Final Thoughts

Integrity checks don’t stop bad things from happening — but they make sure you know when something has gone wrong.

They’re a critical pillar of zero trust, secure communications, and digital forensics. In AWS and beyond, if you don’t check for integrity, you’re trusting blindly — and that’s not security.

Whether you’re securing files, APIs, audit logs, or containers — **hash it, check it, verify it.**

