# Amazon ECS on Fargate Security

ECS is AWS's native container orchestrator; Fargate is the serverless compute engine that runs the tasks. You define task definitions, IAM roles, networking, and logging, and AWS provisions, runs, and tears down the compute node with no EC2 cluster to manage, no host to patch, and no SSH. The attack surface does not disappear, it moves: you no longer own the host, but you fully own task-level IAM scoping, image trust, secrets handling, networking, and runtime behavior. The thing to hold onto: Fargate removes host security from your plate and hands you per-task isolation for free, so the exam's Fargate questions are almost always about the two IAM roles a task carries and the fact that a compromised container fetches credentials from the ECS task credentials endpoint, not the EC2 IMDS.

## How it works

- **Two roles, different jobs.** The **task role** is what the application containers assume to call AWS APIs (S3, DynamoDB); scope it per service to specific actions and ARNs. The **task execution role** is what the ECS agent uses to pull the image from ECR, ship logs via the `awslogs` driver, pull secrets referenced in the task definition, and manage the GuardDuty agent. Conflating them is the classic mistake; app permissions belong on the task role.
- **Credentials delivery.** A Fargate container gets its task-role credentials from the **ECS container credentials endpoint at `169.254.170.2`** (the `AWS_CONTAINER_CREDENTIALS_RELATIVE_URI`), not the EC2 IMDS at `169.254.169.254`. An SSRF or vulnerable dependency that can reach `169.254.170.2` can steal the task's temporary credentials, which is why task-role scope is the real blast radius.
- **Networking (`awsvpc` mode).** Every task gets its own ENI, so you assign the subnet and security group. Put tasks in private subnets, keep public IPs off unless required, tighten SGs, and route egress through **VPC endpoints** (S3, ECR, SQS, Secrets Manager) or a NAT gateway. Enable VPC Flow Logs to catch abnormal egress.
- **Image trust.** The image is the root of trust. Build in CI, store in **private ECR**, scan with **Inspector enhanced scanning**, use immutable version tags (not `:latest`), sign for provenance, and never bake secrets into the image or env vars.
- **Secrets.** Reference **Secrets Manager** or **SSM Parameter Store** SecureStrings through the task definition `secrets:` block so the execution role injects them at runtime. Scope the role to only the needed secrets and restrict `kms:Decrypt` via the key policy. Rotate natively.
- **Runtime hardening.** Drop Linux capabilities, run as non-root, set a read-only root filesystem, and cap CPU/memory. Fargate isolates each task in its own **Firecracker microVM**, so cross-task and task-to-host escape is not the concern it is on a shared node, but inside your container there is no barrier, so app-level privilege escalation still matters.
- **Runtime detection.** **GuardDuty ECS Runtime Monitoring** covers Fargate by running the security agent as a **sidecar container in each task** (on EC2 launch type it runs as a host process/eBPF instead). It needs a task execution role, Fargate platform 1.4.0+, and ECR access for the agent, and detects privilege escalation, exposed-credential use, malicious domains, and crypto-mining.
- **Observability.** CloudWatch Logs per service (`awslogs`), Container Insights for CPU/memory/network, X-Ray for tracing, alarms on task failures. Without a configured log driver you get nothing but "the task failed."
- **Drift detection.** AWS Config rules (task using a public IP, unscoped role), Security Hub aggregation, CloudTrail for `RunTask`/`StartTask`, EventBridge alerts on unusual `RunTask` principals or `PutRolePolicy` against a task role.

## Fargate vs ECS-on-EC2 (the isolation and responsibility split)

| | ECS on Fargate | ECS on EC2 |
|---|---|---|
| Host/OS patching | AWS (microVM + kernel) | You (the EC2 node) |
| Task isolation | Per-task Firecracker microVM | Shared kernel on the node |
| Credentials endpoint | `169.254.170.2` (task) | `169.254.170.2` (task) + node IMDS `169.254.169.254` |
| Co-tenancy risk | None (one task per microVM) | High-priv and low-priv tasks share a host (ECScape) |
| GuardDuty agent | Sidecar container per task | Host process, EC2-managed |
| SSH / host access | None | Possible (node) |
| Best for | Least-ops, strong tenant isolation | Custom kernels, GPU, cost tuning at scale |

## What gets tested

- **Task role vs task execution role.** "The container needs least-privilege access to a DynamoDB table" is the **task role**. "The agent needs to pull the private image / fetch the secret / ship logs" is the **task execution role**. Scenarios swap these deliberately.
- **Fargate credentials come from 169.254.170.2, not the EC2 IMDS.** IMDSv2 hop-limit hardening is an EC2 answer. On Fargate, credential theft is via the ECS container credentials endpoint, so the mitigation is scoping the task role and blocking SSRF, not tuning IMDS.
- **Fargate isolation removes co-tenancy risk.** When a scenario needs hard separation between a high-privilege and a low-privilege workload, Fargate's per-task microVM is the answer; on shared EC2 nodes you must avoid co-locating them (the ECScape credential-masquerade path).
- **Secrets via the task definition, not env vars.** The correct pattern is the `secrets:` block pulling from Secrets Manager/Parameter Store, with the execution role and KMS key policy scoped. Plaintext env vars are the wrong answer.
- **GuardDuty Runtime Monitoring for in-container threats.** Detecting a crypto miner or credential abuse inside a running Fargate task is Runtime Monitoring (sidecar agent), not VPC Flow Logs or CloudTrail alone.
- **Private egress via VPC endpoints.** Reaching S3/ECR/Secrets Manager without internet is interface/gateway VPC endpoints, which also lets tasks run in private subnets without a NAT gateway.
- **Logging is opt-in.** A "no logs to investigate" postmortem means the `awslogs` driver and Container Insights were never configured. The fix is enabling them, since Fargate emits nothing by default.

## Limitations

- Fargate patches the microVM and kernel, not your application or its dependencies. A vulnerable library (old `urllib3`, `openssl`) is still yours to scan and rebuild; serverless is not patch-free at the app layer.
- Per-task isolation protects tasks from each other, not the container from itself. Inside the task there is no VM barrier between processes, so run non-root, drop capabilities, and cap resources.
- GuardDuty Runtime Monitoring on Fargate requires the sidecar agent, a task execution role, platform 1.4.0+, and ECR reachability. Missing any of these means no runtime coverage, and existing tasks are only protected after a new deployment.
- The task credentials endpoint is reachable from inside the container by design, so an app-layer SSRF or RCE can reach it. Isolation does not stop credential theft; only a tightly scoped task role limits what stolen credentials can do.
- `awsvpc` gives each task an ENI, which consumes subnet IP space and has per-account ENI limits. Large task counts can exhaust a subnet, a scaling constraint to plan CIDRs around.
- Config and GuardDuty detect drift and threats but do not prevent them. Preventative posture (scoped roles, private subnets, image scanning, non-root) has to be in the task definition before launch.