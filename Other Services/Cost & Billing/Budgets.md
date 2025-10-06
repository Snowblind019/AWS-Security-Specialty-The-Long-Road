# AWS Budgets

## What Is AWS Budgets

**AWS Budgets** is a cost management service that allows you to set **custom spending limits** and trigger **alerts** when your AWS usage, cost, or **Reserved Instance/Savings Plan** coverage crosses thresholds.

Where **Cost Explorer** shows you *what’s happening*, **AWS Budgets** lets you **act on it** — alerting teams, blocking usage, or enforcing policies based on:

- Actual spend  
- Forecasted spend  
- Usage quantity (e.g., number of hours used)  
- RI/Savings Plan utilization or coverage  

**Budgets are proactive guardrails** that help you:

- Stay within forecasted costs  
- Detect cost anomalies  
- Separate and control budgets by account, project, or tag  
- Trigger automated workflows on overages (e.g., shut down dev workloads)  

---

## Cybersecurity Analogy

Imagine **Snowy** is managing a **shared security lab** on AWS. Each team has a monthly spending cap.

Rather than watching costs manually, Snowy sets up **tripwire budgets**:

- If the **threat intel pipeline** exceeds $500 → ❗ alert Snowy  
- If **S3 usage for prod-security-logs** jumps above baseline → ❗ send Slack alert  
- If **root account usage** spikes → ❗ alert AND trigger auto-remediation via Lambda  

That alerting system? **AWS Budgets**.

> It’s like setting **intrusion alarms on your wallet**.

## Real-World Analogy

Think of AWS Budgets like:

- A credit card limit  
- A bank alert when you spend over $1,000 in a day  
- A smart thermostat that shuts off when usage gets too high  

You’re not just **watching spend** — you’re **controlling it in real time**, with automated consequences.

---

## How It Works

### 1. Create a Budget

You choose what kind of budget:

- **Cost Budget**: “Notify me if I spend over $X”  
- **Usage Budget**: “Alert if EC2 usage > 100 hours”  
- **RI/Savings Plan Coverage Budget**: “Coverage drops below 90%? Alert me”  
- **Forecast Budget**: “Projected to overspend? Alert early”  

### 2. Scope It

Apply filters like:

- Specific linked accounts  
- Tags (`Project = Snowstorm`, `Team = InfraSec`)  
- Services (e.g., GuardDuty, EC2, S3)  
- Regions  

### 3. Set Thresholds and Alerts

Set multiple thresholds:

- 50% → internal team alert  
- 80% → Slack + email  
- 100% → Email + trigger a Budget Action (like disabling access)  

### 4. (Optional) Budget Actions

On breach, you can automatically apply IAM or SCP changes:

- Remove IAM permissions to launch EC2  
- Detach IAM roles from cost offenders  
- Apply SCPs to stop non-essential service usage  

---

## Key Features
| **Feature**             | **Why It’s Useful**                                         |
|--------------------------|-------------------------------------------------------------|
| Cost + Usage Thresholds | Alert on actual and forecasted spend                        |
| Tag and Account Scoping | Budget per team, project, or OU                            |
| Email + SNS Alerts      | Notify individuals or send alerts to automation pipelines  |
| Budget Actions (Enforcement) | Auto-apply IAM/SCP changes on threshold breach        |
| RI + SP Tracking        | Monitor coverage and utilization for RIs and Savings Plans |

| Forecasting             | Don’t just react — predict and act ahead of time           |

---

## Where AWS Budgets Fits in Security

| **Use Case**                    | **Budget Strategy**                                                    |
|----------------------------------|------------------------------------------------------------------------|
| Prevent Resource Sprawl         | Budget by environment: Dev capped at $1,000/month                     |
| Threat Detection                | Alert on spikes in usage (e.g., unusual GuardDuty or NAT Gateway cost) |

| Credential Compromise Watch     | Unexpected EC2 or Lambda usage increase → trigger alert                |
| Compliance & FinOps Alignment   | Tie budgets to cost centers via tags, show audit trail                 |
| Security Lab Governance         | Set budgets per experiment/project to avoid overspend                  |

---

## Real-Life Example

At **SnowySec**, the `red-team-dev` account is used for **simulation testing**. Snowy sets a monthly budget:

- $750 budget  
- Alert at 50%, 80%, and 100%  
- Apply **SCP** if the 100% threshold is crossed, **blocking new EC2 launches**

Mid-month, red-team gets carried away — an alert triggers at 80%.  
Snowy sees a spike in `t3.medium` instances across 2 AZs.

At 100%, the Budget Action **auto-applies an SCP** that:

- Denies `EC2 RunInstances`  
- Denies `AttachVolume`  

Snowy gets notified. The test halts. **Spend is capped** — no post-mortem CFO emails.

---

## AWS Budgets vs Cost Explorer vs Anomaly Detection

| **Tool**             | **Primary Use**                 | **Proactive?** | **Enforcement?** | **Alerting?** |
|----------------------|----------------------------------|----------------|------------------|---------------|
| **Budgets**          | Threshold-based guardrails       | ✔️ Yes         | ✔️ Yes           | ✔️ Yes        |
| **Cost Explorer**    | Historical + forecasted views    | ✖️ No          | ✖️ No            | ✖️ No         |
| **Anomaly Detection**| ML-based pattern break alerts    | ✔️ Yes         | ✖️ No            | ✔️ Yes        |

> Use **Budgets** for fixed guardrails, **Anomaly Detection** for unexpected behavior, and **Cost Explorer** for manual analysis.

---

## Pricing

| **Feature**         | **Pricing**                                            |
|---------------------|--------------------------------------------------------|
| First 2 budgets      | ✔️ Free                                                |
| Additional Budgets   | $0.02 per day per budget (≈ $0.60/month)              |
| Alerts via SNS       | ✔️ Free (unless using SMS or external integrations)   |
| Budget Actions       | ✔️ Free — built-in with IAM/SCP support               |

In most use cases, the cost of Budgets is **negligible compared to the spend it prevents**.

---

## Final Thoughts

**AWS Budgets** is your **tripwire for cloud spend and resource governance**.

It’s the layer where **finance meets security**:

- Detect drift  
- Enforce control  
- Alert early  
- Prove you're not just building securely — you’re running smart and accountable too  

> In cloud-native environments, **cost is a security vector**.  
> **Budgets make sure you treat it that way.**
