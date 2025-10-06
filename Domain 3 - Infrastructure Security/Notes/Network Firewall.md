# AWS Network Firewall

## What Is It

AWS Network Firewall is a fully managed Layer 3/Layer 4/Layer 7 firewall built directly into your VPCs. It provides:

- **Stateful traffic filtering** (track connections, not just packets)  
- **Deep packet inspection (DPI)** using Suricata rules  
- **Domain-based blocking** (FQDNs like `*.malware.com`)  
- **IP, port, protocol filtering**  
- **TLS inspection support**  
- **Central logging** to CloudWatch, S3, or Kinesis  

**Why it matters in security:**  
Most AWS environments are secure *inside* the cloud, but porous *at the edges*. Network Firewall acts as a security perimeter around your VPCs — not just blocking bad IPs, but inspecting payloads, blocking outbound exfiltration, and defending East-West traffic between subnets, workloads, and even Regions.

Unlike Security Groups (which are stateless per packet), Network Firewall can say:

> “That connection looks like outbound beaconing to a C2 server. Block it.”  
> “This S3 access is wrapped in a Tor tunnel. Deny and log it.”

It’s your **cloud IDS/IPS**, built into the fabric.

---

## Cybersecurity Analogy

Imagine you’ve got a smart border checkpoint.

- **Security Groups** = metal detectors at individual doors  
- **NACLs** = security guards checking each ID without memory  
- **Network Firewall** = AI-powered border patrol checkpoint:

  - Knows if someone is coming back too often  
  - Detects payloads that match known threat signatures  
  - Has a clipboard of banned destinations  
  - Allows safe commerce while blocking contraband  

It watches the **flows**, not just the **doorframe**.

## Real-World Analogy

Think of a smart customs gate at an international airport.

- Checks passports (IP rules)  
- Flags suspicious behavior patterns (stateful inspection)  
- Detects banned substances (DPI)  
- Redirects flagged people to secondary inspection (log + alert)  

And best of all? **You don’t have to run the gate** — it scales automatically.

---

## How It Works

AWS Network Firewall is deployed inside a dedicated VPC subnet called a **firewall subnet**, within a **VPC firewall endpoint**. It acts as a central inspection point for traffic.

### Key Components

| Component         | Description                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| **Firewall**       | Logical resource that holds rules, endpoints, logging, etc.                |
| **Firewall Policy**| Collection of rule groups + logging config                                 |
| **Rule Groups**    | Stateless or Stateful (Suricata rules, domain rules, or IP filters)        |
| **Firewall Endpoint**| The network interface inside a subnet that handles traffic              |
| **Routing Integration** | Route tables must redirect traffic to the firewall subnet             |

---

## Types of Rule Groups

| Type         | Use Cases                                                                 |
|--------------|---------------------------------------------------------------------------|
| **Stateless** | Simple packet filtering (IP, port, protocol) — used at the front line     |
| **Stateful**  | Deep inspection (Suricata, DNS, domain, payload) — sees full flow         |
| **Domain-based** | Block access to known bad domains (e.g., `*.crypto-malware.net`)     |
| **Suricata rules** | Full IDS/IPS syntax — allow/deny/mirror based on DPI               |

**Example Stateless Rule:**  
“Drop all outbound TCP port 6667 (IRC)”
**Example Stateful Rule:**  
“Alert if payload matches known Cobalt Strike beacon signature”

---

## SnowySec Traffic Flow (Simplified)


Let’s say **SnowySec** has a tiered VPC with public and private subnets:

- Firewall Subnet sits between **NAT Gateway** and **Internet Gateway**
- Route table sends outbound Internet traffic from private subnets → Firewall

### 🔹 Network Firewall Applies:

- **Stateless rule:** Deny all TCP to `198.51.100.10`  
- **Stateful rule:** Alert on DNS lookups to `*.coinminer.cx`  
- **TLS rule:** Block SSL traffic to IPs without valid certs  

- **Logging:** All blocked/allowed connections sent to S3  
- **Alerting:** Findings forwarded to **Security Hub**

Result:  
SnowySec has **inline threat detection, exfiltration control, and an audit trail** — without deploying any EC2-based IDS.

---

## Use Cases


| Use Case                           | Feature Used                                           |
|------------------------------------|--------------------------------------------------------|
| Stop known bad domains             | Stateful domain list rule group (`*.tor2web.com`)      |

| Prevent IRC-based C2 traffic       | Stateless deny TCP port 6667                           |
| TLS inspection for HTTPS exfil     | TLS-based Suricata rules (deep inspection)            |
| Block high-risk geo IP ranges      | IP deny rules (stateless)                              |
| Alert on malware signature payload | Stateful Suricata rule w/ logging                      |
| Detect DNS tunneling exfil         | Stateful DNS packet rule + resolver logs              |
| Isolate VPCs by trust level        | Separate firewall endpoints per subnet                |
| Audit network attempts             | Logging to S3 + CloudWatch metrics                    |

---

## Security Event Flow Example

**Scenario:**  
Compromised EC2 in `PrivateSubnet-A` attempts to beacon out to `beacon.l33t-c2.xyz`

1. Route table forces outbound through Firewall Endpoint  
2. Stateful rule matches DNS query → `*.l33t-c2.xyz`  
3. Traffic is denied  
4. Log is sent to **S3**  
5. **CloudWatch** Metric Filter triggers alert → **SNS** → **Slack**  
6. **GuardDuty** enriches flow data, confirms persistence  
7. **Lambda** remediates EC2 via tag + quarantine SG  

**Result:**  
SnowySec shuts down the C2 channel in under 30 seconds with a full audit trail.

---

## Integration with Other Services

| Service           | Integration Benefit                                              |
|------------------|------------------------------------------------------------------|
| **CloudWatch Logs** | Real-time alerting on blocked/allowed flows                  |
| **S3**              | Long-term archive of traffic metadata                        |
| **Kinesis**         | Live log streaming into SIEMs or Lambda pipelines            |
| **Security Hub**    | Normalize and triage findings                                |
| **GuardDuty**       | Layered detection via flow + DNS + Firewall + threat intel  |
| **AWS Organizations** | Centralized firewall deployments in hub-and-spoke VPCs     |

---

## Pricing Overview (2025 Estimates)

| Item                     | Cost Estimate                                         |
|--------------------------|------------------------------------------------------|
| **Firewall Endpoint Hourly** | ~$0.395/hr per AZ                              |
| **Data Processed**           | ~$0.065 per GB processed                        |
| **Logging to S3/CloudWatch**| Billed by destination service                    |
| **Rule Evaluation**         | Included in endpoint hourly cost                |

> **Note:** Heavy traffic + deep inspection = higher data costs. But worth it in regulated or high-risk environments.

---

## Final Thoughts

Most teams stop at **Security Groups** and **NACLs**, but that’s like locking your front door while leaving the windows open.

**AWS Network Firewall** is what transforms your cloud into a **defensible castle**:

- Monitors all traffic  
- Inspects payloads  
- Responds in real-time  
- Logs everything  
- Blocks exfiltration  
- Detects malware patterns  

And you don’t have to manage infrastructure.

> Security at scale isn’t just IAM and encryption.  
> It’s **visibility + enforcement at the network layer**.

If SnowySec’s workloads ever get hit, this firewall won’t just block the threat — it’ll **record it, alert it, route it**, and let the rest of the pipeline **contain and respond**.

**Build with defense in depth.**  
Let this be your **cloud perimeter**.

