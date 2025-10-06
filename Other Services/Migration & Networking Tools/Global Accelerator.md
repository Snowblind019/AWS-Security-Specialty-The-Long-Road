# AWS Global Accelerator

## What Is AWS Global Accelerator

AWS Global Accelerator is a global traffic steering service designed to improve the performance, availability, and fault tolerance of your internet-facing applications. It does this by routing your users through the AWS global network instead of the unpredictable public internet.

When you deploy applications in multiple AWS Regions (e.g., one in Oregon and another in Frankfurt), Global Accelerator:

- Provides static IP addresses to act as a stable entry point  
- Uses Anycast routing to bring user traffic into the nearest AWS edge location  
- Forwards that traffic across the AWS global fiber backbone to your application’s endpoint in the optimal Region  
- Automatically detects and fails over to healthy endpoints in case of failures  

It’s ideal when you need fast, consistent performance for global users and can’t rely on DNS or the latency of public ISPs.

---

## Cybersecurity Analogy

Think of your AWS Regions as data centers guarded by highly trained security teams.  
Now imagine people around the world trying to send messages to your application.

- Without Global Accelerator, those messages take random public roads — filled with potholes, slowdowns, and no protection. A message might get delayed, dropped, or intercepted.  
- With Global Accelerator, you instead give users direct access to your secure private highway — one that's built, maintained, and monitored entirely by AWS.  

Messages enter the nearest AWS entry point, travel across high-speed encrypted lanes, and get delivered quickly to whichever data center is healthy and closest.

From a security standpoint, you’ve just reduced exposure, removed blind spots, and gained end-to-end observability.

## Real-World Analogy

Imagine you're running a chain of warehouses across the world. You ship to customers in dozens of countries.  
Now you want:

- A single customer support phone number for everyone, no matter their region  
- Instant redirection of their request to the nearest warehouse  
- If one warehouse goes offline, calls are automatically rerouted to the next best  

This is what AWS Global Accelerator does — it’s your single, global front door, always directing customers to the best location behind the scenes.

---

## How AWS Global Accelerator Works

### 1. Static Anycast IPs

- When you create a Global Accelerator, you’re given **two static IPv4 addresses**.  
- These IPs are **anycasted** — which means they’re broadcast from all AWS edge locations around the world.  
- When a user connects to one of these IPs, **BGP (Border Gateway Protocol)** automatically routes the traffic to the nearest AWS edge PoP (Point of Presence).  

You can associate custom domain names (via Route 53 or your DNS provider) with these static IPs.

### 2. AWS Global Network Routing

Once inside the AWS edge, the traffic is routed across AWS's **private, high-speed global backbone** instead of traveling over the unreliable public internet.

This minimizes:

- Latency fluctuations  
- Packet loss  
- Congestion-related slowdowns  

It’s the equivalent of giving your traffic access to an **express bullet train** that connects global AWS data centers directly.

### 3. Regional Endpoint Groups

You configure **endpoint groups**, typically per Region.  
Each group contains one or more endpoints, such as:

- Application Load Balancers (ALBs)  
- Network Load Balancers (NLBs)  
- EC2 instances with Elastic IPs  
- Elastic IPs associated with services  

You can define **traffic weights** to distribute load among endpoints and configure **health checks** so that Global Accelerator can detect and automatically fail over if an endpoint or Region becomes unavailable.

### 4. Failover and Health Monitoring

Global Accelerator continuously monitors the health of your endpoints:

- If an endpoint fails its health checks, traffic is **automatically rerouted** to healthy alternatives — within the same Region or another Region altogether  
- **No DNS propagation delay**, no manual updates needed  
- Traffic is shifted instantly, minimizing downtime for users  

This is ideal for **active-passive or active-active** multi-Region architectures.

### 5. Traffic Dialing and Control

You can dial traffic between endpoint groups:

- Set a traffic dial to 0% for one Region if you’re doing maintenance  
- Send a percentage of traffic to a test Region before full rollout (e.g., 10% to Europe, 90% to US)  
- Shift all users to a disaster recovery site instantly by dialing traffic to 100% there  

This gives you **real-time traffic orchestration**, unlike traditional DNS which relies on TTL and resolver caching.

### 6. Static IPs for Security and Compliance

In many enterprise environments, static IPs are required to:

- Whitelist traffic through firewalls or VPNs  
- Meet compliance standards that require fixed ingress points  
- Integrate with legacy partners or third-party systems  

Without Global Accelerator, using ALBs or NLBs directly results in dynamic IPs.  
Global Accelerator solves this with **globally consistent IPs** that don’t change — even if your backend infrastructure moves or scales.

---

## What Global Accelerator Is (And Isn’t)

| It Is                                                   | It Is Not                            |
|----------------------------------------------------------|---------------------------------------|
| A traffic accelerator over AWS's backbone                | A CDN (that’s CloudFront)             |
| A provider of static IP addresses for global entry       | A DNS resolver (that’s Route 53)      |
| A way to improve TCP/UDP latency and resiliency          | A firewall or packet inspector        |
| Region-aware, fault-tolerant routing system              | Not tied to HTTP/S or caching logic   |

---

## Key Use Cases

- Global APIs that serve users in North America, Europe, and Asia  
- Gaming apps needing ultra-low latency and regional failover  
- SaaS platforms with multi-Region HA and global onboarding  
- Hybrid networking with predictable ingress IPs  
- IoT applications with widespread distributed devices  
- Secure B2B services where partners need static IPs for firewall rules

---

## Pricing Model

There are two cost components:

- **Fixed hourly charge per accelerator**  
  - Example: `$0.025 per hour` = ~$18 per month  
- **Data transfer out (DTO)** through the accelerator  
  - Example: `$0.015 per GB` (in addition to normal AWS data transfer)

> **Important:**  
> This is *in addition* to backend service costs (like ALB, EC2, etc.).  
> If you're moving huge volumes of media, CloudFront might be more cost-effective.  
> Global Accelerator is designed for **low-latency, high-resiliency TCP/UDP frontends**, not bulk data delivery.

---

## Security Implications

- Supports TLS termination at the backend ALBs/NLBs  
- Can be used in tandem with **WAF**, **Shield**, and **CloudFront**  
- Integrates with **Firewall Manager** to apply global security policies  
- Does **not decrypt traffic** or inspect payloads — it operates at the **transport layer**  
- Because Global Accelerator does **not expose the origin IP**, it adds a subtle layer of obfuscation against scanning and enumeration.

---

## Snowy’s Example: Secure Dashboard Rollout

Snowy deploys a compliance dashboard used by auditors in the U.S., Europe, and Japan.

- The dashboard is hosted in `us-west-2`, `eu-central-1`, and `ap-northeast-1`  
- Snowy spins up a **Global Accelerator** and maps all traffic to the two static IPs  
- **Regional failover** is configured automatically via health checks  
- **Partners whitelist those two IPs** on their internal firewalls  
- In case of a patch outage in Frankfurt, all traffic shifts to Oregon instantly  
- **TLS termination** is done at the ALBs, and logs are pushed to **CloudWatch** for visibility  

Snowy gains **reliability, control, security, and visibility** — all while maintaining a **single global entry point** for auditors.

---

## Final Thoughts

AWS Global Accelerator is often overlooked but incredibly powerful for workloads requiring **static global entry points**, **fast failover**, and **low-latency routing** across Regions.

It’s *not* a CDN, it’s *not* a DNS service — it’s a **routing optimization layer** that’s laser-focused on **performance**, **uptime**, and **consistency**.

Use it when:

- You need static IPs  
- Your app serves global users  
- You want control over where and how users connect  
- You need to quickly fail over between Regions without DNS delays  

Leave it out if:

- Your use case is focused on HTTP content caching (use CloudFront)  
- You don't need global static IPs  
- You're doing internal-only routing (use Route 53 + VPC endpoints)  

For **distributed SaaS**, **multi-player games**, **real-time APIs**, and **compliance-sensitive environments**, Global Accelerator is a **rock-solid backbone** to build on — especially when you value **resilience, performance, and predictability at scale**.
