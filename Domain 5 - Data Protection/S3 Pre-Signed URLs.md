# Amazon S3 Pre-Signed URLs — Snowy Edition Deep Dive

## What Is a Pre-Signed URL (And Why It’s Important)

A pre-signed URL is a temporary, secure link that grants time-limited access to an S3 object. It’s signed using the credentials of the person or system generating it and allows someone without AWS credentials to securely:

- Download a private object (`GET`)
- Upload an object (`PUT`)
- But only what the signer allowed — nothing else

It’s one of the most elegant least-privilege tools in AWS. Instead of opening the bucket with public access or giving IAM credentials, you say:

> "Here’s a signed ticket — valid for 5 minutes — use it to download this one file, then it self-destructs."

---

## Cybersecurity Analogy

Imagine **Snowy** controls access to a vault.
**Blizzard** needs to read one document, but Snowy doesn’t want to give him the master key to the vault.

So instead, Snowy:

- Prepares a read-only pass
- Stamps it with an expiry time
- Signs it with his own unique seal
- Hands it to Blizzard, who uses it to get in once, for one file, before the timer runs out

That pass? It’s the **pre-signed URL**.

## Real-World Analogy

Think of a **boarding pass** at the airport:

- It lets you on one specific flight
- At one gate
- Only within a certain window
- Issued by the airline (authority), not forged
- Scanned at the gate to check validity and identity

You can’t reuse it tomorrow, you can’t use it at a different gate, and you can’t board a different plane — same with **pre-signed URLs**.

---

## How It Works

Here’s what happens step-by-step when **Snowy** generates a pre-signed URL:

1. Snowy’s backend (running with IAM permissions) prepares a URL to access an S3 object
2. The SDK signs that URL using:
   - **AWS SigV4**
   - **Snowy’s access key + secret key**
   - Includes:
     - HTTP verb (`GET`, `PUT`, etc.)
     - Bucket + object key
     - Expiry time (in seconds, max 7 days)
3. The result is a long URL containing:
   - Bucket/object path
   - Query params:
     - `X-Amz-Algorithm`
     - `X-Amz-Credential`
     - `X-Amz-Signature`
     - `X-Amz-Expires`
4. Snowy sends this URL to **Blizzard**

5. Blizzard uses the link with **no AWS credentials**

6. If the signature is valid and the time window hasn’t passed — ✅ access granted
   If not — ❌ 403 Forbidden

---

## Security Benefits

| Benefit                     | Why It Matters                                                                |
|-----------------------------|-------------------------------------------------------------------------------|

| **Time-Limited Access**     | Reduces window of exposure if leaked                                         |
| **No IAM Needed for Receiver** | User doesn't need AWS credentials, access keys, or roles                 |
| **Granular Permissions**    | Only allows one operation (`GET`, `PUT`) for one object                      |
| **Temporary & Self-Destructing** | Can't be used after expiration                                          |
| **Secure Auth via SigV4**   | Hard to forge, based on AWS HMAC-SHA256 signature of the URL + headers       |

---

## Common Use Cases

### Secure File Download

Snowy wants to let customers download invoices stored in S3, but:

- Doesn’t want to expose the bucket
- Doesn’t want to create IAM users

Instead, he:

- Generates a pre-signed URL for `invoices/Winterday_2025.pdf`
- Expires in 2 minutes
- Sends it via email or in the app

The customer can only download that one file, once, in a short window.

### Secure File Upload

**Winterday** is uploading logs from an edge device. Snowy doesn’t want to give the device IAM keys.

Instead:

- Snowy’s backend generates a pre-signed `PUT` URL
- Winterday's device uses `curl -X PUT --upload-file log.json 'https://...X-Amz-Signature=...'`

- The object is uploaded without ever touching IAM

### Temporary Secure Access Between Services

- Web servers or apps need to give clients access to files
- Data pipelines temporarily upload files to shared S3 buckets
- You want **zero trust**, **minimal exposure**, **no over-permissioning**

---

## Key Configs and Limits

| Feature              | Value / Notes                                           |
|----------------------|---------------------------------------------------------|
| **Max Expiration**    | 7 days (604800 seconds)                                 |
| **Minimum Expiration**| As short as 1 second                                    |
| **Signing Algorithm** | AWS Signature Version 4 (HMAC-SHA256 based)             |
| **Allowed Methods**   | `GET`, `PUT`, `DELETE`, `HEAD` (depending on SDK)       |
| **Permissions Needed**| Generator needs IAM perms (`s3:GetObject`, `s3:PutObject`) |
| **Receiver Needs IAM?**| ❌ No — anonymous users can use the link (if signed properly) |

---

## Security Caveats

| Risk                   | Mitigation                                                              |
|------------------------|-------------------------------------------------------------------------|
| ❌ Link Leaking         | Short expiration + HTTPS delivery only                                  |
| ❌ Reusing Old Links    | Use very short TTL (30–300s) for one-time access                        |
| ❌ Over-permissioning   | Only generate per-object, per-method links (no wildcards)               |
| ❌ Insider Misuse       | Log generation of pre-signed URLs using CloudTrail                      |
| ❌ Logging URLs in Full | Avoid storing or logging full URL with credentials in plaintext logs    |

---

## Real-Life Example

**Snowy** builds a document signing app. Customers upload documents for signature.

But instead of giving the front-end IAM access:

- Snowy's server creates a pre-signed `PUT` URL for `uploads/Blizzard_Terms.pdf`
- Frontend uploads the file to that URL
- Snowy then generates a pre-signed `GET` URL to allow Blizzard to download it once
- All links expire after 2 minutes
- All actions are logged in **CloudTrail**

> Zero IAM credentials were exposed.
> Zero bucket permissions were made public.

The whole thing? **Elegant**, **secure**, and **minimum blast radius**.

---

## Final Thoughts

S3 Pre-Signed URLs are one of AWS’s most underused gems. They strike a perfect balance between **security** and **usability**, allowing you to delegate access without delegating identity.

- No credentials
- No policies
- No buckets left open to the world

Just a **cryptographically signed URL** that **self-destructs**.

Use them wherever you need **secure**, **temporary**, and **auditable** access to S3 — and you’ll sleep better knowing your data flows are **tight**, **scoped**, and **traceable**.
