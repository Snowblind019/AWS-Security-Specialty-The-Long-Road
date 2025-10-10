# Amazon ECS on Fargate

## What Is ECS Fargate (And Why Security Still Matters)

ECS (Elastic Container Service) is AWS’s native container orchestration platform.  
Fargate is the **serverless compute engine** for containers — meaning:

- You don’t manage EC2 clusters or underlying instances  
- You define task definitions (container configs), IAM roles, networking, and logging  
- AWS spins up the actual compute node, runs your container, and tears it down  

**Sounds perfect for security, right?**  
No host management, no patching, no SSH — just isolated workloads running as needed.

But here’s the catch:  
The surface area **moves**. It doesn’t **disappear**.  
You’re no longer responsible for the EC2 host —  
But you’re fully responsible for the **task-level security**, **IAM scoping**, **image trust**, and **runtime behavior**.

---

## Cybersecurity Analogy

Using Fargate is like **renting a sealed food truck** for your pop-up kitchen.  
You don’t own the engine, tires, or generator — AWS keeps that running.

But:

- You still bring your own ingredients (container images)  
- You decide the recipes (task definitions)  
- You’re still the one liable if a customer gets food poisoning (security breach)  

So if you:

- Use a tainted base image  
- Leave the fridge door open (overpermissioned IAM)  
- Let unverified people into the truck (bad networking rules)  

It’s still your problem, even if AWS owns the vehicle.

## Real-World Analogy

**Winterday** is deploying an event processing service on Fargate.  
Each task:

- Pulls from an SQS queue  
- Writes processed results to S3  
- Runs Python code with third-party pip dependencies  

The dev team:

- Reuses an old Docker image with outdated OpenSSL  
- Grants the task role `s3:*` for speed  
- Doesn’t restrict task ingress/egress  

**Within a month**:

- A vulnerability in a pip package gets exploited  
- Attacker uses SSRF to query the metadata endpoint  
- Steals temporary IAM credentials  
- Uses them to list and download sensitive S3 data  

**Fargate ran perfectly.**  
But Fargate didn’t fail — *Winterday’s configuration did*.

---

## What to Secure in Fargate (And Why)

### 1. Task IAM Roles (Scoped Execution Permissions)

Each ECS Task running on Fargate assumes an **IAM Task Role**.

**Common mistakes:**

- Using the same role across all services  
- Granting `s3:*`, `ssm:*`, or full `AdministratorAccess`  
- Not scoping by `Resource:` — allowing access to any bucket, table, secret  

**Best practices:**

- One IAM role per service  
- Scope down to specific actions and ARNs  
- Tag and version roles for audit  
- Use IAM Access Analyzer to detect risky permissions  
- Rotate secrets and credentials regularly  

This role is used by the container **inside** the task, and it’s fetched via the metadata endpoint —  
So if someone compromises your container, **they can use it**.

### 2. Networking Configuration

Fargate tasks run in your VPC, but **security is up to you**.

**Network mode:** `awsvpc`

- Each task gets its own ENI (Elastic Network Interface)  
- You must assign **Security Groups** and **Subnets**  

**Common issues:**

- Assigning public IPs to tasks unnecessarily  
- Using broad SGs (`0.0.0.0/0` ingress on all ports)  
- Allowing outbound traffic to the internet with no egress control  
- Placing tasks in private subnets without NAT — breaking outbound comms  

**Best practices:**

- Put tasks in **private subnets behind NAT**  
- Use tight Security Groups  
- Route egress through **VPC endpoints** for S3, SQS, etc.  
- Enable **Flow Logs** to detect abnormal communication  
- Use **Service Connect + App Mesh** for mTLS and traffic observability (if needed)  

### 3. Container Image Security

The image is the **root of trust** in Fargate.

**Threats:**

- Outdated dependencies  
- Public base images with CVEs  
- Typosquatting (`requests3` vs `requests`)  
- Secrets baked into environment variables  

**How to secure it:**

- Build images in CI/CD with signed provenance  
- Store in **Amazon ECR**  
- Enable **Amazon Inspector ECR Scanning**  
- Use immutability tags (`:v1.2.3`, not `:latest`)  
- Never include secrets or private keys inside the image  

### 4. Secrets Handling

Secrets (like API keys, DB credentials, tokens) must be **handled outside** the image.

Fargate supports:

- **AWS Secrets Manager** (pull into task at runtime)  
- **SSM Parameter Store (SecureString)**  
- ECS task **environment variables** (not ideal unless injected securely)  

**Best practices:**

- Never hardcode secrets  
- Use `secrets:` block in ECS task definition to pull from Secrets Manager  
- Scope IAM role to only decrypt **needed** secrets  
- Rotate secrets automatically with Lambda or native integration  
- Use **KMS key policies** to restrict decryption  

### 5. Logging and Observability

If you don’t configure logging, you get **nothing**.  
No stdout, no stderr, no metrics — just *“the task failed.”*

ECS Fargate supports:

- **CloudWatch Logs** (`log driver: awslogs`)  
- **X-Ray** (for tracing)  
- **Container Insights** (CPU, memory, network metrics)  
- **GuardDuty** (analyzes VPC traffic, DNS behavior)  

You should:

- Always enable CloudWatch Logs per task  
- Create log groups **per service** (rotate via retention policy)  
- Monitor task failures with **CloudWatch Alarms**  
- Enable runtime metrics via **CloudWatch Container Insights**  

### 6. Runtime Isolation and Defense

Fargate isolates containers per task with **Firecracker microVMs**.

But once **inside** the container:

- There is **no VM barrier** — you’re in the process space  
- There’s no root filesystem isolation between layers of your own container  
- Privilege escalation is still possible if your app has flaws  

You should:

- Drop Linux capabilities (`cap-drop`)  
- Run containers as **non-root**  
- Set **read-only root filesystems** if possible  
- Limit memory and CPU to avoid DoS  
- Add runtime EDR (e.g., **Falco** or **GuardDuty ECS Runtime Monitoring**)  

Fargate doesn’t patch **your app** — only the microVM and kernel it runs on.

### 7. Drift and Misconfiguration Detection

Fargate tasks can **silently drift** out of secure config.  
There’s no alarm when:

- A task runs with a public IP  
- A new IAM policy gets attached to a task role  
- A secret is rotated, but the task still uses the old one  

**Use these tools:**

- **AWS Config** (rules for `fargate-task-uses-public-ip`, etc.)  
- **Security Hub** (aggregates misconfigs)  
- **CloudTrail** (task creation events)  
- **EventBridge** to alert on:  
  - `StartTask` from unusual principal  
  - `PutRolePolicy` modifying execution role  

---

## Pricing Considerations (Security-Linked)

| Feature               | Cost                                  |
|-----------------------|----------------------------------------|
| Fargate vCPU/Memory   | Pay per second                        |
| CloudWatch Logs       | Charged by ingestion + storage        |
| Secrets Manager       | $0.40/secret/month + API calls        |
| KMS CMK usage         | $1/month/key + usage                  |
| Amazon Inspector      | Charged per scan                      |
| GuardDuty Runtime     | Charged per task + log volume         |

> Security costs scale with how many moving parts you add —  
> But skipping logging or scanning to “save money” costs way more during a breach.

---

## Snowy Real-Life Use Case

**Snowy’s startup** launches a “quote calculator” microservice via ECS Fargate.  
It runs **Python Flask**, pulls pricing data from **DynamoDB**, and gets hit **1,000+ times/day** via API Gateway.

The dev team:

- Grants the task `dynamodb:*`  
- Pulls image from **public DockerHub**  
- Runs containers **as root**  
- Doesn’t enable **logging**  

A **pentester reports**:

- The image contains an old version of `urllib3` with a known RCE  
- The IAM task role could access **every table**, not just pricing  
- No logs exist to verify access patterns or abuse  

**Postmortem:**

- CI/CD is updated to use hardened **ECR images**  
- IAM roles are scoped to `dynamodb:GetItem` on **PricingTable**  
- **GuardDuty + Inspector** enabled  
- **Logging** turned on across all new services  

---

## Final Thoughts

Fargate is **secure by design** —  
But **not secure by default**.

You get:

- No OS patching  
- No host exposure  
- No SSH  

But you still need to secure:

- IAM  
- Secrets  
- Images  
- Logging  
- Networking  
- Runtime behavior  

If you don't do that, it doesn't matter that there's no EC2 node —  
You're still the one getting breached.

> *The container is your castle — but you’re still the one guarding the gate.*
