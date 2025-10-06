# TLS 1.2+

## What Is TLS (and Why 1.2+ Matters)

**TLS (Transport Layer Security)** is the protocol that encrypts data in **transit** — securing everything from HTTPS websites to secure APIs, RDS connections, and email relays.

It:

- Encrypts your data on the wire
- Authenticates endpoints via certificates
- Detects tampering and **MITM** attempts

But here's the catch:
There are multiple versions of **TLS** — and **only TLS 1.2 and TLS 1.3** are secure by today’s standards.

| Version  | Status        | Notes                                      |
|----------|---------------|--------------------------------------------|
| **TLS** 1.0 | ✖️ Deprecated | Vulnerable to POODLE, BEAST, etc.          |
| **TLS** 1.1 | ✖️ Deprecated | Weak ciphers, no longer supported          |
| **TLS** 1.2 | ✔️ Secure     | Widely used, strong ciphers                |
| **TLS** 1.3 | ✔️ Most Secure| Faster handshake, perfect forward secrecy |

---

## How to Enforce **TLS 1.2+** in AWS

**CloudFront (CDN)**

```plaintext
ViewerProtocolPolicy: https-only
MinimumProtocolVersion: TLSv1.2_2021
```

- Use custom **SSL** with **ACM**
- Use **Security Policy** to enforce **TLS** version and cipher suite
- Redirect **HTTP to HTTPS** at viewer level

**ALB (Application Load Balancer)**

- Choose HTTPS Listener
- Set security policy to one of:
  - `ELBSecurityPolicy-TLS-1-2-2017-01`
  - `ELBSecurityPolicy-TLS-1-2-Ext-2018-06`
  - Or `ELBSecurityPolicy-TLS-1-3-2021-06` for **TLS 1.3** support

```bash
aws elbv2 modify-listener \
  --listener-arn arn:... \
  --protocol HTTPS \
  --ssl-policy ELBSecurityPolicy-TLS-1-2-Ext-2018-06
```

**S3 — Deny Unencrypted Requests**

```json
"Condition": {
  "Bool": {
    "aws:SecureTransport": "false"
  }
}
```

- This blocks any **non-TLS** S3 request
- Works across AWS **CLI**, **SDKs**, third-party tools

**RDS**

- Enable `require_ssl` or `rds.force_ssl=1` in DB parameter group
- Use **SSL** connection strings (e.g., `?sslmode=require`)
- Enforce client certs if needed (for **mTLS**)

**API Gateway**

- **TLS 1.2 is enforced by default** — you can’t downgrade it
- Attach custom domain and **ACM** cert for public APIs

---

## Common TLS Mistakes in AWS

| Mistake                          | Consequence                                  |
|----------------------------------|----------------------------------------------|
| Allowing **TLS 1.0/1.1** in ALB | Weak encryption; non-compliance              |
| Not setting `aws:SecureTransport` | Allows plaintext access to S3               |
| No cert rotation for EC2 apps   | Expired certs → outages, insecure fallback   |
| Not validating certs in **SDKs** | Opens door to **MITM** even with **TLS**     |
| Misconfigured cipher suites     | Prevents modern clients from connecting      |

---

## Best Practices Summary

| Recommendation                              | Why It Matters                              |
|---------------------------------------------|----------------------------------------------|
| Enforce **TLS 1.2 or 1.3** on all endpoints | Avoid legacy downgrade attacks              |
| Use **ACM certificates**                   | Simplifies management, auto-renew           |
| Use **Security Policies** on ALB/CF        | Controls cipher suite + **TLS** version     |
| Block **non-TLS** with S3 bucket policy    | Prevents API access over HTTP               |
| Monitor **TLS** connections with **CloudWatch** | Detect **TLS** errors or downgrade attempts |
| Validate **TLS** in all client **SDKs**    | Ensures traffic is actually encrypted       |

---

## Real-Life Example (Winterday’s FinTech App)

**Winterday’s** API is hosted behind:

**CloudFront → ALB → EC2**

They configure:

- **CloudFront** to use `TLSv1.2_2021` only
- **ALB** with `ELBSecurityPolicy-TLS-1-2-Ext-2018-06`
- **S3** bucket with `aws:SecureTransport` policy
- **RDS** with **SSL** required and PostgreSQL cert validation
- All clients use **SDKs** that enforce **TLS 1.2**

**CloudWatch** alarms trigger if:

- A **TLS** negotiation fails
- **S3** denies a plaintext request
- **ACM** cert renewal fails

This ensure:
✔️ Compliance with **PCI DSS**
✔️ **TLS 1.0/1.1** completely blocked
✔️ Everything encrypted, monitored, and policy-enforced

---

## Final Thoughts

**TLS is the backbone of encryption in transit.**
And in the cloud, that means **TLS 1.2 is the baseline** — and **TLS 1.3 is the future**.

If you’re still accepting **TLS 1.0 or 1.1**, you’re inviting:

- Compliance violations (**PCI**, **HIPAA**, **NIST**)
- Downgrade attacks
- Insecure connections in your most exposed layer

**Enforce TLS at every edge.**
Rotate certs.
Use strong ciphers.
Monitor for failures.

Because plaintext belongs in history books — not production systems.
