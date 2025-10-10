# NLB Logs

## What Are NLB Logs

**Network Load Balancers (NLBs)** operate at **Layer 4 (TCP/UDP)**, unlike ALBs which live at Layer 7. That means you’re not seeing HTTP headers, cookies, or URLs — you're getting **connection-level data** like:

- Source/Destination IP addresses
- Source/Destination ports
- TLS handshake metadata (if termination is enabled)
- Connection start/end time
- Bytes sent and received
- TLS version and cipher

This is **wire-level visibility**, not application-level.

### Why It Matters

- If you're balancing **non-HTTP protocols** (TLS, RDP, MySQL, DNS), **NLB** is your only AWS-native option.
- If you're under a **DDoS**, brute-force, or port-scanning attack — these logs tell you *who connected* and *how*.
- For **VPNs, SMTP/POP3, bastion hosts, or gRPC**, NLB logs help you trace activity *even without app-level data*.

---

## Cybersecurity Analogy

NLB logs are like **airport runway surveillance footage**.

- You're not reading people's **boarding passes** (like ALB might)
- You're seeing:  
  - *Plane XYZ landed at Gate 7*  
  - *Stayed 3 minutes*  
  - *Came from X country*  
  - *Took off again*

It’s not deep… but when you need **who/when/how long** — this is the log you grab.

## Real-World Analogy

SnowyCorp runs a **proprietary trading system** using raw TCP over an NLB.

- **Trade latency spikes**
- **No alarms fire**
- **No app logs show anything**

Snowy enables **NLB Access Logs** and sees:

- A single IP hammering port 443 with *empty payloads*
- Millions of short connections opening and closing
- It’s a **low-and-slow SYN flood DDoS**

Now they can geo-block or firewall the attacker **before customer impact**.

---

## How It Works

NLB logging is **off by default**. Once enabled, AWS delivers logs in **plain text** to an **S3 bucket** of your choice.

### Log Fields

| Field          | Description                                         |
|----------------|-----------------------------------------------------|
| `type`         | Always `connection-log`                             |
| `version`      | Schema version                                      |
| `account-id`   | Your AWS Account ID                                 |
| `interface-id` | ENI used by the NLB                                 |
| `srcaddr`      | Source IP address                                   |
| `dstaddr`      | Destination IP address                              |
| `srcport`      | Source port                                         |
| `dstport`      | Destination port                                    |
| `protocol`     | `6` = TCP, `17` = UDP                               |
| `packets`      | Total packets                                       |
| `bytes`        | Bytes transferred                                   |
| `start` / `end`| Connection timestamps (Unix epoch)                  |
| `action`       | `ACCEPT`                                            |
| `log-status`   | `OK`, `NODATA`, or `SKIP`                           |

### TLS Metadata (if TLS termination is enabled)

- TLS version
- Cipher suite
- Target response time
- Connection status
- Negotiated ALPN protocol (HTTP/2 or gRPC)

> Huge win for encrypted workload observability.

---

## How to Enable It

1. Go to **EC2 → Load Balancers**
2. Select your **Network Load Balancer**
3. Under **Attributes**, enable **Access Logs**
4. Choose an **S3 bucket**
   - Ensure proper **bucket policy** for log delivery
5. Logs are delivered as **`.log.gz` compressed files**

> **Best Practice:** Use separate S3 prefixes per environment:
```
/nlb-logs/prod/
/nlb-logs/staging/
```

You can query them with **Athena**, or ingest into:

- Splunk
- Elastic Stack (ELK)
- AWS Security Lake
- Custom Lambda analytics

---

## Use Cases for Security and Ops

| Use Case                        | What to Look For                                                 |
|----------------------------------|------------------------------------------------------------------|
| **Port Scanning**                | Multiple destination ports across many ENIs                     |
| **Brute-Force Detection**        | Repeated TCP hits to RDP/SSH (22, 3389)                          |

| **SYN Flood or Low-Slow DDoS**   | High connections, low byte count                                 |
| **TLS Cipher Downgrade Attacks** | Weak cipher negotiation attempts (requires TLS termination)     |
| **Internal Compromise / Beaconing** | Unexpected egress to unapproved IPs                        |

| **TLS 1.0/1.1 Usage**            | Compliance red flags                                             |
| **VPN or Bastion Auditing**      | Track source IPs + session durations                             |

---

## Athena Example: Find Top Talkers

```sql
SELECT srcaddr, COUNT(*) AS connections
FROM nlb_logs
WHERE start_time BETWEEN TIMESTAMP '2025-09-27 00:00:00'
  AND TIMESTAMP '2025-09-27 23:59:59'
GROUP BY srcaddr
ORDER BY connections DESC
LIMIT 20;
```

---

## Pricing Model

| Component              | Cost Estimate                       |
|------------------------|-------------------------------------|
| **NLB Access Logs**    | Free to generate                    |
| **S3 Storage**         | Billed by GB/month                  |
| **Athena Queries**     | ~$5 per TB scanned                  |
| **Log Processing (Glue/Lambda)** | Billed separately          |
| **TLS Termination**    | Slightly higher per-connection cost |

---

## Snowy Real-Life Use Case

BlizzardMedia runs a **gRPC backend** behind an NLB with TLS termination.

Symptoms:

- Latency spikes at **3:00 AM UTC**
- No CloudWatch metrics triggered
- No alarms fired

Snowy:

1. Enables **NLB Access Logs**
2. Filters logs using **Athena** for the 10-minute window
3. Finds 1,000+ TLS connections from 4 IPs
4. ALPN mismatches + connection resets

**Root Cause:** Partner’s **misconfigured load tester**  
**Resolution:** Blocked offending IPs and filed bug with partner

> Without NLB logs: it’s guessing.  
> With NLB logs: it’s **evidence**.

---

## Final Thoughts

**NLB Logs** are:

- Low-level
- Packet-agnostic
- Protocol-flexible

They’re not for pretty dashboards.  
They’re for **forensics**, **compliance**, and **layer 4 observability**.

If **ALB logs** are your **door camera**,  
then **NLB logs** are your **motion sensor at the fence**.


They don’t tell you what someone said.  
But they **do** tell you:

- Who came
- What door they knocked on
- What cipher they offered
- How long they stayed

In modern cloud security, sometimes that’s all you need to:

- Reconstruct a breach
- Confirm lateral movement
- Detect early compromise

**Turn them on. Query them smart. Archive them well.**  
Because when it hits the fan, you won’t wish for less telemetry.
