# Glue

A serverless ETL service plus the **Glue Data Catalog**, a central schema/metadata store. For SCS it matters in two ways: the Data Catalog is what Athena, Redshift Spectrum, and EMR query against (Crawlers build the table schemas for CloudTrail/VPC Flow/access-log analysis), and a Glue job is an IAM-role + KMS + S3 delegation surface that can become a data-exfiltration path if over-permissioned.

Treat Glue as two things on the exam: a piece of the detection/log-analysis pipeline (the catalog behind Athena), and an identity/encryption surface to scope tightly. It is reference-level otherwise.

## How it works

- **Data Catalog**: central metadata (databases, tables, schemas, partitions), shared by Athena, Redshift Spectrum, and EMR.
- **Crawlers** scan sources (S3, JDBC) to infer schema and populate the catalog — this is how log table definitions get built.
- **Jobs** run Spark/Python ETL under an **IAM role**; **triggers** schedule or event-fire them; **connections** hold JDBC configs.
- **Security configurations** use **KMS** to encrypt job bookmarks, output data, CloudWatch logs, and connection credentials.
- Jobs can run **in a VPC** to reach private data sources; **Lake Formation** layers fine-grained access control on the catalog.

## Glue and its neighbors

| Piece | Role |
|---|---|
| Glue Data Catalog | Central schema/metadata store |
| Crawler / Job | Discovers schema / runs ETL |
| Lake Formation | Fine-grained (column/row/cell) access on the catalog |
| Athena / Redshift Spectrum / EMR | Query engines that read the catalog |

## What gets tested

- The Glue Data Catalog is the shared schema store Athena/Redshift Spectrum/EMR use; Crawlers build the log table schemas for analysis. This is Glue's place in the detection pipeline.
- A Glue job is an IAM + KMS + S3 delegation surface. Scope the job role to specific buckets and keys (never `s3:*` / `kms:*`), and add KMS **encryption-context** conditions so a job cannot decrypt arbitrary data.
- **Lake Formation** is the answer for column/row-level access control over the catalog; IAM alone is coarse-grained.
- Glue security configurations encrypt bookmarks, outputs, logs, and connection credentials with KMS.
- Run Glue **in a VPC** to reach private databases without internet exposure.
- Monitor CloudTrail (`CreateJob`, `StartJobRun`, script edits, catalog changes) and KMS `Decrypt` / `GenerateDataKey` by the Glue principal; an over-permissioned job writing cross-account or to a public bucket is the exfil scenario.

## Limitations

- Powerful delegation surface — over-permissioned roles or keys turn Glue into a data-exfiltration path.
- IAM on the catalog is coarse; column/row granularity needs Lake Formation.
- Not a security service itself; recognition-level for SCS beyond the catalog and the IAM/KMS surface.
- Crawlers can keep discovering data in new prefixes; stale crawlers widen exposure.