# AWS Migration Hub

## What Is the Service

**AWS Migration Hub** is a **central tracking service** that helps you **plan**, **monitor**, and **manage application and server migrations** to AWS from a **single unified dashboard**.

It’s *not* a migration tool itself, but rather the **command center** that lets you orchestrate and observe multiple migrations — whether you're using:

- AWS-native tools (like **Application Migration Service**, **Database Migration Service**)  
- Third-party tools (like **CloudEndure**, **ATADATA**, or **RiverMeadow**)  

### Why It Matters

Without Migration Hub, you'd be **jumping between multiple tools and consoles**.  
It’s built for **large-scale migrations**:

- Thousands of servers  
- Complex interdependencies  
- Multiple stakeholders  

It tracks both the **discovery** and **migration** phases to keep everything coordinated.

---

## Cybersecurity and Real-World Analogy

### Cybersecurity Analogy
Think of **Migration Hub** as your **SIEM for migration** —  
It doesn’t move the data itself but **collects and centralizes status, metrics, and risks** from all the migration agents.

It lets you:

- See what's in scope  
- Track what's already moved  
- Understand dependencies  
- Flag potential failures or drift  

### Real-World Analogy

Imagine migrating a **hospital** from one building to another.  
Some teams handle patient data, others medical devices, others handle labs and pharmacies.

**Migration Hub** is the **war room whiteboard** that tracks:

- Which department moved  
- What’s still in motion  

- Who’s responsible  

---

## What It Tracks

| **Phase**         | **What Migration Hub Does**                                                                 |

|-------------------|---------------------------------------------------------------------------------------------|
| **Discovery**     | Gathers server, application, and dependency data using the Discovery Agent or Collector     |
| **Assessment**    | Groups servers into apps, visualizes dependencies, identifies lift-and-shift vs modernization |
| **Migration**     | Tracks real-time status of each app/server/db being migrated (regardless of tool used)      |

| **Post-Migration**| Verifies app health, flags divergence or drift                                              |

---

## Core Components

| **Component**                    | **Description**                                                                 |
|----------------------------------|---------------------------------------------------------------------------------|
| **Migration Hub Dashboard**      | Central view of all ongoing migrations                                          |

| **Migration Hub Orchestrator**   | Automates workflow steps for migrating specific applications                    |
| **Discovery Tools**              | Lightweight agents or collectors that pull config, usage, and dependency info   |
| **Integration with AWS Services**| Syncs status from DMS, Application Migration Service, etc.                      |

---

## Security & Compliance Relevance

- **Tracks Data Movement** — Audit where sensitive data (PII, PHI) moved and when  
- **Shows App Dependencies** — Prevents insecure migrations (e.g., database moved before DNS)  
- **IAM Integration** — Fine-grained control over viewing vs orchestrating migrations  
- **Visibility into Drift** — Identify when post-migration differs from pre-migration config  
- **Encryption** — Discovery data is encrypted in-transit and at-rest using **KMS**  
- **Auditability** — Integrated with **CloudTrail** for tracking who approved/started what

---

## Pricing Model

| **Feature**                      | **Cost**                               |
|----------------------------------|----------------------------------------|
| Migration Hub dashboard + tracking | Free                                 |
| Discovery tools (agent/collector) | Free                                  |
| Orchestration                    | Free                                   |
| Underlying migration tools       | Pay per use (e.g., EC2, DMS, MGN, S3)  |

The **Hub itself is free**, but **tools under the hood may incur charges**.

---

## Real-World Cloud Security Engineering Usage

When **Snowy’s team** is tasked with migrating a **legacy on-prem app** (MySQL DB, three-tier web servers, VPN backhaul), they use **Migration Hub** to:

- Discover the **server specs and network layout**  
- Identify dependency on **on-prem LDAP**  
- Track which parts use **Application Migration Service** vs **need refactoring**  
- Monitor that the **S3 data transfer** doesn’t violate **retention policies**  
- Ensure **no dev/test artifacts** are reintroduced in prod  

---

## Common Exam & Real-World Scenarios

- **“Which tool helps you track all migration tasks across teams in one place?”**  
  → **Migration Hub**

- **“How do you ensure your compliance auditor sees which data moved, when, and how?”**  
  → Use **CloudTrail + Migration Hub logs** for visibility

- **“Your app fails post-migration. How do you confirm whether the database moved before the backend?”**  
  → Use **Migration Hub dependency mapping + timestamps**

---

## Final Thoughts

**Migration Hub** isn’t a flashy service —  
But it’s a **high-leverage coordination layer** when you’re doing **serious migrations**.

It’s like a **project manager meets security auditor**:  

It doesn’t move the bits, but it makes sure the **bits don’t move wrong**.

In environments with **compliance needs** (PCI, HIPAA, FedRAMP), being able to **prove what migrated when** is as important as the migration itself.

