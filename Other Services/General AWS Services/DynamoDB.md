# Amazon DynamoDB

## What Is DynamoDB

Amazon DynamoDB is a fully managed **NoSQL** key-value and document database designed for millisecond response time, infinite scalability, and **serverless** operation. It requires **no infrastructure management**, scales seamlessly, and integrates deeply with AWS security and monitoring services.

DynamoDB is widely used for:

- Real-time dashboards and user profiles  
- Session state storage  
- E-commerce carts  
- Leaderboards  
- Serverless architectures  
- IoT and mobile app backends  

From a security perspective, DynamoDB is powerful because:

- It’s integrated with **IAM**, **KMS**, **VPC endpoints**, and **CloudTrail**  
- It has fine-grained access control down to the item level  
- It supports **encryption at rest** and **in transit**  
- It avoids traditional attack surfaces like open ports or database daemons  

In zero-trust, serverless architectures, DynamoDB becomes a **foundational pillar for high-security, low-maintenance data storage**.

---

## Cybersecurity Analogy

Imagine DynamoDB as a **secure vault with individually locked boxes** inside.  
You can decide:

- Which identities can open which boxes  
- Which actions they’re allowed to perform (`read`, `write`, `update`, etc.)  
- How long each key is valid (via **IAM** roles)  
- Whether boxes are encrypted with a rotating master key  

Unlike traditional databases, there’s no control plane you can hack, no port to scan, and no SQL injection to attempt. The only way in is through **signed AWS API calls**, governed by **IAM** and **KMS**.

## Real-World Analogy

Let’s say **Blizzard** stores all **player session tokens** and **matchmaking data** in DynamoDB.

**Why?**

- The app needs **fast, consistent performance**  
- They don’t want to manage scaling, replication, or **sharding**  
- Session data must expire, replicate globally, and be encrypted  
- Access to sensitive rows (e.g., admin or dev-only keys) must be scoped per user/service  

DynamoDB lets them **enforce access by role, identity, and even item attributes**, while handling massive game traffic at global scale — without touching a single server.

---

# Key Security Features in DynamoDB

## 1. IAM-Only Access Model (No DB Users)

DynamoDB **does not support usernames, passwords, or database roles**.

All access is governed by **IAM policies**, which control:

- Who can `GetItem`, `PutItem`, `Query`, `Scan`, etc.  
- Which items or attributes they can access (via condition keys)  
- Which tables or global secondary indexes are visible  

You can scope **IAM** policies by:

- Table name  
- Partition key value  
- Sort key range  
- IP source (using `aws:SourceIp`)  
- Time-based controls (using `aws:CurrentTime`)  

This means **no password rotation**, **no credential leaks**, and native integration with every AWS identity system.

## 2. Fine-Grained Access Control (FGAC)

With **FGAC**, you can use **IAM condition keys** to limit access at the item or attribute level.

**Example:**

```json
"Condition": {
  "dynamodb:LeadingKeys": ["${aws:username}"]
}
```

This allows each user to access **only their own records** — a critical feature for multi-tenant, serverless, or SaaS systems.

You can also restrict:

- `PutItem` to deny writing `isAdmin = true`  
- `Scan` operations entirely (to prevent abuse or data leaks)  

**FGAC** allows **least privilege enforcement at scale**, baked into your infrastructure.

## 3. Encryption at Rest (KMS)

DynamoDB supports:

- **Default AWS-managed keys** (`aws/dynamodb`)  
- **Customer-managed KMS keys (CMKs)**  

**CMKs** provide:

- Full key usage visibility (via **CloudTrail**)  
- Rotatable keys (auto or manual)  
- Fine-grained **KMS** permissions  
- Cross-account snapshot access control (for exports to S3)  

All table data, including backups, global replicas, and streams, is encrypted transparently.  
Once a table is encrypted, **you cannot remove encryption** — it’s permanent.

## 4. Encryption in Transit

All traffic to/from DynamoDB uses **TLS 1.2+** encryption.  
You don’t need to configure this — it’s enforced at the API level. There’s **no option to send plaintext traffic**, and no database port to open or misconfigure.

This protects:

- Data from Lambda, EC2, API Gateway, or SDK clients  
- Replication between regions  
- Streams and event triggers  

All communications are **TLS-encrypted**, **signed**, and **IAM-authenticated**.

## 5. VPC Endpoints (Private Access)

By default, DynamoDB is accessed **over the public internet**, even though traffic is encrypted.

To enhance security:

- Create a **VPC Gateway Endpoint** for DynamoDB  
- Deny all traffic unless it comes from your **VPC** or **private subnet**  
- Use **IAM** policies like:

```json
"Condition": {
  "aws:SourceVpce": "vpce-0123456789abcdef"
}
```

This is essential for:

- Isolating workloads from the public network  
- Preventing exfiltration from rogue workloads  
- Locking down resource access to known infrastructure  

There’s **no additional cost** for Gateway Endpoints to DynamoDB.

## 6. Logging and Auditing

| Service                         | Function                                                             |
|--------------------------------|----------------------------------------------------------------------|
| **CloudTrail**                 | Logs all API calls: who queried, inserted, deleted, or changed items |
| **AWS Config**                 | Tracks changes to table configuration (e.g., encryption, throughput mode) |
| **CloudWatch Contributor Insights** | Helps detect access spikes, hot partitions, abuse patterns      |
| **EventBridge**                | Can trigger alerts or workflows on specific changes (e.g., new table created) |

You should always monitor:

- Unusual `Scan` requests (e.g., data scraping)  
- Table exports to S3  
- Unexpected **IAM** usage or broad permissions  
- Access patterns during off-hours or cross-account usage  

## 7. Streams and Event-Driven Security

DynamoDB Streams allow you to **capture all changes** to items in a table.

You can:

- Trigger **Lambda** functions for insert/update/delete events  
- Record mutations for **forensics, compliance, or alerts**  
- Replicate to other regions or S3 for **immutability**  

For security use cases:

- Monitor for privilege escalation attempts  
- Alert on suspicious record creation (e.g., new admin sessions)  
- Archive critical data changes to encrypted, write-once S3 buckets  

Streams provide **real-time audit capability** — a key building block in **zero-trust pipelines**.

---

## Snowy’s Example: Secure Session Table

Snowy builds a DynamoDB table to store web app sessions for users.

**Security goals:**

- Sessions should be encrypted and expire automatically  
- Each user should only access their own session  
- Logs should track all read/write attempts  
- No internet exposure allowed  

**Implementation:**

- Table encrypted at rest with a **CMK** (`alias/snowy-session-key`)  
- **FGAC** via **IAM** role using `dynamodb:LeadingKeys = ${aws:username}`  
- Lambda only accesses DynamoDB via **VPC Endpoint**  
- Logs sent to **CloudTrail**, with alarms on large `Scan` events  
- **TTL** enabled to expire sessions after 30 minutes  
- Streams send session deletes to S3 for audit trail  

This setup provides full **encryption, isolation, visibility, and compliance**, all with zero server maintenance.

---

## When to Use DynamoDB for Secure Workloads

- You need **millisecond read/write** at scale  
- You want **serverless, fully-managed** data storage  
- You require **FGAC**, **encryption**, and **audit logging**  
- Your workloads demand **burst performance with zero warmup**  
- You’re building **multi-tenant** or **SaaS** applications  

---

## When DynamoDB May Not Be Ideal

- You require **complex joins, transactions across tables, or foreign key constraints**  
- You need **row-level locking** or **ACID compliance** across multiple records (Aurora is better here)  
- You’re storing **large binary objects** (use S3)  
- Your team lacks **NoSQL design experience** (bad schema = bad UX)

---

## Final Thoughts

**Amazon DynamoDB** is the gold standard for **secure, scalable NoSQL storage in AWS** — especially when **IAM**, **KMS**, and **VPC** security controls are used correctly.

You don’t need to think about:

- Patching servers  
- Running backups  
- Replicating data across **AZs** or **Regions**

But you do need to think about:

- **IAM** access controls  
- Encryption key scoping  
- Item-level permissions  
- Monitoring access and usage behavior  

DynamoDB shines when you need **speed, scale, and security without infrastructure overhead**.  
When paired with **Secrets Manager**, **VPC endpoints**, **CloudTrail**, and **least-privilege IAM**, it becomes a secure backbone for event-driven, zero-trust AWS architectures.
