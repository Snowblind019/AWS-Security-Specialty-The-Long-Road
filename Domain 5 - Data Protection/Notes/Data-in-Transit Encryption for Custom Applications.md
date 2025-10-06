# Data-in-Transit Encryption for Custom Applications (AWS)

## What This Means

You’re building and running your own applications — maybe in EC2, containers, Lambda, or hybrid architectures. That means **you** are in charge of how data moves across the network and whether it’s encrypted or not.

This isn’t like S3 or RDS where AWS handles part of the security model for you.  
In custom apps, you’re fully responsible for implementing encryption in transit:

- Between microservices  
- Between frontends and backends  
- Between apps and third-party APIs  
- Between app and AWS services via SDK  

If you don’t explicitly implement TLS, your data is flying across the wire in plaintext — even inside the VPC, even on private IPs, even across regions.

---

## Cybersecurity and Real-World Analogy

**Cybersecurity analogy:**  
Building a custom app without TLS is like writing secrets on postcards and mailing them through your company’s internal mail.  
Anyone (malicious insider, compromised pod, packet sniffer) can intercept and read the contents.

**Real-world analogy:**  
Imagine you're running an internal delivery system between warehouses.  
Would you send sensitive customer data on open clipboards just because it's "in the building"?  
**TLS is the sealed envelope + wax seal + delivery confirmation.**

---

## Where This Applies

Your encryption responsibility covers any place you control the code, including:

- Python/Node.js/Java microservices calling each other  
- ECS services communicating over ENIs  
- Containers using service discovery (DNS)  
- Lambda functions making outbound calls (HTTPS, REST APIs, etc.)  

- App ↔ DB connections using libraries like `psycopg2`, `mysqlclient`, `SQLAlchemy`  
- Internal APIs talking through ALBs, NLBs, or service meshes  

---

## What Encryption in Transit Looks Like in Custom Apps

### Use TLS for All HTTP Requests

Use `https://` everywhere — both for external APIs and internal microservices.

```python
# TLS enabled

r = requests.get("https://myapp.internal.local/api/data")

# BAD: Plaintext request
r = requests.get("http://myapp.internal.local/api/data")
```

### Use TLS for Database Drivers
Databases often support TLS, but you must explicitly:

- Use the SSL flag or parameter
- Supply certs if required (e.g., RDS root cert)
- Validate server identity (CA verification)
Examples:
```sql
# PostgreSQL with SSL
conn = psycopg2.connect(
  dbname="prod",
  user="app",
  password="secret",
  host="myrds.cluster.amazonaws.com",
  sslmode="require"
)
```

```json
// Node.js to MongoDB Atlas (with TLS)
mongoose.connect('mongodb+srv://user:pass@cluster.mongodb.net/mydb?retryWrites=true&w=majority')
```

---

## What Happens If You Don’t Encrypt

| Risk                | What It Means                                                                 |
|---------------------|-------------------------------------------------------------------------------|
| Packet Sniffing     | Internal attackers (or bugs) can capture requests via tcpdump, Wireshark, etc. |
| Token Theft         | API tokens, passwords, JWTs in plaintext can be reused by attackers.          |
| Compliance Violation| PCI, HIPAA, SOC 2, etc. mandate encryption in transit for sensitive data.     |
| Man-in-the-Middle   | If routing or DNS is compromised, attacker can intercept + alter messages.    |
| Service Impersonation| Without TLS and certificate verification, clients may talk to a malicious backend. |

---

## TLS Configuration for Custom Apps

| Layer           | Configuration Needed                                                               |

|-----------------|------------------------------------------------------------------------------------|

| Frontend        | Enforce HTTPS-only via web server (Nginx/Apache/CloudFront). Redirect HTTP to HTTPS.|
| Backend API     | Serve via TLS (e.g., Nginx with certs, Express.js with https module).               |

| ALB/NLB         | Use HTTPS listener with ACM certificate. Require TLS 1.2 or above.                 |
| Client Libraries| Use HTTPS URLs, verify certs, enable strict SSL mode.                              |
| Database Drivers| Use SSL/TLS flags, set `sslmode=require` or equivalent.                            |
| SDKs (e.g., boto3, AWS SDK)| AWS SDKs use TLS by default — don’t override this.                      |

---

## Secure Protocol Checklist

| Protocol           | Status | Use Case                                          |
|-------------------|--------|---------------------------------------------------|
| HTTPS             | ✔️      | For all REST APIs, frontend/backend, external requests |
| TLS 1.2+          | ✔️      | For all services that allow version enforcement   |
| SFTP              | ✔️      | Instead of plain FTP for file transfers           |
| SMTPS             | ✔️      | Secure email delivery                            |
| gRPC over TLS     | ✔️      | For high-performance microservices               |
| WebSocket Secure (WSS)| ✔️  | Realtime apps (chat, stock feeds, etc.)           |

> Avoid plaintext versions of protocols: HTTP, FTP, SMTP, Telnet, MySQL over port 3306 without SSL, etc.

---

## How to Validate TLS Is Working

| Tool                            | What It Does                                      |
|---------------------------------|---------------------------------------------------|
| `curl -v https://`              | See TLS handshake, cert chain                     |
| `openssl s_client -connect host:port` | Test TLS, view server certs                  |
| AWS Inspector / GuardDuty       | Alert on plaintext requests (in some cases)       |
| VPC Traffic Mirroring           | Advanced — sniff and inspect internal traffic     |
| Logs                            | Look for signs of plaintext: `http://`, failed SSL handshakes, etc. |

---

## Security Best Practices for Custom Apps

- Never assume internal = secure  
- Default to HTTPS everywhere  
- Rotate certificates (ACM, self-signed, etc.)  
- Validate certs and disable insecure protocols (no TLS 1.0/1.1)  
- Use environment variables or Parameter Store for secrets — not in URL params  
- Don’t skip verification for self-signed or internal certs  
- Use ALB or Nginx as a TLS terminator for legacy backends  
- Integrate with AWS ACM, Secrets Manager, and/or service mesh for automation  

---

## Final Thoughts

When you're building the app, the encryption is **your responsibility**.

No matter how secure AWS infrastructure is, if your app talks over `http://` or sends secrets in cleartext — you’ve created an exploit path.

In modern architectures, **every hop is untrusted**.  
Every component — frontend, backend, internal API, cron job — must use TLS as a default language.

**Security is not about where the packet is. It’s about whether anyone can read it.**

With custom apps, the only thing standing between your data and compromise… **is you.**

