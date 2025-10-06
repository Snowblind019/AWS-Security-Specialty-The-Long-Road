# Amazon Kendra

## What Is the Service
Amazon Kendra is an intelligent enterprise search engine powered by machine learning and natural language processing (NLP). It lets you ask natural questions and get relevant answers — not just keyword matches — from a vast collection of internal unstructured content like PDFs, Word docs, emails, SharePoint, wikis, Confluence pages, and more.

Instead of “Ctrl+F” chaos, Snowy’s team can now search with purpose:
- "Which servers are still running Log4j?"
- "Where’s the S3 bucket access control policy document?"
- "What is our DR plan for Oregon?"

And Kendra will understand the question and fetch the answer — even if it's hidden inside a 73-page Word doc or a Jira comment from 2021.

For security teams, that’s critical visibility into scattered compliance docs, IR reports, SOPs, and policy wikis — especially in fast-moving environments.

---

## Cybersecurity and Real-World Analogy

### Cybersecurity Analogy
Amazon Kendra is your knowledge SIEM — it centralizes your organization’s documentation and correlates it semantically.
Where a SIEM ingests logs and correlates anomalies…
Kendra ingests documents and correlates meaning.

You don’t need to grep logs to find out why an alert triggered — you can ask:
**“Why did we whitelist 10.11.22.0/24 in the WAF?”**
…and Kendra will find:
- the architecture decision memo from 2022
- the Slack discussion from the networking team
- the Jira ticket from the firewall change

### Real-World Analogy
Imagine Blizzard asks:

**“What’s the last time we updated our S3 public access policy?”**

Instead of digging through:
- 50 GitHub commits

- 4 Confluence pages
- 19 Slack threads
- 12 AWS Config snapshots...

Kendra reads it all, understands context, and gives a concise, ranked answer.
It’s like ChatGPT trained exclusively on your enterprise knowledge base — but deterministic and scoped to your real data.

---

## What It Actually Does

| Feature                  | Description                                                                 |
|--------------------------|-----------------------------------------------------------------------------|
| Semantic Search          | Understands the meaning behind a query, not just keyword matching           |
| Natural Language Questions | Ask things like “Who owns our incident response playbook?”                |
| Document Parsing         | Handles PDFs, Word, Excel, HTML, TXT, Markdown, Jira, Confluence, Salesforce, ServiceNow, etc. |
| Intelligent Ranking      | Prioritizes accurate, contextual answers — not just file matches            |
| FAQ Matching             | Perfect for known Q&A formats (runbooks, onboarding guides, IR flowcharts) |
| ACL-Aware Results        | Respects IAM and source system permissions                                  |
| Incremental Syncing      | Updates only new/modified docs from data sources                            |
| Feedback + Relevance Tuning | You can fine-tune ranking logic and retrain results over time           |
| Multi-index + Multi-tenant | Works across projects, org units, tenants                                 |

---

## Architecture: How It Works

1. **Data Sources are connected** (S3, SharePoint, Confluence, RDS, etc.)
2. **Document Ingestion begins**:
   - Documents are parsed and chunked
   - Text is vectorized using AWS deep learning models
   - Indexing stores the vectors in a semantic search index
3. **Users query using natural language**
4. **Kendra returns ranked results** with:
   - Answer snippets
   - Source document links
   - Confidence scores

> It’s like vector search + NLP + document preview + access control all in one.

---

## Security Use Cases

| Use Case             | How Kendra Helps                                                              |
|----------------------|-------------------------------------------------------------------------------|
| Policy Discovery     | “What’s our MFA policy?” → Finds official doc + change logs                   |
| IR Runbook Lookup    | “How do we handle S3 ransomware recovery?” → Finds PDF from last workshop     |

| Compliance Mapping   | “Where do we store SOC 2 policies?” or “Show GDPR asset list”                 |
| Jira/Slack Audit     | “Why did we delay patching that EC2 fleet?” → Finds Slack/Confluence discussion |
| Change Reasoning     | “Why is port 22 open on dev-env?” → Finds Git issue and waiver form           |
| Red Team Reports     | “What did the last pentest flag?” → Summarizes PDF report                     |
| Internal SOC Search  | “What’s the API limit for GuardDuty findings?” → Finds internal wikis + docs  |

---

## Integration With Other AWS Services

| Integration    | Purpose                                         |
|----------------|-------------------------------------------------|
| S3             | Store & index document repositories             |
| IAM            | Control user access to indexes and results      |
| Lambda         | Triggered after document ingestion for tagging/filtering |
| CloudTrail     | Audit Kendra access and queries                 |
| EventBridge    | Monitor Kendra sync errors or ingestion failures |
| Amazon Q       | Under the hood, Q uses Kendra to understand enterprise data |
| KMS            | Encrypts document data and indexes              |

---

## Pricing Breakdown

**Kendra has two main pricing modes:**

### Enterprise Edition (Full NLP + Connectors)

| Item            | Price                                      |
|------------------|--------------------------------------------|
| Indexing         | ~$1.125 per hour per index                 |
| Documents        | $0.00075 per document per day              |
| Queries          | ~$0.004 per query                          |
| Connector Syncs  | Free up to limit, then charges apply       |

**Free Tier:**
750 hours/month + 30k queries (for first 30 days)

---

## Real-World Scenario: Snowy SOC

Let’s say Snowy’s Red Team finished a tabletop on RDS exposure.
The Blue Team asks:
**“Where are our DB encryption-at-rest standards defined?”**

### Without Kendra:
Blizzard spends 45 minutes searching Jira, Confluence, Slack, and S3

### With Kendra:
One query returns:
- The master security policy doc
- A runbook for KMS key creation
- A Slack convo where Axel confirms all RDS are now encrypted

Same story for:
- Incident response flowcharts
- Certificate expiration SOPs
- Zayo circuit IP allocations
- Legacy app firewall rules

**Kendra doesn’t just “search.” It unlocks tribal knowledge and makes security scalable.**

---

## Final Thoughts
Amazon Kendra is what enterprise search should’ve been: contextual, fast, and actually usable by real teams.

For Snowy’s SOC and engineering teams, it fills the massive gap between *“we have the doc”* and *“we can find the doc.”*

It empowers:
- Security ops to trace policy to reasoning
- IR teams to pull historical evidence instantly
- Compliance staff to answer auditor questions confidently
- DevSecOps to automate secure behavior at scale

> In a world where knowledge is fragmented across 12 tools and 10 teams, Kendra brings it back together.
> And makes it queryable like a brain.
