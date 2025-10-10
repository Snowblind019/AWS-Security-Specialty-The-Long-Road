# Amazon Route 53 Failover

## What Is the Service

**Amazon Route 53 Failover** is a feature of Route 53 that allows you to automatically route traffic **away from unhealthy resources to healthy backup targets**. It’s DNS-based failover — simple, fast, and entirely infrastructure-agnostic.

At its core, Route 53 Failover watches your **primary endpoint via health checks** (e.g., an IP, an ALB, or a Lambda function). If it becomes unhealthy, Route 53 stops routing DNS traffic to it and instead forwards traffic to a designated **secondary resource** — often in a separate **Availability Zone** or **AWS Region**.

### For Snowy’s team, this was the first line of defense in their tiered disaster recovery strategy:

- Fast detection of regional outages
- Reroute of user-facing DNS
- No app-level coordination required
- Works globally with zero client-side changes

When combined with **static S3 websites**, **API Gateways**, or **multi-Region ALBs**, Route 53 Failover enables **simple, cost-effective high availability** — even without ARC or complex automation.

---

## Cybersecurity Analogy

- As long as the monitor sees a pulse (health check is healthy), traffic flows normally
- If that pulse stops — DNS is immediately updated to point elsewhere

- No approval needed, no human intervention — it just flips the switch

> It’s fast, automatic, and invisible to users
> But it can be triggered by flakey health checks without review

That’s why Snowy’s team pairs this with **tighter controls** (like ARC) when failover decisions carry major impact.

## Real-World Analogy

Imagine you’re running a security checkpoint at a major airport.

- Your **primary scanner line** goes down
- You **don’t call a meeting** — you **reroute passengers** to the backup scanner

- The user never knows anything broke — they just take a different path

That’s Route 53 Failover. No central decision-making — it reacts to predefined health conditions and immediately redirects users.

---

## How It Works

Route 53 Failover uses **DNS record routing policies and health checks** to determine whether traffic should be routed to a primary or secondary endpoint.

### Key Concepts

| Component              | Description                                                 |
|------------------------|-------------------------------------------------------------|
| Health Check           | Monitors a resource (IP, domain, ALB, Lambda, etc.)         |
| Primary Record         | DNS target used under normal conditions                     |
| Secondary Record       | DNS target used when primary is marked unhealthy            |
| Failover Routing Policy| Special Route 53 policy type with Primary/Secondary roles   |
| TTL                    | Affects how quickly DNS clients pick up failover updates    |

> Failover is **Region-agnostic** — you can route from `us-east-1` to `us-west-2`, from AWS to on-prem, or even to **Cloudflare or Azure endpoints**.

---

## Security and Compliance Relevance

While simple, Route 53 Failover has **security and operational implications** that Snowy’s team takes seriously:

| Risk or Requirement               | Route 53 Feature                                                             |
|-----------------------------------|------------------------------------------------------------------------------|
| Service outage protection         | Automatic redirection based on real-time health                             |
| Low blast radius                  | Works at the DNS layer — no VPC, IAM, or app-level involvement              |
| Limited false positive resistance | No quorum or override — once health is "down", failover triggers            |
| Visibility and auditability       | CloudWatch logs health checks, but no CloudTrail API log for failover switch |
| Mitigation of DDoS against origin | Can point DNS to backup site, CDN, or WAF-protected static failover         |
| Compliance for uptime SLAs        | Helps maintain RTO < 5 minutes for web traffic in passive DR scenarios      |
| No TLS validation                 | Health checks use HTTP/S or TCP only — no mutual TLS or auth supported      |

> For workloads requiring **intentional operator approval**, Route 53 Failover isn’t sufficient — use ARC, SCPs, or Control Tower guardrails.

---

## Pricing Model

| Component             | Cost                                                   |
|------------------------|--------------------------------------------------------|
| Health Checks         | ~$0.50/month each (standard)                           |
| DNS Queries           | Standard Route 53 pricing (e.g., $0.40/million queries)|

| Failover Records      | No extra charge — it’s just a routing policy type      |
| CloudWatch Integration| Optional, adds CloudWatch charges for metrics          |

> It’s one of the **lowest-cost failover options AWS offers** — ideal for SaaS apps, startup backends, and small DR setups.

---

## Real-Life Example — Snowy’s Cold Standby Static Failover

Snowy’s team wanted failover for their **public status site**, but didn’t need real-time sync or compute in the backup Region. They used a **cold standby** pattern:

1. Deployed **S3 static website with CloudFront** in `us-east-1` (primary)
2. Created a **copy of the bucket in `us-west-2`** with last known status page
3. Created Route 53 failover records:

    - `status.snowy.app` (Primary) → CloudFront-us-east-1
    - `status.snowy.app` (Secondary) → CloudFront-us-west-2
4. Configured a **Health Check** on the primary S3 endpoint
5. Set TTL to **30 seconds**

If the east bucket failed, users were routed to the west version. It wasn’t real-time, but it was:

- Zero touch
- <60 seconds failover time
- Resilient to Region failure

> Perfect for **non-critical public-facing systems**, without needing App Mesh or ARC.

---

## Final Thoughts

**Route 53 Failover** is a fast, infrastructure-agnostic DNS-level failover — ideal for:

- Simple **active/passive apps**
- **Static websites** or **read-only APIs**
- **Cost-conscious DR** setups
- Environments without complex traffic routing needs

But in **Snowy’s world** — where failover must be **intentional, verified, and controlled** — Route 53 is often:

- The **first layer**, not the final gate
- Supplemented with **ARC, EDR, or cross-region active-active replication**

> Still, Route 53 Failover remains one of the simplest, most effective tools for **quick resilience wins**, especially when paired with:

- Health checks scoped tightly to real app health
- Short TTLs (30s or less)
- Monitoring and alerting tied to failover triggers
