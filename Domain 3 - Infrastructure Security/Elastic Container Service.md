# Amazon ECS

Amazon ECS (Elastic Container Service) is AWS's native container orchestrator: it schedules, places, and scales containers across a fleet, either on EC2 instances you own or on Fargate where AWS owns the host. From a security standpoint ECS enforces nothing on its own. It exposes the hooks (task IAM roles, network modes, secrets injection, logging drivers, runtime flags) and leaves the actual posture to you, which means a single bad task definition replicates the same misconfiguration across hundreds of workloads at machine speed. The thing to hold onto: ECS is neutral orchestration, the security boundary is the task definition plus its IAM roles and network mode, and the EC2-versus-Fargate split decides how much of the host you are still responsible for.

## How it works

- **Task definition is the unit of security.** It declares the image, the execution role, the task role, the network mode, the secrets block, logging config, and runtime flags. Everything below is a field in this document, so review it the way you would review an IAM policy.
- **Execution role vs task role (the distinction the exam loves).** The execution role is used by the ECS agent to pull images from ECR and fetch secrets from Secrets Manager or SSM before the container starts. The task role is assumed inside the running container and carries the workload's actual AWS permissions. Conflating them, or sharing one role across every service, is the classic over-grant.
- **Secrets belong in the `secrets` block, not the image or env vars.** Reference Secrets Manager or SSM Parameter Store so values inject at runtime and never bake into the image layers or appear in plaintext `environment`. Back the secret with a customer-managed KMS key and a restrictive key policy.
- **Network mode sets the isolation ceiling.** `awsvpc` gives each task its own ENI, so real security groups apply per task. `bridge` (EC2 default) puts tasks on a shared Docker network where they reach each other freely and no SG applies. `host` binds container ports straight to the instance. Fargate is always `awsvpc`.
- **Runtime hardening is opt-in.** Containers default to root with full capabilities. Set a non-root user, `readOnlyRootFilesystem: true`, drop capabilities with `cap-drop`, avoid `privileged: true`, and set CPU/memory limits so one task cannot starve the host.
- **Image provenance is the first control plane.** Build and scan in CI/CD, push to private ECR, enable Inspector ECR scanning, and pin immutable tags (`:v1.2.4`, never `:latest`) so what runs is what you scanned.
- **Logging is the only forensic artifact.** Configure the `awslogs` driver to CloudWatch (or FireLens to another sink). On Fargate a compromised task leaves nothing behind but its logs, so absent logging you have no incident story at all.

## ECS security surfaces vs the rest of the stack

| Surface | What it controls | Get it wrong and |
|---|---|---|
| **Execution role** | Agent-side pulls: ECR image, Secrets/SSM fetch pre-start | Broad role lets the agent read secrets it should never touch |
| **Task role** | In-container AWS permissions | `s3:*` shared across tasks means one RCE reaches everything |
| **Network mode** | Task-to-task and task-to-VPC reachability | `bridge`/`host` skip per-task SGs, enabling lateral movement |
| **Secrets block** | Runtime secret injection | Env-var or baked secrets leak via image layers and `describe-task` |
| **Runtime flags** | Root, capabilities, FS write, privilege | Root + writable FS + full caps hands an attacker the host |
| **ECR + Inspector** | Image provenance and CVE scanning | `:latest` from DockerHub ships unknown CVEs to prod |
| **Logging driver** | CloudWatch/FireLens observability | No logs means no detection and no forensics, worst on Fargate |

## What gets tested

- **Execution role vs task role.** Given a symptom (agent cannot pull the image or fetch a secret vs the app cannot call an AWS API), pick the correct role to fix. Pre-start failures point at the execution role, in-app `AccessDenied` points at the task role.
- **Pick `awsvpc` when the question wants per-task security groups or task isolation.** `bridge` and `host` cannot give you that. If the scenario is Fargate, `awsvpc` is already implied.
- **Fargate vs EC2 responsibility split.** Fargate removes host, OS, kernel, Docker, and agent patching from your plate but still leaves you the task definition, IAM, image, and network. EC2 mode keeps all of the host patching. Runtime Monitoring in GuardDuty and `hostPath` mounts are EC2-mode concepts.
- **Secrets injection.** The correct answer references Secrets Manager or SSM via the task definition `secrets` block, not plaintext `environment` and not values baked into the image.
- **Least privilege on the task role.** One scoped role per service, permissions bound by `Resource` and IAM conditions, is preferred over a single shared `*` role.
- **Image trust.** Private ECR plus Inspector scanning plus immutable tags beats pulling `:latest` from a public registry.

## Limitations

- ECS enforces no security by default. Root, full capabilities, a writable root filesystem, and open egress are the out-of-the-box state, so an unhardened task definition is an insecure task definition.
- `bridge` and `host` network modes do not support per-task security groups. If you need SG-level isolation on EC2 mode you must opt into `awsvpc`, which consumes an ENI per task and can hit ENI limits on smaller instances.
- On EC2 mode the host is yours: kernel, OS, Docker, ECS agent, and AMI patching all fall to you, and a stale agent or AMI becomes a persistent vulnerability across every task placed on it.
- GuardDuty Runtime Monitoring coverage and `hostPath` volume access differ between EC2 and Fargate, so a control that exists in one launch type may not exist in the other.
- Secrets injected at runtime still land in the container's environment or filesystem, so a compromised task with the right task role can read them. Runtime hardening and scoped roles limit the blast radius, they do not remove it.
- Logging and Container Insights are opt-in. Skip them and a Fargate compromise leaves only the CloudTrail control-plane record, not the in-container activity.