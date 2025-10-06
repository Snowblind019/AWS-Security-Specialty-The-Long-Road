# Enforcing HTTPS on Amazon S3

## What It Is

Amazon S3 supports both **HTTP and HTTPS by default** — and it won’t stop users from accessing your bucket over unencrypted HTTP **unless you explicitly tell it to**.

So while you can securely connect to S3 via HTTPS, if you don't enforce it, someone using `http://s3.amazonaws.com/...` could be leaking your data across the public internet.

✔️ S3 is secure by design  
✖️ But insecure by default if you allow plaintext access

That’s where **HTTPS enforcement** comes in — and you control it through a simple **bucket policy**.

---

## Cybersecurity Analogy

S3 is like a **digital safe**.

You can access it via **secure keypad (HTTPS)** or via an **open flap anyone can reach into (HTTP)**.  
By default, the flap is open.  
**Enforcing HTTPS slams that flap shut** — only encrypted, authenticated requests make it through.

## Real-World Analogy

Imagine a front desk that accepts both **sealed envelopes (HTTPS)** and **postcards (HTTP)**.

- The sealed envelope ensures only the recipient can read it.  
- The postcard? Everyone in the mailroom sees it.  

**Enforcing HTTPS = “we only accept sealed envelopes from now on.”**

---

## How to Enforce HTTPS for S3

The golden solution is the `aws:SecureTransport` **bucket policy condition**.

### Step-by-Step Bucket Policy

```json
{
  "Version": "2012-10-17",
  "Id": "DenyInsecureRequests",
  "Statement": [
    {
      "Sid": "EnforceHTTPSOnly",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::snowy-secure-bucket",
        "arn:aws:s3:::snowy-secure-bucket/*"
      ],
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "false"
        }
      }
    }
  ]
}
```

- Denies all actions (`s3:*`)  
- Applies to all objects in the bucket  
- If request is not over HTTPS, it's automatically denied  

> This works for **SDKs, AWS CLI, signed URLs, applications, scripts**, etc.

---

## What Happens on Violation?

If someone tries:

```bash
curl http://s3.amazonaws.com/snowy-secure-bucket/myfile.txt
```

→ They get a **403 Access Denied**, and the request is **logged in CloudTrail** (if logging enabled).

---

## Other Ways to Enforce HTTPS

### 1. Use CloudFront (Recommended)

Put CloudFront in front of your S3 bucket:

- Set **Viewer Protocol Policy** to:
  - `Redirect HTTP to HTTPS` (for user experience) or  
  - `HTTPS Only` (for strict enforcement)
- Use **ACM certificates**
- Protect origin access with **Origin Access Control (OAC)**

- Adds CDN + HTTPS enforcement + WAF option  
- Obscures the raw S3 URL  
- Ideal for websites or public asset distribution

### 2. Signed URLs or Signed Cookies

- Generate pre-signed URLs using `https://` only  
- Set short expiration times (e.g. 15 minutes)  
- Use IAM roles or Lambda@Edge to create them  

- Ensures clients access over HTTPS only  
- Still needs `SecureTransport` policy to block other access

### 3. Block All Public Access (In Addition to HTTPS Enforcement)

Go to **S3 Console → Bucket → Permissions → Block Public Access**  
Enable **all 4 settings**

This is not directly related to HTTPS, but **complements encryption in transit** by preventing anonymous exposure.

---

## Common Mistakes

| Mistake                          | Why It's Dangerous                          |
|----------------------------------|----------------------------------------------|
| Not setting `aws:SecureTransport`| Allows plaintext access to sensitive data    |
| Relying on SDKs alone            | SDK defaults to HTTPS — but users can override |
| Using signed URLs with `http://` | Sends tokens and data in plaintext           |
| Allowing public S3 access without HTTPS | Anyone with a link can download over HTTP |
| Not monitoring 403s             | You won't know if someone tries to bypass HTTPS |

---

## Best Practices Summary

| Control                               | Purpose                                         |
|----------------------------------------|-------------------------------------------------|
| `aws:SecureTransport` bucket policy    | Blocks unencrypted access at the bucket level   |
| Use CloudFront + HTTPS-only viewer policy | Enforces encryption at the edge, adds CDN     |
| Use signed URLs with HTTPS             | Grants temporary, encrypted access              |
| Rotate access credentials used by clients | Prevent stale tokens being reused via HTTP   |
| Monitor CloudTrail + S3 Access Logs    | Catch any attempted insecure access             |

---

## Real-Life Example (Snowy’s File Upload Portal)

Snowy runs an upload portal backed by S3:

- Users upload photos and documents via mobile app  
- App uses **pre-signed HTTPS URLs** to PUT files into S3  
- The target bucket has this config:
  - `aws:SecureTransport = false` → ✖️ denied  
  - Public access completely blocked  
- Upload endpoint is fronted by **CloudFront**:
  - TLS 1.2 only  
  - HTTPS-only viewer policy  
  - Signed cookies for access to protected content

**Result:**

✔️ No one can upload/download over HTTP  
✔️ Every client interaction is encrypted in transit  
✔️ Attempted plaintext connections are rejected and logged

---

## Final Thoughts

**S3 is secure — if you make it so.**  
Out of the box, it’s just open enough to cause trouble:

- It’ll accept HTTP.  
- It’ll let users misconfigure clients.  
- And if you’re not enforcing HTTPS, someone eventually will go around it.

So slam that door shut.

- Use `aws:SecureTransport`  
- Use CloudFront with HTTPS-only policies  
- Use signed HTTPS URLs when needed  
- Monitor for anyone trying to sneak around it

> If your data is worth storing in S3, it’s worth protecting on the wire.
