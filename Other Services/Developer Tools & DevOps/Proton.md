# AWS Proton

## What Is the Service

AWS Proton is a fully managed platform engineering service that allows you to automate, standardize, and govern infrastructure and application deployments across an organization. It helps platform teams define infrastructure templates (VPCs, ECS/Fargate services, CI/CD, observability stacks, etc.) that developers can self-service — without breaking security policies or reinventing the wheel.

Think of it as a secure golden path factory — platform engineers define the paved road, and application teams stay on it without needing to write CloudFormation or Terraform.

For Snowy’s team, this solves a painful reality:
- Too many devs writing their own IaC templates  
- Inconsistent CI/CD pipelines  
- No guarantees that apps followed tagging, logging, encryption, or compliance rules  
- Difficult to audit multi-account deployments

With Proton, Snowy builds pre-approved infrastructure stacks that:
- Are version-controlled  
- Enforce tagging, IAM boundaries, and guardrails  
- Deploy via integrated pipelines  
- Expose just enough inputs to devs, but not the keys to the kingdom

---

## Cybersecurity Analogy

Imagine you’re running a secure research lab. You can’t allow every scientist to design their own containment facility from scratch — but they still need to run experiments.

**Proton is like giving them sealed, approved laboratory templates.**  
They:
- Provide inputs (e.g., repo URL, env name)  
- Proton deploys the full lab environment (network, compute, pipeline, observability)  
- And ensures you still control the blueprints, not them

This creates standardization without sacrifice, and enforces security by design.

## Real-World Analogy

Proton is like a food truck franchise builder. You’re the platform team. You’ve built:
- The truck design (VPC)  
- The equipment layout (ECS + CI/CD pipeline)  

- The food safety checklists (IAM roles + CloudWatch + tagging)  
- The signage and theme (naming conventions, route53, TLS)

Now anyone in your org can spin up a new food truck by just saying:
- What city they want to deploy to  

- What menu (repo) they want to use

**Proton spins it up — identical, auditable, and compliant — in minutes.**  
No one’s writing the plumbing. No one’s opening security holes. It’s paved, governed, and observable.

---

## How It Works

Proton is built around templates, environments, and services.

### Core Concepts:

| Concept            | Description                                                          |
|--------------------|----------------------------------------------------------------------|
| Environment Template | Defines shared infrastructure like VPC, subnets, ALB, IAM, secrets, logging |
| Service Template     | Defines individual deployable services (e.g., ECS app, Lambda API)     |
| Environment          | Instantiated stack based on environment template                     |
| Service              | Instantiated app deployed into an environment                         |
| Inputs (Parameters)  | Values the developer supplies (Git repo URL, service name, etc.)      |
| Provisioning Method  | Can use CloudFormation, Terraform, or CodeBuild-based pipelines       |

### Flow:
- Platform team defines reusable templates with IaC + CI/CD + observability baked in  
- App teams provision services via Proton console or API  

**Proton:**
- Provisions infra (e.g., ECS, VPC)  
- Deploys app from source control  
- Connects to CodePipeline/GitHub  
- Hooks into CloudWatch/X-Ray/Grafana  
- All deployments are version-controlled  
- Platform team can update templates, roll out changes org-wide  
- App teams get notified if their environment is outdated  

---

## Security and Compliance Relevance

This is where Proton shines. It’s not just a developer enablement tool — it’s a security enforcer for scalable, governed infrastructure.

### Security Benefits:

| Requirement                    | Proton Capability                                                           |
|--------------------------------|------------------------------------------------------------------------------|
| Centralized control of IaC     | Platform team owns templates; app teams can’t edit infra                    |
| IAM least privilege            | Predefined roles assigned per template                                      |
| Network zoning                 | VPCs, subnets, SGs all defined in the environment template                  |
| Logging & tagging enforced     | All resources come with baked-in CloudWatch and tags                        |
| Template versioning            | Track changes across accounts; update stale stacks                          |
| CI/CD pipelines pre-approved   | No rogue pipelines — every deployment runs through defined CodePipeline     |
| Secrets management             | Integrate with Secrets Manager or SSM Parameter Store in template code      |
| Cross-account deployment       | Supports multi-account setups via CodePipeline, StackSets, or TF backends   |
| Audit trail                    | CloudTrail logs template usage, updates, and deployments                    |

### Potential Risks (Mitigated with Guardrails):

| Risk                            | Mitigation                                                                 |
|----------------------------------|----------------------------------------------------------------------------|
| App teams modifying stacks       | Proton doesn't expose underlying stacks unless explicitly allowed         |
| Environment drift                | Templates are version-controlled; teams notified when out of date         |
| Deployment bypass                | All infra deployed through Proton CI/CD; manual changes not supported     |
| Secrets exposed in inputs        | Use secretsManager inputs and encrypted variables                         |
| Rogue template uploads           | IAM scoping limits who can define templates (usually just platform team)  |

---

## Pricing Model

As of now, **AWS Proton itself does not charge directly** — you pay for:
- The underlying resources it deploys (ECS, VPC, ALB, etc.)  
- CodeBuild or CodePipeline runs  
- Monitoring and logging (CloudWatch, X-Ray)  
- Secrets Manager usage

Platform teams manage this by enforcing **resource tagging + quota monitoring**, so no one launches $2,000/month templates by mistake.

---

## Real-Life Example (Snowy’s Platform Engineering Team)

**Snowy’s org had:**
- 15 dev teams  
- 100+ microservices  
- ECS, Lambda, and VPC stacks  
- Compliance requirements: All services must log to CloudWatch, encrypt at rest, rotate secrets, and use IAM boundary roles

### The challenge:
- Every team wrote their own Terraform  
- Inconsistent tagging, patching, and audit coverage  
- Insecure S3 buckets were getting deployed accidentally  

### The fix: AWS Proton

**Platform team created:**
- One environment template with VPC, SGs, IAM boundary roles, logging  
- Two service templates:  
  - ECS service with ALB + CI/CD  
  - Lambda + API Gateway + Secrets

**Dev teams launched services by filling in:**
- GitHub repo  
- Env name  
- Team tag

Each service was:
- Auto-wired into CloudWatch Logs and Metrics  
- Enforced with tagging, encryption, and secrets policies  
- Deployable via CodePipeline with guardrails

**Platform team rolled out a patch to environment template for new VPC policy — all environments updated with a click.**

**Now:**
- Compliance is enforced by design  
- Dev teams move faster  
- No Terraform drift  
- No hand-deployed resources  
- Snowy sleeps easier

---

## Final Thoughts

**AWS Proton is platform engineering with security built in.**

It’s not just a fancy IaC wrapper — it’s:
- A **governance layer**
- A **developer accelerator**
- A **compliance enforcer**

For orgs like Snowy's that operate at scale, with dozens of accounts and strict operational control needs, Proton provides:
- Standardization of every service  
- Secure self-service infrastructure  
- Built-in versioning and auditability  
- Peace of mind for security, ops, and compliance

**It’s IaC done right — without letting devs deploy ticking time bombs.**

