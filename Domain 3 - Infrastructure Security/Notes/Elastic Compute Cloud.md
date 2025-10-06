# Amazon EC2

## What Is Amazon EC2

Amazon EC2 gives you **virtual machines in the cloud**. You pick an AMI (OS image), a type (CPU/mem), and a network (**VPC**), and AWS gives you a **bootable** instance.

But here’s the thing:  
**You manage everything inside the instance.**  
From OS patches to SSH keys to firewalls to software versions — **AWS doesn’t touch your guest OS.** You’re on the hook.

That means if you:

- Forget to patch a public-facing EC2 running Ubuntu 18.04  
- Leave a stale SSH key for a terminated contractor  
- Install `nginx` and forget to disable directory listing  
- Or let an EC2 **IAM** role write to `s3://snowy-prod-finance` …

Then you’ve basically handed attackers the keys and said, “Welcome in.”

---

## Cybersecurity Analogy

Think of EC2 as renting a secure apartment inside a skyscraper.  
AWS gives you:

- The building (data center)  
- The walls (hypervisor)  
- The lock on your front door  

**But you bring everything else inside:**

- Who gets keys  
- What you install  
- Whether your windows are locked  
- Whether your security camera is running  

And if you forget to install antivirus, leave the oven on, and hand out 12 spare keys to old roommates… that’s on you.

## Real-World Analogy

**SnowyCorp** spins up a temporary EC2 instance to run a data transformation job over the weekend.

- They give it full `AdministratorAccess` so it can debug issues fast  
- It has port 22 open to the world  
- And they forget to shut it down  

**Monday morning:**

- It’s been brute-forced overnight  
- A crypto miner is now running inside  
- **CloudTrail** is full of `s3:GetObject` calls to sensitive buckets  

No alarms fired. No **GuardDuty** finding.  
Why? Because **nobody configured anything.**

---

## Key Security Concepts You Must Lock Down

### 1. Instance Roles (**IAM**)

Each EC2 instance can assume an **IAM** role at boot.  
This is where **blast radius gets real**:

- **Overpermissioned** roles (e.g., `s3:*`, `kms:*`, `ec2:*`)  
- **Unscoped** roles (no `Resource:` scoping)  
- Roles shared across too many environments  

**Best Practices:**

- Create one **IAM** role per purpose (least privilege)  
- Attach roles via **Instance Profile**  
- Use `iam:PassRole` restrictions in pipelines to control who can assign what  
- Rotate temporary credentials regularly  
- Monitor `GetRoleCredentials` via **CloudTrail**

### 2. Instance Metadata Service (IMDSv2)

**IMDS** is what the instance uses to get its own credentials, region info, tags, and more.

**In IMDSv1:**

- Anyone who got access to the OS could `curl` their way to stealing **IAM** credentials

**In IMDSv2:**

- AWS requires a **session token** and uses a **TTL** + hop limit to prevent **SSRF**

**You should:**

- Enforce **IMDSv2 only**  
- Set **hop limit = 1** to prevent **SSRF** from containers  
- Monitor for failed token fetches — could indicate probing  

### 3. SSH Access and Key Management

This is where most teams mess up.

**Risks:**

- Stale `authorized_keys`  
- Insecure ciphers or SSH versions  
- Public AMIs with **pre-installed backdoors**  
- Default login user with reused keys  

**Fix it:**

- Use **EC2 Instance Connect**, not manual key distros  
- Or better: **SSM Session Manager** (no SSH at all)  
- Use **cloud-init** to inject ephemeral keys on launch  
- Rotate SSH keys regularly and script the rotation  
- Restrict source IPs via **Security Groups**

### 4. Networking: Security Groups + NACLs

#### **Security Groups (SGs):**

- **Stateful**  
- Allow rules only (no denies)  
- Applied at **ENI** level  
- Default outbound is wide open  

#### **Network ACLs:**

- **Stateless**  
- Can deny  
- Work at **subnet** level  
- Evaluated in order  

**You should:**

- Apply tight **SGs** per workload  
- Use **SG** references instead of **CIDRs** when possible  
- Deny all inbound except known ports  
- Limit outbound to only required services (S3, RDS, etc.)  
- Alert on `0.0.0.0/0` ingress or egress rules  

### 5. AMI Hygiene and Hardening

If your AMI is insecure, every EC2 launched from it will be too.

**Risks:**

- Outdated packages  
- Embedded secrets  
- Debugging tools left enabled  
- Firewall off  
- Root login via SSH  

**What to do:**

- Use **golden AMIs** with baseline controls  
- Scan with **Amazon Inspector**  
- Harden OS with **CIS benchmarks**  
- Store AMI source code (Packer, Ansible, etc.) in Git  
- Tag AMIs with owner + patch status  

### 6. Monitoring and Visibility

By default, EC2 instances are a black box.

You need to add:

- **CloudWatch Agent** for system metrics  
- **CloudWatch Logs** for `/var/log/secure`, `nginx` logs, etc.  
- **SSM Agent** for command execution, patching, and session control  
- **Inspector** for vulnerability scans (OS + apps)  
- **GuardDuty** for detecting:
  - Crypto mining  
  - Port scanning  
  - Credential **exfil**  
  - Unusual traffic  

> **You must explicitly install, enable, and configure these.**

### 7. Patch Management

EC2 is **not automatically patched** — that’s your job.

**You can:**

- Use **SSM Patch Manager** to define patch baselines  
- Schedule patch windows with **Maintenance Windows**  
- Tag instances by environment (`PatchGroup = prod`)  
- Monitor patch compliance via **SSM Compliance dashboard**  

> Neglect this, and you’ll fall behind on kernel updates, SSH flaws, SSL bugs, and more.

---

## Pricing Model (Security-Relevant)

| Component           | Cost                                                                 |
|---------------------|----------------------------------------------------------------------|
| EC2 instance hours  | Billed per second or hour                                            |
| **EBS volumes**     | Charged per GB provisioned + **IOPS** if applicable                 |
| Inspector scans     | Billed per instance scanned                                          |
| **SSM usage**       | Free for most, some features (like advanced inventory) are billed    |
| **CloudWatch Logs** | Charged by ingestion and storage                                     |
| **GuardDuty**       | Charged by **VPC** flow log volume, **DNS**, **CloudTrail** events  |

> So yeah — a **poorly secured EC2** that’s logging too much, running scans 24/7, and getting hammered by attackers can cost you **more than just the VM.**

---

## Snowy Real-Life Scenario

**BlizzardFinance** spins up an EC2 for an RDS migration tool.

It has:

- An **IAM** role with `rds:*`, `s3:*`, and `kms:*`  
- SSH open to `0.0.0.0/0` “for quick debugging”  
- **CloudWatch** Agent not configured  
- No patching  
- A leftover key from a **dev** that quit last month  

**Within a week:**

- The instance gets brute-forced  
- The attacker installs a backdoor and scripts to enumerate S3 buckets  
- The **IAM** role grants access to snapshots from `blizzard-prod-audit`  
- They **exfil** sensitive audit logs via HTTPS  

**Blizzard** only finds out because of a **GuardDuty** finding, triggered too late.

**Lesson?** EC2 is **dangerous if neglected**, and AWS doesn’t hold your hand once it boots.

---

## Final Thoughts

You don’t “set and forget” EC2.  
You babysit it. You harden it. You rotate keys. You scan **AMIs**. You monitor roles. You restrict ports. You patch. You log. You tag. You restrict outbound traffic. You treat every instance like it’s already compromised.

Because one day, it might be.
