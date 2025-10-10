# AWS Direct Connect

## What Is AWS Direct Connect

AWS Direct Connect (DX) is a dedicated, private network connection from your on-premises data center, colocation facility, or office network directly into AWS.  
Unlike a VPN — which travels over the public internet — **Direct Connect uses private fiber links** to reach AWS infrastructure.

**Why it matters**:

- Lower latency  
- Higher bandwidth  
- Predictable performance  
- Greater security than internet-based connections  
- Bypasses ISPs and public internet unpredictability  
- Reduces egress costs  

In the real world of cloud security — where milliseconds matter and so does packet integrity — **DX is how SnowyCorp and other enterprises enforce reliable and secure hybrid networking**.

---

## Cybersecurity Analogy

Think of AWS Direct Connect as your company’s **private, dedicated tunnel through a mountain — built only for you**.  

While VPN rides over the internet highway (where accidents, congestion, and surveillance are always possible), DX is your **exclusive underground railway**, immune to public traffic, eavesdroppers, and BGP hijacks.  

**It’s the fiber-based express lane to AWS — quiet, controlled, and secure.**

## Real-World Analogy

Say SnowyCorp’s NOC in Spokane handles **10 TB of log data daily**. Uploading that to S3 via the internet:

- Eats bandwidth  
- Introduces latency  
- Risks throttling or unpredictable outages  

Instead, they lease a **1 Gbps Direct Connect link to `us-west-2`**. Now their data moves:

- Over a **dedicated circuit**  
- With **no ISP middlemen**  
- At a **predictable and private throughput**  

They layer VPN/IPSec on top for encryption, but now the path itself is **under their control** — no BGP leaks, no internet weather.

---

## How It Works

There are two deployment models:

| **Deployment Type**  | **Description**                                                                 |
|----------------------|----------------------------------------------------------------------------------|
| Dedicated Connection | Provisioned directly from AWS, usually 1 or 10 Gbps physical ports at a DX site |
| Hosted Connection    | Provisioned via an AWS partner (colocation provider), supports 50 Mbps–500 Mbps |

Then you create **Virtual Interfaces (VIFs)**:

| **VIF Type**   | **Use Case**                                                            |
|----------------|-------------------------------------------------------------------------|
| Private VIF    | To access private AWS resources in a VPC (EC2, RDS, etc.)               |
| Public VIF     | To access public AWS services (like S3, DynamoDB) via DX                |
| Transit VIF    | To access multiple VPCs via AWS Transit Gateway (multi-account hybrid)  |

---

## Security Architecture Relevance

| **Security Feature**      | **Relevance**                                                                 |
|---------------------------|--------------------------------------------------------------------------------|
| Bypasses public internet  | Eliminates exposure to DDoS, BGP hijacks, sniffing                            |
| MACsec encryption (opt)   | Physical layer encryption (hardware support required)                         |
| Traffic Segmentation      | Each VIF is isolated — you choose reachable accounts/services                 |
| Supports IPsec overlay    | Add VPN/IPsec over DX for end-to-end encryption                               |
| Compliance & audit        | PCI, HIPAA, FedRAMP, CJIS, and other regulated environments                   |
| Routing control           | Full control over BGP advertisements, prefixes, and ASNs                      |

---

## When to Use AWS Direct Connect

**Use when**:

- You need **low-latency**, **high-throughput**, predictable bandwidth  
- You move **tons of data** (S3 ingestion, replication, backups, logging)  
- You have regulatory mandates to **avoid internet** for sensitive workloads  
- You already have **co-location or cross-connect infrastructure**

**Don’t use when**:

- You have **light/occasional data needs** — VPN is easier  
- You can’t access a **DX location or partner presence**  
- You need **user-level access** — use **Client VPN** for that

---

## SnowyCorp Example

SnowyCorp uses a **10 Gbps Dedicated DX** link from their primary Spokane data center to AWS `us-west-2`. They:

- Create a **Private VIF** to access production VPCs  
- Create a **Public VIF** to access S3 and DynamoDB without public internet  
- Use **MACsec** encryption at Layer 2 (hardware-supported)  
- Add **IPsec overlay** for full stack encryption  
- Monitor traffic using **CloudWatch**, **VPC Flow Logs**, and custom metrics  
- Use **route propagation + ACLs** to block backdoor AWS → internal access  
- Apply **AWS Network Firewall + Firewall Manager** for egress and segmentation  

Their DX setup isn’t just for performance — it’s a **strategic security investment**.  
**It’s how they own the path, not just the packet.**

---

## Pricing Overview

| **Component**           | **Cost**                                                      |
|--------------------------|---------------------------------------------------------------|
| DX Port (1 / 10 Gbps)    | Charged hourly based on port size                             |
| Data Transfer            | Priced per GB — cheaper than public internet egress          |
| Hosted DX from Partner   | Varies — partners may charge additional fees                  |
| MACsec                   | No extra AWS charge — hardware must support it                |
| Cross Connect (colo side)| Paid separately to the colocation facility                    |

**DX is often cheaper per GB than internet**, but setup and colocation costs can add up.

---

## Final Thoughts

**AWS Direct Connect is the gold standard for hybrid connectivity.**

- Secure by path  
- Fast by design  
- Mature enough for enterprise workloads  

It **doesn’t replace VPN** — it **enhances** it.  
It doesn’t mean you ignore **IAM** or **encryption** — it **complements** them.

It’s how SnowyCorp moves from:

> “We're using the cloud”

to:

> “The cloud is an extension of our internal network — secure, fast, and under our governance.”
