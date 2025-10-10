# AWS VPN

## What Is AWS VPN

**AWS VPN** allows you to securely connect your **on-premises network, data center**, or even other cloud environments to your **Amazon VPC** using an **encrypted IPsec tunnel** over the internet.

It’s part of a **hybrid cloud architecture**, enabling secure, scalable communication between cloud and **on-prem** infrastructure. You typically use it to:

- Extend your internal corporate network to the cloud
- Route specific traffic through AWS
- Support **failover** connectivity when **Direct Connect** is down

In security-sensitive **orgs** like **SnowyCorp**, AWS VPN is the *secure pipe* — the layer that makes sure **data-in-transit is encrypted, auditable, and protected from interception.**

---

## Cybersecurity Analogy

Think of AWS VPN as your **company’s armored convoy** driving across the open internet.
Instead of sending unencrypted packets across the Wild West, you're bundling everything up in a **military-grade transport truck**, slapping encryption on it, and driving it through hostile territory with **secure keys and strong authentication**.

The tunnel doesn’t protect what happens once it’s inside either end — it protects **everything in transit** from prying eyes and packet sniffers.

## Real-World Analogy

Let’s say Blizzard runs a data center in Spokane and wants to migrate workloads to a **VPC** in us-west-2.

Instead of moving everything to the cloud at once (risky), they start routing certain workloads (like backups, identity federation, log aggregation) through a **VPN tunnel** — gradually building trust and visibility in the cloud.

As they scale, they might move to **Direct Connect** for performance, but VPN is the **first secure bridge** between home base and cloud frontier.

---

## How It Works

There are **two core components** involved:

| Component                              | Description                                                                 |
|----------------------------------------|-----------------------------------------------------------------------------|
| **Customer Gateway (CGW)**             | Your *on-premise device* or software client. It’s the initiator of the tunnel (e.g., Cisco ASA, Palo Alto, pfSense, etc.) |
| **Virtual Private Gateway (VGW)** or **Transit Gateway (TGW)** | AWS-side component that terminates the VPN connection inside your **VPC**. |

Once configured:

- An **IPsec tunnel** is established (you can have 2 for redundancy)
- **Routing** is set up using either static or **BGP dynamic routing**
- You define **which prefixes** are allowed in/out
- Optional **CloudWatch alarms**, **Flow Logs**, and **NACLs** can monitor and secure the setup

---

## Types of AWS VPN

| Type                                | Description                                                                 |
|-------------------------------------|-----------------------------------------------------------------------------|
| **Site-to-Site VPN**                | Connects your **on-prem** network or another cloud provider to your **VPC** using **IPsec** tunnels |
| **Client VPN (OpenVPN)**            | Lets users connect to AWS securely over **OpenVPN** protocol from laptops, mobile devices |
| **CloudHub (Multi-site over VGW)**  | Connects multiple remote networks to the same **VGW** using **BGP**        |
| **Accelerated VPN (Global Accelerator)** | Uses AWS edge locations to optimize VPN traffic performance (premium setup) |

---

## Security Architecture Relevance

| Security Feature       | Details                                                                 |
|------------------------|-------------------------------------------------------------------------|
| **Encryption in Transit** | **IPsec** tunnels with AES-256 or stronger ciphers                   |
| **Authentication**        | **Pre-shared key (PSK)** by default; supports certificate-based **auth** (for Client VPN) |
| **High Availability**     | Two tunnels per VPN connection; supports route **failover**          |
| **Auditability**          | Fully integrated with **VPC Flow Logs**, **CloudTrail**, **GuardDuty** |
| **Access Control**        | Combine with **Security Groups**, **NACLs**, **IAM** to restrict access inside the **VPC** |
| **Blast Radius Control**  | Use **route tables + network segmentation** to limit what **on-prem** can access |
| **Cost Predictability**   | Priced per connection per hour + data transfer                        |

---

## When to Use AWS VPN

**Use when:**

- You need **quick, secure hybrid connectivity**
- You're migrating workloads from **on-prem** and need a **bridge**
- You want a **redundant backup** for Direct Connect
- You need secure user-level remote access (Client VPN)

**Don’t use when:**

- You need **low-latency, high-throughput** connections (use Direct Connect)
- You **don’t trust the internet at all** (use **DX** with **MACsec** or **MPLS**)

---

## SnowyCorp Example

Snowy sets up:

- Two **Site-to-Site VPN tunnels** from their **NOC** to a **VGW** in AWS us-west-2
- **BGP routing** to allow dynamic **failover**
- **Prefix filters** to only allow 10.10.0.0/16 and block internal **subnets**
- **CloudWatch** alarms on tunnel state and **VPC Flow Logs** for auditing
- **GuardDuty** to detect unusual cross-tunnel behavior
- Later, they add **Client VPN** for remote engineers to access AWS **dev** environment

The VPN isn’t just a pipe — it’s **instrumented, segmented, monitored, and revocable**.
No trust by default. Snowy-style.

---

## Pricing Summary

| Feature                 | Pricing Model                                                  |
|-------------------------|----------------------------------------------------------------|
| **Site-to-Site VPN**    | Per hour per connection + data out                            |
| **Client VPN**          | Per active client connection/hour + hourly endpoint fee       |
| **Accelerated VPN**     | Additional charges for Global Accelerator usage               |

---

## Final Thoughts

VPN is **step 1** in hybrid security.
But just setting up a tunnel isn’t enough — you have to:

- Define what routes go where
- Monitor everything crossing it
- Segment access once inside AWS

If the cloud is your new data center, then VPN is the **drawbridge** — secure, but only if you control *who’s crossing, what they’re carrying, and where they go once inside*.
