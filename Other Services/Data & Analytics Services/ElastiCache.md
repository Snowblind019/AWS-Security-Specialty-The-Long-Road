# Amazon ElastiCache

## What Is the Service

Amazon ElastiCache is a fully managed, in-memory data store and caching service that supports:

- **Redis** (feature-rich, persistent option)  
- **Memcached** (simple, volatile, high-speed cache)

Instead of reading from a database over and over, you cache frequently accessed data (like session tokens, product info, auth results) into ElastiCache — reducing latency from 100ms to sub-millisecond.

**Why it matters in security:**

- ElastiCache can store sensitive session tokens, authentication info, and API payloads  
- Misconfigured clusters can be exposed and exploited (e.g. `redis-cli` shell access, no encryption, weak auth)  
- Used in many identity management, fraud detection, and rate limiting architectures

---

## Cybersecurity Analogy

Imagine Snowy runs a theme park.  
The master guest list is stored in a secure vault (database).  
But every 2 seconds, guests ask: **“Am I allowed on this ride?”**

Rather than constantly opening the vault, Snowy’s team uses sticky notes — pre-approved access decisions stored on a whiteboard.  
That’s ElastiCache: blazing fast memory that holds temporary but valuable truth.

But… if someone breaks into the whiteboard room?  
They can see who’s VIP, copy session tokens, or modify ride eligibility.

---

## Redis vs Memcached (For Security Context)

| Feature            | Redis                               | Memcached                      |
|--------------------|--------------------------------------|--------------------------------|
| **Persistence**     | Optional (AOF, RDB snapshots)        | Volatile only                  |
| **Replication**     | ✔️ Multi-AZ, read replicas           | ✖️ None                         |
| **Authentication**  | ✔️ AUTH token support               | ✖️ No auth                      |
| **Encryption**      | ✔️ In transit & at rest             | ✖️ None                         |
| **Advanced Features**| Streams, Pub/Sub, Sorted Sets       | Simple key-value               |
| **Security Verdict**| ✔️ Safer for sensitive data         | ✖️ Not recommended for sensitive workloads |

**For SCS or production security:**  
Always use **Redis**, never expose **Memcached** publicly.

---

## How ElastiCache Works

- Deployed inside a VPC  
- You choose subnet group for AZ placement  
- You get a DNS name to connect (e.g. `mycache.xxxxxx.use1.cache.amazonaws.com`)  
- Applications connect over:
  - `6379` (Redis)
  - `11211` (Memcached)

**You can enable:**

- AUTH token (for Redis)  
- TLS in-transit encryption  
- At-rest encryption (KMS-managed CMK)  

You can scale:

- **Horizontally** (sharding)
- **Vertically** (node size)  
Redis supports replication + failover for high availability.

---

## Security Controls

### Network Isolation

- Deployed inside VPC  
- Controlled by security groups  
- **No public access unless you explicitly allow it** (don’t.)

### IAM for Management

- IAM controls who can create/modify ElastiCache resources  
- **BUT**: No IAM authentication for connecting to the cache  
  - Use `AUTH` for Redis

### Encryption

| Mode       | Redis     | Memcached        |
|------------|-----------|------------------|
| In-Transit | ✔️ TLS    | ✖️ Not supported  |
| At-Rest    | ✔️ KMS    | ✖️ Not supported  |

Enable **TLS + AUTH token** in Redis or it’s just plaintext over the wire.

### Authentication

- Redis AUTH token is a shared secret  
- Store in Secrets Manager or Env vars  
- Not IAM-backed  
- **Rotate it regularly** using automation

### Logging

- No native logging of read/writes  
- Use **VPC Flow Logs** to track connections  
- Monitor control plane actions via **CloudTrail**

---

## Common Use Cases (And Why Security Matters)

| Use Case                    | Why ElastiCache?             | Security Implications                            |
|-----------------------------|------------------------------|--------------------------------------------------|
| Session Storage (e.g. Cognito, JWT cache) | Ultra-low latency, fast auth  | Do **NOT** expose; use **encryption + auth**     |
| Rate Limiting               | Store IP counters per second | Easily DOS’d if not subnet-isolated              |
| Fraud Detection             | Real-time rules and cache hits | Store red flags, must protect                   |
| Gaming Leaderboards         | Sorted sets in Redis         | No auth = anyone can overwrite scores            |
| Token Blacklists (JWT, OAuth)| Store revoked tokens        | Must be high availability and secure             |

---

## Real-World Snowy Setup

Winterday’s eCommerce app uses Cognito for identity, and stores session state in Redis:

- Redis (ElastiCache) in private subnets  
- Security group only allows EC2 instances from App tier  
- AUTH token stored in Secrets Manager  
- TLS enabled, managed by ElastiCache  

**Used for:**

- JWT token revocation checks  
- CSRF session tokens  
- Real-time fraud flags

---

## Misconfig Risks

| Risk                     | Impact                                               |
|--------------------------|------------------------------------------------------|
| ✖️ Public access          | Exposes Redis to Internet (common in CTFs!)          |
| ✖️ No AUTH token          | Anyone in subnet can read/write                      |
| ✖️ No TLS                 | Tokens, secrets sent in cleartext                    |
| ✖️ Use of Memcached       | No encryption, no auth — **NEVER** for sensitive workloads |
| ✖️ No security group restrictions | Any VPC host can probe it                    |
| ✖️ Default port scanning  | Redis exposes info on unprotected port `6379`        |

---

## Compliance + Audit Strategy

- Encrypt at rest with **CMK** (customer-managed key)  
- Enable **TLS in transit**  
- Use **CloudTrail** to monitor cluster modifications  
- Use **VPC Flow Logs** to detect suspicious access patterns  
- Store Redis **AUTH token in Secrets Manager** (with auto-rotation)  
- Isolate in **private subnet with NACL lockdown**

---

## Final Thoughts

ElastiCache is blazing fast — but with great speed comes great risk.

If you’re storing **tokens, sessions, fraud flags, or rate limits**, then:

- Use **Redis**, not **Memcached**  
- Turn on **AUTH + TLS + KMS encryption**  
- Limit access via **security groups and private subnets**  
- Rotate tokens and secrets regularly

**Treat your cache as Tier-1 sensitive infrastructure**, not just a performance booster.
