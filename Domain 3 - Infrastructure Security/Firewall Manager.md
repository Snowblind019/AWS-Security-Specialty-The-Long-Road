# AWS Firewall Manager

## What Is AWS Firewall Manager

AWS Firewall Manager is a **centralized security policy enforcement tool** that lets you define firewall rules and enforce them across multiple **AWS accounts**, **Regions**, and **VPCs** — all from one place.

At its core, Firewall Manager is about **scaling security controls**. It allows cloud security teams to:

- Automatically apply **WAF rules**, **VPC security groups**, **Shield Advanced protections**, and **Route 53 resolver rules**  
- Ensure that **new accounts and new resources** get protected automatically  
- Enforce **non-deletable rules** or **mandatory protections** across distributed architectures  

> If you're running a multi-account AWS Organization and want no surprises in how resources are secured — Firewall Manager is your **policy enforcer**.

---

## Cybersecurity Analogy

Imagine **SnowySec** has offices in **30 different cities**. Every office manages its own building, but **Snowy** — the head of security — wants every building to:

- Have cameras  
- Use biometric access  
- Disable all guest Wi-Fi  

If Snowy had to fly to each office and configure this manually — **chaos**.  
Instead, he writes a **standard security policy** and distributes it through a **remote compliance system**. Each office applies it automatically — and new buildings also inherit the policy when opened.

> That system? **AWS Firewall Manager**.

## Real-World Analogy

Think of Firewall Manager like **Group Policy (GPO)** in Active Directory:

- You configure the policy once  
- All new and existing computers (accounts) receive and apply it  
- If someone disables antivirus or firewall locally — the GPO re-enables it at next sync  

> Firewall Manager works the same way for AWS security services — **guardrails**, not just suggestions.

---

## How It Works (Key Flow)

### 1. Enable AWS Organizations

- You must have **AWS Organizations** set up with **all features enabled**  
- Designate a **Firewall Manager admin account** (separate from management/root account)

### 2. Define Policies

Firewall Manager supports multiple policy types:

- **AWS WAFv2 Web ACLs** (for ALBs, API Gateway, CloudFront)  
- **Security Group auditing** (flag overly permissive rules)  
- **Shield Advanced protections**  
- **VPC Network Firewall policies**  
- **DNS Firewall rules** (Route 53 Resolver)

Each policy can target:

- Specific **Organizational Units (OUs)**  
- **Resource types** (e.g., all ALBs)  
- **Tags** (e.g., `Environment = Prod`)

### 3. Auto-Enforcement and Remediation

- **Existing resources** are evaluated and corrected  
- **New resources** launched in the Org will have the policy applied automatically  
- You can **remediate non-compliant resources** or just **monitor violations**

---

## Supported Policy Types

| Policy Type          | Description                                                 |
|----------------------|-------------------------------------------------------------|
| **WAF Policy**        | Apply WAF Web ACLs to ALBs, API Gateway, CloudFront         |
| **VPC Firewall Policy** | Apply AWS Network Firewall rules to VPCs                  |
| **DNS Firewall Rules** | Enforce DNS-level protections (block C2 domains, DGA)      |
| **Shield Advanced Policy** | Enroll all relevant resources into Shield Advanced     |
| **Security Group Audits** | Detect and remediate overly permissive SGs              |
| **Third-Party Firewall** | Integration with partner firewalls (e.g., Palo Alto, Fortinet via GWLB) |

---

## Security and Compliance Benefits

| Feature                    | Why It’s Valuable                                          |
|----------------------------|------------------------------------------------------------|
| **Consistent Security Posture** | No account or Region left behind — everyone inherits the same guardrails |
| **Automatic Remediation**   | Optional enforcement means drift gets corrected automatically |
| **Policy Scoping**          | Target based on Org Unit, Region, tag, or resource type   |
| **Visibility**              | Central dashboard of policy compliance across the Org     |
| **Integration**             | Works with AWS WAF, Shield, Config, Organizations, CloudTrail |
| **Prevention**              | Stop resource exposure (e.g., open SGs) before incidents   |

---

## Real AWS Use Case

Let’s say **SnowySec** is building a SaaS platform with:

- 1 AWS Org  
- 10 accounts  
- 3 OUs: `Dev`, `QA`, `Prod`

Snowy enables **Firewall Manager** in the **security tooling account** and sets:

- **WAF Policy**  
  - Applies to all **ALBs in Prod OU**  
  - Attaches a Web ACL that blocks **SQLi, XSS, bad bots**

- **Security Group Audit**  
  - Flags any SG in any OU that allows `0.0.0.0/0` on port 22  
  - Optionally auto-remediates to lock it down

- **DNS Firewall**  
  - Applies Route 53 resolver rules to all VPCs  
  - Blocks domains from a managed threat intel feed

- **Shield Advanced**  
  - Automatically enrolls all **CloudFront + ELBs** in Prod

**Result:**

✔️ Any new ALB in Prod immediately gets WAF applied  
✔️ Any open SSH port is flagged and optionally remediated  
✔️ Every account stays in sync — **zero manual setup needed**

---

## Pricing Model

Firewall Manager itself is **free** — but the services it orchestrates are **not**.

| Component                        | Pricing Detail                                         |
|----------------------------------|--------------------------------------------------------|
| **Firewall Manager**             | No additional cost                                     |
| **WAF Web ACLs**                 | Priced per ACL + rule + requests                       |
| **Network Firewall**             | Charged for endpoint hours and data inspection         |
| **Shield Advanced**              | ~$3,000/month per account (flat fee)                   |
| **Route 53 Resolver DNS Firewall** | Priced per rule and query volume                      |
| **Config/CloudTrail**            | Billed separately if enabled                           |

> If you’re using this org-wide, costs scale with resources — **plan accordingly**.

---

## Final Thoughts

**Firewall Manager is your cloud-wide security enforcer.**

It turns **isolated security rules** into **org-wide policies**.  
It replaces:

> “I *think* the team remembered to enable WAF”  
With:  
> “WAF is *always enforced* in Prod.”

If you’re managing a **multi-account AWS environment**, and especially if you care about:

✦ Reducing attack surface  
✦ Auditability  
✦ Auto-remediation  
✦ Enterprise-wide compliance  

…then **Firewall Manager belongs in your toolbox.**
