# Serverless Security

## What Is Serverless Security

Serverless architecture allows developers to run applications without managing underlying infrastructure. In AWS, the most common serverless compute service is AWS Lambda, but others like API Gateway, Step Functions, AppSync, EventBridge, and Fargate (to some extent) also count.
While serverless platforms abstract away servers, they do not eliminate the need for security — they just shift it.
In traditional models, you worry about patching OSs, firewall rules, AMI hardening, etc. In serverless, those responsibilities fall to AWS — but you're now in charge of securing your code, configurations, permissions, and event triggers.

Serverless doesn’t mean "secure by default." You must still address:

- Overprivileged IAM roles
- Event injection attacks
- Function-level isolation
- Secrets management
- Logging and traceability
- CI/CD pipeline risks

---

## Cybersecurity Analogy

Think of serverless like renting a locked storage unit that automatically opens when you arrive. You don't need to worry about the building, locks, or maintenance — just what you store inside.
But if you leave the door open, share the key with everyone (overbroad IAM roles), or let anyone call you to open it (API Gateway with public access), you’re at serious risk.

## Real-World Analogy

Imagine you're hosting a restaurant pop-up where the city provides the infrastructure: tables, power, water. All you need is your team and your recipes.
But if your staff doesn't wash hands (insecure code), shares the tip jar with everyone (too many IAM permissions), or lets anyone modify the recipe cards (CI/CD risks), the whole setup collapses.
You didn’t run the building — but you’re still responsible for how safe the food is and who handles it.

---

## How It Works / What to Secure

### 1. Function Permissions (IAM)

Each Lambda function runs with an IAM execution role
This role should follow least privilege — grant only what’s required (read from S3, write to DynamoDB, etc.)
Avoid wildcards (*) in policies — especially `iam:*`, `kms:*`, `ssm:*`
Use resource-level constraints: limit access to specific bucket ARNs, secret ARNs, table names
You can use IAM Access Analyzer to detect unused permissions over time.

### 2. Event Trigger Hardening

Serverless apps are event-driven — they’re triggered by:

- API Gateway
- S3 events
- DynamoDB Streams
- EventBridge
- SNS/SQS

If the event source is public-facing (e.g., API Gateway), you must:

- Enforce authorization (IAM auth, Cognito, JWT)
- Validate payloads to avoid event injection
- Rate-limit with WAF or usage plans
- Encrypt data in transit with TLS (API Gateway enforces HTTPS by default)

### 3. Secrets Management

Never hardcode credentials in Lambda environment variables or code

Use:

- AWS Secrets Manager (auto-rotation + KMS encryption)
- SSM Parameter Store (SecureString)
Retrieve secrets at runtime (decryption requires KMS permissions scoped to role)


Example: a Lambda needing RDS credentials should fetch them on-demand using IAM + KMS + Secrets Manager.

### 4. Code & Dependency Risks


Lambda bundles often contain 3rd party libraries (`node_modules`, `site-packages`)

Risks:

- Vulnerable packages
- Obfuscated malicious dependencies (typosquatting: aws-sdk vs aws_sdk)

Use:

- Static analysis in CI/CD (SonarQube, Checkov, Semgrep)
- Software Composition Analysis (SCA) tools to scan dependencies

- Amazon Inspector (for container images, not Lambda ZIPs yet)

Also watch for logic bugs — there's no OS sandbox to blame if something misbehaves.

### 5. Logging, Monitoring & Detection

Lambda logs go to CloudWatch Logs by default

You should:

- Enable structured logging (JSON format)
- Add correlation IDs to trace across services
- Use X-Ray for distributed tracing
- Aggregate findings in Security Hub, GuardDuty, or your SIEM

Enable CloudTrail for invocation logs (via API Gateway, EventBridge, etc.)
For S3 triggers: enable S3 object-level logging to know who uploaded the file that triggered the function.

### 6. CI/CD and Deployment Security

Serverless deployments use IaC (CloudFormation, SAM, CDK, Terraform)

Secure the pipeline:

- Sign artifacts (SAM + Code Signing)
- Use IAM conditions to restrict deploy access to specific roles
- Prevent privilege escalation via drift detection
- Avoid deploying from personal developer accounts

Enable CloudTrail + CodePipeline logs to detect tampering.

### 7. Runtime Constraints and Isolation

Lambda functions run in microVMs (Firecracker) that are:

- Isolated per function
- Ephemeral (no persistence)
- Auto-scaled per event

But beware:

- Execution context reuse can leak memory state (keep function stateless!)
- Timeouts and concurrency limits must be managed to prevent DOS

Set timeout, memory, retry, and DLQ policies per function.

---

## Pricing Models

| **Component**     | **Pricing Considerations**                          |
|-------------------|-----------------------------------------------------|
| **Lambda**        | Pay per request + duration (GB-s)                   |
| **Secrets Manager**| Charged per secret + API calls                     |
| **CloudWatch Logs**| Pay per GB ingested + stored                       |
| **X-Ray**         | Charged by traces captured                          |
| **API Gateway**   | Pay per million requests + data transferred         |
| **WAF**           | Charged by rules + requests inspected               |
| **Code Signing**  | No extra charge, but AWS Certificate Manager KMS keys apply |

No charge for IAM, but overbroad policies can cost you in blast radius.

---

## Real-Life Snowy-Style Example

Let’s say Blizzard’s startup uses Lambda to process photo uploads.

- Users hit an API Gateway endpoint that triggers a Lambda to resize the photo.
- The resized image is stored in an S3 bucket.
- Metadata is logged in DynamoDB.

If Blizzard:

- Allows `s3:*` on all buckets
- Uses environment variables for secrets
- Skips input validation
- Forgets to set a timeout
- Doesn’t track invocations

Then:

- An attacker could upload a malformed image that DoS-es the function
- Secrets could leak on a memory snapshot
- A malicious user could modify the event payload to write to a different S3 bucket
- There’s no trace of who triggered what

Instead, Snowy implements:

- Least privilege IAM roles
- S3 bucket policies scoped to only allow access from that Lambda ARN
- Secrets pulled from SSM
- WAF on API Gateway with input validation and rate limiting
- CloudTrail and CloudWatch Alarms to detect abuse
- Code Signing config in place via SAM templates

---

## Final Thoughts

Serverless doesn’t mean you’re off the hook — it just moves the attack surface. You now secure code, events, identities, and configurations, not OS patches and VPCs.

### Your biggest risks:

- Overpermissioned IAM roles
- Unvalidated triggers
- Secrets exposure
- Untracked invocations

### Your best defenses:

- IAM scoping + access analysis
- GuardDuty (anomalies), CloudTrail (history), Config (drift)
- Code Signing + SCA
- Runtime constraints + observability

AWS gives you the tools — but you own the glue logic between them. And that’s where most breaches happen.
