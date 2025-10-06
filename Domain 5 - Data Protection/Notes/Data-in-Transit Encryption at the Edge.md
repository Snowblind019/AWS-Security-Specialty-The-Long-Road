# Data-in-Transit Encryption at the Edge

## What Is Data-in-Transit Encryption (Public/Edge)

When your users connect to your app or API over the public internet — through **CloudFront**, **API Gateway**, **Load Balancers**, or **Route 53** — you need to protect that traffic from eavesdropping, tampering, or MITM (Man-in-the-Middle) attacks.

That’s where data-in-transit encryption comes in — encrypting traffic as it flows over the network between:

- Client ↔ CDN (e.g., CloudFront)  
- Client ↔ ALB / NLB / API Gateway  
- CDN ↔ Origin servers (your S3, ALB, EC2, etc.)

**TLS (Transport Layer Security)** is the standard — and AWS gives you tools to enforce, inspect, terminate, and propagate it all the way from edge → origin.

---
## Cybersecurity and Real-World Analogy

### Cybersecurity Analogy

Imagine your public website is like a storefront, and your customers are yelling credit card numbers over a megaphone (HTTP).  
Anyone walking by can hear.

**TLS is like switching to a whisper in a secure soundproof room (HTTPS).**  
Even if someone’s standing outside with a stethoscope, they can’t decode what’s being said.

And at scale — with CDNs, global DNS, load balancers — the room gets bigger.  
So encryption must extend from customer to edge to origin.

### Real-World Analogy

You’re sending private mail through a long chain of couriers.

- No encryption: anyone handling it can read it.  
- TLS at edge only: courier 1 sees it encrypted, courier 2 (origin) gets it in plaintext.  
- TLS end-to-end: the message is sealed, and only your recipient can open it — even if couriers are compromised.

**That’s why TLS everywhere matters — not just on the edge.**

---

## What Services Are Involved?

| Service             | Role in Edge/Internet Exposure     | TLS Role                             |
|---------------------|-------------------------------------|---------------------------------------|
| CloudFront          | Global CDN — first point of contact| Terminates TLS from client           |
| ALB / NLB           | Load balancing into VPC            | Can terminate or pass TLS            |
| API Gateway         | Public APIs                        | TLS termination enforced             |
| S3 (static hosting) | Static sites behind CloudFront     | Origin encryption optional           |
| Route 53            | DNS resolver                       | Points to HTTPS endpoints            |
| Certificate Manager | TLS certificate provisioning       | Central to managing secure comms     |

---

## How AWS Handles TLS at the Edge

### TLS 1.2+ Everywhere

AWS strongly recommends using **TLS 1.2 or 1.3**.  
TLS 1.0 and 1.1 are deprecated and should be disabled via security policies (e.g., CloudFront, API Gateway settings).

### CloudFront (CDN)

CloudFront **terminates TLS at edge locations worldwide**. You can:

- Use ACM-issued certs (free, auto-renewed)  
- Enforce minimum protocol version (TLS 1.2)  
- Set custom cipher suites  
- Use HTTPS-only viewer protocols  

**Encrypts: Client ↔ Edge**  
**Optional: Edge ↔ Origin encryption (HTTPS origin)**  
> You must explicitly configure CloudFront to use HTTPS when calling your S3/ALB/EC2 origin.

### Application Load Balancer (ALB)

- Supports **HTTPS listeners** with ACM or imported certs  
- Can **terminate TLS** (client-side encryption ends here)  
- Can **forward unencrypted traffic to backend**, or:  
- **Re-encrypt to origin** for full end-to-end TLS  

**Use HTTPS → HTTPS from client all the way to target group**  
**Set ALB to reject HTTP or redirect to HTTPS**

### API Gateway

- **Enforces HTTPS by default** — no HTTP fallback  
- Uses AWS-managed certificates  
- Supports custom domains with ACM certs  
- No option to allow insecure protocols  

**Client ↔ Gateway: Encrypted**  
**Backend ↔ Lambda/HTTP Integration: You control encryption**

### S3 (Static Site Behind CloudFront)
```python
  "Bool": { "aws:SecureTransport": "false" }
}
```
This blocks all unencrypted S3 access at the policy level.

---

## Certificate Management with ACM

| Feature                  | ACM (AWS Certificate Manager)                       |
|--------------------------|-----------------------------------------------------|
| Auto-issued certs         | For use with CloudFront, ALB, API Gateway           |
| Free, auto-renewing       | No cost or manual rotation headaches                |

| Regional + global         | Use regional certs for ALB; global for CloudFront   |
| Private CA integration    | For internal-only TLS                              |

**Best practice:** Use ACM for all public certs — reduces attack surface from manual cert handling.

---

## Best Practices Summary

| Practice                        | Why It Matters                                   |
|---------------------------------|--------------------------------------------------|
| Enforce TLS 1.2+                | Old versions have known vulnerabilities          |
| Use HTTPS-only viewer policies  | Prevent downgrade to HTTP (CloudFront, ALB)      |
| Configure origin to use HTTPS   | TLS from edge to backend is not automatic        |

| Use ACM for certs               | Easy management and auto-renewal                 |
| Add S3 `aws:SecureTransport`    | Prevent insecure API calls to buckets            |

| Redirect HTTP to HTTPS at ALB   | Avoid mixed-content problems                     |
| Use custom domain with API GW   | Control certs, branding, and security policies   |

| Monitor TLS usage in CloudWatch | Detect downgraded or failed handshakes           |

---

## Real-Life Example (Blizzard's Website)


Blizzard is hosting a global SaaS dashboard:

- Uses CloudFront as CDN  
- Static content from S3  
- Backend APIs behind API Gateway  
- Admin login behind ALB → EC2 App  

He implements:

- TLS 1.2 minimum at CloudFront + HTTPS-only viewer protocol  
- S3 bucket policy that blocks any request without SecureTransport  
- ALB set to redirect HTTP → HTTPS  
- ACM certs on CloudFront, ALB, and API Gateway  
- Daily CloudWatch metric filter on TLSNegotiationError  

Now, even if someone spoofs DNS or sniffs packets, they get nothing but encrypted TLS streams.  
And if a teammate tries to expose something over HTTP?

✔️ Blocked at policy level.  
✔️ Caught by drift detection.  
✔️ Alerted in Slack via CloudWatch.

---

## Final Thoughts

Data-in-transit encryption at the edge is your first security barrier — it protects your users from the noisy, dangerous public internet.

But just terminating TLS at the edge isn’t enough.  
To be truly secure, you must enforce end-to-end TLS:
- Internal services → downstream microservices  

Don’t leave it half-encrypted. Encrypt everything from start to finish.

Because in the cloud — the wire is public, the DNS is global, and the weakest link is usually the default setting someone forgot to change.

- Client → CloudFront  
- CloudFront → ALB/S3/API  

