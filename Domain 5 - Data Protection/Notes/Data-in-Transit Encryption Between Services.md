# Data-in-Transit Encryption Between Services (Private)

## What This Means

When we talk about data in transit, most people immediately think about internet-facing traffic (TLS over HTTPS, CloudFront to origin, API Gateway, etc.).

But this deep dive is focused on a far more overlooked but equally critical surface: **encryption of internal AWS service-to-service traffic** — what happens when:

- EC2 talks to RDS  
- Lambda invokes a private endpoint  
- ALB routes to your backend  

This is your **“east-west” traffic**, versus public-facing “north-south.”

If your internal network is compromised or misconfigured, unencrypted internal traffic is an easy attack surface — and even if the AWS backbone is “secure,” **you** are responsible for enforcing encryption wherever possible, especially for sensitive workloads.

---

## Cybersecurity and Real-World Analogy

### **Cybersecurity analogy:**  
Think of your private AWS traffic as office mail.  
If you don’t seal the envelopes (TLS), anyone walking through the building can read the contents.

If an attacker compromises an internal host (e.g., EC2 with weak permissions), and you're sending credentials or plaintext data over HTTP inside the VPC, they can sniff it with tools like `tcpdump`.

### **Real-world analogy:**  
You still use encryption — not just because someone might be listening, but because **compliance and confidentiality demand it.**

---

## Why This Matters in AWS

AWS offers multiple services that allow internal (VPC-level) communications:

- EC2 ↔ RDS  
- ECS ↔ S3 via VPC endpoint  
- Lambda ↔ SQS via VPC  

- ALB ↔ EC2 in private subnet  
- CloudMap DNS for service discovery  

And in many of these, **encryption in transit is not enforced by default** — you must enable TLS, enforce specific protocols, or design the architecture to require it.

---

## Key Concepts and Examples

### 1. TLS Enforcement on Internal Traffic

Just because services are talking over AWS backbone doesn’t mean traffic is encrypted unless:

- You use HTTPS/TLS explicitly  
- You enable TLS listeners on your ALBs  
- You configure RDS to force SSL  
- You enable TLS-only policies on services like MQ, MSK, ElastiCache  

> AWS does not transparently TLS-wrap all internal connections unless you configure it.

### 2. Services That Support TLS Enforcement (Private)

| AWS Service                | TLS In-Transit?     | Enforced By Default? | You Should Do This                                      |
|---------------------------|----------------------|------------------------|----------------------------------------------------------|
| Application Load Balancer | Yes (via HTTPS)      | ✖️ No                  | Use HTTPS listener + backend certs                      |
| API Gateway (Private)     | Yes (TLS 1.2+)       | ✔️ Yes                 | ✔️ Already enforced                                     |
| RDS (MySQL, Postgres)     | Yes (SSL/TLS)        | ✖️ No                  | Enforce SSL from client, deny non-SSL connections       |
| Aurora                    | Yes                  | ✖️ No                  | Use SSL param group + restrict                         |
| ElastiCache (Redis)       | Yes (if enabled)     | ✖️ No                  | Enable in-transit encryption and enforce auth           |
| Amazon MQ / MSK (Kafka)   | Yes                  | ✔️ Yes                 | Choose TLS endpoints only                               |
| SQS (via VPC endpoint)    | Yes                  | ✔️ Yes                 | Uses HTTPS via interface endpoint                       |
| DynamoDB via VPC Endpoint | Yes                  | ✔️ Yes                 | No config needed – uses HTTPS                           |

| OpenSearch                | Yes (HTTPS)          | ✖️ No                  | Enable HTTPS-only access policy                         |
| VPC Lattice               | Yes                  | ✔️ Yes                 | TLS enforced automatically                              |

| Lambda → VPC Resources    | Depends              | ✖️ No                  | Use HTTPS libraries or enforce TLS on RDS, ALB, etc.    |

### 3. Example: ALB with TLS to Backend

You want to route ALB to EC2 in a private subnet.

- Set ALB listener to HTTPS (443)  
- Upload certificate via ACM  
- Backend EC2 must host HTTPS server (e.g., Nginx with TLS cert)  
- ALB target group uses port 443, not 80  

**Result:** TLS from user → ALB **AND** ALB → EC2  
> If EC2 only listens on HTTP, ALB will still send data in plaintext — over private network, yes, but still unencrypted.

### 4. Example: EC2 to RDS with TLS

RDS supports SSL (MySQL, Postgres, etc.)  
RDS provides `.pem` root cert

You must:

- Modify DB parameter group: `rds.force_ssl=1`  
- Use client library to connect with SSL  
- Rotate certs before expiration  

> Otherwise, traffic between your EC2 app and RDS can be sniffed within the VPC.

---

## Compliance Implications

- **PCI DSS** and **HIPAA** require encryption for sensitive data in transit, even internally  

Using secure internal TLS ensures you're covered in:

- Zero Trust architectures  
- Compromised subnet containment  
- Secure microservices communication  
- Insider threat mitigation  

---

## Misconceptions to Avoid

| Myth                                           | Reality                                                                 |
|------------------------------------------------|-------------------------------------------------------------------------|
| “It’s inside the VPC, so it’s secure.”         | ✖️ Wrong. VPC traffic can be compromised from within (e.g., lateral movement). |
| “AWS automatically encrypts all traffic.”      | ✖️ Only some services do (SQS, DynamoDB via endpoint). Many do not unless configured. |
| “TLS is just for internet-facing apps.”        | ✖️ No. Internal TLS is essential for zero trust — everything is untrusted.      |

---

## Security Best Practices

- Use HTTPS for all service-to-service communication (even internal)  
- Enforce TLS 1.2 or higher  
- Rotate certs before expiration (especially RDS, OpenSearch)  
- Use interface VPC endpoints instead of public access  
- Deny unencrypted connections at the protocol or security group level  
- Use private DNS with interface endpoints to force TLS-based routing  
- Consider using service meshes (e.g., App Mesh) for mTLS across microservices  

---

## Final Thoughts

**Encrypting internal service traffic is no longer optional.**

Attackers assume you’ve got edge security. They go lateral. They probe inside.

**TLS between services is your sealed envelope** — it doesn’t matter if the postman is trustworthy or not.

AWS gives you the tools.  
But you’re the one who has to flip the switches:

- Enable encryption  
- Enforce protocols  
- Deny plaintext traffic  

Just because it’s private doesn’t mean it’s safe.  
**Treat every packet like it’s crossing the public internet — because one misstep, and it might be.**

