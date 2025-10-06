# SNS vs SQS

## What Are They (And Why It Matters)

Amazon **SNS** (Simple Notification Service) and Amazon **SQS** (Simple Queue Service) are both **messaging services**, but they serve different use cases and patterns:

| **Service** | **Pattern**            | **Style**     |
|-------------|------------------------|---------------|
| **SNS**     | Pub/Sub (Fan-out)      | Push-based    |
| **SQS**     | Message Queuing        | Pull-based    |

You **publish** to **SNS** → it **pushes** to subscribers (like Lambda, SQS, HTTP/S endpoints, email).  
You **send** a message to **SQS** → consumers **poll** the queue and process it when ready.

These tools help **decouple systems**, **buffer workloads**, and **distribute alerts**, but their behavior, delivery guarantees, and **security implications** differ.

---

## Cybersecurity Analogy

Imagine Snowy runs a security **NOC**.

- **SNS** is the _intercom system_ — when something happens (e.g. alert fired), the message is **blasted out** to everyone subscribed: monitoring apps, email alerts, ticketing systems, etc.
- **SQS** is a _ticket queue_. Alerts come in, and each analyst (consumer) grabs the next one when ready.

**Key Distinction:**

- **SNS** is broadcast and immediate  
- **SQS** is buffered and reliable  

---

## Side-by-Side Breakdown

| **Feature**     | **SNS**                                          | **SQS**                                             |
|------------------|---------------------------------------------------|-----------------------------------------------------|
| **Pattern**      | Publish / Subscribe                               | Producer / Consumer                                 |
| **Delivery**     | Push (to HTTP/S, Lambda, SQS, Email, SMS, etc.)   | Pull (consumer retrieves messages)                 |
| **Durability**   | No persistence unless using **SQS** or **Kinesis** as a subscriber | Messages stored redundantly, retained until deleted or expired |
| **Ordering**     | No guarantee                                      | FIFO (optional)                                     |
| **Fan-out**      | Native                                            | Not native (requires multiple queues)              |
| **Retries**      | Built-in for certain endpoints (like Lambda, HTTP) | Controlled via `maxReceiveCount`, **DLQ**          |
| **Encryption**   | SSE with **KMS** + **TLS**                        | SSE with **KMS** + **TLS**                         |
| **Access Control** | Topic Policies + **IAM**                        | Queue Policies + **IAM**                           |
| **Auditability** | **CloudTrail** logs + **KMS** decryption events   | **CloudTrail** logs + **KMS** + **DLQ** activity   |
| **Use Case**     | Broadcast alerts, event distribution              | Job queues, processing buffers                     |

---

## Real-World Examples

### Snowy’s Security Alert System

Snowy’s **GuardDuty** detector finds a threat.  
It **publishes to SNS**:

- Notifies:
  - A **PagerDuty** webhook  
  - A **Lambda** that writes to Slack  
  - An **SQS** queue for long-term alert ingestion

> That **SQS** queue then buffers alerts to a secure analytics system (like **OpenSearch** or **Athena**)

### This is called an **SNS → SQS fan-out** architecture.

You get the best of both worlds:

- **SNS** pushes immediately to whoever’s listening  
- **SQS** holds alerts for deeper, batch analysis  

---

### Winterday’s Document Processing App

User uploads a document to S3.

- Lambda detects upload and **sends a message to SQS**  
- A pool of secure workers **polls** the queue and processes files  
- If workers fail 3x, message goes to a **Dead Letter Queue**  
- All messages are **encrypted with CMKs** and **logged via CloudTrail**

> **SNS** isn’t used here — because we want **durable, buffered processing**, not instant broadcasts.

---

## Security Implications

| **Concern**               | **SNS**                                                  | **SQS**                                               |
|---------------------------|-----------------------------------------------------------|--------------------------------------------------------|
| **Message Loss**          | Possible if subscribers are **misconfigured** or offline (unless using SQS subscribers) | Safe — message stays until deleted or expired          |
| **Replayability**         | No                                                        | Yes — can reprocess messages                           |
| **Access Control Granularity** | Medium (topic-wide)                                | Fine-grained (per queue, per action)                  |
| **DLQ Support**           | No (not directly)                                         | Yes (native)                                           |
| **Encryption**            | **KMS** + **TLS**                                        | **KMS** + **TLS**                                      |
| **Audit**                 | **CloudTrail** + **KMS**                                  | **CloudTrail** + **KMS** + **DLQ** metrics             |

---

## Which Should I Use?

| **Scenario**                                     | **Recommendation**                     |
|--------------------------------------------------|----------------------------------------|
| Need to **broadcast** alerts to multiple systems | Use **SNS**                            |
| Need to **process jobs reliably**, even if slow or delayed | Use **SQS**                    |
| Need both?                                       | Use **SNS to SQS** fan-out pattern     |
| Want Lambda triggered on every alert instantly   | **SNS → Lambda**                       |
| Need to buffer and retry with visibility         | **SQS with DLQ**                       |
| Want messages stored for days or weeks?          | **SQS (not SNS)**                      |

---

## Final Thoughts

**SNS** and **SQS** aren’t competitors — they’re **teammates** in AWS event-driven design.

- Use **SNS** when you want speed and scale — push to many.  
- Use **SQS** when you want durability and reliability — let someone pull and retry.  
- Combine them when you need both: **SNS → multiple SQS queues**, each doing something different (alerting, archiving, processing, etc.).

**Security-wise**, **SQS** gives **durability**, **DLQs**, and **strict access**.  
**SNS** gives **speed**, **fan-out**, and **quick integration with external systems**.
