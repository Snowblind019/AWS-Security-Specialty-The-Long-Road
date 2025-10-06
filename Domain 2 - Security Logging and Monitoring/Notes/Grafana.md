# Grafana

## What Is The Service

Grafana is an open-source observability and visualization platform used to build dashboards, alerts, and exploratory queries from multiple telemetry data sources — including CloudWatch, Prometheus, Loki, Elasticsearch, InfluxDB, AWS X-Ray, and many others.

Grafana isn’t a database. It’s a frontend brain that helps you see, query, and correlate logs, metrics, and traces — regardless of where they live.

For Snowy and team, Grafana became the mission control dashboard — a single pane of glass across:
- Multi-account AWS CloudWatch Logs and Metrics
- VPC Flow Logs + GuardDuty alerts via Athena queries
- Container metrics from Prometheus and ECS
- Audit data from Elasticsearch or OpenSearch
- Even SQL queries from RDS and Athena for governance

Whether you’re a security engineer watching for spikes, a platform engineer monitoring EKS memory, or an analyst reviewing login attempts — Grafana lets you see the patterns and act before damage spreads.

---

## Cybersecurity Analogy

Grafana is like the tactical operations center in a cyber defense bunker. It doesn’t store the war logs or conduct the operations — but it gives you:
- A real-time map of what’s happening
- Cross-panel visibility across logs, metrics, and traces
- Alert sirens for anomalies or breaches
- A place to overlay context, such as account ID, source IP, threat type, region, or user agent

Without it, you’re staring at thousands of logs in isolation.
With it, you can correlate events, spot abnormal behavior, and track impact across the whole stack.
It’s not your SIEM — but it’s often the first place you see the incident before it becomes a ticket.

## Real-World Analogy

Imagine you’re in a power grid control room. You’re not adjusting voltages or repairing towers — you’re watching dials, alerts, trends, and load across cities.

Grafana is that control panel — except for:
- Lambda error rates
- CPU throttling
- Auth API 500s
- BGP flap counts
- GuardDuty finding spikes
- CloudTrail anomalies by region

It’s a real-time heartbeat display of your AWS estate, and it's infinitely customizable.

---

## How It Works

Grafana uses a plugin-based data source model. That means it doesn’t ingest or store data — it queries other systems on demand and visualizes the results.

### Key Components

| Component       | Description                                                  |
|----------------|--------------------------------------------------------------|
| Data Sources    | Where Grafana fetches from (CloudWatch, Prometheus, etc.)    |
| Panels          | Widgets like graphs, gauges, logs, tables                    |
| Dashboards      | Layouts composed of panels                                   |
| Variables       | Inputs like region/account to filter dashboards              |
| Alert Rules     | Thresholds + conditions that trigger notifications           |
| Organizations   | Multi-tenant separation within Grafana                       |
| Users & Roles   | IAM-style access to dashboards, folders, and settings        |

### Supported AWS Sources

- Amazon CloudWatch
- Amazon Athena
- Amazon OpenSearch Service
- AWS X-Ray
- AWS Timestream
- AWS IoT SiteWise

All authenticated using:
- Access/Secret Keys
- IAM roles via EC2 metadata
- AWS SigV4 plugin

You can also self-host Grafana or use the fully managed **Amazon Managed Grafana (AMG)** service.

---

## Security And Compliance Relevance

Grafana plays a critical role in security observability — but like all dashboards, it comes with attack surface:

### Security Benefits

| Use Case                     | Grafana Role                                                                 |
|-----------------------------|------------------------------------------------------------------------------|
| Alerting on threats          | Trigger CloudWatch alarms or Prometheus alerts based on abnormal metrics    |
| Audit trail visualization    | Ingest CloudTrail into Athena or OpenSearch, query it via dashboards        |
| GuardDuty/Inspector dashboards | Surface severity-3+ findings by type, resource, or account               |
| Data exfil alerting          | Build VPC Flow Log dashboards showing large egress volumes                  |
| Correlating trace + log + metric | Use tempo/loki/prometheus trio for full triage stack                  |
| Visual anomaly detection     | Zoom in on IAM policy changes, RDS connection attempts, etc.                |

### Security Concerns

| Risk                          | Mitigation                                                                 |
|------------------------------|---------------------------------------------------------------------------|
| Exposed dashboards           | Restrict access with fine-grained roles or SSO                            |
| Overprivileged data source roles | Use scoped IAM roles with read-only metrics/log permissions         |
| Stored alert destinations (Slack/webhooks) | Rotate tokens and encrypt secrets using AWS Secrets Manager    |
| Unlogged dashboard changes   | Enable version history and CloudWatch Logs for Managed Grafana           |
| Unaudited access             | Integrate with SSO + CloudTrail (for AMG) to track admin behavior         |

Snowy’s team uses **Amazon Managed Grafana (AMG)** with **IAM Identity Center** (formerly SSO), CloudWatch log ingestion, and Athena queries on CloudTrail logs — all in dashboards that auto-rotate variables by account and region.

---

## Pricing Model

### 1. Self-Hosted Grafana
- Free tier via OSS (Apache 2.0)
- Costs come from:
  - EC2/EKS hosting
  - Data source API calls (e.g., CloudWatch)
  - Alerting + webhook infra

### 2. Amazon Managed Grafana (AMG)
- $9/user/month (Editor)
- $5/user/month (Viewer)
- $0.01–$0.03 per alert evaluation
- Ingest/query data is charged by source (CloudWatch/Athena/Prometheus)
- Free tier available via AWS Console that integrates tightly with:
  - AWS Organizations
  - AWS SSO
  - VPC access and PrivateLink

---

## Real-Life Example (Snowy’s Security Observability Wall)

Snowy’s team built a multi-account, multi-Region dashboard showing:
- CPU usage and throttling across production Lambdas
- Inspector critical findings grouped by service
- CloudTrail-based dashboards filtering `PutPolicy`, `AssumeRole`, and `CreateUser` events
- GuardDuty spike visualization (heatmap by region)
- Route 53 query rate anomalies
- VPC egress logs filtered for sensitive S3 destinations

They pulled logs from:
- CloudWatch Logs
- Athena (for long-term queries)
- Prometheus (for app metrics)
- OpenSearch (for fast lookup)

**Alert rules**:
Notify Slack + email if:
- VPC egress > 5GB to unapproved region
- Inspector findings > 10 in any 5-minute window
- CPU throttling on production Lambdas > 40%
- Route 53 DNS queries spike beyond 2x baseline

They applied IAM boundaries, private VPC endpoints, and role-based dashboard scoping per team.

---

## Final Thoughts

Grafana is not a SIEM. It’s not a log store. But it’s one of the most flexible, powerful visibility layers you can place in front of your telemetry stack — especially in environments where multi-account, multi-region, and multi-service data correlation is necessary.

In **Snowy’s world** — where real-time observability and security are deeply intertwined — Grafana provides:
- Secure, real-time visibility across accounts
- Actionable alerting before an incident escalates
- A common language between security, ops, and dev
- Cross-source correlation from CloudWatch to Prometheus to Athena to X-Ray

Whether you're hunting, auditing, monitoring, or tuning — **Grafana is often the first and last dashboard open** during every incident, deploy, or security review.
