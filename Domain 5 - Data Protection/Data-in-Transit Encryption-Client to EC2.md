# Data-in-Transit Encryption: Client to EC2

## What It Is

If users or systems connect to your EC2 instances, that traffic moves across the public internet. That means it’s vulnerable to eavesdropping, MITM attacks, traffic injection, and session hijacking — **unless it’s encrypted**.

This includes:

- Web clients talking to a server on EC2 (`https://yourapp.com`)  
- Mobile apps calling a REST API hosted on EC2  
- Admins connecting via SSH  
- Partners pushing files via SFTP, RDP, or custom protocols  

Unless you explicitly wrap these connections in TLS, the data is readable in transit — including passwords, session tokens, PII, images, API keys, or SQL queries.  
AWS gives you tools — **but you must build the encryption path**.

---

## Cybersecurity Analogy

Think of EC2 like your house, and public users are talking to it through the windows.

- HTTP is like leaving the window open — anyone outside can hear  
- HTTPS (TLS) is like soundproofing the window and giving each guest a secure intercom line  
- SSH is a secure tunnel with a secret knock — but still needs protection  

**Data in transit is the sound — and it should always be encrypted, authenticated, and tamper-proof.**

## Real-World Analogy

You run a doctor’s office, and you take calls from patients.

- Unencrypted lines (HTTP): anyone can listen in from the hallway  
- Encrypted lines (HTTPS, SSH): the conversation is private, authenticated, and protected from tampering  

If your EC2 instance is handling sensitive or regulated data, **encrypting the communication isn't optional — it's non-negotiable.**

---

## How Clients Connect to EC2

| **Method**                 | **Encrypted by Default?** | **Protocol**           |
|---------------------------|----------------------------|------------------------|
| Web app via HTTP          | ✖️ No                      | Port 80 (plaintext)    |
| Web app via HTTPS         | ✔️ Yes                     | Port 443 (TLS)         |
| ALB forwarding to EC2     | ✖️ Optional                | Depends on listener    |
| CloudFront → ALB → EC2    | ✔️ Configurable            | TLS at each layer      |
| SSH (from admin)          | ✔️ Yes                     | Port 22 (OpenSSH)      |
| RDP (Windows Admin)       | ✔️ Yes                     | Port 3389 (TLS-based)  |
| Custom app (e.g. TCP/UDP) | ✖️ Usually No              | You must build TLS in  |

---

## How to Secure Client-to-EC2 Connections

### 1. Use TLS (HTTPS) for All Web Traffic

If you’re serving websites, APIs, or mobile backends from EC2:

- Install valid TLS certificates (via Let’s Encrypt, ACM, or others)  
- Enforce HTTPS only  
- Redirect HTTP → HTTPS at app level or via reverse proxy (e.g., NGINX, Apache)  

**Best Practice**: Terminate TLS at ALB or CloudFront, not directly on EC2 if possible

### 2. Terminate TLS at ALB or CloudFront (Recommended)

Let Application Load Balancer (ALB) or CloudFront handle TLS termination:

- Attach an ACM certificate  
- Enforce TLS 1.2+  
- Set Viewer Protocol Policy to HTTPS-only  

You can choose:

- HTTPS → HTTP to EC2 _(not ideal)_  
- HTTPS → HTTPS to EC2 _(best for end-to-end encryption)_  

✔️ Simplifies cert management  
✔️ Offloads encryption overhead  
✔️ Works with WAF, Shield, etc.

### 3. Encrypt SSH / RDP Admin Access

- Use SSH key pairs instead of passwords  
- Store private key in Secrets Manager, not on disk  
- Restrict SSH access via Security Group (e.g., office IP only)  
- Consider SSM Session Manager for encrypted, auditable shell access (replaces SSH/RDP)  
RDP is TLS-based by default — but ensure your Windows firewall + encryption policies are strong

### 4. Use Strong TLS Configurations

| **Component**     | **Best Practice**                                   |
|-------------------|-----------------------------------------------------|
| TLS Version       | TLS 1.2 or 1.3 only                                 |
| Cipher Suites     | Prefer modern, forward-secret ones                 |
| ALB/CloudFront    | Use predefined security policies (`ELBSecurityPolicy-TLS-1-2-Ext-2018-06`) |
| Certs             | ACM (preferred) or rotated via automation           |

### 5. Application-Level TLS

If you’re not using ALB or CF:

- Install certs directly on EC2  
- Use NGINX/Apache as TLS proxy  
- Terminate HTTPS at instance level  
- Rotate certs automatically (e.g., with certbot)  

✔️ Works for simple setups  
✖️ Requires manual cert handling  
✖️ Doesn’t scale as easily

---

## Additional Hardening

| **Strategy**                          | **Benefit**                                   |
|--------------------------------------|-----------------------------------------------|
| Security Groups (allow 443 only)     | Blocks HTTP/80 entirely                       |
| WAF on ALB                           | Protects web apps from injection, XSS, etc.   |
| ACM Certificate with Auto-Renew      | Avoids expired cert outages                   |
| CloudFront + Origin TLS              | Full edge-to-EC2 encryption + CDN protection  |
| SSM Session Manager                  | Replaces SSH with audited, encrypted shell    |
| TLS monitoring in CloudWatch/GuardDuty | Detects downgrade attacks or strange clients |

---

## Real-Life Example (Snowy’s Secure EC2 API)

Snowy’s EC2 instance hosts an internal API:

- A public ALB fronts the EC2 instance  
- TLS 1.2 enforced at the ALB with ACM cert  
- Security Group blocks port 80 entirely  
- ALB forwards HTTPS directly to EC2 running NGINX with TLS, for full end-to-end encryption  
- Admin access is handled via SSM Session Manager, not SSH  
- CloudFront is used in front of ALB to cache responses and serve static assets globally  
- Any HTTP attempt is auto-redirected to HTTPS, logged, and rate-limited  

✔️ User connections encrypted  
✔️ Admin access encrypted  
✔️ Certs auto-rotated  
✔️ Entire path encrypted: client → CloudFront → ALB → EC2

---

## Best Practices Summary

| **Control**                     | **Description**                                |
|----------------------------------|------------------------------------------------|
| HTTPS everywhere                 | Never expose EC2 over HTTP                     |
| TLS termination at ALB/CloudFront| Offloads work + scales better                 |
| Enforce TLS 1.2+                | Avoid downgrade + legacy attack vectors        |
| Use ACM certs (auto-renew)      | Don’t manage certs manually                   |
| Redirect HTTP to HTTPS          | Prevent mixed-content + force encryption       |
| Block port 80 at Security Group | Enforce HTTPS at infra level                  |
| Use SSH keys or SSM for access  | Avoid brute-force, improve auditability        |
| CloudWatch/GuardDuty TLS alerts | Catch anomalies and MITM attempts              |

---

## Final Thoughts

EC2 is the default compute engine in AWS — and when exposed, it becomes a high-value target.  
You wouldn’t let someone walk into your datacenter and plug in a laptop — so why allow plaintext traffic to your EC2?

- TLS isn’t just for the browser.  
- It’s for your API, your app, your login, your admin access.  
- Every packet should be encrypted, authenticated, and traceable.

And the best part? **AWS gives you the tools — you just have to use them correctly.**
