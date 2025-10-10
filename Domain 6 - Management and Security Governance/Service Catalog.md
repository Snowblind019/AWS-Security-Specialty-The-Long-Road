# AWS Service Catalog

## What Is AWS Service Catalog

AWS Service Catalog is a governance and self-service tool that allows organizations to curate and control the deployment of approved AWS resources. Think of it as your internal cloud product marketplace, but with guardrails.
You, as the cloud architect or security engineer, define pre-approved templates for infrastructure — EC2 instances, RDS databases, VPCs, S3 buckets, or entire applications. Then you publish them to end users, who can launch them through a UI or CLI — without needing full admin access.

Service Catalog lets you:
- Enforce security, cost, and tagging policies
- Enable self-service for developers or teams
- Maintain standardization and compliance
- Automate complex stacks (CloudFormation behind the scenes)
- Reduce cloud sprawl and unauthorized resource creation

---

## Cybersecurity Analogy

Imagine **SnowySec** is a fast-growing startup. Developers keep spinning up EC2s, S3 buckets, and VPCs… and forgetting things like encryption, MFA, backups, or tagging.

So Snowy builds a company catalog:
- “Here’s the official EC2 template” — with hardened AMIs, proper IAM roles, and logging enabled
- “Here’s the RDS PostgreSQL stack” — encrypted, backed up, with alerts baked in
- “Here’s the VPC layout” — following SnowySec’s zero-trust network policy

Developers can launch any of these stacks — but only these. That’s AWS Service Catalog in action.

## Real-World Analogy

Think of Service Catalog like a company vending machine:
- You choose what snacks go in (CloudFormation products)
- You set who can access what rows (IAM + portfolios)
- You limit how often each snack can be picked (budgets, quotas)
- Employees don’t get to stock or mix snacks — only consume what’s approved

It creates safe freedom — autonomy with boundaries.

---

## How It Works (Core Concepts)

**Products**
- A “product” is a CloudFormation template + version history
- It could be as simple as an S3 bucket or as complex as a 3-tier web app
- Products have parameters, descriptions, and constraints

**Portfolios**
- A portfolio is a collection of products
- You assign permissions to portfolios (who can access what)
- Portfolios can be shared across accounts via AWS Organizations

**Constraints**
Controls that restrict how a product can be used:
- Launch constraints — enforce a specific IAM role
- Template constraints — limit parameter values
- Tag options — enforce tagging standards
- Notification constraints — add SNS for approval/workflow alerts

**Provisioned Products**
- Once a user launches a product, it becomes a provisioned product
- These are the actual deployed stacks (CloudFormation-managed)

---

## Security and Governance Benefits

| Feature                  | Why It Matters                                                                 |
|--------------------------|--------------------------------------------------------------------------------|
| Least Privilege by Design | Users don’t need full IAM permissions — they launch through pre-approved roles |
| Standardization          | Every resource is deployed with baked-in controls (logging, encryption, tags) |
| Auditability             | CloudTrail logs all provisioning activity                                     |
| Multi-Account Support    | Share portfolios across accounts with AWS Organizations                       |
| Parameter Constraints    | Prevent dangerous choices (e.g., no t2.micro in prod, only encrypted volumes) |
| Drift Detection          | Compare provisioned products to template state                                |

---

## Where You’ll See It in Real AWS Architectures

**Control Tower Integration**
- Control Tower uses Service Catalog for Account Factory
- New AWS accounts are “products” launched through Service Catalog with templates

**DevSecOps Pipelines**
- Security teams publish hardened templates
- Dev teams consume them via pipelines or CLI without deviating

**Regulated Environments**
- Launch only HIPAA-compliant EC2 instances
- RDS databases with encrypted backups
- Templates pre-validated for compliance

**ISV or Internal Developer Portals**
- Create a custom web interface on top of Service Catalog
- Expose curated products to internal teams or customers

---

## Common Use Cases

| Use Case                     | How Service Catalog Helps                                                    |
|-----------------------------|------------------------------------------------------------------------------|
| Self-Service EC2 Launching  | Developers launch hardened EC2 stacks without full AWS Console access       |
| Multi-Account Cloud Governance | Share centralized portfolios across 50+ accounts in AWS Org              |
| Secure VPC + Subnet Creation | Pre-configure subnets, NACLs, route tables with guardrails                 |
| Compliance Automation        | Bake in encryption, tags, backups, and notifications into templates        |
| Dev/Test/Prod Environment Setup | Give teams isolated, reproducible environments — standardized by design |

---

## Real-Life Example

Blizzard works on a team at **SnowySec** and needs an EC2 machine for testing. Instead of:
- Clicking through the AWS Console
- Forgetting encryption
- Opening SSH to 0.0.0.0
- Leaving cost tags blank

He goes to the internal portal, sees:
**“Linux EC2 — Standard (hardened, 30GB, encrypted, tagged, auto-stop @ 6PM)”**

He clicks **"Launch."** Service Catalog:
- Uses a pre-approved CloudFormation template
- Deploys it with the right IAM role
- Applies cost tags
- Triggers GuardDuty + CloudTrail monitoring
- Emails the security team

Blizzard gets what he needs. Snowy stays compliant.

---

Service Catalog itself is free — you only pay for:
- The AWS resources deployed by the products
- Underlying services like CloudFormation, S3, Lambda, etc.

So it’s a governance overlay — not a billable service. **High value, no cost.**

---

## Final Thoughts

AWS Service Catalog is the cloud equivalent of giving developers a secure sandbox — with the rails already laid down.
You get:
- Governance without micromanagement
- Standardization without killing creativity
- Compliance without audits turning into nightmares

It fits perfectly into secure multi-account architectures, DevSecOps, and internal developer platforms — especially in organizations scaling beyond “just one AWS account.”
