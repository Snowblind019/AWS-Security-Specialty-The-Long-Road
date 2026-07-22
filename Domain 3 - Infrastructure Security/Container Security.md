# Compute Security in AWS

Compute security is the set of protections applied to the layer that runs code: EC2 (virtual machines), ECS/EKS/Fargate (containers), and Lambda (serverless). What you own shifts by service under the shared responsibility model, but the concern is constant: the compute unit holds an identity, sits on a network, and touches data, so a compromised one is the launch point for exfiltration, lateral movement, and persistence. The thing to hold onto: compute security is the same four questions at every layer, what identity does it carry (IAM role), what can it reach (network), what does it run (image/OS/runtime), and can you see it (logging), and the exam usually tests which lever applies to which compute type and where the responsibility line sits.

## How it works

- **Identity per compute unit.** Every unit gets its own role, least privilege, never an admin policy and never long-lived keys. **EC2**: instance profile. **ECS**: task role (per task, distinct from the task *execution* role that pulls images and writes logs). **Lambda**: execution role. **EKS**: **IRSA** or **EKS Pod Identity**, both yielding short-lived pod-scoped credentials with no static secrets. Node IAM roles are the anti-pattern because every pod on the node inherits them.
- **Network boundaries.** VPC, private subnets for sensitive workloads, security groups scoped by port/protocol/source, NACLs for coarse subnet rules, VPC endpoints so service traffic (S3, DynamoDB, Secrets Manager) never traverses the internet, TLS on intra-service calls.
- **Access to the host.** Replace SSH with **SSM Session Manager** (no open port 22, no key management, full session logging) or EC2 Instance Connect. Disable password auth, restrict root, enforce **IMDSv2**.
- **OS and image hygiene.** Hardened base AMIs, **SSM Patch Manager** on a cadence, **Amazon Inspector** for continuous CVE scanning of EC2, container images in ECR, and Lambda functions. Minimal base images, **read-only root filesystems**, drop unneeded Linux capabilities, never run containers as root, no host filesystem mounts.
- **Secrets.** Out of environment variables and images. Pull from **Secrets Manager** or **SSM Parameter Store** at runtime; encrypt Lambda env vars with KMS; mount into pods via the Secrets Store CSI driver. Never log decrypted secrets.
- **Encryption.** EBS encryption for EC2, Lambda ephemeral (`/tmp`) storage encrypted with an AWS-managed or customer key, EFS/ECS volumes encrypted, data fetched to the container rather than baked into the image.
- **Detection.** CloudTrail all-Region, centralized CloudWatch Logs, VPC Flow Logs, **GuardDuty** (EC2 port scanning and crypto-mining, credential exfiltration, anomalous IAM calls, EKS audit and runtime findings, Lambda network anomalies), findings centralized in **Security Hub**, alarms on high CPU (mining), unexpected egress, and AssumeRole spikes.
- **Blast-radius design.** Immutable, replaceable instances in Auto Scaling groups (destroy and rebuild rather than patch a compromised host), one Lambda per responsibility, per-namespace/per-task role scoping, segmentation so one popped unit cannot reach far.

## Security model by compute type

| | EC2 | ECS / EKS on EC2 | Fargate | Lambda |
|---|---|---|---|---|
| You manage | OS, patching, runtime, app, IAM | Container config, runtime, task/pod IAM, node OS (EC2 mode) | Container config, task/pod IAM | Function code, IAM, env config |
| AWS manages | Hypervisor, hardware | Underlying infra | OS, node, isolation | Runtime, patching, scaling |
| Identity mechanism | Instance profile | Task role / IRSA / Pod Identity | Task role / Pod Identity | Execution role |
| Host access | SSM Session Manager (no SSH) | Node via SSM; no exec into prod pods | No host access | No host access |
| Patch responsibility | You (Patch Manager) | You for nodes; images you rebuild | Image rebuild only | AWS |
| CVE scanning | Inspector (instance) | Inspector (ECR image + node) | Inspector (image) | Inspector (function) |

## What gets tested

- **Where the responsibility line falls.** Fargate and Lambda move OS patching to AWS; EC2 and EKS-on-EC2 nodes keep it with you. A "who patches the OS" question is answered by the compute type, not by a tool.
- **Task role vs execution role (ECS).** The **task role** is what the app code assumes to call AWS APIs; the **execution role** lets the agent pull the image and ship logs. Scenarios swap these to see if you know which grants app-level access.
- **IRSA vs Pod Identity (EKS).** Both give per-pod short-lived credentials. IRSA uses OIDC federation and works across EKS, EKS Anywhere, and self-managed clusters but needs an OIDC provider and per-cluster trust policy. Pod Identity uses a simpler association API and an in-cluster agent, is EKS-in-cloud only, and adds session tags. Either beats node IAM roles or static keys in a manifest.
- **SSH vs Session Manager.** "Access an instance without opening inbound ports or managing keys" is SSM Session Manager. It also gives you an auditable session log, which a bastion + SSH does not by default.
- **Secrets not in env vars.** Leaked-credential-in-logs scenarios point to Secrets Manager/Parameter Store retrieval at runtime plus KMS-encrypted env vars, not "rotate the key" alone.
- **IMDSv2.** Enforcing IMDSv2 is the control that defeats SSRF-driven credential theft from the instance metadata endpoint. Recognize it as the answer to "app was tricked into fetching its own role credentials."
- **Immutable replacement over in-place fix.** For a compromised instance, contain then destroy-and-replace from a known-good AMI in an ASG. Rebuilding is the containment pattern, not SSHing in to clean it.

## Limitations

- Least-privilege roles are only as good as their scope. An over-broad instance profile or execution role plus IMDSv1 or a leaked token is the standard path from one unit to account compromise; the role is the blast radius.
- GuardDuty and Inspector detect, they do not prevent. They shorten time-to-detection but a runtime exploit still executes; prevention is hardening, network isolation, and least privilege.
- Fargate and Lambda remove OS patching but not application-dependency risk. Vulnerable libraries in your image or function still need Inspector scanning and rebuilds; "serverless" is not "patch-free."
- Session Manager logging and VPC Flow Logs are opt-in and cost money at volume. Absence of logs is an absence of forensics, so the control has to be enabled before the incident, not after.
- Container isolation on shared EC2 nodes is not a hard boundary. Privileged containers, host mounts, or `CAP_SYS_ADMIN` allow container-to-host escape; Fargate's per-task isolation is the stronger boundary when tenancy separation matters.
- Immutable-replacement design assumes stateless compute. Stateful workloads need the data and secrets externalized first, or "destroy and rebuild" loses state along with the attacker.