# Network ACLs (NACLs)  

## What Is It

Network ACLs (Access Control Lists) are subnet-level firewalls that control traffic entering or leaving an entire subnet in your Amazon VPC. Unlike Security Groups, NACLs are stateless, meaning every single request and response is evaluated independently — there’s no memory of prior connections.  
They process traffic before it even hits your instance, enforcing rules at the perimeter of your subnet.

**Why this matters:**  
Security Groups are great for controlling access to specific resources, but what if you want to block a known malicious IP range at the subnet level, or apply blanket deny rules for non-compliant protocols? That’s where NACLs shine — they operate at the first line of network entry, often acting as a coarse filter to reduce the blast radius of a breach or misconfiguration.

---

## Cybersecurity Analogy

Imagine your subnet is a gated community.  
Security Groups are the guards at each home, while NACLs are the checkpoint at the neighborhood entrance.  

But this checkpoint doesn’t care who you are — it just follows its list.  
If you match a rule, you’re allowed. If you don’t, you’re stopped.  

Also: this guard doesn’t remember if you just walked in 10 seconds ago.  
If you want to come back in, you go through the entire screening again.  
That’s stateless logic.

## Real-World Analogy

Picture a toll booth at the entrance of a private road. Every vehicle is checked — every time.  

- It doesn’t remember that you were allowed in yesterday.  
- It doesn’t assume that returning traffic is okay.  
- If your direction isn’t explicitly allowed, you don’t get through.  

Now apply that to IP packets, and you’ve got a NACL.

---

## How It Works

Every NACL has **two rule sets**:

- **Inbound Rules** — evaluated for traffic coming into the subnet  
- **Outbound Rules** — evaluated for traffic leaving the subnet  

- Rule number (1–32766; lower numbers take precedence)  
- Protocol (TCP, UDP, ICMP, ALL)  
- Port range (e.g., 80–80 for HTTP, or ALL)  
- Source/Destination (CIDR blocks)  
- Action: ALLOW or DENY  

### Key characteristics:

| **Feature**             | **Behavior**                                           |

|-------------------------|--------------------------------------------------------|
| Stateless               | Must allow traffic in both directions explicitly       |
| Ordered Evaluation      | Rules processed in ascending order; first match wins   |
| Default Behavior        | If no rule matches, traffic is denied by default       |
| Associated to Subnets   | Each subnet can only have 1 NACL at a time             |
| Shared Across Subnets   | NACLs can be reused across multiple subnets            |
| Logging                 | No native logging; use VPC Flow Logs instead           |

---

## NACLs vs Security Groups

| **Property**     | **NACL**                             | **Security Group**                      |
|------------------|--------------------------------------|------------------------------------------|
| **Scope**        | Subnet-level                         | Resource-level (ENI)                     |

| **Statefulness** | Stateless — both directions must be allowed | Stateful — return traffic allowed automatically |
| **Rules**        | Allow or Deny                        | Allow only                               |
| **Rule Eval**    | Ordered (lowest first)               | All rules evaluated                      |
| **Defaults**     | Default NACL allows all              | Default SG denies all                    |
| **Best For**     | Broad deny lists, subnet-wide filtering | Precise instance-level access control  |

---

## Common Use Cases

| **Use Case**                          | **NACL Rule Configuration**                                |
|---------------------------------------|-------------------------------------------------------------|
| Block all SSH access from the internet | Inbound: DENY TCP 22 from 0.0.0.0/0                         |
| Allow HTTP/HTTPS from the internet     | Inbound: ALLOW TCP 80/443 from 0.0.0.0/0                   |
| Allow response traffic from web servers| Outbound: ALLOW TCP 1024–65535 to 0.0.0.0/0                |
| Isolate backend subnet from public     | Inbound: DENY ALL from public CIDR range                   |
| Block known bad IP ranges              | Inbound: DENY ALL from 203.0.113.0/24                      |
| Egress filtering for compliance        | Outbound: ALLOW ports 443/80; DENY ALL others             |

---

## Network Flow Example

Let’s say **Winterday’s VPC** has:

- A public subnet for an ALB  
- A private subnet for EC2 instances  

**Flow:**  
1. Client makes HTTPS request to ALB  
2. NACL on public subnet allows TCP 443 inbound  
3. NACL allows outbound ephemeral ports to send response  
4. ALB forwards traffic to EC2 in private subnet  
5. Private subnet NACL allows inbound from ALB CIDR on port 443  
6. EC2 replies → outbound rule allows ephemeral range  

**Failure Example:**  
If Winterday forgets to add the outbound rule on the public subnet, return traffic is blocked.  
That’s the **stateless pain point** — *both directions must be explicitly allowed.*

---

## Security Automation + Detection

| **Security Concern**                    | **Tool/Strategy**                                           |
|----------------------------------------|-------------------------------------------------------------|
| NACL allows SSH from 0.0.0.0/0          | AWS Config rule + EventBridge + Lambda remediation          |
| Open to ALL traffic (0.0.0.0/0 ANY)     | Security Hub finding + central NACL scanner                |
| No return traffic allowed               | Flow logs + Reachability Analyzer                          |
| Known bad IPs accessing subnets         | GuardDuty + Athena lookup → update NACL deny rules         |
| Inconsistent NACLs across subnets       | Custom Lambda to audit and normalize rule sets             |

---

## Real-Life Example: SnowySec Perimeter Hardening

To comply with SOC 2 and reduce attack surface, **SnowySec** enforced:

- A hardened default NACL:
  - DENY all inbound except ports 80, 443  
  - DENY port 22 from all IPs  
  - ALLOW outbound ports 80, 443, 53 (DNS)  
  - DENY all other outbound traffic  

- **GuardDuty + EventBridge integration**:  
  Recon behavior detected (e.g., port scanning) → Lambda added `DENY ALL` for that CIDR to NACL.  
  → Subnet blocked at the edge within seconds.

- **VPC Flow Logs → Athena**:  
  Tracked patterns of blocked connections.

- **App subnet NACLs**:  
  ALLOW only traffic from trusted internal CIDRs — blocked lateral movement in red team sim.

**Result:**  
During a simulated EC2 compromise, the attacker couldn’t:

- Pivot laterally  
- Reach the internet  

NACLs acted as a *killbox* around the subnet.

---

## Pricing

| **Feature**           | **Cost**                                 |
|------------------------|-------------------------------------------|
| NACL Rules             | Free                                      |
| Evaluation per packet  | Free                                      |
| Flow Log visibility    | Standard CloudWatch/S3 pricing applies    |

---

## Final Thoughts

Network ACLs don’t replace Security Groups — they **reinforce** them.

They’re **stateless**, **brutal**, and **surgical**.  
No memory, no mercy. Perfect for:

- Quick reaction to suspicious IPs  
- Hard perimeter enforcement  
- Compliance-driven egress filtering  
- Subnet-wide kill switches  

**But use them wisely.**  
A single missing rule can blackhole your traffic.  
And no, AWS won’t tell you which packet got dropped.

**Treat NACLs as your early warning fence. Let Security Groups be your precision guards.**

