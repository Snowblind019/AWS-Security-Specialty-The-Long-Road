# Amazon S3 Server Access Logs (a.k.a. S3 Access Logs)

> Also known as: **S3 Access Logs**  
> Official name: **S3 Server Access Logging**

---

## What Is It

Amazon S3 Server Access Logging is a feature that records every access request made to your S3 buckets. It gives you a detailed history of activity including:

- Who accessed the bucket  
- Which object they requested  
- What action they took (GET, PUT, DELETE, etc.)  
- When it happened  
- Where it came from (IP)  
- Whether it succeeded or failed  
- How big the object was  
- How long it took  
- What tool they used (CLI, SDK, browser)

These logs are stored as text files in another S3 bucket that you choose. Each line in a log file represents one request. The logs use an Apache-style format, with one entry per access event.

> **Important:** Logging is *not* enabled by default — you must opt-in and configure it per bucket.

---

## Why It’s Important

- **Security auditing**: Who accessed sensitive files, and how?  
- **Compliance**: Necessary for HIPAA, PCI-DSS, SOX, and more.  
- **Incident response**: Helps reconstruct what happened during a breach or anomaly.  
- **Access analysis**: Detect patterns, misconfigurations, abuse, and unusual behavior.  
- **Forensics**: Create a timeline of data access leading up to an incident.  
- **Billing and usage optimization**: Understand who’s accessing large objects and when.

---

## Cybersecurity Analogy

Your S3 bucket is like a **secure vault** or **file room** in a building.

- **CloudTrail** is like a security system that logs administrative actions — who added a new lock or changed access rules.  
- **S3 Server Access Logs** are like a **security guard’s notebook** or **surveillance camera** — they log who actually opened the drawers, what they looked at, and what they copied or deleted.

Without access logs, someone could walk into your vault, take sensitive records, and you’d have no idea it happened.

---

## Real-World Analogy

Imagine a hotel with thousands of rooms (S3 objects).  
**CloudTrail** is the system that logs who books rooms and who reconfigures room access.  
**S3 Access Logs** are the **security camera footage** or **visitor sign-in sheet** that shows:

- Who entered which room  
- What time  
- What they did inside (opened minibar, stole towel, etc.)

You don’t see inside the room, but you know who interacted with it.

---

## How It Works

You enable logging per bucket and configure:

- A **target bucket** (where logs will be written)  
- An optional **prefix** (to organize logs by source bucket or category)

### The Logs Are:

- Written in plaintext, one request per line  
- Delivered to the target bucket as `.log` files  
- Partitioned by time (hourly batches)  
- Not retroactive — they start from the moment you enable logging

> The target bucket must be in the **same AWS Region** as the source bucket.  
> **Do NOT** log to the same bucket you're logging — it creates recursive logs and log spam.

---

## Log Format (Fields Overview)

Each log line contains the following fields:

- `bucket_owner` – Canonical ID of the bucket owner  
- `bucket` – Name of the accessed bucket  
- `time` – When the request occurred  
- `remote_ip` – IP address of the requester  
- `requester` – IAM user/role or "anonymous"  
- `request_id` – Unique request ID for debugging  
- `operation` – What was done (GET, PUT, DELETE, etc.)  
- `key` – The object key (path) accessed  
- `request_uri` – Full HTTP request  
- `http_status` – HTTP response code (e.g., 200, 403, 404)  
- `error_code` – If any error occurred (e.g., AccessDenied)  
- `bytes_sent` – Size of the response sent  
- `object_size` – Size of the object accessed  
- `total_time` – Time to complete request  
- `turnaround_time` – Server-side latency  
- `referrer` – Referring URL  
- `user_agent` – Client or SDK used  
- `version_id` – S3 version ID (if applicable)

---

### Example Entry

```log
79a3e7... my-bucket [18/Sep/2025:12:34:56 +0000] 198.51.100.1 arn:aws:iam::111122223333:user/snowy 3E57427F3EXAMPLE REST.GET.OBJECT logs/2025/09/report.pdf "GET /logs/2025/09/report.pdf HTTP/1.1" 200 - 15243 15243 27 26 "-" "aws-cli/2.13.1"
```


This means:

- **Snowy** (an IAM user) used the **AWS CLI**  
- From IP `198.51.100.1`  
- To request object `report.pdf`  
- On **Sept 18, 2025 at 12:34 UTC**  
- The request succeeded (`HTTP 200`)  
- And transferred 15KB of data

---

## Security Use Cases

| Use Case                  | What to Look For                                                      |
|---------------------------|------------------------------------------------------------------------|
| Unauthorized Access       | Repeated 403s, strange user agents, anonymous access                   |
| Data Exfiltration         | High number of GETs from single IP or role                            |
| Misconfigured Permissions | Anonymous access accepted? Roles doing DELETE unexpectedly?           |
| Access From Suspicious IPs| Foreign IPs accessing sensitive data                                  |
| Insider Threats           | Unusual access by a backup or automation role                         |
| Tool Misuse               | `curl`, `wget`, or strange user-agents accessing en masse             |
| Brute Force Activity      | Many failed requests across short time window                         |

---

## What You Can Use It For

| Purpose                  | Details                                                                 |
|--------------------------|-------------------------------------------------------------------------|
| Forensics                | Reconstruct what happened before or during an incident                 |
| Auditing                 | Who accessed what and when                                              |
| Monitoring MFA           | Compare user-agent/IP to known MFA patterns                             |
| Cost Optimization        | Spot which files are frequently accessed to optimize storage tiering    |
| Security Investigation   | Look for signs of scanning, scraping, or data leakage                   |
| Policy Validation        | Check if certain IAM users or roles are following least privilege        |

---

## Best Practices

- ✔️ Enable for all sensitive/shared buckets  
- ✔️ Use a **dedicated logging bucket**  
- ✔️ Set up **prefixes** to separate logs by source bucket  
- ✔️ **Do NOT** enable logging on the logging bucket itself  
- ✔️ Use **lifecycle rules** to expire old logs (e.g., move to Glacier)  
- ✔️ Combine logs with **Athena**, **CloudTrail Lake**, or **SIEM**  
- ✔️ Use **GuardDuty** — it can analyze these logs for anomalies

---

## Tooling and Analysis

- **Athena**: Query logs using SQL directly from S3  
- **CloudTrail Lake**: Store and query access logs along with control-plane events  
- **CloudWatch Logs**: Ingest logs for near real-time streaming  
- **SIEMs**: Forward to Splunk, Datadog, Elastic for correlation

---

## Pricing Model

Logging itself is **free**.  
You pay for:

- S3 storage of the logs  
- Athena queries (per GB scanned)  
- CloudTrail Lake ingestion (if used)  
- Data transfer (if logs cross regions or VPC boundaries)

> Logs can grow quickly if you have high-volume buckets — plan lifecycle storage accordingly.

---

## CloudTrail vs. S3 Access Logs

| Feature                | CloudTrail                               | S3 Server Access Logs                              |
|------------------------|-------------------------------------------|-----------------------------------------------------|
| Type of Logging        | Control plane (API-level)                | Data plane (object-level)                           |
| Logs GET/PUT?          | Only if data events enabled              | Yes, always                                         |
| Format                 | Structured JSON                          | Apache-style text                                   |
| IAM Action Tracking    | Yes                                      | Indirect (via requester field)                      |
| Payload Visibility     | No                                       | No (only metadata)                                  |
| Granularity            | Per API Call                             | Per object-level request                            |
| Delivery Latency       | Minutes                                  | Hours                                               |
| Enablement             | Default (control plane) / Opt-in (data)  | Must be explicitly enabled                          |

---

## Real-Life Example

Snowy's company hosts onboarding PDFs in a public S3 bucket.  
One night, logs show a **spike of GET requests from Eastern Europe** at 3:14 AM UTC.

Log fields reveal:

- IP addresses involved  
- Object accessed: `internal-design-guide-v2.pdf`  
- User-agent: `curl`  
- IAM role: junior intern (compromised)

**Response:**

- IAM role disabled  
- Bucket policy updated  
- Credentials rotated  
- GuardDuty enabled  
- Logging bucket moved to tighter access  

---

## Retention and Compliance

Because these logs contain **sensitive audit trails**, they fall under many compliance frameworks:

- **HIPAA**: PHI access tracking  
- **PCI-DSS**: Cardholder data logging  
- **SOX**: Financial record traceability  
- **GDPR**: Data subject access event logging  
- **ISO 27001**: Operational monitoring controls

Typical retention ranges from **90 days to 7 years**, depending on the regulation and your industry.

---

## Final Thoughts

S3 Server Access Logs are like **footprints in the snow** around your data.

They don’t show the payload, but they tell you:

- Who approached your data  
- What they tried to do  
- When, where, and how  
- Whether they succeeded

In a cloud full of invisible traffic, this is your only **first-party record of data access**.

If you don’t enable them, you’re blind.  
If you don’t store them, you’re forgetful.  
If you don’t analyze them, you’re vulnerable.

**Turn them on. Store them smart. Query them often.**

Because when your data disappears, **these logs are the only trail left behind**.
