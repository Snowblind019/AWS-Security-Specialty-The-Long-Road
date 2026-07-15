# AWS Security Hub (and Security Hub CSPM)

As of late 2025, "Security Hub" is two services, and knowing which is which is the whole exam point. The original findings-aggregator and posture service was renamed **AWS Security Hub CSPM**: it still aggregates findings in **ASFF**, runs security **standards and controls**, and produces a **security score**. A new service took the name **AWS Security Hub** (GA December 2025, previewed at re:Inforce 2025): it automatically **correlates and enriches** signals from CSPM, Inspector, GuardDuty, and Macie into prioritized **exposure findings**, and it uses **OCSF**. Both can run at once, and the format difference between them is a real operational trap.

The mental split is Security Hub CSPM vs the new Security Hub. CSPM is the engine running configuration and compliance checks and scoring your posture (ASFF, standards, controls). The new Hub is the layer that fuses everyone's signals into ranked exposures (OCSF, exposure findings). Neither is a SIEM, neither detects threats itself (GuardDuty), and neither is a log lake (Security Lake). They aggregate and prioritize findings, they do not generate the underlying detections.

## How it works

- **Security Hub CSPM (the posture engine, ASFF)**: ingests findings from AWS services (GuardDuty, Inspector, Macie, IAM Access Analyzer, Config, Detective) and third-party products, normalizing them into the **AWS Security Finding Format (ASFF)**. You enable **standards** (AWS Foundational Security Best Practices, CIS AWS Foundations, PCI DSS, NIST 800-53), each a set of **controls** that evaluate to PASSED, FAILED, WARNING, NOT_AVAILABLE, or SUPPRESSED. The **security score** is passed controls over enabled controls. Findings carry `Workflow.Status` and `RecordState` you can drive with automation rules keyed on **ASFF fields**. It also offers Insights (saved queries) and Custom Actions (buttons that fire EventBridge). CSPM findings reach EventBridge with detail type **"Security Hub Findings - Imported."**
- **The new Security Hub (the correlation layer, OCSF)**: consumes signals from **CSPM, Inspector, GuardDuty, and Macie** and automatically correlates them into **exposure findings**, each assembling several contributing **signals** into one prioritized risk. Each exposure carries **traits** categorized as **Reachability, Vulnerability, Sensitive data, Misconfiguration, and Assumability**, so a publicly reachable resource that also has an exploitable vulnerability and access to sensitive data surfaces as a single high-severity exposure. Findings are formatted in **OCSF**, calculated in near real time, with a Trends dashboard (up to a year of history) and a resource inventory that highlights publicly exposed assets. Automation rules here key on **OCSF fields**, and these findings reach EventBridge with detail type **"Findings Imported V2."**
- **Shared plumbing**: multi-account through **AWS Organizations** with a **delegated administrator**, and cross-Region through an **aggregation Region** with **linked Regions**. Response for both routes via **EventBridge** to **Lambda**, **SSM Automation**, or a SOAR.
- **The incompatibility**: ASFF and OCSF do not interoperate. Automation built on ASFF will not process the new Hub's OCSF output. You can run both services, but each automation path must match its schema, and migrating CSPM automation rules to the new Hub requires an ASFF-to-OCSF transformation where not every field maps.

## Security Hub CSPM vs the new Security Hub

| Dimension | Security Hub CSPM (formerly Security Hub) | Security Hub (new / enhanced) |
|---|---|---|
| Job | Posture management: aggregate findings, run standards, score compliance | Correlate and prioritize signals into exposure findings |
| Schema | ASFF | OCSF |
| Signature output | Control pass/fail and security score | Exposure findings with traits and severity |
| Sources | AWS services and third-party products | CSPM, Inspector, GuardDuty, Macie |
| Standards and controls | Yes (AWS FSBP, CIS, PCI DSS, NIST 800-53) | No, it consumes the results |
| EventBridge detail type | "Security Hub Findings - Imported" | "Findings Imported V2" |
| Automation rules | Keyed on ASFF fields | Keyed on OCSF fields |

## What gets tested

- The naming split is the headline trap. The service you knew as Security Hub is now Security Hub CSPM (ASFF, standards, controls, security score, posture). The new Security Hub (OCSF) correlates signals into exposure findings. Match schema to service every time: CSPM speaks ASFF, the new Hub speaks OCSF.
- Security Hub aggregates and correlates findings, it does not detect. GuardDuty detects threats, Inspector scans vulnerabilities, Macie classifies sensitive data, Config checks configuration. Those are its sources, not its job.
- Exposure findings are the new prioritization concept: several signals (reachable plus exploitable vulnerability plus sensitive data plus assumable role) fused into one ranked risk with named traits. If a question asks how to prioritize which risk to fix first across correlated signals, that is the new Security Hub.
- Standards and the security score live in CSPM: AWS FSBP, CIS AWS Foundations, PCI DSS, NIST 800-53, scored as passed over enabled controls. Compliance-framework questions point at CSPM.
- Format incompatibility is a live operational trap. An ASFF-based SOAR cannot consume the new Hub's OCSF output without rework. You can run both, but automation must match the schema.
- Multi-account is Organizations plus a delegated administrator. Cross-Region is an aggregation Region with linked Regions. Response for both is EventBridge to Lambda, SSM Automation, or SOAR. The Hub triages and routes, it does not remediate on its own.
- Do not confuse either Hub with Security Lake. Both Hubs deal with findings. Security Lake normalizes raw log and event data to OCSF and Parquet in your S3. Even though the new Hub and Security Lake both speak OCSF, one carries findings and the other carries log data.

## Limitations

- Aggregation and prioritization, not detection or remediation. Both Hubs depend on GuardDuty, Inspector, Macie, Config, and CSPM as sources, and on EventBridge, SSM, Lambda, or SOAR to act.
- The ASFF-versus-OCSF split means existing ASFF automation will not consume new-Hub OCSF output without rework, and rule migration is lossy where fields do not map.
- The CSPM security score is directional and gated by which standards and controls you enable and where. Enabling everything everywhere drives both cost and noise.
- Cost scales with ingested finding events and control evaluations (accounts times Regions times controls). High-volume sources inflate it quickly.
- Not a SIEM. For long-term correlation and retention, export to a SIEM or feed CSPM findings into Security Lake.