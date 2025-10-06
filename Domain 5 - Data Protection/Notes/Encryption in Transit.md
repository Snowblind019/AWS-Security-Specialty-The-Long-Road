# Encryption in Transit in AWS

## What Is Encryption in Transit 

Encryption in transit ensures that any data moving between systems, services, or users is protected from eavesdropping, tampering, or man-in-the-middle attacks.

In AWS, this is achieved primarily through **TLS (Transport Layer Security)** — the industry-standard protocol for securing data in motion. TLS is used:

- **For external communication**: between users and AWS (like HTTPS, ALB, CloudFront)  
- **For internal communication**: between AWS services, inside VPCs, and across regions (like App Mesh, PrivateLink, inter-service APIs)

**Why it matters:**

- Protects credentials, tokens, PII, and business data  
- Required by most compliance frameworks: NIST 800-53, HIPAA, PCI-DSS, CIS Benchmarks  
- Shields against packet sniffing, DNS poisoning, and TLS downgrade attacks  

> It’s not enough to encrypt storage. You must encrypt the journey, too.

---

## Cybersecurity Analogy

Imagine data is like a sealed envelope.  
Encryption at rest is locking it in a vault.  
Encryption in transit is sealing the envelope and using an armored vehicle with a security escort during delivery.

Without it, someone could:

- Open the envelope mid-transit  
- Swap it with a fake  
- Read it silently and reseal it  

**TLS ensures nobody sees or tampers with the envelope while it moves.**

## Real-World Analogy

Think of credit card processing. When you swipe your card:

- It leaves your phone or card reader  
- Travels through the internet  
- Hits a bank, a processor, and maybe another service  

If that journey isn’t encrypted, **anyone on the path can steal it.**  
**TLS** is the equivalent of **bank-grade armored tunnels** between every point.

---

## How AWS Enforces Encryption in Transit

AWS provides TLS-based encryption across all layers — from external user requests to internal service-to-service APIs.

### 1. Elastic Load Balancing (ALB / NLB / Classic ELB)

- ALBs and NLBs support **HTTPS listeners** and enforce TLS with configurable security policies  
- Example TLS policy: `ELBSecurityPolicy-TLS13-2021-06`  
  - Enforces TLS 1.3  
  - Removes old ciphers and protocols  
  - Blocks known downgrade vectors (e.g., POODLE, BEAST)  

You can enforce:

- Minimum protocol version  
- Specific cipher suites  
- Client certificate verification (for **mTLS**)

### 2. CloudFront

- CDN that **terminates TLS at edge locations**  
- Supports custom TLS policies, client certificate validation  
- Allows you to serve HTTPS-only content  
- Integrates with **ACM** for free certs

### 3. Application Load Balancer (ALB)

- Layer 7 (HTTP/HTTPS) TLS termination  
- Can use **SNI (Server Name Indication)** for hosting multiple certs  
- Supports **mTLS** with client authentication via trust stores

### 4. App Mesh

- AWS service mesh that encrypts **service-to-service traffic** with mTLS  
- Uses **Envoy sidecars** to enforce TLS for all east-west traffic  
- Strong fit for **zero trust architectures and microservices**  
- TLS is configured via **Mesh policies**, not per app

### 5. Amazon S3

- Access via **HTTPS endpoints only**  
- Bucket policies can require `aws:SecureTransport == true`  
Example:

```json
"Condition": {
  "Bool": { "aws:SecureTransport": "false" }
}
```

→ Deny unencrypted (HTTP) requests

### 6. RDS, Redshift, DynamoDB

- All support **TLS for database connections**  
- You must **download the region-specific CA cert** and enforce encryption on the client side  
- Some services (like Aurora) let you require TLS for all users  

PostgreSQL example:  
`sslmode=require`

### 7. PrivateLink

- Creates private endpoints in your VPC that connect securely to AWS services  
- Encrypts traffic using **TLS over AWS’s backbone**  
- Used heavily for **internal service communication**  
- Helps meet compliance and network segmentation goals

---

## TLS Certificate Management: ACM vs BYOC

You need certificates to enable TLS. You have two options:

| Feature              | ACM (AWS Certificate Manager) | Bring Your Own Certificate (BYOC) |
|----------------------|-------------------------------|-----------------------------------|
| **Automation**        | ✔️ Fully managed              | ✖️ Manual renewals                |
| **Cost**              | ✔️ Free public certs          | ✖️ Must buy/manage certs          |
| **Expiration handling**| ✔️ Auto-rotation              | ✖️ You monitor & renew manually   |
| **Integration**       | Works with ALB, CloudFront, API GW | Works with any TLS listener   |
| **Custom CAs / mTLS** | ✖️ Not supported              | ✔️ Needed for mTLS                |

If you control a private CA or require **mTLS (mutual TLS)**, you usually bring your own cert.

---

## TLS Policies (Example: ELBSecurityPolicy-TLS13-2021-06)

You can choose predefined security policies for ELBs:

| Policy Name                    | Protocols | Cipher Suites  | Minimum TLS | Forward Secrecy |
|--------------------------------|-----------|----------------|--------------|------------------|
| ELBSecurityPolicy-TLS13-2021-06 | TLS 1.3   | modern only    | TLS 1.2/1.3 | ✔️ Yes           |
| ELBSecurityPolicy-2016-08      | TLS 1.0+  | legacy included| TLS 1.0     | ✖️ Weak          |

> **Best practice:** use the most restrictive supported policy unless you have legacy needs.

---

## Mutual TLS (mTLS)

For services like **ALB**, **API Gateway**, and **App Mesh**, AWS supports **mutual TLS**, where both:

- The client presents a certificate  
- The server verifies it before establishing connection

This provides strong authentication and is used in:

- Internal service APIs  
- Machine-to-machine authentication  
- Zero trust environments

---

## Best Practices Across AWS

- Use HTTPS everywhere — enforce `aws:SecureTransport`  
- Choose strong TLS policies — TLS 1.2 minimum, ideally TLS 1.3  
- Monitor cert expiry — automate with ACM or alert on BYOC expiry  
- Use PrivateLink and mTLS for sensitive internal services  
- Enforce TLS in database clients — don't rely on defaults

---

## Real-Life Example: Snowy Internal Billing API

Let’s say Snowy’s internal billing API lives on a private VPC and uses:

- API Gateway for request routing  
- PrivateLink for internal access  
- ACM certificates for TLS  
- Client certificate validation to require **mTLS**  
- DynamoDB for storage (`tls=true` on all DB clients)

This stack ensures:

- All communication is encrypted at every hop  
- Unauthorized services are blocked even within the VPC  
- Certs are auto-rotated via ACM  
- Snowy’s devs can focus on features — not building crypto workflows from scratch

---

## Final Thoughts

**Encryption in Transit is no longer optional — it’s baseline hygiene.**  
Whether you're building public APIs, internal service meshes, or DR architectures, AWS gives you all the tools to enforce **TLS Everywhere**.

But:

- You must configure it — defaults aren’t always strict  
- Audit and test TLS endpoints regularly  
- Pair it with encryption at rest for full-stack data security  

In security reviews and interviews, expect to be asked:

> “How do you ensure encryption in transit across your AWS services?”

Now you can answer with:

- TLS at edge (CloudFront, ALB)  
- TLS internally (App Mesh, PrivateLink, mTLS)  
- TLS to data (S3, RDS, DynamoDB)  
- Strict policies and automation
