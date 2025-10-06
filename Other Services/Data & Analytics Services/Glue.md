# AWS Glue  

## What Is AWS Glue

AWS Glue is a fully managed ETL (Extract, Transform, Load) service that helps you:

- Discover data across various sources  
- Clean, transform, and enrich that data  
- Load it into data lakes, data warehouses, or analytics systems  

It’s **serverless**, meaning you don’t provision any infrastructure — and it integrates natively with:

- S3 (data lake)  
- Athena / Redshift / RDS  
- Glue Data Catalog  
- KMS (encryption)  
- IAM (permissions)  
- Lake Formation (fine-grained access control)  

But from a **security and detection** standpoint, it’s also:

- A potential data exfiltration path  
- A shadow analytics pipeline  
- A multi-service access bridge with implications for IAM roles, KMS key use, network paths, and CloudTrail visibility  

---

## Cybersecurity Analogy

Think of Glue as a robotic janitor with access to every room.  
It knows:

- Where the data lives (S3, RDS, DynamoDB)  
- How to scrub, reformat, and merge it  
- Where to ship it next (Redshift, S3, analytics teams)  

But if you don’t tightly control what rooms it can access — or what cleaning products it’s allowed to use (KMS keys, roles) — it can accidentally (or maliciously) mop up sensitive data and dump it somewhere it shouldn’t.

## Real-World Analogy

Picture Snowy running a healthcare data platform.

- S3 contains patient records in JSON  
- Redshift is used by the analytics team  
- Snowy uses Glue to transform and filter records before loading them into Redshift  

All good — until someone:

- Rewrites a Glue script  
- Adds a new output path to a public S3 bucket  
- Uses a broad IAM role to read from everything  
- Leaves the ETL job schedule active during off-hours  

Now you’ve got **automated, invisible data leaks** — happening via a system you thought was just doing ETL.

---

## How Glue Works

### Core Components

| Component     | Description                                                    |
|---------------|----------------------------------------------------------------|
| Data Catalog  | Central metadata repository — schema, partitions, tables       |
| Crawler       | Scans sources (S3, JDBC, etc.) to discover schema and populate catalog |
| Job           | The ETL logic — written in Spark or Python (PySpark, Scala, Pandas, etc.) |
| Triggers      | Can schedule or event-trigger jobs (e.g., when a new file lands in S3) |
| Connections   | JDBC or other data source configs (Redshift, RDS, etc.)        |
| Dev Endpoints | Interactive notebook-based environments for data scientists    |

Glue jobs run in **isolated containers**, access data via **IAM roles**, and store logs in **CloudWatch or S3**.  
**Encryption at rest and in transit** can be enabled via **KMS**.

---

## Security Surface Area

| Security Layer     | Description                                                                              |
|--------------------|------------------------------------------------------------------------------------------|
| IAM Roles          | Each job, crawler, or notebook must assume a role with specific permissions              |
| KMS Integration    | Encrypt job bookmarks, output data, logs, connection creds                               |
| S3 Bucket Policies | Control Glue’s read/write access — avoid `s3:*` on `*`                                   |
| CloudTrail Logging | All job runs, script edits, and catalog changes are loggable                            |
| Network Pathing    | Can run in VPC for access to private databases                                           |
| Lake Formation     | Can be used to enforce column-level access on top of Glue Catalog                        |
| CloudWatch Logs    | Capture stdout, stderr, and tracebacks from ETL jobs                                     |

---

## Common Attack Paths

- **Overly permissive IAM role:**  
  Glue job role has `s3:GetObject` on all buckets → lateral data read risk  

- **No encryption context:**  
  KMS usage without proper `EncryptionContext` conditions → any job can decrypt anything  

- **Stale crawler:**  
  Old crawler continues discovering data in newly created S3 prefixes  

- **Cross-account write:**  
  Job writes to a destination bucket in another account, possibly public  

---

## Detection and Response

Monitor the following:

| Event Source         | What to Watch                                        |
|----------------------|------------------------------------------------------|
| CloudTrail           | `StartJobRun`, `CreateJob`, `DeleteTable`, `PutScript` |
| Glue Logs (CloudWatch) | Sudden schema change, long runtime, large data volumes |
| KMS                  | `Decrypt` and `GenerateDataKey` events from Glue principal |
| S3 Server Access Logs| Cross-prefix read/write behavior                     |
| Athena               | If Glue is feeding data into query pipelines, watch for bursty or off-hours usage |

> For tighter visibility, tie each Glue job to a **dedicated role**, use **strict KMS conditions**, and run **anomaly detection** on CloudTrail + Glue logs + S3 access logs together.

---

## Example IAM Policy for a Glue Job Role

```json
{
  "Effect": "Allow",
  "Action": [
    "s3:GetObject",
    "s3:PutObject",
    "kms:Decrypt",
    "kms:GenerateDataKey"
  ],
  "Resource": [
    "arn:aws:s3:::snowy-prod-data/*",
    "arn:aws:s3:::snowy-clean-output/*",
    "arn:aws:kms:us-west-2:111122223333:key/abc123"
  ],
  "Condition": {
    "StringEquals": {
      "kms:EncryptionContext:Environment": "GlueJob"
    }
  }
}
```

---

## Glue + KMS + IAM = Delegation Chain

A misconfigured Glue job could:

- Assume a **broad role**  
- Decrypt a **customer key**  
- Transform **PII**  
- Dump it into a **dev account bucket**

If no one checks:

- The role’s **assume policy**  
- The **grant constraints** on the KMS key  
- The **bucket policy** on the destination S3  

Then you won’t catch it until it’s already leaked.

---

## Real-Life Snowy Scenario

Snowy’s team builds a Glue job to process monthly billing records.  
The IAM role used by the job had:

- Full `s3:*` on all Snowy buckets  
- `kms:*` on all keys tagged `Billing`  
- No CloudTrail alerting on `PutObject`  

A dev accidentally modified the script to write to:  
`s3://snowy-logs-public/` instead of `snowy-secure-data/`.

> The job ran successfully every night for **3 weeks** — pushing **customer invoices to a public bucket** — until someone noticed the logs in Athena.

**Lesson learned:**  
ETL is code. Glue is a pipeline. IAM is your firewall. KMS is your gate. You need them all scoped tightly.

---

## Final Thoughts

AWS Glue is a **powerful tool** for data transformation and movement.  
But it’s also a **high-risk identity and encryption surface** if you don’t:

- Scope IAM roles tightly per job  
- Restrict KMS keys via encryption context and grants  
- Monitor S3 data flows continuously  
- Track changes to Glue scripts, crawlers, and jobs in CloudTrail  
- Enforce job segregation and tagging  

> If you treat Glue like just a “data ETL engine,” you’re missing its **identity**, **encryption**, and **delegation depth**.
