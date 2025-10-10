# Hashing

## What Is Hashing

Hashing is a one-way cryptographic function that takes any input (file, password, message) and transforms it into a fixed-length string — called a hash or digest.

- The output is always the same size, no matter how big or small the input is.
- A tiny change in the input results in a completely different hash.
- It’s deterministic — same input always gives same hash.
- But it’s irreversible — you can’t go backward and get the original input from the hash.

In AWS, cloud security, and general cybersecurity, hashing is a foundational building block for:
- File integrity checks
- Password storage
- Digital signatures
- Tamper detection
- Message authentication (HMAC)
- Blockchain
- Malware detection and SIEM correlation

You’ll find hashes everywhere: in IAM password policies, S3 object integrity checks (ETags), Lambda versioning (function hashes), Certificate fingerprints, and GuardDuty malware findings.

---

## Cybersecurity Analogy

Imagine you own a library vault filled with ancient books. You want to make sure none of the books are tampered with, but you don’t want to open each one daily to check.

So instead, you:
- Weigh each book
- Take a photo of its cover
- Count the number of pages
- Combine all those into a unique tag

Now every time you check the vault, you recalculate those 3 things and compare them to the original tag. If the tag doesn’t match, someone’s tampered with the book.

That unique tag is your **hash** — a compact fingerprint proving the object hasn’t been altered.

## Real-World Analogy

Hashing is like a digital fingerprint. Just like your fingerprint uniquely identifies you — but can’t be used to recreate your entire DNA — a hash represents data without exposing the actual content.

Or, imagine a blender:
- You throw in a file (banana, milk, berries)
- Hit "blend"
- You get a smoothie (the hash)

You can taste the smoothie and know it's yours — but there’s no way to get the banana back from that blended mess.

---

## How It Works

Hashing algorithms take an input and run it through a mathematical function that produces a fixed-size output.

### Common Hash Functions

| Hash Algorithm | Output Size | Use Case                      | Notes                                     |
|----------------|-------------|-------------------------------|-------------------------------------------|
| MD5            | 128 bits    | Legacy file checksums         | Weak, collision-prone — don’t use         |
| SHA-1          | 160 bits    | Digital signatures (legacy)   | Broken, vulnerable to collisions          |
| SHA-256        | 256 bits    | Password hashing, data integrity | Standard secure hash (used in S3, Lambda) |
| SHA-512        | 512 bits    | High-security apps, blockchain | Slower but more bits of entropy           |
| bcrypt         | Variable    | Password hashing              | Slow, salted, includes cost factor        |
| scrypt         | Variable    | Password hashing (memory hard) | Good for preventing GPU attacks           |
| HMAC-SHA256    | 256 bits    | Message integrity/authentication | Used in API signing, IAM SigV4         |

---

## Hashing ≠ Encryption

| Feature           | Hashing                    | Encryption                        |
|------------------|----------------------------|-----------------------------------|
| One-Way?          | ✔️ Yes                     | ✖️ No — reversible with key       |
| Fixed Size?       | ✔️ Yes                     | ✖️ No — ciphertext size varies     |
| Used For          | Integrity, fingerprints    | Confidentiality, secrecy          |
| Can Decrypt?      | ✖️ No                      | ✔️ Yes (if key is known)          |

- **Hashing** proves nothing was altered
- **Encryption** hides the content from others

---

## Common Use Cases In Security & AWS

### 1. Password Hashing
- Never store plaintext passwords.
- Use salted hashing (bcrypt, scrypt, Argon2)
- On login, hash the entered password and compare hashes

### 2. File Integrity
- Calculate the hash of a file before upload
- Recalculate after download
- If the hash matches, the file wasn’t tampered with
- S3 does this with ETags and `Content-MD5`

### 3. Lambda Versioning
- Each deployment gets a unique hash based on the function package
- Prevents code tampering

### 4. CloudTrail + GuardDuty
- Findings include SHA-256 hashes of files flagged as malware
- Lets you search VirusTotal or threat feeds for known malware

### 5. API Signing (IAM SigV4)
- Uses HMAC (hash + secret key) to sign API requests
- Prevents man-in-the-middle or unauthorized calls

---

## Advanced Concepts

### Salting
- Add random data to the input before hashing (like `password123 + random_salt`)
- Prevents precomputed hash attacks (rainbow tables)
- Used in bcrypt, scrypt, Argon2

### Stretching
- Intentionally slow down the hash (by repeating it many times)
- Makes brute force attacks more expensive
- Example: `bcrypt($password, cost=12)`

### HMAC
- Hash-based Message Authentication Code
- Combines a secret key with the input before hashing
- Ensures both integrity and authenticity
- Used in SigV4, S3 presigned URLs, Cognito tokens

---

## Real-Life Example

Snowy wants to store customer passwords securely in a DynamoDB table (not best practice, but for learning).

Instead of saving:

```json
{ "user": "Blizzard", "password": "hunter2" }
```

He saves:

```json
{ "user": "Blizzard", "password_hash": "bcrypt$2a$12$eW91IGFjdHVhbGx5IHJlYWQgdGhpcyE=" }
```

Now even if the table is leaked, attackers can't reverse the hash — especially with salting and high cost factors.

Later, Snowy uploads config files to S3 and enables checksum validation using SHA-256 to ensure deployment files are never silently corrupted in transit.

---

## Final Thoughts

Hashing is the backbone of integrity in cybersecurity. It’s invisible, under-the-hood, but critical for everything from password security to file uploads to forensic evidence in threat reports.

If encryption is the **lock on the door**, hashing is the **seal that proves the door hasn’t been picked**.

In a zero-trust world where everything needs verification, hashing makes it possible to say:

> “Yes, this is exactly what it claims to be.”
