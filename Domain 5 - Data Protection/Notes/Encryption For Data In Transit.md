# Encryption for Data in Transit

## What Is It 

Encryption for data in transit refers to securing data as it travels between two points — whether between a user’s browser and your web app, between microservices in your architecture, or from your on-premises environment to AWS.  
It ensures that data, while in motion, remains confidential, intact, and authenticated — meaning:

- No one can read it (confidentiality)  
- No one can change it undetected (integrity)  
- No one can pretend to be a trusted source (authenticity)  

In AWS, transit encryption is supported (and in many cases, enforced) across all services through protocols like:

- TLS 1.2/1.3 (for HTTPS APIs, AWS SDK calls, ALBs, CloudFront, etc.)  
- IPsec (for VPN tunnels, hybrid networking)  
- MACsec (for Direct Connect encryption at Layer 2)  
- SSH, SFTP, SSL, and Mutual TLS (mTLS)  
- Custom encryption layers on top of raw protocols (e.g., TLS within a WebSocket, or client-side PGP before upload)  

This is not about *what* data you’re protecting.  
It’s about *how* you move that data without letting anyone intercept, inspect, or manipulate it.

Whether it’s credentials, personal info, config files, or even session cookies — if it crosses a network boundary, it needs encryption in transit.

---

## Cybersecurity Analogy

Anyone along the delivery chain — the mailman, the clerk, the person at the desk — can read it.

With encryption in transit, it’s like putting that message in a tamper-evident, opaque, locked container, and handing it to a courier who requires biometric authentication from the receiver before it’s opened.

Even if someone intercepts the parcel — all they get is a sealed box with gibberish inside.

## Real-World Analogy

Imagine you're talking to your doctor over the phone about your medical results.  
If the call is unencrypted, anyone on the line (think public Wi-Fi snooper, rogue ISP employee, compromised router) can listen in or modify what you hear.

**Encryption in transit ensures:**

- The call is encrypted end to end  
- The doctor you're speaking with is really your doctor, not an imposter  
- No one can change your results in transit and say you're fine when you're not  

---

## How It Works: TLS 101

The most common encryption in transit protocol is **TLS (Transport Layer Security)**.  
Here’s how a secure session typically works:

1. Client initiates a connection (e.g., HTTPS to `https://api.snowysec.com`)  
2. Server presents a certificate, which:  
    - Identifies the server (domain, public key, CA signature)  
    - Is signed by a trusted Certificate Authority (CA)  
3. Client validates the certificate using a list of trusted CAs  
4. Key Exchange occurs:  
    - Both sides negotiate a shared symmetric session key using algorithms like ECDHE  
    - This key is temporary (ephemeral), rotated per session  
5. Data is encrypted using AES-256 or ChaCha20 and authenticated via HMAC  
6. All traffic — headers, body, cookies, sessions — is now encrypted and verified  

This applies to:

- Browsers talking to web servers  
- EC2s talking to S3  
- RDS clients connecting over SSL  
- IoT devices using MQTT over TLS  
- Internal Lambda-to-API Gateway calls  

---

## Where It’s Used in AWS (Broad Coverage)

| Context                             | Encryption Method                            |
|-------------------------------------|-----------------------------------------------|

| Web apps (ALB, CloudFront, API GW) | TLS 1.2 or 1.3, ACM-managed certs             |

| AWS CLI & SDKs                     | HTTPS for all service calls                  |

| Inter-service AWS traffic          | Encrypted by default on AWS backbone         |

| S3 Access                          | HTTPS endpoints + optional signed URLs       |
| RDS / Aurora                       | SSL/TLS connections supported and enforceable|
| VPC to on-prem                     | VPN (IPsec/IKE), Direct Connect + MACsec     |

| Admin Access                       | SSM Session Manager (TLS), or SSH (manual)   |
| Load Balancing & CDN              | ALB, NLB, CloudFront with TLS cert policies  |
| Private APIs and IoT              | Mutual TLS (mTLS) support                    |

| Custom protocols (SFTP, MQTT)     | TLS or custom wrappers required             |

---


## Security Use Cases and Enforcement

| Use Case                         | Encryption in Transit Strategy                           |
|----------------------------------|-----------------------------------------------------------|
| Prevent password leakage         | Enforce HTTPS-only for login endpoints                   |
| Stop snooping on public Wi-Fi    | TLS on all API traffic from frontend to backend          |
| Block man-in-the-middle attacks  | Certificate pinning, mTLS in sensitive apps              |
| Enforce org-wide encryption      | SCPs or Config rules to deny non-TLS traffic             |
| Secure hybrid cloud data flow    | VPN tunnels or Direct Connect with MACsec                |
| Comply with PCI-DSS, HIPAA       | TLS 1.2 minimum + cert rotation + audit logging          |
| Eliminate deprecated ciphers     | Enforce strict TLS policies on ALB, CF, API Gateway      |

---

## TLS Version & Cipher Control

In AWS, you control what versions and ciphers are allowed:

- CloudFront, ALB, and API Gateway let you set TLS versions and cipher suites  
- **Best practice:** disable TLS 1.0/1.1, allow only TLS 1.2+  
- Use **AWS Certificate Manager (ACM)** to issue and rotate certs  
- Monitor with **AWS Config** for weak configurations  
- For stricter environments: enable **mutual TLS (mTLS)** for service-to-service auth  

---

## PrivateLink vs Public Internet TLS

If you're using **AWS PrivateLink**, traffic doesn't traverse the public internet at all — and is still encrypted.

| Mode                   | Encryption? | Goes over internet?  |
|------------------------|-------------|-----------------------|
| HTTPS via Public IP    | Yes (TLS)   | Yes                   |
| HTTPS via PrivateLink  | Yes (TLS)   | No (uses VPC endpoint)|
| VPN (Site-to-Site)     | Yes (IPsec) | Yes                   |
| Direct Connect + MACsec| Yes (L2)    | No (dedicated fiber)  |

---

## Real-World Example

Snowy runs a multi-region platform serving customers and internal analysts:

- Frontend served via CloudFront and ALB with TLS 1.3, ACM certs, and HSTS headers  
- API Gateway is locked to TLS 1.2+, and all requests must include a valid auth token  
- Lambda functions in private VPCs use PrivateLink to access S3, DynamoDB, and Secrets Manager without public endpoints  
- Internal EC2 workloads use TLS-based PostgreSQL connections to RDS, enforced via parameter group  
- Admin access is done via **SSM Session Manager**, which uses end-to-end TLS and logs every session  
- All VPC-to-on-prem connections are encrypted over a **Site-to-Site VPN tunnel with IPsec**  
- **AWS Config** detects any API Gateway or Load Balancer with TLS 1.0 enabled and alerts the SecOps team via SNS  

**SnowySec's policy:**  
No traffic ever hits the wire unencrypted — internal or external.  
Periodic TLS audits are automated via Lambda and Config.

---

## Pricing Model

| Component                 | Cost Notes                                             |
|---------------------------|--------------------------------------------------------|
| HTTPS to AWS Services     | Free (included in endpoint usage)                      |
| ACM Certificates          | Free for public TLS certs in AWS                       |
| ACM Private CA            | Charged by CA/month + per cert issuance                |
| VPN (IPsec)               | ~$0.05/hr per connection + data transfer charges       |
| Direct Connect w/ MACsec  | Custom — requires Enterprise-grade DX connection       |
| PrivateLink               | Charged per endpoint-hour + per GB data                |

---

## Final Thoughts

**Encryption in transit is silent, invisible, and critical** — and it’s your first layer of defense every time data crosses a wire.

You don’t know which part of the network is hostile.  
You can’t assume your users, edge nodes, or cross-region calls are protected.  
You must assume someone’s watching — and act accordingly.

In AWS, you have the tools:

- TLS for all services  
- ACM for painless certs  
- PrivateLink for VPC isolation  
- VPN and MACsec for hybrid cloud  
- Monitoring for misconfigs  

**Don’t rely on hope.**  
**Don’t rely on default.**

Design for encryption everywhere, all the time — even internally.

> *If it moves, encrypt it.*  
> *If it doesn’t, encrypt it anyway.*

