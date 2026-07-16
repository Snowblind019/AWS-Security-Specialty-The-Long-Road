# AWS Resilience Hub

A service to define, validate, and track the resilience of your AWS applications from one place. It runs automated assessments against a **resilience policy** (your RTO/RPO targets), Well-Architected best practices, and the AWS Resilience Analysis Framework, then returns a **0-100 resiliency score**, prescriptive recommendations, and drift detection. It is a resilience-domain service, and on the security exam it sits alongside DR and ARC in the recovery and continuity space, so it is more resilience than pure security.

The mental model is policy, assessment, score, recommendations, validate. You set RTO/RPO targets per disruption type, Resilience Hub estimates whether your architecture can meet them, scores the gap, and recommends CloudWatch alarms, SOPs, and FIS experiments to close and prove it. It **assesses recoverability, it does not perform the failover**, which is the job of ARC, DRS, and AWS Backup.

## How it works

- **Define the application**: import resources from CloudFormation, Terraform, AppRegistry, or EKS, or add them manually. Resources group into **Application Components (AppComponents)**, units that work and fail together (a primary and its replica database are one AppComponent).
- **Resiliency policy**: RTO and RPO targets set for four **disruption types**: Application, Infrastructure, Availability Zone, and Region. Policies are reusable across applications.
- **Assessment**: estimates the achievable RTO and RPO per AppComponent, compares them to the policy (compliant or non-compliant), and produces the 0-100 **resiliency score**. The score reflects both policy compliance and how much of the recommended alarms, SOPs, and tests you have implemented.
- **Recommendations**: come in three operational categories: **CloudWatch alarms**, **SOPs** (standard operating procedures, delivered as **SSM Automation runbooks**), and **FIS experiment templates** (as CloudFormation). This ties directly to your runbook practice.
- **Validate with FIS**: run the recommended **AWS Fault Injection Service** experiments (AZ failure, resource termination, network disruption) to confirm the alarm fires, the SOP runs, and recovery lands within the RTO and RPO targets.
- **Drift detection**: flags when deployed infrastructure drifts out of policy compliance between assessments (for example, a cross-Region replica removed).
- **Integrations**: it assesses **AWS Backup** (RPO), **DRS** (DR configuration), and **ARC** (readiness) setups, Trusted Advisor surfaces scores and alerts below a threshold, and Organizations gives an org-wide delegated-administrator view.
- **Next-generation engine (2026)**: a multi-agent, Bedrock-powered assessment engine adds dependency discovery, topology mapping, and failure-mode analysis against single points of failure, excessive load, excessive latency, misconfiguration, and shared fate.

## Core concepts

| Concept | What it is |
|---|---|
| Application | A collection of AWS resources assessed as one workload |
| Application Component | Resources that work and fail as a unit (for example, a primary and replica DB) |
| Resiliency policy | RTO/RPO targets per disruption type (Application, Infrastructure, AZ, Region) |
| Assessment | Estimated RTO/RPO plus findings and recommendations |
| Resiliency score | 0-100, reflecting policy compliance and implemented alarms, SOPs, and tests |
| Recommendations | CloudWatch alarms, SOPs (as SSM runbooks), FIS experiments (as CloudFormation) |
| Drift detection | Flags when deployed infra falls out of policy compliance |

## What gets tested

- Resilience Hub assesses, scores, and tracks application resilience against an RTO/RPO policy and returns prescriptive recommendations. It does not perform failover, which ARC, DRS, and AWS Backup do. It measures and recommends.
- The resiliency score is 0-100 and reflects RTO/RPO compliance plus implementation of the recommended alarms, SOPs, and FIS tests.
- The four disruption types are Application, Infrastructure, AZ, and Region, and the policy sets RTO and RPO for each.
- Recommendations arrive as CloudWatch alarms, SOPs delivered as SSM Automation runbooks, and FIS experiments as CloudFormation templates. The SOPs connect straight to your runbook practice.
- FIS is how you validate resilience through chaos engineering, and Resilience Hub generates the experiment templates for you.
- Drift detection catches configuration that falls out of policy compliance between assessments.
- It integrates with and assesses Backup, DRS, and ARC configurations, so it sits above them as the assessment layer.

## Limitations

- Assessment and recommendation, not execution. It will not fail you over or remediate. You implement the recommendations or wire them to ARC, DRS, and Backup.
- It estimates RTO and RPO from the architecture. Real numbers come from actually running the FIS experiments and SOPs.
- Cost scales with the number of applications and assessment frequency, and FIS experiments are billed separately.
- It is resilience-focused, and the security exam touches it only lightly (continuity, availability, Well-Architected), so do not overweight it.
- The generative-AI assessment summaries are suggestions and can be wrong, so review them before acting.