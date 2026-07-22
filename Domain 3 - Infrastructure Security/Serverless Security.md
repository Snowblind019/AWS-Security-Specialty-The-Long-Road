# Serverless Security

Serverless runs application code without managing the underlying infrastructure. In AWS the core service is Lambda, with API Gateway, Step Functions, AppSync, EventBridge, SNS/SQS, and Fargate rounding out the event-driven stack. Serverless does not remove security, it shifts it: AWS owns the OS, hypervisor, runtime patching, and Firecracker microVM isolation, while you own the code, the IAM execution role, event-trigger authorization, secrets, and the CI/CD pipeline. The thing to hold onto: serverless collapses the attack surface to identity, events, code/dependencies, and configuration, so the exam's serverless questions are almost always "least-privilege execution role," "authorize and validate the trigger," or "get secrets and vulnerable dependencies out of the function," not OS or network hardening.

## How it works

- **Execution role (IAM).** Every function assumes an execution role. Least privilege, resource-scoped ARNs, no wildcards (`s3:*`, `kms:*`, `iam:*`). Use IAM Access Analyzer to find unused permissions. The role is the blast radius if the function is compromised.
- **Event-trigger hardening.** Functions fire from API Gateway, S3 events, DynamoDB Streams, EventBridge, SNS/SQS. For public triggers (API Gateway) enforce authorization (IAM/SigV4, Cognito, JWT/Lambda authorizer), validate and schema-check the payload to prevent event injection, rate-limit with WAF or usage plans, and rely on enforced HTTPS.
- **Secrets.** Never hardcode in code or plaintext env vars. Pull from Secrets Manager (rotation + KMS) or SSM Parameter Store SecureString at runtime, with `kms:Decrypt` scoped to the role. Lambda environment variables can be encrypted at rest with a customer-managed KMS key (and encryption helpers for in-transit protection), but a secret still belongs in a secrets store.
- **Code and dependency scanning.** Function packages bundle third-party libraries (risk: vulnerable and typosquatted packages). **Amazon Inspector now scans Lambda functions and layers for both dependency vulnerabilities and custom application code** (injection, data leaks, weak crypto, missing encryption), with remediation guidance. Pair it with SCA and SAST (Semgrep, Checkov) in CI, since Inspector is one signal, not the whole pipeline.
- **Logging and tracing.** Lambda logs to CloudWatch by default; add structured JSON logs and correlation IDs, X-Ray for distributed tracing, CloudTrail for invocation and control-plane events (and S3 object-level logging for S3-triggered functions), aggregate in Security Hub/GuardDuty.
- **CI/CD.** Deploy via IaC (SAM/CDK/CloudFormation/Terraform). Sign artifacts with **Lambda code signing**, restrict deploy roles with IAM conditions, detect drift, and never deploy from personal accounts. CloudTrail plus pipeline logs catch tampering.
- **Runtime and isolation.** Functions run in per-function **Firecracker microVMs**, ephemeral and auto-scaled. But the **execution environment is reused** across invocations, so global/static state and `/tmp` persist for that environment's lifetime. Keep functions stateless, clear `/tmp`, and set timeout, memory, concurrency, retry, and DLQ per function to bound abuse and cost.

## Serverless responsibility and controls at a glance

| Concern | AWS owns | You own | Control |
|---|---|---|---|
| Host/OS/runtime patching | Yes | No | Managed by Lambda |
| microVM isolation | Yes | No | Firecracker |
| Function permissions | No | Yes | Least-privilege execution role |
| Trigger auth | No | Yes | API GW authorizer, WAF, validation |
| Secrets | No | Yes | Secrets Manager / SSM + KMS |
| Dependencies + code | No | Yes | Inspector + SCA/SAST in CI |
| Deploy integrity | No | Yes | Code signing, scoped deploy roles |

## What gets tested

- **Least-privilege execution role.** Overbroad function permissions plus a compromised dependency is the standard serverless breach path. The fix is a resource-scoped role, not a network change; there is no OS or SG to hide behind.
- **Authorize and validate the trigger.** Public API Gateway to Lambda needs an authorizer (Cognito/JWT/IAM), payload validation against event injection, and WAF/usage-plan rate limiting. "Anyone can invoke / malformed event reaches the function" maps here.
- **Secrets out of env vars.** Leaked-credential scenarios point to Secrets Manager/Parameter Store retrieval at runtime with scoped KMS, and optionally CMK-encrypted env vars, not hardcoding.
- **Inspector scans Lambda now.** Note the current state: Inspector does dependency and code scanning for Lambda functions and layers. An older "Inspector can't scan Lambda" assumption is wrong. It is the AWS-native answer for finding vulnerable serverless code and packages.
- **Cross-resource scoping.** A function writing to the wrong bucket is contained by an S3 bucket policy that allows only the function's role/ARN plus a tightly scoped execution role, so a manipulated event cannot redirect writes.
- **Statelessness and environment reuse.** Because execution environments are reused, secrets or PII left in global state or `/tmp` can leak into a later invocation. "Data from one invocation appears in another" is the reuse trap; keep functions stateless.
- **Deployment integrity.** Preventing tampered function code is Lambda **code signing** plus scoped deploy roles and CloudTrail, distinct from runtime controls.

## Limitations

- Serverless removes OS and runtime patching but not application-layer risk. Vulnerable dependencies, injection, and logic bugs are entirely yours; managed infrastructure does not make code safe.
- The execution environment is reused, so statefulness leaks across invocations. Isolation is per-function, not per-invocation, which surprises people expecting a clean slate each call.
- Inspector is one signal. It scans dependencies and code but does not replace pre-deployment SCA/SAST, PR gating, SBOMs, or layer scanning in the pipeline.
- Env var encryption protects at rest but a value still lives in the function configuration; true secrets belong in Secrets Manager/Parameter Store, fetched at runtime.
- Event-driven sprawl expands the trigger surface. Each source (S3, SNS, EventBridge, API GW) is its own authorization and validation problem; one unhardened trigger undermines the rest.
- Concurrency and timeout misconfiguration enable denial-of-wallet and DoS. Serverless auto-scales, so unbounded concurrency turns an abusive caller into a cost and availability incident; limits and DLQs are mandatory.