# Data-in-Transit Encryption: Client to S3

## What It Is

Whenever users — whether human or machine — interact with your S3 buckets over the internet, they’re transmitting sensitive data across untrusted networks.

- A customer uploads a photo  
- A mobile app pulls a config file  
- A script downloads a CSV  
- A partner system pushes backups via the AWS CLI  

These interactions hit S3 over HTTP or HTTPS.  
And while S3 supports TLS out of the box, it doesn’t enforce it by default.

**Your job as a security engineer is to enforce and monitor TLS at every layer — or risk leaking data in transit.**

---

## Cybersecurity Analogy

Imagine someone mails you a check. They can:

- Seal it in an envelope (TLS)  
- Or send it as a postcard anyone can read (HTTP)  

**Would you trust an open postcard for banking?**  
That’s what happens when you let clients connect to S3 over HTTP — anyone in between (ISPs, proxies, compromised routers) can intercept or tamper with the data.

## Real-World Analogy

Think of S3 as a secure digital filing cabinet.

- If users access it over HTTPS, they’re opening the drawer with a private, encrypted handshake.  
- If they use HTTP, they’re shouting their file contents to the whole office before filing them.  

Even though S3 has locks (IAM, policies), an insecure path to the cabinet undermines everything.

---

## Typical Paths to S3 From a Client

| **Method**                  | **TLS Enforced?**    | **Notes**                                                |
|-----------------------------|----------------------|-----------------------------------------------------------|
| Direct HTTPS to S3 URL      | Optional         | Works by default, but HTTP also allowed unless blocked   |
| AWS SDK/CLI                 | ✔️ Yes              | Always uses HTTPS unless you force it otherwise          |
| CloudFront CDN              | ✔️ Yes (configurable)| You choose TLS settings, enforce HTTPS                   |
| Signed S3 URL               | ✔️ Yes              | Signed with HTTPS by default (optional headers)          |
| Web App (e.g., form upload) | Optional         | Must enforce HTTPS on the client/app                     |

---

## How to Enforce TLS from Client to S3

### 1. S3 Bucket Policy: Enforce `aws:SecureTransport`

You can deny any request made without HTTPS using this policy:

```(json)
{
  "Version": "2012-10-17",
  "Id": "EnforceTLSOnly",
  "Statement": [
    {
      "Sid": "AllowOnlySecureTransport",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::snowy-private-bucket",
        "arn:aws:s3:::snowy-private-bucket/*"
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

- Blocks any insecure HTTP calls  
  - Works globally across all SDKs, tools, scripts  
  - Requires no client changes

### 2. Always Use HTTPS in Signed URLs

If you generate pre-signed URLs (e.g., `s3.amazonaws.com/snowy-bucket/...`), ensure:

- The URL uses `https://` not `http://`  
- You add signed headers that enforce HTTPS-only usage  
- You set short expiration times (5–15 mins) to reduce replay risk  
Avoid exposing raw S3 URLs. Use CloudFront signed URLs instead when possible.

### 3. CloudFront in Front of S3: TLS at the Edge

If clients access your S3 buckets through CloudFront:

- Set the **Viewer Protocol Policy** to:  
  - Redirect HTTP to HTTPS  
  - Or HTTPS Only  
- Choose TLSv1.2 or higher in Security Policy  
- Use an ACM-issued certificate for your domain (`assets.snowycorp.com`)  

Now your users are always encrypted at the edge  
Origin (CloudFront → S3) must be TLS as well

### 4. Ensure HTTPS in Mobile/Web Clients

In apps, SDKs, and frontends:

- Never hardcode `http://` S3 URLs  
- Use `https://s3.amazonaws.com/bucket/...`  
- Or use signed HTTPS URLs from backend  
- Validate that SDKs (React Native, Flutter, etc.) default to HTTPS  

Many breaches happen because a mobile dev just copy-pasted an HTTP link that worked in dev.

---

## Common Pitfalls

| **Mistake**                          | **Impact**                                  |
|--------------------------------------|----------------------------------------------|
| Allowing HTTP access to S3           | Data in transit is unencrypted               |
| No `aws:SecureTransport` policy      | Insecure access silently allowed             |
| Using pre-signed URLs over HTTP      | Leaks data, enables MITM attacks             |
| Letting CloudFront allow HTTP        | Mixed content warnings, downgrade attacks    |
| Users copy-pasting raw S3 links      | Can bypass TLS if not carefully wrapped      |

---

## Best Practices Summary

| **Control**                             | **Why It Matters**                                |
|----------------------------------------|---------------------------------------------------|
| S3 Policy: Deny non-TLS (`SecureTransport`) | Prevents unencrypted calls at the root       |
| CloudFront: HTTPS Only / TLS 1.2       | Protects at CDN layer                             |
| ACM certs + custom domain              | Keeps encryption AND branding unified             |
| Short-lived signed URLs (HTTPS)        | Reduces attack surface for token hijacking        |
| Client-side: enforce HTTPS endpoints   | Ensures apps never talk to S3 in plaintext        |
| Monitor with CloudTrail or VPC Flow Logs | Catch accidental HTTP calls                     |

---

## Real-Life Example (SnowySec Downloads)

Snowy runs a static content hosting setup:

- Docs and assets stored in S3 (`snowy-static`)  
- Served globally via CloudFront (`docs.snowysec.com`)  
- Pre-signed URLs generated for private files  
- TLS 1.2+ enforced on CloudFront and origin  
- `aws:SecureTransport` policy applied to the bucket  
- CloudWatch Alarms on any 403 due to insecure transport  

**Result:**

✔️ Clients always talk over HTTPS  
✔️ Any HTTP attempt is denied at policy level  
✔️ URLs auto-expire  
✔️ No downgrade paths, no replay windows

---

## Final Thoughts

**Data in transit is often the weakest link** — especially when developers assume “S3 is secure” by default.

Yes, S3 supports TLS.  
But you have to enforce it at every layer: **bucket policy, app logic, signed URLs, and edge configuration.**

If you don't, you leave the door open for:

- MITM attacks  
- Token sniffing  
- Stolen files in transit  
- Regulatory non-compliance  

**Encrypt everything — always. Especially when users are on the other end.**
