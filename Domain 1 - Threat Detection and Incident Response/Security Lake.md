# Amazon Security Lake

A fully managed security data lake that centralizes security log and event data from AWS, on-premises, other clouds, and custom sources into a purpose-built lake in **your own account's S3**, automatically normalized to the **OCSF** schema and stored as **Apache Parquet**. You keep ownership of the data and point your own analytics tools at it. In the exam it is the "centralize and normalize security logs across accounts and Regions into one schema" answer, and it is deliberately distinct from Security Hub (findings) and GuardDuty (detection).

The one-line role: Security Lake's lane is normalizing raw security **log data** into your S3 as OCSF and Parquet so your own tools (Athena, OpenSearch, a third-party SIEM) can query one consistent schema. That is its lane: not a SIEM itself, not the aggregation and scoring of **findings** (Security Hub), not threat detection (GuardDuty). It is the data-lake substrate those tools sit on top of.

## How it works

- **Storage and format**: a purpose-built lake backed by S3 in your account, one bucket per Region. Every ingested source is converted to **OCSF** and written as **Parquet**. Do not conflate the schema (OCSF) with the storage format (Parquet), they are two separate facts.
- **Sources**: native AWS sources include **CloudTrail** (management events plus S3 and Lambda data events), **VPC Flow Logs**, **Route 53 resolver query logs**, **Security Hub findings**, **EKS audit logs**, and **WAF logs**. Custom and third-party sources must already be mapped to **OCSF and Parquet** before ingest.
- **Under the hood**: **AWS Glue** crawlers build the Data Catalog, **Lake Formation** creates a separate table per source and governs access, **Lambda** runs the ETL and registers partitions, and **EventBridge** (with SQS/SNS) notifies subscribers when new objects land.
- **Subscribers, two access modes**: **data access** (streaming) notifies the subscriber through EventBridge or SQS as objects are written and the subscriber reads them directly from S3. **Query access** lets the subscriber query the Lake Formation tables with **Athena** or **Redshift**; cross-account query sharing rides on Lake Formation plus **AWS RAM**. A subscriber can hold at most **10 sources** and sees only the data in the Region where it was created.
- **Multi-account and multi-Region**: managed through **AWS Organizations** with a **delegated administrator**, and the **management account cannot be the delegated admin**. **Rollup Regions** consolidate data from one or more contributing Regions into a single Region, for data-residency compliance and to give a subscriber multi-Region reach. Contributing-Region data stays local, the rollup is a consolidated copy (so cross-Region transfer cost applies), and a rollup Region cannot itself be a contributing Region for another rollup.
- **Lifecycle**: customizable retention and tiering (for example, age old data to Glacier). A 15-day free trial covers full features.

## Security Lake vs the rest of the stack

| Service | Job |
|---|---|
| Security Lake | Centralizes and normalizes raw security log/event data to OCSF and Parquet in your S3, for your own analytics tools |
| Security Hub | Aggregates and scores security findings (posture and alerts); OCSF in the new Hub, ASFF in Security Hub CSPM |
| GuardDuty | Detects active threats from logs and produces findings |
| OpenSearch | Searches, correlates, and visualizes; a consumer that subscribes to Security Lake data |
| Athena | Queries the lake with SQL; the query engine for query-access subscribers |

## What gets tested

- Security Lake is the least-operational-overhead answer for centralizing and normalizing security logs across many accounts and Regions into one schema. It converts to OCSF and stores as Parquet in your own S3. The classic distractor is rolling your own S3 bucket plus Glue ETL, which is more overhead.
- Log data vs findings decides the question. Security Lake aggregates raw log and event data for querying. Security Hub aggregates findings for posture and response. Security Hub findings can be a source into Security Lake, so they complement rather than compete. Do not swap them.
- Subscriber model has two modes: data access (streaming, notified via EventBridge or SQS, reads S3 objects directly) and query access (queries Lake Formation tables with Athena or Redshift). Cross-account query sharing uses Lake Formation and RAM.
- Multi-account uses Organizations with a delegated administrator, and the management account cannot be that admin.
- Rollup Regions consolidate contributing Regions into one, for data residency and because a subscriber only sees its creation Region. A rollup cannot be a contributing Region for another rollup.
- Custom and third-party sources must be OCSF and Parquet before ingest. Native AWS sources are converted automatically.
- Consumers are Athena, Redshift, OpenSearch, and third-party SIEMs. Security Lake feeds them, it is not itself the query or visualization tool.

## Limitations

- Not a SIEM and not an analytics UI. It is normalized storage. You bring Athena, OpenSearch, or a SIEM to derive value.
- Custom sources carry the mapping burden: raw logs must be transformed to OCSF and Parquet before Security Lake accepts them.
- Subscriber constraints: at most 10 sources each, and only the creation Region's data unless a rollup Region is used.
- Cost is the sum of underlying services (S3, Glue, Athena, and cross-Region transfer for rollups). High-volume sources like S3 data events and WAF logs inflate it quickly.
- Rollup topology is restricted: a rollup Region cannot also be a contributing Region for another rollup.
- It is a normalization and storage substrate, not prevention or response. Pair it with the tools that detect and act.