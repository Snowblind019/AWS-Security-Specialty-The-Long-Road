# Amazon VPC (Virtual Private Cloud)

## What Is It

Amazon **VPC** (Virtual Private Cloud) lets you provision a **logically isolated section of the AWS cloud** where you define your own IP ranges, **subnets**, routing rules, internet access points, and firewall layers. It’s the **foundation of all modern AWS architecture**.

Every EC2, RDS, Lambda (in **VPC**), container task, or internal endpoint you create lives **inside a VPC**.

But **VPC** isn’t just about IP addresses. It’s your **security perimeter**. It determines:

- What’s public vs private
- Who can talk to whom
- Whether a service can reach the internet or stay internal
- How network traffic flows between AWS accounts, services, and even Regions

### Why this matters for security:

In AWS, the network is **software-defined** — so if you don’t explicitly lock it down, **you’re open**. A public EC2 with port 22 open, a **misrouted** NAT gateway, or a wide-open Security Group can expose sensitive resources instantly.
**VPC** gives you the blueprint to **segment, restrict, monitor, and audit** your cloud traffic — before attackers find the gaps.

---

## Cybersecurity Analogy

Think of AWS as a giant city. A **VPC** is like renting your own gated neighborhood within it.

- You choose the layout (**subnets**)
- You control who comes in or out (**NACLs**, route tables)
- You assign guards to each house (Security Groups)
- You decide if some homes get internet access (Internet Gateway)
- You can even tunnel to another city (**VPC Peering** or **VPN**)

And just like in the real world, the **hardest attacks to detect happen after someone is already inside** — which makes your **internal boundaries inside the VPC** just as important as your public gates.

---

## Real-World Analogy

Imagine a corporate office campus.

- The **VPC** is the entire fenced-off property.
- **Subnets** are the buildings: public ones have visitor access, private ones don’t.
- **Security Groups** are the guards at the door — checking who gets in and out.
- **Route tables** are the campus maps that decide how employees travel between buildings.
- **NAT Gateways** are exit-only turnstiles: employees can leave, but guests can’t come in through them.

> The point isn’t to make the campus invisible. The point is to **control every connection and log every pathway**.

---

## Core Components of a VPC

| **Component**                | **Description**                                                                |
|-----------------------------|--------------------------------------------------------------------------------|
| **CIDR Block**              | Defines the IP range (e.g., 10.0.0.0/16)                                       |
| **Subnets**                 | Split the **VPC** into smaller segments — public/private, zonal, tiered        |
| **Route Tables**            | Determine where packets go (local, **IGW**, NAT, peering, **TGW**, etc.)       |
| **Internet Gateway (IGW)**  | Enables public internet access (required for public-facing EC2s)               |
| **NAT Gateway / NAT Instance** | Allows outbound internet for private **subnets**                            |
| **Security Groups**         | **Stateful**, instance-level firewalls                                         |
| **Network ACLs**            | Stateless, **subnet-level** firewalls                                          |
| **VPC Flow Logs**           | Capture traffic metadata for analysis and detection                            |
| **VPC Peering**             | Connects two **VPCs** directly                                                 |
| **Transit Gateway**         | Hub-and-spoke routing across **VPCs** and **on-prem**                          |
| **Endpoints** (Gateway or Interface) | Private access to AWS services without public internet               |

---

## Network Flow Example

Let’s say a user uploads a file to **Snowy’s** app at `https://app.snowysec.com`:

1. The request hits **CloudFront**, which routes to an **ALB** in a **public subnet**
2. ALB forwards to **EC2 instances** in a **private subnet**
3. EC2 stores metadata in **DynamoDB via VPC endpoint**
4. EC2 uploads file to **S3 over PrivateLink**
5. All outgoing traffic to software updates flows via a **NAT Gateway**
6. **VPC Flow Logs** capture all metadata for audit and **GuardDuty** analysis

> Every step flows **through the VPC**, governed by **routing tables**, **SGs**, and **NACLs** — no public exposure unless explicitly allowed.

---

## Security Use Cases and Controls

| **Use Case**                        | **VPC Component Used**                                                     |
|-------------------------------------|-----------------------------------------------------------------------------|
| Lock down internal services         | Private **subnets**, no **IGW**, **SGs** restrict inbound                   |
| Allow EC2 to reach the internet     | NAT Gateway in public **subnet**                                           |
| Log all traffic in/out of a subnet  | **VPC Flow Logs** enabled at **subnet/ENI** level                          |
| Enforce no public access            | **NACL** blocks 0.0.0.0/0 on ingress                                        |
| Isolate workloads per environment   | Separate **VPCs** for dev, test, prod                                       |
| Prevent S3 bucket from internet access | Gateway endpoint + deny `aws:SourceIp ≠ VPC` in policy                 |
| Secure hybrid access                | Site-to-Site **VPN** or **Direct Connect** + **TGW**                       |

---

## Inter-VPC & Hybrid Connectivity

| **Method**            | **Purpose**                                    | **Notes**                                                |
|-----------------------|------------------------------------------------|----------------------------------------------------------|
| **VPC Peering**       | One-to-one private comms between **VPCs**      | No transitive routing; must manage **SGs** manually       |
| **Transit Gateway**   | Central hub to connect multiple **VPCs** & VPNs| Scalable, transitive routing, route domains              |
| **Site-to-Site VPN**  | Connects **VPC** to **on-prem** data center    | **IPsec** tunnel, encrypted                              |
| **Direct Connect**    | Dedicated fiber to AWS                         | Optional **MACsec**, high throughput, low latency        |
| **VPC Endpoints**     | Private access to AWS services (S3, DynamoDB)  | Keeps traffic off the internet                           |

---

## Real-Life Example: SnowySec Multi-Tier Network

**Snowy’s** architecture is split into **3 VPCs**:

1. **App VPC** — Public + Private **subnets**
   - Public **subnet**: ALB + Bastion
   - Private **subnet**: ECS tasks, Lambda, NAT Gateway
   - **PrivateLink** endpoints to S3, Secrets Manager

2. **Data VPC** — No **IGW**, completely internal
   - Hosts Aurora PostgreSQL, **ElastiCache**, and **OpenSearch**
   - Only reachable via **TGW** and strict **SGs**

3. **SOC VPC** — Centralized detection & logging
   - Runs **GuardDuty**, **Macie**, Security Hub, ELK stack
   - **VPC Flow Logs** from other **VPCs** mirrored here via centralized logging

> All **VPCs** connect through a **Transit Gateway**.
> Traffic between **VPCs** is routed through inspection points, with **VPC Flow Logs**, **GuardDuty**, and **NACLs** acting as **tripwires**.

---

## Pricing Model

| **Item**                   | **Cost Notes**                                                             |
|----------------------------|----------------------------------------------------------------------------|
| **VPC**, **Subnets**, Route Tables | Free                                                           |
| **NAT Gateway**            | ~$0.045/hr + $0.045/GB                                                    |
| **VPC Peering**            | Charged for cross-AZ or cross-region data transfer                        |
| **Transit Gateway**        | ~$0.05 per attachment/hour + per GB data transfer                         |
| **Endpoints (Interface)**  | ~$0.01/hr per AZ + per GB (depends on service)                            |
| **Flow Logs**              | Charged by destination (**CloudWatch Logs** or **S3**) + ingestion fees    |

---

## Final Thoughts

**VPC** is your **cloud perimeter**, your **segmentation layer**, your **guardrail system**.
Everything inside AWS lives in a **VPC** — which means **security starts here**.

But don’t treat your **VPC** like a dumb pipe. Design for:

- **Explicit access** over implicit trust
- **Private by default**, public by exception
- **East-west boundaries**, not just north-south
- **Logging and observability** at the **ENI** and **subnet** level
- **Multi-account, multi-VPC architectures** connected through centralized control points

> Because once an attacker lands inside your **VPC** — **you better hope you built more than just one wall.**
