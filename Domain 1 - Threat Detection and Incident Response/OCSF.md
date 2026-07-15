# OCSF (Open Cybersecurity Schema Framework)

An open-source, vendor-agnostic schema that normalizes security telemetry into one common taxonomy, so events from different tools describe themselves the same way. Co-founded by AWS and Splunk, launched at Black Hat 2022, and now a Linux Foundation project. It is not an AWS service and not a pipeline: it is the shared data language. In the exam it shows up as the schema behind Amazon Security Lake (always) and behind the new AWS Security Hub, and it is the counterpart you contrast against ASFF.

The mental split is OCSF vs ASFF. OCSF is the open, cross-vendor normalized schema used by Security Lake and by the new Security Hub. ASFF (AWS Security Finding Format) is the AWS-proprietary finding format used by Security Hub CSPM (the posture-management service, formerly just "Security Hub"). The exam tests which service speaks which schema, and what happens when data crosses from one to the other.

## How it works

- **Structure**: a set of data types, an attribute dictionary, and a taxonomy. Events roll up as **categories** (System Activity, Findings, Identity and Access Management, and so on), each holding **classes** (File System Activity, Process Activity, etc.), and each class carries a unique **`class_uid`**. Records use normalized attributes like `activity_id`, `category_uid`, and `severity`. **Extensions** and **profiles** let you add organization-specific fields without breaking compatibility, and the schema uses semantic versioning.
- **Storage-agnostic by design**: the schema itself is defined in JSON, but OCSF says nothing about how you store it. This is the trap: in Security Lake the events are written as Apache **Parquet**, so the schema (OCSF) and the storage format (Parquet) are two separate facts.
- **In Amazon Security Lake**: native AWS sources (CloudTrail, VPC Flow Logs, Route 53, Security Hub findings) are converted to OCSF automatically and stored as Parquet in an S3 bucket, one per Region in your account. **Custom and third-party sources must already be mapped to OCSF and written as Parquet** before Security Lake will accept them, typically via a Lambda or Glue transform. Attributes that do not map cleanly go to the `unmapped` object rather than being dropped.
- **In the new AWS Security Hub**: the version that went GA in late 2025 emits findings in **OCSF** (currently schema version 1.6) and its automation rules are written against OCSF fields.
- **In Security Hub CSPM**: findings stay in **ASFF**. When CSPM findings are added as a Security Lake source, Security Lake transforms them **ASFF to OCSF** on the way in. CloudWatch can also ingest CSPM findings in either ASFF or OCSF.

## OCSF vs ASFF

| Dimension | OCSF | ASFF |
|---|---|---|
| Scope | Open, vendor-agnostic, cross-industry | AWS-proprietary |
| Governance | Linux Foundation project (AWS + Splunk co-founders) | AWS only |
| Used by | Security Lake (all data), new Security Hub | Security Hub CSPM |
| Definition | JSON schema, storage-agnostic (Parquet in Security Lake) | JSON, `SchemaVersion` 2018-10-08 |
| Structure | Categories to classes (`class_uid`), dictionary, taxonomy | Flat finding attributes (Resources, Severity, Compliance) |
| Extensibility | Extensions and profiles, semantic versioning | Fixed AWS-defined fields |

## What gets tested

- Match schema to service: OCSF is the open normalized schema behind Security Lake and the new Security Hub. ASFF is the AWS-native finding format behind Security Hub CSPM. If the question says open, vendor-agnostic, or "one schema across many tools," it is OCSF.
- Security Lake always normalizes to OCSF and stores as Parquet, one S3 bucket per Region. Native AWS sources convert automatically. Custom or third-party sources must be transformed to OCSF and Parquet first, or they are rejected.
- The naming shift is a live trap: the posture service is now Security Hub CSPM (ASFF), while the newer aggregation/correlation service is Security Hub (OCSF). Automation rules written on ASFF fields do not map one-to-one to OCSF and require migration, and some fields cannot be migrated at all.
- ASFF to OCSF conversion is what happens when Security Hub CSPM findings flow into Security Lake. Direction matters: CSPM produces ASFF, the lake normalizes it to OCSF.
- Do not conflate the schema with the storage format. OCSF is JSON-defined but storage-agnostic. Parquet is how Security Lake persists it. A question can test either half.
- Structure vocabulary worth recognizing: category, class, `class_uid`, attribute dictionary, taxonomy.

## Limitations

- A schema, not a service. OCSF normalizes format only. You still need something to collect, transform, store, and query it (Security Lake, Athena, OpenSearch). It does not detect, alert, or remediate on its own.
- Custom sources carry the mapping burden: raw logs must be mapped to the correct OCSF class and written as Parquet before ingest, and unmapped attributes land in the `unmapped` object rather than enriching the record.
- Version drift is real. The schema evolves under semantic versioning, and producers and consumers must agree on a version (for example, the new Security Hub on 1.6 while older tooling sits on 1.1). Not every ASFF field has an OCSF equivalent.
- Normalization is upstream of value. Getting data into OCSF is a prerequisite for correlation and detection, not the detection itself.