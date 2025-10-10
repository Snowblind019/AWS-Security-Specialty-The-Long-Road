# Security Groups (SGs)

## What Is It

**Security Groups** in AWS are **virtual firewalls** that operate at the **Elastic Network Interface (ENI)** level — meaning they are applied **directly to the network card** of your resource (EC2, RDS, Lambda in VPC, etc).

They control **inbound and outbound traffic** using **allow-only rules**.
There are no deny rules. Everything is denied by default.

### Why This Matters

If a hacker finds an open port — like **port 22** on an EC2 exposed to the world — they have a **door to walk through**. SGs ensure that only **explicitly allowed traffic** is permitted, and only from **known sources**, **ports**, and **protocols**.

They're **stateful** — once a connection is allowed in, the response is automatically allowed back out.

In a well-designed architecture, Security Groups become the **first gate** for every workload.
Even if IAM is perfect and the app is patched — expose the wrong port to the wrong CIDR, and it’s game over.

---

## Cybersecurity Analogy

Think of each **instance as a locked door**.
**Security Groups** are the **bouncers** posted at the entrance.

They check IDs:

- Who are you? *(source IP or SG)*
- What are you here for? *(port/protocol)*
- Are you on the list?

They don’t remember past visitors, but they’ll allow replies to those they let in.

**Unlike NACLs** (which guard entire buildings/subnets), SGs **guard each door individually**.

## Real-World Analogy

Imagine a **gated apartment building** where each tenant hires their own doorman.

- One tenant only lets friends from Apartment A in on Sundays (port 80, SG-A).
- Another allows anyone with a delivery badge in through the side door (0.0.0.0/0 on port 443).
- One tenant refuses to talk to anyone unless **they were first contacted** by them (outbound-only model).

That’s how **Security Groups** work:
Each tenant sets their own access rules, and those rules are enforced constantly — with **return traffic allowed automatically**.

---

## How It Works

Security Groups have **two sets of rules**:
- **Inbound Rules**: Define what traffic is allowed *into* the resource
- **Outbound Rules**: Define what traffic is allowed *out of* the resource

### Each rule includes:

- **Protocol**: TCP, UDP, ICMP, etc
- **Port Range**: e.g., 22 for SSH, 443 for HTTPS

- **Source (inbound)** or **Destination (outbound)**:

  - CIDR block (e.g., `192.0.2.0/24`, `0.0.0.0/0`)
  - Another Security Group (e.g., “only allow traffic from App SG”)

### Key Characteristics

| **Trait**        | **Behavior**                                     |
|------------------|--------------------------------------------------|
| **Stateful**     | Return traffic is automatically allowed          |
| **Additive**     | Multiple SGs = all rules combined                |
| **Default Deny** | All traffic is denied unless explicitly allowed  |
| **No Deny Rules**| You can’t explicitly block traffic               |
| **Max Rules**    | 60 inbound + 60 outbound per SG (soft limit)     |
| **ENI Limit**    | Up to 5 SGs per ENI — all rules are evaluated    |

---

## Common Use Cases

| **Use Case**                    | **Security Group Logic**                         |
|----------------------------------|--------------------------------------------------|
| Only allow web traffic to ALB    | Inbound TCP 443 from `0.0.0.0/0`                 |
| Lock down EC2 access to API      | Inbound TCP 443 from App SG ID only             |
| Restrict DB access               | Inbound port 3306 only from App SG or CIDR      |
| Prevent outbound internet access| Remove outbound `0.0.0.0/0` rule                |
| Service-to-service trust         | Use SG referencing (App SG → DB SG)             |
| Temporary admin access           | Add IP to port 22 temporarily, then remove      |

---

## Comparison: SGs vs NACLs

| **Feature**         | **Security Group**       | **Network ACL**                 |
|---------------------|--------------------------|----------------------------------|
| **Scope**           | ENI (resource-level)      | Subnet-wide                     |
| **Stateful**        | ✔️ Yes                    | ✖️ No                           |
| **Rules**           | Allow only                | Allow or deny                   |
| **Evaluation**      | All rules evaluated       | Lowest rule number matched      |
| **Default Behavior**| Deny all                  | Allow all (in default NACL)     |
| **Best For**        | EC2, RDS, Lambda in VPC   | Blanket subnet restrictions     |

---

## Security Architecture Flow

Let’s walk through a 3-tier app built by **Snowy**:

### Frontend (Public Subnet)
- SG allows **inbound TCP 443** from `0.0.0.0/0`
- Outbound allows only **TCP 443 to backend SG**

### App Tier (Private Subnet)
- SG allows **inbound from frontend SG** on port 443
- Outbound allowed only to **DB SG** and **S3 endpoint**

### Database Tier (Private Subnet, No Internet)
- SG allows **inbound MySQL (3306)** from App Tier SG
- Outbound limited to **VPC DNS** and **backup services**

This model uses **SG referencing** instead of CIDRs, enabling **tight trust boundaries** that adapt **automatically as instances scale**.

---

## Security Automation & Detection

| **Risk**                           | **Detection Tool**                        | **Remediation**                                |
|------------------------------------|-------------------------------------------|------------------------------------------------|
| Open SSH (port 22) to the world    | Config, Security Hub, GuardDuty           | Auto-remove rule or alert via Lambda           |
| Wide open outbound traffic         | VPC Reachability Analyzer                 | Deny all egress; allow specific destinations    |
| Excessive SGs with no resources    | Custom Lambda + tag scan                  | Cleanup script, IAM enforcement                |
| Legacy TLS exposure via SG         | AWS Inspector with SG context             | Use ALB TLS termination + policies             |

---

## Real-Life Example: **SnowySec Zero Trust Layering**

Snowy’s security architecture enforces **least-privilege** via layered SGs:

- All workloads must use **SGs assigned via Launch Template** — no ad-hoc assignments
- Only **internal ALBs** can access app servers — enforced with SG referencing

- **Bastion hosts** have their own SG with port 22 access from **SnowySec’s static IPs**
- Any attempt to add port **3389** or **80** triggers:
  → EventBridge rule

  → Lambda auto-removal

  → SNS alert to SecOps

Logs of all SG changes are captured via **CloudTrail**, then piped into **Athena + QuickSight dashboards**.


> When a misconfigured Jenkins server tried to accept traffic from `0.0.0.0/0` on port `8080`, the system auto-rolled back the change in **under 30 seconds**.

---

## Pricing

| **Feature**             | **Cost**                                |
|--------------------------|-----------------------------------------|
| Create/Attach SGs        | ✔️ Free                                    |
| Rule Evaluation          | ✔️ Free                                    |
| Logging changes (CloudTrail) | Standard CloudTrail pricing applies  |

---

## Final Thoughts

**Security Groups** are the **first responders** to any unauthorized connection attempt.

They’re quiet, customizable, and powerful — **but only when treated as a layered control**, not as an afterthought.

The worst cloud breaches don’t always come through IAM or malware.
They come through a **single forgotten open port** on an old EC2.

**Build SGs with intent.**
**Audit them regularly.**
And **never** leave port `22` open to the world — unless you like being scanned every 10 seconds.
