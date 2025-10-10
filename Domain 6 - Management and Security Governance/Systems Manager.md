# AWS Systems Manager (SSM)

## What Is the Service

**AWS Systems Manager (SSM)** is a suite of *remote management tools* for your AWS infrastructure. It’s not just one service — it’s a collection of sub-services (called **capabilities**) that give you:

- Secure shell access to EC2s (without SSH)
- Automated patching and AMI baking
- Parameter storage and secret distribution
- Runbook execution and incident response
- Centralized inventory and compliance scanning
- Remote command execution across hundreds of machines

The key difference? **No public IPs, no inbound ports, no bastion hosts, and no SSH keys.** Everything is tunneled through the **SSM Agent** over outbound HTTPS to AWS. It’s encrypted, auditable, identity-based — and far more secure than legacy methods.

If you're trying to design a **Zero Trust**, multi-account, automated cloud environment — **SSM** is the remote control panel.

---

## Cybersecurity Analogy

Imagine a traditional data center. To access servers, you’d open ports, manage jump boxes, handle VPNs, and rotate SSH keys — a nightmare to scale or secure.

**SSM** replaces that with a **central command room** where you issue voice commands to agents inside each room.
They only *listen to trusted commands*, don’t expose themselves to the outside, and report everything they do.

It flips the model: *no one connects in*, the agents *reach out securely*.

## Real-World Analogy

Picture a team of robots (**SSM agents**) deployed across hundreds of factory buildings (EC2s, on-prem VMs, containers). Instead of driving out to each location with a key to open the door, you issue orders from HQ.

Those robots listen on a secure line, execute the tasks, and report back with logs, status, and screenshots.

You didn’t have to drive. You didn’t open any doors. But the job got done.

---

## How It Works (Core Architecture)

The core component of **SSM** is the **SSM Agent**, which must be installed and running on each managed instance.

### SSM Agent

- Communicates **outbound** to the Systems Manager endpoint (HTTPS on port 443)
- Authenticates using **IAM instance profile**
- Must be allowed via **VPC endpoints** or outbound internet access (depending on network config)

### IAM

The instance (or user) needs an **IAM role** granting access to the **SSM actions** (e.g., `ssm:SendCommand`, `ssm:StartSession`, etc.).

---

## Key Services / Capabilities

| **Capability**     | **Description**                                                                 |
|--------------------|----------------------------------------------------------------------------------|
| **Session Manager**| Shell access to EC2 instances (no SSH, no keys, no ports)                        |
| **Run Command**    | Run shell commands or scripts on one or more instances                          |
| **Patch Manager**  | Schedule and apply OS patches                                                    |
| **Automation**     | Define **runbooks** to perform common tasks (backups, restarts, incident responses) |
| **Parameter Store**| Store strings, configs, and secrets (can integrate with **KMS**)                |
| **Inventory**      | Collect metadata from managed instances (packages, users, processes)             |
| **State Manager**  | Enforce desired state (install software, configure settings)                     |

All of these are **region-aware**, **IAM-controlled**, **audit-logged**, and designed for **large-scale fleet operations**.

---

## Session Manager (Highlight)

One of the most critical security features — **SSM Session Manager** — replaces SSH.

- No need to open port 22
- No need for public IPs
- No need to manage SSH key pairs
- All sessions are **recorded and auditable**
- Can stream session logs to **CloudWatch Logs** or **S3**
- Supports **Run As** for privilege escalation
- Can be restricted by **tags, IP allowlists, MFA, source VPC**, and more

**CloudTrail** will log `StartSession`, `TerminateSession`, and even `SendCommand` events, while **CloudWatch** can record every keystroke.

This is foundational to **Zero Trust** server access.

---

## Parameter Store vs Secrets Manager

**SSM** includes **Parameter Store**, which lets you store:

- Plaintext config values (*Standard tier*)
- Encrypted secrets (*Advanced tier*) using **KMS**
- Values can be tagged, versioned, and used in scripts or templates

| **Feature**         | **Parameter Store**              | **Secrets Manager**                   |
|---------------------|----------------------------------|----------------------------------------|
| **Rotation support**| Manual                           | Built-in auto rotation                 |
| **Audit logs**      | CloudTrail                       | CloudTrail + KMS + rotation            |
| **Pricing**         | Free (Standard), $ (Advanced)    | $0.40/secret/month                     |
| **Ideal for**       | App configs, flags               | DB creds, API tokens                   |

Use **Parameter Store** for *configs and non-sensitive flags*.
Use **Secrets Manager** for *high-entropy secrets* that need rotation and external access control.

---

## Visibility and Auditing

**SSM** is fully integrated with **CloudTrail**. You can see:

- Who started a session
- What commands were run
- When a patch was applied
- What parameters were read or modified
- Who initiated an automation workflow
- What role assumed access to a node

You can also:

- Send session logs to **CloudWatch Logs** or **S3**
- Configure **AWS Config** rules to detect **unpatched** instances or missing agents
- Use **EventBridge** to trigger alerts when sensitive actions occur (e.g., `ssm:GetParameter` on secure values)

---

## Security Considerations

| **Concern**             | **Mitigation**                                                                 |
|--------------------------|-------------------------------------------------------------------------------|
| **Agent tampering**      | Use Config to detect stopped agents or missing installations                  |
| **Unauthorized access**  | Lock down IAM roles (`ssm:SendCommand`, `ssm:StartSession`)                   |
| **Overly broad parameters**| Use IAM conditions for resource ARNs, tags, or path restrictions           |
| **Insecure parameter storage**| Use `SecureString` + `KMS` + policies                                 |
| **Shell escalation**     | Restrict Run As behavior, use IAM for command scoping                         |
| **Audit bypass**         | Require session logging and validate trail completeness                      |

**SSM** can be used **securely or dangerously** — the difference is in how tightly you configure the policies and **observability**.

---

## Pricing Model

Most **SSM** features are **free**, but some are tied to **advanced tiers**:

| **Feature**        | **Cost**                                     |
|--------------------|----------------------------------------------|
| **Session Manager**| Free                                         |
| **Run Command**    | Free                                         |
| **Patch Manager**  | Free                                         |
| **Automation**     | Free up to 100 steps/day, then paid          |
| **Parameter Store**| Free (Standard tier), paid (Advanced)        |
| **Inventory**      | Free                                         |
| **CloudWatch Logs**| Priced separately per log group usage        |

> **Secrets Manager** is *more expensive*, but **Parameter Store** (Advanced tier) can cover some overlap at a lower cost.

---

## Real-Life Example: Snowy’s No-Bastion EC2 Management

You’ve got a private **subnet** with 50 EC2 instances spread across **dev**, **staging**, and **prod**.
No public IPs. No bastion hosts. No SSH.

You assign the **SSM Agent** role (`AmazonSSMManagedInstanceCore`) to each EC2 and configure **VPC Endpoints** for `ssm`, `ec2messages`, and `ssmmessages`.

Now, your team can:

• Connect to any instance using **Session Manager**, with logs sent to **CloudWatch**
• Run fleet-wide updates using **Run Command** or **Patch Manager**
• Store environment flags (like feature toggles) in **Parameter Store**
• Trigger incident response scripts using **Automation runbooks**
• Monitor compliance status using **Inventory** and **State Manager**

Every action is **tracked, authorized, and scoped** by **IAM**, with no inbound access ever exposed to the internet.

---

## Final Thoughts

**AWS Systems Manager is the most underrated service in AWS security.**
It touches every stage of the lifecycle:

• Access control (**Session Manager**)
• Patch and compliance (**Patch**, **Inventory**)
• Secure storage (**Parameter Store**)
• Automation and remediation (**Run Command**, **Automation**)
• Logging and audit trails (**CloudTrail**, **Config**, **CW Logs**)

And it does it **without requiring SSH, bastions, or manual scripts.**

If you want a **modern, automated, secure cloud** — you’re going to use **SSM**.
The only question is **how well** you configure it.
