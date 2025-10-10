# Container Security

## What Is Container Security

Container security is the practice of securing everything involved in the lifecycle of containers — from the build stage to runtime, including the image, infrastructure, orchestration platform, and the supply chain. Containers offer lightweight, portable environments to run applications — but they also bring new attack surfaces:

- Vulnerable base images  
- Insecure container runtimes  
- Poorly isolated workloads  
- Overprivileged containers  
- Insecure orchestration (like Kubernetes)  
- Secrets baked into images or environment variables  
- Unscanned dependencies and CI/CD pipelines

In AWS, containers usually run on:

- Amazon ECS (Elastic Container Service)  
- Amazon EKS (Elastic Kubernetes Service)  
- AWS Fargate (serverless containers)  

And container images are stored in **Amazon ECR** (Elastic Container Registry).

If you don't secure containers from build to runtime, attackers can exploit:

- Public base images with known CVEs  
- Lack of image signing or provenance  
- Misconfigured Kubernetes roles (RBAC)  
- Unencrypted secrets  
- Outdated libraries inside containers  
- Or even host escape into the EC2/Fargate host

---

## Cybersecurity and Real-World Analogy

### Cybersecurity Analogy

Think of containers like shipping containers on a cargo ship.

If the container itself is tampered with at the source (build stage), or if the seals are broken (image signature missing), or if customs checks are skipped (no vulnerability scans), then you’re blindly shipping in potentially dangerous goods.

And if the cargo ship (host EC2) doesn’t enforce compartmentalization between containers, one bad actor can compromise the entire vessel.

### Real-World Analogy

Imagine you're renting booths to food vendors at a massive festival. Each vendor (container) should be isolated — with its own supplies, burners, and rules.

But if you allow one vendor to walk into another's booth, or share a burner, or leave raw meat next to cooked food (insecure shared resources), you're inviting cross-contamination.

---

## How It Works / What to Secure

### 1. Image-Level Security

- Use minimal base images (e.g., distroless, Alpine)  
- Scan images continuously for vulnerabilities (CVEs)  
- Sign images and enforce image provenance  
- Remove hardcoded credentials from Dockerfiles  
- Store images in **Amazon ECR**, which supports:  
  - Vulnerability scanning (w/ Inspector)  
  - Immutable tags  
  - Lifecycle policies for stale images  

### 2. Build Pipeline Security

- Use CI/CD scanning tools to catch issues early (e.g., Trivy, Clair, Checkov)  
- Enforce linting + policy-as-code (e.g., OPA/Gatekeeper for Kubernetes)  
- Avoid pulling images from untrusted sources  

### 3. Runtime Security

- Drop unnecessary Linux capabilities (`cap-drop`)  
- Run containers as non-root  
- Use read-only filesystems where possible  
- Set resource limits (CPU, memory)  
- Monitor runtime behavior (unexpected processes, open ports, etc.)  

### 4. Orchestration Security (EKS/Kubernetes)

- Use RBAC to restrict access to Kubernetes resources  
- Enable audit logging and VPC Flow Logs  
- Use PodSecurityPolicies or OPA/Gatekeeper  
- Rotate secrets via AWS Secrets Manager or SSM Parameter Store  
- Avoid exposing services via public LoadBalancers unless needed  
- Limit node access to specific container registries only  

### 5. Host and Network Security

- Harden EC2 or Fargate base hosts  
- Enforce Security Groups per ECS task or EKS pod  
- Use Service Mesh (like App Mesh) for fine-grained traffic control and mTLS  
- Enable encryption in transit and at rest  

---

## Pricing Models (AWS)

| AWS Component        | Pricing Considerations                                  |
|----------------------|----------------------------------------------------------|
| Amazon ECR           | Pay for GB stored + GB data transferred                  |
| Inspector (ECR scan) | Charged per image scan                                   |
| EKS                  | $0.10/hour per cluster (plus EC2 or Fargate costs)       |
| ECS                  | Free; pay for compute (EC2 or Fargate)                   |
| Fargate              | Pay per vCPU and memory used                             |
| Secrets Manager      | Charged per secret + API calls                           |
| VPC Logs / GuardDuty / CloudTrail | Charged by ingestion, storage, and queries |

---

## Other Important Notes

- **Amazon Inspector** now supports ECR image scanning natively:  
  - It integrates with your repositories and automatically scans pushed images.  
  - It highlights CVEs and provides remediation steps.  

- **Kubernetes audit logs** can be sent to CloudWatch Logs or S3 + Athena for SIEM-like analysis.

- **AWS Security Hub** can aggregate findings from EKS, Inspector, GuardDuty, IAM Access Analyzer, etc.

- **AWS Bottlerocket** is a special Linux OS designed for containers — secure by default.


- **IAM Roles for Service Accounts (IRSA)** in EKS lets your containers get temporary credentials scoped just to them (*least privilege*).

---

## Real-Life Snowy-Style Example

Let’s say **Winterday** is deploying a SaaS analytics platform on **EKS**. Each customer gets their own containerized microservice.

If Winterday just pulls a random open-source container image with `apt-get` and hardcodes a secret token in an environment variable — and skips image scanning — then even a small vulnerability (say, outdated `openssl`) opens the door to an attacker breaking out and accessing logs or secrets.

Instead, **Snowy** enforces:

- Signed base images from a private ECR repo  
- Inspector scans on push  
- Least privilege IRSA roles  
- PodSecurityPolicies to deny `hostPath` mounts  
- Secrets fetched at runtime from AWS SSM with KMS  
- All traffic goes through App Mesh with TLS enforcement  

**Result?** The blast radius is minimized. Even if one container gets hit, it can't pivot or escalate.

---

## Final Thoughts

Containers aren’t secure by default — they’re just smaller and faster VMs with more moving parts.

The ephemeral nature of containers doesn’t remove the need for diligence — it *increases* it.

You need **layered security at every stage**:  
`build → image → registry → runtime → orchestration → network`

In AWS, use:

- **ECR + Inspector**  
- **IAM**  
- **Fargate / EKS / ECS**  
- **Secrets Manager**  
- **GuardDuty + Security Hub**  
- **CloudWatch, VPC Flow Logs, Athena**  

as your toolbox — and wrap them together with governance, alerting, and tight privilege boundaries.

Container security is a **shared responsibility**: AWS handles infra, *you harden the workloads*.

