# Private Communication Path: EC2 → RDS (MySQL/Postgres)

## What Is This Flow

When an **EC2 instance in a VPC** connects to an **Amazon RDS instance** (MySQL or Postgres), it’s often for:

- Application backends  
- Analytics dashboards  
- Logging databases  
- Transactional workloads  

This is one of the most common internal communication paths in cloud-native architecture.

But just because traffic stays inside a **VPC** doesn’t mean it’s **encrypted**.

> **Encryption is not automatic. You must enable it in the client app.**

If your EC2 app connects to RDS **without explicitly enabling SSL/TLS** (e.g., JDBC flags, `psql` options), that traffic may be **plaintext** — even inside AWS.

---

## Cybersecurity Analogy

Imagine you’re running a company and your **accounting team (EC2)** sends financial reports to your **bank (RDS)**.

- If you use a **secure envelope (TLS)** — no one in the mailroom can read it.  
- If you just drop the document **raw into the mailbox** — even inside the building — someone can peek.

> AWS gives you the **option** to seal the envelope. But it’s **your job** to enable it.

## Real-World Analogy

You’re in an office building where **you (EC2)** and your colleague **(RDS)** are on the same floor (same subnet).

- If you pass them a note directly — that’s **raw TCP**. Fast, but interceptable.
- If you use a **locked folder** with a secret code — that’s **TLS**.

> AWS gives you the folder. But you have to **ask for it** in your connection string.

---

## How This Works (Technically)

| Component     | Behavior                                                                 |
|---------------|--------------------------------------------------------------------------|
| EC2 Instance  | App must **explicitly configure TLS/SSL** in the DB client (JDBC, psycopg2, etc.) |
| RDS Endpoint  | Supports both **encrypted** and **unencrypted** connections              |
| Network Path  | Traffic flows over **private VPC network**, not the public internet      |
| TLS Optional? | ✔️ Yes — but only if you configure it                                     |

> Key Point:  
RDS does **not enforce TLS by default**. Your EC2 client must **request encryption**.

Without TLS config, connections to `3306` (MySQL) or `5432` (Postgres) are **plaintext**.

---

## Encryption Configuration Details

| Area             | Details                                                                 |
|------------------|-------------------------------------------------------------------------|
| Connection String| Include `ssl=true` or equivalent (`?useSSL=true` for MySQL JDBC)        |
| Cert Validation  | Use **RDS CA bundle** from AWS trust store to enforce server validation |
| Auto-Rotate Certs| AWS rotates RDS TLS certs periodically — update your trust store        |
| TLS Protocols    | RDS supports **modern TLS (1.2+)**, but clients may **downgrade** unless locked in |

---

## Compliance & Risk Considerations

**Why You Should Enable TLS**:

- Protects **sensitive data** (PII, passwords, tokens)
- Helps meet **compliance standards** (HIPAA, SOC 2, ISO)
- Blocks internal sniffing or misconfigured clients

**If You Don’t**:

- Data is **sent plaintext** across AWS's infrastructure  
- Compromised systems or AWS personnel **could inspect traffic**  
- Fails **security scans** and **compliance audits**

---

## Security Gotchas

- Default **RDS security groups** won’t block plaintext
- **VPC Flow Logs** show connections, but **not encryption state**
- No **AWS-wide setting** to force TLS globally
- TLS is only **enforced if you set `rds.force_ssl = 1`** (Postgres only)

---

This one trips up a lot of teams.  
You think:

> “Oh it’s internal VPC traffic. We’re fine.”

But that’s exactly how **visibility gaps** and **lateral movement risks** sneak in.

Just because the **pipe is private** doesn’t mean the **water is clean**.

If Snowy’s team is handling **passwords, tokens, billing data** — enabling TLS is **non-negotiable**.

You already paid for RDS. TLS is **free**.  
Why risk it?

**The good news?**  
Once you set it up in your `JDBC`, `psycopg2`, or `sqlalchemy` config — it’s **one and done**.

Just don’t forget to stay on top of **RDS TLS cert rotations**.

