# AWS Signature Version 4 (SigV4)

## What Is SigV4

**AWS Signature Version 4 (SigV4)** is the **cryptographic signing process** AWS uses to **authenticate API requests** and **ensure their integrity**.

Every time you use the AWS CLI, SDK, or **presign an S3 URL**, you're creating a **SigV4-signed request** — whether you know it or not.

It ties together:

- Your identity (via IAM credentials)
- The request contents (method, headers, body, etc.)
- The timestamp and region
- The target service

So AWS can say:

> “Yep, this request was made by **Snowy**, hasn’t been tampered with, and was signed using **Snowy's IAM credentials**.”

It’s **cryptographic accountability** on every request — like **signing a check** and **fingerprinting it** at the same time.

---

## Cybersecurity and Real-World Analogy

### **Cybersecurity Analogy:**

Imagine you’re sending a **sealed envelope** (an API request) to AWS. But instead of just sealing it, you:

- Include your name
- Timestamp it
- Write a **fingerprinted summary** of what’s inside
- Sign the envelope in a way that AWS can independently verify — using only your **public key** (IAM)

> If anything changes — even the casing of a header — the signature breaks.
> AWS will reject the request with a `403 SignatureDoesNotMatch`.

### **Real-World Analogy:**

It’s like using a **tamper-evident envelope** with a **wax seal embossed with your family crest**.
**AWS is the doorman** checking the crest and date.

---

## How It Works (Step-by-Step)

Here’s the **4-part process** to generate a SigV4 signature:

### 1. Create a Canonical Request

A **normalized** version of your HTTP request. Includes:

- `HTTPMethod`
- `CanonicalURI`
- `CanonicalQueryString`
- `CanonicalHeaders`
- `SignedHeaders`
- `HashedPayload`

**Example:**

```
GET
/snowy.png
X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20250927T000000Z
host:s3.amazonaws.com
host
UNSIGNED-PAYLOAD
```

- Everything must be **sorted**, **lowercased**, **trimmed**
- **Whitespace**, **header order**, and **query param order** matter

### 2. Create a String to Sign

This is what you actually sign with your **derived key**. It includes:

- `AWS4-HMAC-SHA256`
- `<ISO8601 timestamp>`
- `<CredentialScope>`
- `<SHA256 hash of CanonicalRequest>`

**Credential Scope Format:**

```
YYYYMMDD/region/service/aws4_request
```

**Example:**

```
AWS4-HMAC-SHA256
20250927T000000Z
20250927/us-west-2/s3/aws4_request
ab12cdef3456789...(hashed canonical request)
```

### 3. Calculate the Signing Key (aka HMAC Chain)

This is the **"signature math"** step using **HMAC-SHA256**:

```text
kSecret  = "AWS4" + <YourSecretAccessKey>
kDate    = HMAC("20250927", kSecret)
kRegion  = HMAC("us-west-2", kDate)
kService = HMAC("s3", kRegion)
kSigning = HMAC("aws4_request", kService)

Signature = HMAC(<StringToSign>, kSigning)
```

Each step uses the **previous HMAC output** as the next key.
The final signature is **locked to**:

- Your **secret access key**
- That **specific date**
- That **specific region**
- That **specific service**

> Change **any** of those → ❌ Signature becomes invalid

### 4. Add the Signature to the Request

This can go either:

- In the `Authorization` **header**, or
- In the **query string** (for **presigned URLs**)

**Header Format:**

```
Authorization: AWS4-HMAC-SHA256 Credential=AKIA..., SignedHeaders=host;x-amz-date, Signature=<calculated_sig>
```

---

## What AWS Does on the Backend

AWS will:

- Parse your request
- Rebuild the **canonical request**
- Recreate the **string to sign**
- Look up your **IAM credentials**
- Derive the **signing key**
- Recalculate the **signature**
- Compare it against what you sent

> Mismatch = **rejection**

---

## Common Use Cases

| **Use Case**            | **How SigV4 Works There**                        |
|-------------------------|--------------------------------------------------|
| **Presigned S3 URL**    | Signature is added to the query string          |
| **API Gateway IAM auth**| Signature is in Authorization header            |
| **CLI/SDK requests**    | Handled automatically behind the scenes         |
| **Custom curl/API**     | You must manually create headers + sign         |

---

## Example Breakdown: S3 Presigned URL

**Presigned GET Request:**

```
https://bucket.s3.amazonaws.com/snowy.png?
X-Amz-Algorithm=AWS4-HMAC-SHA256&
X-Amz-Credential=AKIA.../20250927/us-west-2/s3/aws4_request&
X-Amz-Date=20250927T000000Z&
X-Amz-Expires=3600&
X-Amz-SignedHeaders=host&
X-Amz-Signature=abcdef123456...
```

AWS will:

- Reconstruct the **canonical request**
- Recalculate the **HMAC chain**
- Check the **signature**
- If valid and not expired → **allow download**

---

## Why SigV4 Matters (Security Benefits)

| **Security Property** | **How SigV4 Delivers It**                                   |
|-----------------------|--------------------------------------------------------------|
| **Authentication**    | Signature ties request to IAM identity                       |
| **Integrity**         | Hashing proves request wasn't modified                       |
| **Replay Protection** | Timestamps + short TTLs prevent re-use                       |
| **Scoping**           | Signature is bound to date, region, and service              |
| **No Secrets Sent**   | Signature is derived; the secret key itself is never sent    |

---

## Gotchas and Errors

| **Error**                 | **Cause**                                                        |
|---------------------------|------------------------------------------------------------------|
| `SignatureDoesNotMatch`   | Headers don't match, hash is wrong, wrong region/date/service    |
| `RequestExpired`          | Clock skew or URL expired                                       |
| `AccessDenied`            | IAM policy doesn't allow action — not a SigV4 issue              |
| `MissingAuthentication`   | No Authorization header or presigned query params                |

---

## Final Thoughts

**SigV4** is AWS’s way of saying:

> _“I’ll only let you in if you prove it was really you, the request hasn’t been altered, and you’re doing this right now — not later.”_

It’s the **cryptographic firewall** at the **front door** of every AWS service.

You’ll see this on the **exam**, especially tied to:

- IAM roles + credential use
- Presigned URL security
- API Gateway + Lambda integrations
- Identity federation edge cases

Understanding how the **signature is constructed** — especially the **HMAC chain** and **string-to-sign** — will not only help you **debug** but also **design more secure systems**.
