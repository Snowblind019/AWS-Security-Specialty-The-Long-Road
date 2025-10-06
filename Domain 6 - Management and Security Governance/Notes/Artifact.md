# AWS Artifact

## What Is AWS Artifact

AWS Artifact is your central hub for compliance and audit documentation from AWS. It gives you on-demand access to AWS’s security and compliance reports, as well as agreements like the Business Associate Addendum (BAA) for HIPAA, or NDA/DPAs for legal controls.  
Unlike other services that perform actions, Artifact is a read-only portal designed to support compliance assurance, due diligence, risk assessments, and vendor audits.

This is where SnowyCorp’s compliance officer goes when they need to answer:

- “Is AWS SOC 2 Type II compliant?”  
- “Can we legally store PHI data in S3?”  
- “Where can I get AWS’s ISO 27001 certificate?”  
- “Can we sign a BAA with AWS to handle HIPAA data?”

---

## Cybersecurity and Real-World Analogy

**Cybersecurity analogy:**  
Think of AWS Artifact as your compliance file cabinet, but in the cloud.  
It’s full of notarized, signed documents from AWS that say:

- “Here’s proof we encrypt data”  
- “Here’s how we maintain physical security”  
- “Here’s who audited us last year”

And you can download them at any time, show them to your auditors, or use them to defend your AWS usage in risk reviews.

**Real-world analogy:**  
Imagine SnowyCorp wants to bid for a healthcare contract.  
The client asks: “Is your cloud provider HIPAA-compliant?”  
You log into AWS Artifact, download the HIPAA BAA, SOC 2 Report, and ISO 27001 cert, then attach them to your proposal.  
No emails. No back-and-forth. One-click trust assurance.

---

## What You Can Do With AWS Artifact

| **Feature**                | **What It Does**                                                                 |
|----------------------------|----------------------------------------------------------------------------------|
| View Reports               | Browse/download audit artifacts like SOC 1, SOC 2, ISO 27001, PCI DSS, etc.     |
| Accept Agreements          | Programmatically accept NDAs, DPAs, HIPAA BAAs                                  |
| Track Agreement Acceptance | See who accepted what, when, and for which accounts                             |
| Multi-account Support      | Supports consolidated organizations for compliance tracking                     |
| Used for Vendor Risk Management | Share documents internally or with regulators                              |

---

## Types of Documents in Artifact


### Reports (Read-Only)  
These are pre-signed compliance reports from AWS auditors:


| **Report**        | **Description**                                                              |
|-------------------|------------------------------------------------------------------------------|
| SOC 1 Type II     | Financial controls (relevant to finance/audit teams)                         |

| SOC 2 Type II     | Security, Availability, Confidentiality controls                             |
| ISO 27001/27017/27018 | InfoSec, Cloud, and Privacy standards                                    |
| PCI DSS           | Proof AWS infrastructure meets PCI standards                                 |

| FedRAMP           | U.S. government cloud compliance (for GovCloud)                              |
| IRAP, MTCS, ENS, etc. | International compliance frameworks                                      |

### Agreements (Signed by You)  
These are legal agreements between your org and AWS:

| **Agreement**  | **Purpose**                                              |
|----------------|----------------------------------------------------------|
| HIPAA BAA      | Legally required to store/process PHI on AWS             |
| NDA            | Allows AWS to share sensitive documents                   |
| GDPR DPA       | For personal data processing under GDPR                  |
| CCPA Addenda   | For handling California data subjects                    |

---

## Security & Compliance Relevance

| **Area**               | **How Artifact Helps**                                                                 |
|------------------------|-----------------------------------------------------------------------------------------|
| Audit Readiness        | Download official auditor reports to satisfy third-party or internal audits            |
| Due Diligence          | Use Artifact to prove AWS’s compliance stance when choosing services                   |
| Risk Management        | Evaluate AWS risks based on real-world controls                                        |
| Legal Compliance       | Sign HIPAA BAA or DPA for data residency/privacy requirements                          |
| Multi-account Governance | Centrally view which accounts accepted what agreements                             |

It’s especially useful when you're deploying workloads in regulated sectors: healthcare, finance, government, education, etc.

---

## SnowyCorp Example

SnowyCorp is onboarding a new client in the healthcare sector, which requires all infrastructure handling PHI to be HIPAA-compliant.  
Here’s what they do:

1. Visit AWS Artifact  
2. Download the HIPAA Compliance Whitepaper, SOC 2, and ISO 27001 cert  
3. Programmatically accept the HIPAA BAA on behalf of the root account  
4. Attach these documents to the client’s audit package  
5. Store logs of agreement acceptance in their internal GRC tool  

This process shaves weeks off client onboarding, ensures legal defensibility, and improves their cloud security posture in regulated environments.

---

## Pricing

✔️ **Free.**  
There is no cost to use AWS Artifact. All reports and agreements are freely downloadable and usable by all AWS customers.

---

## Final Thoughts

AWS Artifact is not a tool that *does* security — it’s a tool that *proves you’re doing it*.  
It’s your evidence binder, your compliance portal, your audit defense strategy.  
It doesn't replace encryption, firewalls, or IAM — it documents that AWS is doing its part in the shared responsibility model.

You can't secure healthcare data on AWS without Artifact.  
You can't pass audits without showing Artifact documents.  
You can’t do real security governance without proving your infrastructure is built on certified ground — and that’s what Artifact gives you.

