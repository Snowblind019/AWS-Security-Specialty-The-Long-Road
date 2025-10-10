# Amazon Route 53

## What Is It

**Amazon Route 53** is AWS’s highly available and scalable DNS (Domain Name System) service. It does three major things:

- Resolves domain names to IP addresses (DNS service)
- Monitors the health of endpoints and routes traffic accordingly (Health Checks & Routing Policies)
- Registers and manages domain names (Domain Registrar)

This might sound simple — but Route 53 is at the front door of every AWS service you expose to the world. If it’s misconfigured, everything behind it can be:

- Unreachable
- Impersonated
- Exposed to attack

### Why It Matters for Security

DNS is invisible when it works — and catastrophic when it doesn’t. Route 53 controls **who finds your services**, **where they get routed**, and **how failover happens**.

If an attacker hijacks your DNS or if you expose internal services via public records, you’re in trouble. Done right, Route 53 gives you tight, audit-friendly, programmable control over every name-to-IP mapping — across public and private spaces.

---

## Cybersecurity Analogy

Route 53 is like your organization’s **switchboard operator**.

If someone calls “www.snowysec.com,” this operator checks the internal directory and forwards them to the correct extension.

> But here’s the catch — if the operator is compromised, they could send callers to an imposter line or a dead number.

That’s why **securing DNS is just as important as securing the server** — because if you trust names, but names are wrong, everything falls apart.

## Real-World Analogy

Imagine a logistics hub with smart signs:

- Visitors ask for directions (DNS queries)
- Route 53 gives them the best path — closest office, least congested road, or backup location
- If a building is down (via health check), signs redirect them to the next best site
- The system auto-updates in real-time — with no humans needed

> If someone tampers with those signs? Visitors end up at fake locations or offline warehouses.

---

## How It Works

### 1. Key functions

Route 53 supports several key functions:

- A **hosted zone** = a DNS namespace (e.g., `snowysec.com`)
- Contains **resource record sets** like A, AAAA, CNAME, MX, TXT, etc.
- Each record maps names to IPs or other names

### 2. Routing Policies

Control how queries are answered:

| Policy              | Use Case                                                  |
|---------------------|-----------------------------------------------------------|

| Simple              | Basic 1:1 record resolution                               |
| Weighted            | Split traffic by percentage (e.g., 80% to us-east-1)      |
| Latency-based       | Route to lowest latency region                            |

| Failover            | Route to healthy endpoint only; use backup if unhealthy   |
| Geolocation         | Route based on user’s location (e.g., EU vs US users)     |
| Geoproximity        | Adjust traffic flow based on region and “bias” weighting  |
| Multi-value Answer  | Return multiple healthy endpoints randomly, with health checks |

### 3. Health Checks

- Monitor endpoints via **HTTP, HTTPS, or TCP**
- If an endpoint fails, Route 53 **stops routing traffic to it**
- Can **trigger CloudWatch Alarms** or be integrated with **failover routing**

### 4. Domain Registration

- Buy domains directly in Route 53
- Manage WHOIS, registrar info, name servers
- Fully integrated into IAM for access control

### 5. Private DNS (for VPCs)

- Create **private hosted zones** only resolvable from within a VPC
- Used for internal services like `db.internal.snowysec.local`
- Resolves over **Route 53 Resolver** (`169.254.169.253`)

---

## Security Use Cases

| Use Case                         | Route 53 Feature Used                                              |
|----------------------------------|--------------------------------------------------------------------|
| Block DNS-based exfiltration     | Route 53 Resolver Query Logging + GuardDuty alerts                 |
| Contain region-specific DDoS     | Geo-based routing with regional firewalls                          |
| Auto-failover for compromised endpoint | Health check + failover routing to backup region            |
| Protect internal service names   | Private Hosted Zones only accessible from trusted VPCs             |
| Prevent DNS hijacking            | Use Route 53 as registrar + DNS to centralize trust                |

| Alert on suspicious resolution   | Resolver logs + Athena queries for IOC domains                     |

---

## Query Flow Example

Let’s walk through a sample DNS resolution:

1. A user in Europe browses to `app.snowysec.com`
2. Their recursive resolver (e.g., `8.8.8.8`) queries Route 53’s authoritative nameservers
3. Route 53 checks:
   - Which routing policy applies? (latency-based)

   - Are all endpoints healthy? (health check passed)
   - What region is the user in? (Europe)
4. Returns the IP of the Frankfurt ALB

5. If Frankfurt fails, Route 53 automatically returns us-east-1 ALB instead

> No human intervention. No redeploys.

---

## SnowySec Architecture Example

**Snowy’s platform includes:**

### `app.snowysec.com`
- Latency-based routing between ALBs in `us-east-1` and `eu-west-1`
- Each ALB backed by health checks
- Failover routing to static **S3 bucket** in case both regions go down

### `internal.snowysec.local`
- Private Hosted Zone resolving internal service names
- Only resolvable from inside the **app VPC**
- **Resolver logs** enabled + shipped to S3 for Athena analysis

### `alerts.snowysec.com`
- **Geolocation routing**:
  - US users → `us-west-2` SNS
  - EU users → `eu-central-1` SNS
- TLS enforced via **ALB** — DNS just routes them to the right region

> Snowy also uses **ACM** for HTTPS, but relies on **Route 53** for endpoint discovery, routing decisions, and auto-healing logic.

---

## Security Observability & Detection

| Threat                           | Detection/Response Strategy                                       |
|----------------------------------|-------------------------------------------------------------------|
| DNS tunneling/exfiltration       | Enable Resolver Query Logs, scan for weird domains                |
| Misrouted DNS to malicious IP    | Use simple routing only + pinned IPs + ACM cert validation        |
| Data exfil via TXT records       | Monitor TXT queries via Athena on resolver logs                   |
| Public DNS record for internal service | Scan hosted zones + automate zone diffing checks             |
| DNS-based phishing/impersonation | Protect domain ownership, monitor WHOIS + domain expiry           |
| Malicious domains resolving in VPC | Block via DNS Firewall (Route 53 Resolver rules)               |

---

## Pricing

| Feature                  | Cost                                                    |
|--------------------------|---------------------------------------------------------|
| Public hosted zone       | ~$0.50/month per zone                                   |
| Private hosted zone      | ~$0.50/month per zone (queries free in-VPC)             |
| DNS queries (public)     | ~$0.40/million for first 1B queries                     |
| Health checks            | ~$0.50/month per check                                  |
| Domain registration      | Varies (~$12/year for `.com`, etc.)                     |
| Resolver query logs      | Billed by CloudWatch/S3 ingestion                       |
| DNS Firewall (advanced)  | Extra per rule group + queries filtered                 |

---

## Final Thoughts

**Route 53 is one of the most overlooked security layers in AWS.**

You might secure your APIs, encrypt your data, harden your IAM — but if your **DNS is hijacked or misrouted**, none of that matters. Attackers often go around your firewalls by compromising the names people use to find you.

Treat Route 53 not just as DNS, but as a **security control surface**:

- Watch your record sets
- Validate domain ownership
- Monitor query logs
- Use routing policies to automate failover and resilience

> If **IAM is your identity perimeter**, **DNS is your access gateway**.
> **Don’t let it be the weakest link.**
