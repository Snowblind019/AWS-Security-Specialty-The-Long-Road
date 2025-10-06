# Enforcing HTTPS on Amazon CloudFront

## What It Is

CloudFront is AWS’s global CDN and edge distribution layer. When users hit your site — whether that’s a static app, dynamic API, or a signed download — CloudFront is the first thing they touch.

And by default?

- It accepts both HTTP and HTTPS traffic  
- It allows you to choose what TLS version and cipher suites to support  
- It can connect to origins over HTTP or HTTPS (not enforced unless configured)

So unless you explicitly configure HTTPS-only at every layer, you might unknowingly be:

- Accepting plaintext requests from clients  
- Allowing downgrade attacks  
- Connecting from **CloudFront → origin** without encryption

---

## Cybersecurity Analogy

Think of CloudFront like a **concierge for your cloud castle**.

- **HTTPS** = verified guest with badge, secure radio, and voice authentication  
- **HTTP** = someone yelling instructions across the courtyard hoping to be heard correctly

> Without HTTPS enforcement, anyone can yell at your CDN and hope it relays the message — even if malicious.

## Real-World Analogy

Imagine your storefront takes orders by phone.

- With **HTTPS**, every order is whispered securely over an encrypted phone line  
- With **HTTP**, it’s shouted across a crowded room  

You don’t just want *some* customers using secure lines — you want **all of them required to**.

---

## Where and How HTTPS Can Be Enforced in CloudFront

### 1. Viewer Protocol Policy (Client → CloudFront)

This controls how users connect to CloudFront.

| Option              | Description                                          |
|---------------------|------------------------------------------------------|
| Allow All           | Accepts both HTTP and HTTPS                         |
| Redirect HTTP to HTTPS | Redirects all HTTP to HTTPS (recommended for websites) |
| HTTPS Only          | Rejects all HTTP traffic (403) (recommended for APIs) |

> This setting is per-cache behavior (per path/pattern), so you can enforce different rules per route.

---

### 2. TLS Security Policy (TLS Version + Ciphers)

This controls which TLS versions and cipher suites are allowed when clients use HTTPS.

| TLS Policy Name     | TLS Min Version | Notes                       |
|---------------------|------------------|------------------------------|
| TLSv1.2_2021        | TLS 1.2          | Strongest recommended policy |
| TLSv1.2_2019        | TLS 1.2          | Still solid, but less strict |
| TLSv1.1_2016        | TLS 1.1          | Deprecated — avoid           |
| TLSv1_2016          | TLS 1.0          | ❌ Legacy — do not use        |

> For PCI DSS and modern compliance: use **TLSv1.2_2021** or later.

---

### 3. Origin Protocol Policy (CloudFront → Origin)

This controls how CloudFront communicates with your origin (e.g., S3, ALB, EC2).

| Option          | Description                                  |
|------------------|----------------------------------------------|
| HTTP Only        | ❌ Insecure — avoid                          |
| Match Viewer     | Mirrors the client's protocol               |
| HTTPS Only       | ✅ Enforces secure communication to origin  |

> If your origin (like S3) supports HTTP, CloudFront will happily use it unless you stop it.

---

## How to Configure HTTPS Enforcement in CloudFront

### Step-by-Step (for a Secure Setup)

**Set Viewer Protocol Policy to Redirect HTTP to HTTPS or HTTPS Only**

```yaml
DefaultCacheBehavior:
  ViewerProtocolPolicy: "redirect-to-https"
```

**Choose a Secure TLS Policy**

```yaml
ViewerCertificate:
  SslSupportMethod: "sni-only"
  MinimumProtocolVersion: "TLSv1.2_2021"
```

**Use an ACM Certificate**

- Must be in `us-east-1` for CloudFront  
- Attach to the distribution’s `ViewerCertificate`

**Set Origin Protocol Policy to HTTPS Only**

```yaml
Origins:
  - DomainName: "myapp.s3.amazonaws.com"
    CustomOriginConfig:
      OriginProtocolPolicy: "https-only"
```

> For **S3**, use **Origin Access Control (OAC)** + HTTPS origin  
> For **ALB/EC2**, use valid cert on backend or terminate at ALB

---

### Optional: Lambda@Edge Enforcement (For Signed URLs)

If someone tries using HTTP in a signed URL, Lambda@Edge can deny it with a `403`:

```js
if (request.headers['cloudfront-forwarded-proto'][0].value !== 'https') {
  return {
    status: '403',
    statusDescription: 'HTTPS Required',
    body: 'Only HTTPS allowed.'
  };
}
```

> Use for ultra-strict security scenarios or signed URL enforcement

---

## Common Pitfalls

| Mistake                         | Why It’s Risky                                  |
|----------------------------------|--------------------------------------------------|
| Viewer Protocol = “Allow All”    | Allows plaintext HTTP → MITM and downgrade       |
| Origin Protocol = “Match Viewer”| Can connect over HTTP if client does — insecure |
| TLS policy too loose (TLSv1.0)  | Outdated, non-compliant                          |
| No cert rotation                | May cause downtime or insecure fallback          |
| Forgetting to update cache behaviors | Paths like `/api/*` may default to HTTP allowed |

---

## Best Practices Summary

| Control                  | Why It Matters                                      |
|--------------------------|------------------------------------------------------|
| Viewer Protocol: HTTPS Only / Redirect | Prevents plaintext access at the edge       |
| TLS Policy: TLSv1.2_2021 or newer      | Enforces modern, strong encryption standards |
| Origin Protocol: HTTPS Only            | Prevents CloudFront from using HTTP to origin|
| Use ACM Certificates                   | Simplifies TLS at scale, auto-renews         |
| Monitor TLS errors (CloudWatch, Logs)  | Catch failures or downgrade attempts         |
| Use OAC for S3 origins                 | Prevents direct access, secures origin path  |

---

## Real-Life Example (Snowy’s Static Site)

Snowy’s static app is served via CloudFront:

- **Viewer Protocol Policy**: Redirect HTTP to HTTPS  
- **TLS Policy**: TLSv1.2_2021  
- **ACM cert** for `www.snowysec.com`  
- **S3 origin** behind **Origin Access Control (OAC)**  
- **Origin Protocol Policy**: HTTPS Only  
- **CloudWatch metrics** for TLS handshake failures  
- **Lambda@Edge** for signed URL validation  

**Result:**

✔️ All client traffic is encrypted  
✔️ No HTTP downgrade allowed  
✔️ Edge-to-origin encryption enforced  
✔️ Compliant with PCI DSS + best practices

---

## Final Thoughts

CloudFront is your **edge layer**, your **front door**, your **TLS terminator** — and if you don’t enforce HTTPS here, everything downstream loses integrity.

- Encrypt the viewer connection  
- Encrypt the origin connection  
- Enforce TLS 1.2+  
- Use ACM and secure policies  
- Catch anything weird with CloudWatch + logs  

> If you control CloudFront, you control the wire. Use that power wisely.
