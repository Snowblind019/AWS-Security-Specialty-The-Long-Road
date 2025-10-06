# HTTPS Enforcement For APIs

## What It Is

Any API exposed over the internet (or even internally!) must encrypt all traffic **in transit**. Otherwise, you're exposing:

- Credentials  
- Tokens (JWT, OAuth)  
- Query params  
- PII  
- Business logic  
- Responses  

Without HTTPS, all of it can be:
- **Sniffed** (on open Wi-Fi, compromised proxies, etc.)  
- **Modified** (MITM-injection)  
- **Replayed** (session hijacking)  

**HTTPS ≠ Optional**  
It’s your first line of defense for any client-to-API connection.

---

## Cybersecurity Analogy

Your API is a courier picking up and delivering sensitive information.

- With HTTP: he’s driving an open convertible shouting your data at traffic lights.  
- With HTTPS: he’s inside an **armored truck** with bulletproof glass and sealed doors.

---

## Real-World Analogy

Think of HTTPS as the **envelope** your message goes in.

Sending an API call over HTTP is like writing sensitive medical data on a **postcard** and mailing it.  
HTTPS is the **sealed envelope** that only the recipient can open — even if someone intercepts it, they see nothing.

---

## Where To Enforce HTTPS For APIs In AWS

| API Pattern               | Enforcement Method                                       |
|---------------------------|----------------------------------------------------------|
| API Gateway (REST/HTTP)   | HTTPS enforced by default                                |
| ALB-backed EC2 or ECS     | HTTPS listener + redirect from HTTP                      |
| CloudFront in front of API| Viewer & origin protocol policy                          |
| Raw EC2 API               | Install/manage certs manually                            |
| App Mesh / Service Mesh   | Use mTLS or TLS via sidecar proxy                        |

## 1. Amazon API Gateway

**HTTPS enforced by default** — listens only on port 443.

Still, you must secure:

- **Custom Domain Names**: Use ACM certs, enforce TLS 1.2+  
- **Signed URLs / API Keys / Tokens**:  
  - Always send over HTTPS  
  - Never leak in HTTP referrers or logs  

**Do not terminate TLS in front of API Gateway** and forward insecure traffic.

## 2. ALB-Backed APIs (ECS or EC2)

Very common: **ALB → public API → EC2/ECS**  

### How To Enforce HTTPS

- Create HTTPS Listener (port 443)  
- Attach ACM certificate  
- Set security policy to `ELBSecurityPolicy-TLS-1-2-Ext-2018-06` or newer  
- Add HTTP Listener (port 80) that redirects to HTTPS  

```bash
aws elbv2 modify-listener \
  --listener-arn ... \
  --default-actions Type=redirect,...
```

Now all API calls are forced over HTTPS with automatic redirect from HTTP.

## 3. CloudFront → API

If CloudFront fronts your API (caching, edge access):

- **Viewer Protocol Policy**:  
  - `Redirect HTTP to HTTPS` (usable)  
  - `HTTPS Only` (stricter)  
- **Client TLS Policy**: Enforce `TLSv1.2_2021` or newer  
- **Origin Protocol Policy**: `HTTPS Only`  

This ensures TLS from **client → edge → origin**

## 4. Raw EC2 API (No Load Balancer)

If exposing APIs directly from EC2:

- Install NGINX/Apache with valid certs  
- Use **Let’s Encrypt** or **ACM** (via ALB)  
- Configure app to:
  - Listen only on `https://`  
  - Redirect `http://` to HTTPS with 301  

> Avoid exposing APIs directly on EC2 unless absolutely necessary.

## 5. mTLS For Internal APIs (Advanced)

For internal microservice APIs, enforce **mutual TLS (mTLS)**:

- Use NGINX or Envoy **sidecars**  
- Validate client certs  
- Rotate certs using **ACM PCA** or **SPIRE/SDS**

This gives you **zero-trust-level identity enforcement** on internal service calls.

---

## Common Pitfalls

| Mistake                        | Why It’s Risky                              |
|-------------------------------|---------------------------------------------|
| ALB listener is HTTP-only      | Entire API exposed in plaintext             |
| Forgot to redirect port 80     | Users may still use HTTP                    |
| CloudFront viewer = `AllowAll` | Allows downgrade + MITM                     |
| No TLS at origin               | CloudFront → API traffic is unencrypted     |
| Self-signed certs unpinned     | Breaks trust model — vulnerable to spoofing |

---

## Best Practices Summary

| Control                        | Purpose                                     |
|-------------------------------|---------------------------------------------|
| HTTPS-only listener / protocol| Prevents plaintext API exposure             |
| TLS 1.2+ security policy       | Strong ciphers, forward secrecy             |
| ACM certificate management     | Auto-rotating trusted certs                 |
| Redirect HTTP to HTTPS (301)  | Seamless enforcement without breakage       |
| mTLS for internal APIs         | Authenticate caller identity over TLS       |
| CloudWatch logs / metrics      | Detect failed TLS handshakes, downgrade attempts |

---

## Real-Life Example (Snowy’s Auth API)

Snowy deploys an ECS service behind ALB:

- HTTPS Listener only  
- ACM cert with TLS 1.2 policy  
- HTTP listener redirects to HTTPS  
- Internal service-to-service calls use **mTLS** via NGINX  
- CloudFront caches `/public/*` paths with **HTTPS-only** viewer policy  

### Result:

- End-users can only hit the API via HTTPS  
- All tokens/PII are protected in transit  
- Admins get alerts if a TLS negotiation fails  
- Even **inside the VPC**, traffic is authenticated and encrypted

---

## Final Thoughts

APIs are the **front doors** to your business logic — and if those doors allow HTTP, you're leaving your app, users, and data wide open.

Enforcing HTTPS for APIs isn't just about privacy — it’s about **integrity**, **identity**, **trust**, and **compliance**.

Whether you're using **API Gateway**, **ALB**, **CloudFront**, or **raw EC2** —  
**encrypt every byte**, from **edge to origin**.
