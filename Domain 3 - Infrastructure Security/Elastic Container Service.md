# Amazon ECS

## What Is ECS

Amazon **ECS** is a **container orchestration service** — AWS’s native answer to “How do I run and scale hundreds of containers across a fleet?”

**ECS** can run on:

- **EC2**: You manage the instances (hosts, patching, capacity)  
- **Fargate**: AWS runs the infrastructure, you just define the tasks  

**Security-wise**:

- **ECS** doesn’t enforce safety  
- It provides the **hooks**  
- **You** secure the containers, **IAM**, networking, secrets, logging, runtime, and CI/CD pipelines  

> If you get it wrong, containers become an **extremely fast way to misconfigure hundreds of workloads at once.**

---

## Cybersecurity Analogy

**ECS** is like setting up a massive convention hall with booths for 300 vendors (containers).

AWS gives you:

- The walls  
- The electricity  
- The basic blueprints  

But **you** decide:

- Who gets which booth  
- Who can talk to whom  
- Which vendor has access to the speaker system (**IAM**)  
- Whether anyone bothered locking their cash register (secrets, runtime controls)  

> If you don’t control that?  
> You’ve created a **loud, insecure free-for-all** where **compromise spreads fast**.

## Real-World Analogy

**BlizzardTech** moves from monoliths to containers.  
They deploy 12 **microservices** via **ECS** on **EC2**.

Each task:

- Runs as root  
- Pulls from public **DockerHub**  
- Assumes a shared **IAM** role with `s3:*`  
- Has full egress to the internet  
- Logs to `/tmp/app.log` but nothing else  

**Six months later**:

- An **RCE** in the analytics container lets an attacker drop a reverse shell  
- The task steals credentials via **IMDS**  
- Accesses `s3://prod-billing-archive`  
- And there’s no **CloudTrail**, no logs, no detection  

> Welcome to orchestration **without segmentation**.

---

## Core ECS Security Surfaces

### 1. Task IAM Roles (Execution Role vs Task Role)

**Execution Role**  
Used by the **ECS** agent to:

- Pull images from **ECR**  
- Fetch secrets from Secrets Manager or **SSM**

**Task Role**  
Used **inside the container** — this is where actual workload permissions live

**Mistakes to avoid:**

- Reusing the same role across tasks  
- Granting `s3:*`, `dynamodb:*`, `ssm:GetParameter` with no scoping  
- Not using **IAM Conditions** to restrict resource access  

**Fix it:**

- One **IAM** task role per service  
- Scope every permission by **Resource**  
- Use **Access Analyzer** to detect unused or risky permissions  
- Monitor via **CloudTrail**: `AssumeRole`, `GetSecretValue`, `GetObject`

### 2. Image Security

This is where most breaches begin.

**Threats:**

- Outdated images  
- Pulled from public **DockerHub**  
- **Hardcoded secrets**  
- Compromised base images  

**Best practices:**

- Build and scan images in **CI/CD**  
- Push to **Amazon ECR**  
- Enable **Amazon Inspector ECR scanning**  
- Use immutable tags (`:v1.2.4`, not `:latest`)  
- Use **multi-stage builds** to strip **dev** tools  

> Remember: if your container runs `curl` and `bash`, so can the attacker.

### 3. Secrets and Config Management

**ECS** supports:

- **Secrets Manager**  
- **SSM Parameter Store**  
- Environment variables (dangerous if misused)

**Do not:**

- Bake secrets into the Docker image  
- Inject secrets via plaintext environment variables  

**Do:**

- Use `secrets` block in **ECS Task Definition**  
- Inject at runtime  
- Use **CMKs** with restrictive **KMS** policies  
- Rotate secrets regularly  

Audit access via:

- **CloudTrail** (`secretsmanager:GetSecretValue`)  
- **GuardDuty** (unusual calls from tasks)

### 4. Networking and Isolation

**ECS** supports different **network modes**:

- `bridge` (default on EC2): shared Docker network  
- `host`: binds container ports to host ports  
- `awsvpc`: gives each task its own **ENI (Elastic Network Interface)**

**Fargate always uses `awsvpc`**  
For EC2 mode, `awsvpc` is optional but **highly recommended for isolation**

**Security implications:**

- Tasks in `bridge` mode can talk to each other by default  
- No **SGs** apply unless using `awsvpc`  
- Without **VPC-level control**, a compromised container can pivot laterally

**Best practices:**

- Use `awsvpc` mode with tightly scoped **Security Groups**  
- Place tasks in private **subnets** behind NAT  
- Use **VPC endpoints** for S3, Secrets Manager, etc.  
- Block all egress traffic by default unless needed

### 5. Runtime Hardening

Out of the box, containers are not secure:

- Run as root  
- Full capabilities (`cap-add`)  
- Can mount `hostPath` volumes (EC2 mode)  
- Can write anywhere in the **FS**

**To harden:**

- Drop unnecessary capabilities (`cap-drop`)  
- Set `readOnlyRootFilesystem: true`  
- Run as a **non-root user**  
- Set memory and CPU limits (to avoid **DoS**)  
- Disable `privileged: true` unless absolutely needed  
- Use **AppArmor/SELinux** for host-level isolation (EC2 mode)

### 6. Logging and Observability

If you don’t configure logging, you get nothing.

**ECS** supports:

- **CloudWatch Logs** (via `awslogs` log driver)  
- **X-Ray** for tracing  
- **CloudWatch Container Insights**  
- **GuardDuty** (Runtime Monitoring for **ECS EC2** only)

**Best practices:**

- Enable structured logging  
- Create log groups per service  
- Set log retention policies  
- Use **CW Alarms** for:  
  - Task failure spikes  
  - High CPU/memory  
  - Unexpected restarts

> For **Fargate**: logs are your **only forensic artifact** if the container is compromised.

### 7. Patching and Drift Detection

- **Fargate**: no patching needed — AWS owns the host  
- **EC2 mode**: you patch the instance, Docker, ECS agent, OS, kernel, etc.

If you:

- Forget to patch a kernel **vuln** (like Dirty COW)  
- Leave **ECS** agent 3 versions behind  
- Reuse outdated **AMIs**

You’ve created a **persistent vulnerability distribution system**

**Best practices:**

- Use EC2 Auto Scaling Groups with golden **AMIs**  
- Patch **AMIs** regularly  
- Rotate EC2 instances every 30–60 days  
- Use **SSM Patch Manager + AWS Config** for drift detection

---

## Pricing Model (Security-Relevant)

| Component           | Notes                                                  |
|---------------------|--------------------------------------------------------|
| **EC2 Mode**        | Charged by instance size + **EBS**                     |
| **Fargate Mode**    | Billed by **vCPU** + RAM per second                    |
| **ECR**             | Charged by GB/month + transfer                         |
| **CloudWatch Logs** | Charged by ingestion and storage                       |
| **Secrets Manager** | $0.40/secret/month + API calls                         |
| **Inspector Scanning** | Per image scan                                    |
| **GuardDuty Runtime** | Per task/month (**Fargate** support coming)         |

> Security costs scale linearly — but **cost avoidance** leads to exponentially higher incident costs.

---

## Snowy Real-Life Example

**BlizzardSecurity** inherits an **ECS** environment that:

- Runs in EC2 mode  
- Uses bridge networking  
- Shares one **IAM** task role across all services  
- Pulls images from **DockerHub** `latest`  
- Has no **CloudWatch** logs or **GuardDuty** enabled  

**During a routine check**, Snowy finds:

- One task talking to `198.51.100.4` every 10 seconds  
- Secrets pulled from **SSM**, but the same role can decrypt **20+ secrets**  
- No visibility into task launches, restarts, or failures  

**Fixes:**

- Switch to `awsvpc` networking + **SGs**  
- Break apart **IAM** roles per service  
- Enable **Inspector** + **ECR** scanning  
- Push images to private **ECR**  
- Lock down outbound traffic via **SG** egress rules  
- Tag every resource and enable **AWS Config** to enforce security posture  

---

## Final Thoughts

**ECS** isn’t insecure. It’s just **neutral**.  
You decide if it becomes a secure platform — or a ticking time bomb.

If you:

- Scope **IAM** roles  
- Harden containers  
- Use **VPC** isolation  
- Secure your secrets  
- Push from trusted CI/CD  
- And monitor what’s running  

Then **ECS** becomes one of the most powerful ways to **orchestrate securely** at scale.

But if you don’t?  
You’ve just made it easier to compromise **hundreds of workloads at once**.
