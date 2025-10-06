# Compute Security in AWS

## What Is Compute Security

Compute security in AWS refers to the protections and hardening you apply to **virtual machines (EC2)**, **containers (ECS, EKS, Fargate)**, and **serverless workloads (Lambda)**.

Every application has a compute layer — and in the cloud, you’re responsible for securing:

- The code you run  
- The runtime environment (to varying degrees)  
- The permissions the compute unit has  
- The network it's allowed to talk to  
- The data it accesses or exposes  

Your shared responsibility depends on the compute service:

| **Service** | **You manage** | **AWS manages** |
|--------------|----------------|----------------|
| **EC2** | OS, patching, IAM, app code | Hypervisor, hardware, facility |
| **ECS/EKS** | Container config, IAM, runtime, code | Underlying EC2 infra (if using Fargate, AWS also manages OS) |
| **Lambda** | Function code, IAM, env vars | Runtime, patching, availability |

Compute is the front door of execution. If it’s compromised, **data exfiltration, lateral movement, and persistence** are all possible. Attackers target it early and often.

---

## Cybersecurity Analogy

Think of your compute environments like **rented workshops**.

- **EC2** is like renting a full warehouse — you're in charge of the doors, lighting, locks, and fire extinguishers.  
- **Containers** are like setting up workstations inside a shared warehouse — you control your space, but if you mislabel chemicals, it spreads.  
- **Lambda** is like a robot arm doing tasks for you on command — fast, efficient, but you better verify what it's handling and who’s commanding it.  

Security in compute is about:

- Who can walk into the shop (**IAM**)  
- What’s locked down (**security groups, roles**)  
- What tools are laying around (**data in env vars, tokens, secrets**)  
- Whether the lights are on and you’re recording (**CloudTrail, GuardDuty, CW Logs**)  

## Real-World Analogy

Imagine Blizzard spins up a compute cluster to handle matchmaking in a multiplayer game.

- **EC2** runs the matchmaking engine  
- **ECS** runs containers for chat  
- **Lambda** runs cheat-detection automation  

Now imagine:

- EC2 is running an outdated OS with SSH exposed  
- ECS containers have `CAP_SYS_ADMIN` enabled and mount the host file system  
- Lambda has admin IAM role and puts temporary keys in logs  

One exploit and an attacker could:

- Lateral move from container to host  
- Use EC2 as a pivot point  
- Exfiltrate data via Lambda with unrestricted permissions  

But if Blizzard follows best practices:

- EC2 is patched, uses **SSM Session Manager**, no SSH  
- ECS runs with task-level **IAM roles**, no host mounts  
- Lambda uses scoped-down roles, encrypted **env vars**  
- **CloudTrail** records all activity  
- **CW Alarms** fire on anomalies  
- **GuardDuty** watches for port scanning, unusual patterns  

They’ve built a **multi-layered defense across compute** — breach resilience, containment, and forensics.

---

## How It Works — Key Components of Compute Security

### 1. Identity and Access Management (IAM)

- Every compute resource needs a role — but **least privilege is non-negotiable**  
- Never use admin-level IAM policies for EC2, Lambda, or containers  
- Use **IAM roles for service accounts in EKS**, **task roles in ECS**, and **execution roles in Lambda**  
- Rotate access tokens and credentials  
- Avoid storing secrets in environment variables (use **Secrets Manager** or **SSM Parameter Store**)  

### 2. Network Boundaries

- Use **VPC**, **subnets**, **security groups**, and **NACLs** to isolate workloads  
- Private subnets for sensitive workloads  
- Security groups scoped tightly: by port, protocol, and **CIDR**  
- Use **VPC endpoints** for services like S3, so traffic never hits the internet  
- Enable **TLS everywhere** — especially for intra-service communication  

### 3. Operating System Hardening (EC2)

- Use latest **Amazon Linux 2023** or hardened Ubuntu **AMIs**  
- Patch regularly with **SSM Patch Manager**  
- Use **EC2 Instance Connect** or **SSM Session Manager** instead of SSH  
- Disable password-based **auth**, restrict root access  
- Install **AWS Inspector** to scan for **CVEs**  

### 4. Runtime Security (Containers & Lambda)

- Use **read-only file systems** and minimal base images  
- Scan containers for vulnerabilities (**Amazon Inspector**, **ECR scan**)  
- Drop unnecessary Linux capabilities (`cap_drop`)  
- Don’t run containers as root  

For Lambda:

- Limit function timeout and memory  
- Encrypt environment variables  
- Avoid writing secrets to logs  
- Use **layers** responsibly and scan them  

### 5. Monitoring and Detection

- Enable **CloudTrail** for all regions and services  
- Send **CloudWatch Logs** for compute services to a central log group  
- Enable **VPC Flow Logs** to track network patterns  
- Use **GuardDuty** to detect:
  - Port scanning from EC2  
  - Data exfiltration  
  - Unauthorized **IAM** calls  
- Integrate with **Security Hub** to centralize findings  
- Create **CloudWatch Alarms** for:
  - High CPU (possible cryptomining)  
  - Unexpected outbound traffic  
  - Role assumption spikes  

### 6. Isolation and Blast Radius

- Use **auto-scaling groups** for EC2 — if one is compromised, destroy and replace  
- Deploy **Lambda functions per responsibility**, not as catch-alls  
- Use **dedicated namespaces in EKS**, **task definitions in ECS**, and restrict **IAM roles per compute unit**  
- Design for **least privilege, segmentation, and rotation**  

### 7. Encryption and Data Access

- Use **EBS encryption** for EC2  
- Encrypt ephemeral storage in Lambda  
- For containers, store sensitive data outside the image — fetch securely at runtime  
- For all compute, audit access to:
  - **S3**
  - **RDS/EFS**
  - **DynamoDB**
  - **Parameter Store**

---

## Pricing Implications

Security features are mostly **free** unless tied to other services:

- **CloudTrail**, **CloudWatch Logs**, and **GuardDuty** have ingestion and analysis costs  

- **AWS Inspector** charges per EC2 instance/container scanned  
- **Patch Manager**, **Session Manager** — no extra charge  
- **EC2/ECS/Lambda** pricing as usual — **no premium for being secure**, but insecure configs could cost you via incident response  

The biggest cost isn't the bill — it's the **blast radius** if you don't secure compute.

---

## Real-Life Example: *SnowyCorp’s Incident Response Rewrite*

**SnowyCorp** once had a Lambda function with:

- Overprivileged **IAM role**  
- Debug logs storing decrypted secrets  
- 12-hour token validity  
- Public API Gateway with no **auth**  

One day, a junior **dev** deployed a change. Within minutes:

- Attacker scraped the public endpoint  
- Found leaked **JWT** token in logs  
- Assumed role with `s3:*` and `kms:Decrypt`  
- Downloaded customer reports and **PII**  

Post-incident, **SnowyCorp** rewrote compute security:

- All functions moved to private **VPC**  
- Secrets encrypted with **KMS** and pulled at runtime  
- **IAM** role scoped to 4 permissions  
- Logs scrubbed via **Lambda layers**  
- API Gateway protected with **JWT authorizer**  

They now treat every compute unit as a **blast zone** and build with the assumption that **any one function or container could get popped.**

---

## Final Thoughts

In cloud security, compute is **where it all goes live.**  
It’s where your code, your secrets, and your data touch the open world.

If your EC2 instance runs **unpatched software**, you're one `curl | bash` away from a breach.  
If your Lambda runs as admin, you're one bad deployment away from lateral movement.  
If your ECS container stores AWS keys in **env vars**, you’re one log dump away from account compromise.

Compute security isn’t optional — it’s foundational.  

**Design with zero trust. Operate with least privilege. Monitor like you’ve already been breached.**

And always ask:

> “If this one box goes rogue, how far can it reach?”

If the answer is **“too far”** — you’ve still got work to do.

