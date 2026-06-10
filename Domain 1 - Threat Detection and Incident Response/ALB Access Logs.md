# ALB Access Logs 

## What Are ALB Logs

Application Load Balancer (ALB) logs are detailed records of every request that passes through your ALB. Think of them as the Nginx access logs of AWS, except managed, stored in S3, and tied to AWS-native metadata.

Every single HTTP or HTTPS request is logged — including:

- Client IPs  
- HTTP method + URL path  
- Response codes  
- Target group response time  
- TLS details (protocol, cipher)  
- User-Agent  
- Query strings  
- Redirects  
- And more  

These aren’t just logs for devs to debug broken websites. They are a security analyst’s dream for visibility, threat hunting, bot detection, and compliance auditing.

- If someone hits your /login endpoint 2,000 times in a minute, you’ll see it here.  
- If someone keeps getting 403s from EU IPs, you’ll see it.  
- If your backend is overloaded and returning 504s — it’s in here.  

But only if you enable logging.

---

## Cybersecurity Analogy

Imagine you’ve got a castle with one main gate (your ALB). People come in all day long — some knock nicely, some try to sneak through the side, some just run at it over and over.

Now, imagine you don’t have a gate log. No record of who came in, what door they used, what time, or how long they stayed. You just notice one day that someone’s in the armory and nobody knows how they got in.

**ALB logs are the damn gate logs.** You don’t need packet captures to catch weirdness — sometimes all it takes is a user-agent, a response code, and a 3-second gap between repeat POSTs.

## Real-World Analogy

Say Winterday runs a public web API behind an ALB. They deploy a new login endpoint and suddenly start getting complaints about slow responses.  
But nobody’s logging anything.

If ALB logging was enabled, they'd instantly see:

- Spike in POST requests to /login  
- Repeated IPs from overseas  
- Status code 200...200...200… then a bunch of 401s and 403s  
- All using a suspicious user-agent like `sqlmap/1.6.12#dev`  

This isn’t just a slowdown. It’s a credential stuffing attack.  
But without those logs? You're just guessing. You’ll be stuck grepping through fragmented app logs (if you even have those), while the attacker moves to `/withdraw`.

---

## How It Works / What’s in the Log

Each log entry is one line, space-delimited, and includes:

| Field                    | Example                                           | Meaning                                |
|--------------------------|---------------------------------------------------|----------------------------------------|
| type                     | http                                              | Always http for ALB                    |
| timestamp                | 2024-09-26T15:01:23.123456Z                       | Exact request time                     |
| elb                      | app/my-alb/123abc                                 | ALB name/ID                            |
| client:port              | 198.51.100.23:44321                               | Source IP and port                     |
| target:port              | 10.0.1.4:80                                       | Backend target that handled it         |
| request_processing_time  | 0.001                                             | Time spent by ALB before routing       |
| target_processing_time   | 0.100                                             | Time taken by backend to respond       |
| response_processing_time | 0.001                                             | Time ALB took to send response         |
| elb_status_code          | 200                                               | Response code from ALB                 |
| target_status_code       | 200                                               | Response code from target              |
| received_bytes           | 512                                               | From client to ALB                     |
| sent_bytes               | 1024                                              | From ALB to client                     |
| request                  | `"GET https://example.com/login HTTP/1.1"`        | Full request line                      |
| user_agent               | `"Mozilla/5.0"`                                   | Client software                        |
| ssl_cipher, ssl_protocol | `"ECDHE-RSA-AES128-GCM-SHA256", "TLSv1.2"`        | TLS info (if HTTPS)                    |
| trace_id                 | Root=1-5f84c7dc-2af07d9c7e1                        | Useful for X-Ray or tracing            |
| domain_name, chosen_cert_arn | *(optional)*                              | If using SNI/custom certs              |

There’s even more — fields change slightly based on HTTPS vs HTTP, redirects, SNI, and protocol versions.

---

## How to Enable It

1. Go to **EC2 → Load Balancers → Attributes**  
2. Toggle **Access logs: Enable**  
3. Choose an **S3 bucket** to store logs  
   - Must allow `aws:PrincipalService: delivery.logs.amazonaws.com`  
4. Optionally define a prefix like `/alb-logs/prod/`  
5. Logs are written every **5 minutes** in **Gzip** format  
6. You can partition by time using Athena or S3 Inventory for querying

---

## Security Use Cases

- **Detect brute-force login attempts**  
  - Look for repeated POST /login with 401s or 403s  
  - Combine with high `request_processing_time`

- **GeoIP blocking or anomaly detection**  
  - Map client IPs by country  
  - Flag abnormal countries accessing your admin endpoints

- **Detect bots or scrapers**  
  - Strange user-agents, high frequency  
  - Repeated 404s from a single IP

- **Catch SSRF or internal abuse**  
  - Target IPs in 10.0.0.0/8 range  
  - ALB should only route to known subnets — flag if it doesn’t

- **Identify slow backend targets**  
  - Compare `target_processing_time` between targets  
  - Flag anything > 1s consistently

- **Correlate with GuardDuty alerts**  
  - If GuardDuty flags a known bad IP hitting your ALB, you can trace every request it made

---

## Storage, Querying, and SIEM

- Use **Athena** to run SQL on S3 buckets  
- Partition logs by day/hour for better performance  
- Integrate with **Security Lake**, **CloudWatch**, or **third-party SIEM**

You can even trigger **Lambda** or **EventBridge** rules to:

- Parse logs for anomalies  
- Push IPs to WAF blocklists  
- Notify via SNS or Slack  

---

## Pricing Model

| Component                 | Cost                                  |
|---------------------------|---------------------------------------|
| ALB Logs                  | Free feature — no charge to generate logs |
| S3 Storage                | Standard S3 pricing per GB            |
| Athena Queries            | ~$5 per TB scanned                    |
| Log processing (Glue, Lambda) | Charged separately if used     |
| WAF actions based on logs | Also billed by request inspected      |

> Best practice: use **S3 lifecycle policies** to transition old logs to **Glacier** or delete after 90–180 days.

---

## Real-Life Snowy-Style Use Case

Snowy’s company, **BlizzardFinance**, just launched a tax reporting portal behind an ALB.  
On launch day, everything looks great — until CloudWatch shows a latency spike.

They:

**Snowy:**

- Enables **WAF** with a rate-limit rule  
- Blocks IPs with repeated requests to `/report/`  
- Sets up real-time **Athena queries + EventBridge → Slack** alerting  
- Works with **AppSec** to add token validation per request  

Problem solved.  

Logs saved the day. Again.

---

## Final Thoughts

If you’re not logging your ALB, you’re flying blind.

The logs are:

- Dirt cheap  
- Full of rich data  
- Parseable by Athena  
- Useful for both red team and blue team  
- And in a breach, probably the first place you’ll wish you had turned on  

They don’t give you payloads — but 90% of the time, you don’t need them.  
You just need to know who hit your endpoint, when, how, and what happened after.


**Turn them on. Store them smart. Query them often.**  
And don’t be the one explaining why there’s no logs in your post-incident RCA.

