# Prometheus

## What Is the Service

Prometheus is a time-series metrics collection and storage system designed for reliability, scalability, and real-time alerting. It’s open-source, cloud-native, and purpose-built for **pull-based metric scraping** — which makes it perfect for environments where you need full visibility into every container, service, pod, and process.

Unlike CloudWatch or other push-based services, Prometheus **actively scrapes** data from endpoints that expose metrics in a specific format (`/metrics`), usually over HTTP. It stores those metrics as time-series data, and lets you run rich queries with its **PromQL** language.

**Snowy’s team uses Prometheus for:**

- Monitoring EKS cluster health  
- Collecting per-pod memory, CPU, and network metrics  
- Alerting on container failures or degraded performance  
- Building deep, custom Grafana dashboards  
- Providing real-time anomaly detection when AWS metrics are too slow or too generic  

---

## Cybersecurity Analogy

Think of Prometheus like a **stealth surveillance drone**. It flies over your architecture every 15 seconds, collecting information from each node, service, and system that has an exposed `/metrics` port.

It doesn’t wait for logs to be pushed. It actively pulls structured telemetry, stores it locally, and gives you an on-demand querying interface.

And if anything suspicious shows up — like:

- A sudden CPU spike  
- An unusual restart count  
- A process using 5× more memory than usual  

…it raises an alert and hands it off to Alertmanager, Slack, PagerDuty, or whatever system you’ve wired up.

In a threat-driven world, this is **tactical telemetry** — you see the anomaly before it becomes an incident.

## Real-World Analogy

Prometheus is like a **security patrol team** that walks the floor of a data center every 10 seconds, checking every machine’s temperature, power use, and uptime.

Unlike passive logs (which are like surveillance footage you review later), Prometheus is **active and structured**:

- “This pod is using 95% of its limit.”  
- “This node has failed 4 readiness probes in a row.”  
- “This EBS volume is taking 10× longer to attach.”  

You don’t have to guess. Prometheus tracks it all — with millisecond-level resolution and zero fluff.

---

## How It Works

Prometheus uses a **pull-based model** to scrape metrics from **exporters** — processes or sidecars that expose telemetry in a standardized format.

### Key Components

| Component         | Description                                                        |
|------------------|--------------------------------------------------------------------|
| Prometheus server| Core engine that scrapes, stores, and queries metrics              |
| Exporter         | Component that exposes `/metrics` endpoint (e.g., `node_exporter`) |
| Time-series DB   | Internal TSDB that stores metrics in block format                  |
| PromQL           | Query language for slicing, filtering, aggregating metrics         |
| Alertmanager     | Routes alerts to Slack, PagerDuty, email, etc.                     |
| Scrape configs   | Define which targets to pull from, at what interval                |

### Popular Exporters

| Exporter           | Purpose                                             |
|--------------------|-----------------------------------------------------|
| node_exporter      | Linux system metrics: CPU, disk, memory             |
| kube-state-metrics | Kubernetes objects: pods, deployments, statefulsets|
| cadvisor           | Container-level metrics                             |
| blackbox_exporter  | Synthetic monitoring (ping, HTTP probes, etc.)      |
| cloudwatch_exporter| Pull metrics from CloudWatch into Prometheus        |
| custom app metrics | Instrumented via SDKs (Go, Python, Java, etc.)      |

---

## Security and Compliance Relevance

Prometheus is incredibly powerful — but it’s also deeply technical and **security-sensitive**. Here’s how Snowy’s team thinks about it in production:

### Prometheus in Security Workflows

| Use Case                   | Relevance                                                                 |
|----------------------------|---------------------------------------------------------------------------|
| Runtime anomaly detection  | Alert on pods with excessive restarts, OOM kills, or CPU saturation       |
| Monitoring critical daemons| Alert if kubelet, containerd, or iptables restart                         |
| Detecting priv escalation  | Alert on containers consuming unexpected system resources                 |
| Infrastructure abuse       | Spot bitcoin miners via GPU or CPU spike patterns                         |

| Cold-start detection       | Time-to-readiness metrics on Lambda or Fargate containers                 |
| Pod identity leakage       | Track service-to-service call volume to detect lateral movement attempts  |

### Security Risks & Mitigations


| Risk                        | Mitigation                                                                 |
|-----------------------------|----------------------------------------------------------------------------|
| Exposed `/metrics` endpoints| Require mTLS or IP-based firewalling; never expose directly to public      |

| No built-in auth or encryption| Run behind NGINX or Ingress controller with OIDC or IAM                 |
| Storage unencrypted by default| Use encrypted disks or store via remote write (e.g., Cortex, Thanos)    |
| No native RBAC              | Use external tools (Grafana roles) to limit access                        |

| Alert spam or DOS           | Implement deduplication and rate limiting in Alertmanager                 |

Prometheus needs **guardrails in security environments** — but when hardened, it becomes an invaluable source of truth.

---

## Pricing Model

Prometheus itself is **open-source and free** — but your costs come from associated infrastructure:

| Component              | Cost Driver                                           |
|------------------------|--------------------------------------------------------|
| Self-hosted Prometheus | EC2/EKS node cost + storage (EBS/Gp3)                  |
| Remote write targets   | If using Thanos/Cortex: S3, EFS, etc.                  |
| Managed Prometheus (AMP)| $0.90 per 10M samples ingested per month             |
| Alertmanager           | Free, self-hosted — or part of Grafana Cloud stack     |

**If you're on Amazon Managed Prometheus**, it integrates with:

- Amazon Managed Grafana (AMG)  
- CloudWatch  
- IAM and VPC security groups  

…and it’s **production-ready** with FIPS 140-2 encryption, IAM auth, and audit integration.

---

## Real-Life Example — *Snowy’s Container Threat Monitor*

Snowy’s team runs **multi-tenant workloads on EKS** for internal devs and customers. They needed visibility into:


- Abnormal CPU or memory usage  
- Restart spikes that might signal container escapes or failed updates  

- Network egress to unknown regions  
- System-level daemon restarts  


They deployed:

- `node_exporter` + `kube-state-metrics` in each cluster  
- Prometheus scraping on 15s intervals  

- Alertmanager tied to their on-call Slack channel  

**Custom alerts included:**

- sum(rate(container_cpu_usage_seconds_total[1m])) by (pod) > 1.0
- container_restart_count > 3 in 5 minutes
- if network_bytes_sent > 2GB to unknown / unapproved IP ranges
- kube_node_status_condition{condition="Ready",status="false"}

**Grafana dashboards correlated:**

- Prometheus metrics  
- VPC Flow Logs (via CloudWatch + Loki)  
- Inspector findings (via Athena queries)  

This stack gave them a **real-time, programmable SOC view** of the cluster — with zero third-party agents or SaaS vendor lock-in.

---

## Final Thoughts

Prometheus is the **heartbeat monitor of your cloud-native systems**. It’s fast, extensible, battle-tested, and deeply programmable.

For Snowy's environment — especially across EKS, ECS, EC2, and hybrid clusters — Prometheus adds:

- Fine-grained, real-time visibility  
- Fully custom metric-based alerting  
- Self-hosted sovereignty over telemetry  
- Integration with open observability tools like Grafana, Loki, Thanos, and Alertmanager  

If you're serious about **observability, incident detection, or runtime behavior monitoring** — Prometheus is not optional. It’s **foundational**.

