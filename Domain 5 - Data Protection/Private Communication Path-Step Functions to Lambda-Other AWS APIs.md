# Private Communication Path: Step Functions to Lambda / AWS APIs

Step Functions is the orchestrator that ties serverless logic together (ETL, remediation workflows, approval flows, microservice choreography), calling Lambda, SNS, SQS, DynamoDB, S3, and even third-party HTTPS endpoints as workflow steps. Every one of those calls goes through TLS-secured, SigV4-signed AWS APIs, so encryption in transit is mandatory and automatic, with no plaintext option to misconfigure. As with the other secure-by-default service-to-service paths, the security decisions that matter are not about encryption but about the execution role's permissions, logging, and (for third-party HTTP tasks) how credentials are handled. The thing to hold onto: transit encryption and SigV4 auth are inherent, the real control surface is the state machine's execution role scoped to exactly the downstream resources it invokes, and for the HTTP Task to external endpoints, credentials belong in an EventBridge connection, not hardcoded in the workflow.

## How it works

- **Each state calls a TLS-secured AWS API.** When a state executes, Step Functions makes a SigV4-signed request over TLS 1.2+ to the target service and gets the response back over TLS. There is no plaintext HTTP path, and AWS manages certs, ciphers, and sessions.
- **The execution role governs everything downstream.** The state machine assumes its execution role to invoke Lambda, publish to SNS, write DynamoDB, and so on. This role is the authorization boundary, and it should be scoped to exactly the resources and actions the workflow uses.
- **VPC Lambdas keep TLS.** If a workflow invokes a Lambda that runs in a VPC, the Lambda's networking is scoped by ENIs and security groups, but the Step Functions to Lambda call itself remains a TLS AWS API call.
- **HTTP Task to third parties still enforces TLS.** The HTTP Task calls external HTTPS endpoints and enforces TLS, failing if the remote server is misconfigured. Authentication to those endpoints uses an EventBridge connection (which stores the credentials in Secrets Manager) rather than secrets embedded in the state machine definition.
- **Execution logging and CloudTrail give the audit trail.** Step Functions can log step input/output to CloudWatch Logs (with optional redaction of sensitive fields), and every downstream API call is visible in CloudTrail, so the whole orchestration is auditable.

## Secure-by-default service paths compared

| Feature | Step Functions to Lambda/APIs | Lambda to S3/DynamoDB | Fargate to Secrets Manager |
|---|---|---|---|
| **TLS enforced** | Always | Always (SDK default) | Always |
| **SigV4 auth** | Yes | Yes | Yes |
| **Authorization** | Execution role | Execution role | Task / execution role |
| **User-managed encryption** | No (AWS-handled) | Partial (S3 SSE, DDB key tier) | Partial (KMS key choice) |
| **CloudTrail visibility** | Yes | Yes | Yes |

## What gets tested

- **Encryption is inherent, so the answer is IAM and logging.** Step Functions calls are always TLS and SigV4, so security questions focus on scoping the execution role and enabling logging, not on enabling encryption.
- **Least-privilege execution role.** The correct design grants the state machine only the specific actions on the specific resources it orchestrates, not broad wildcards, since that role is the blast radius if the workflow is abused.
- **Third-party credentials via EventBridge connection.** For the HTTP Task, API keys and secrets belong in an EventBridge connection backed by Secrets Manager, not in the ASL definition or step input. Hardcoding them is the wrong answer.
- **Step Functions for automated remediation.** A common exam use is orchestrating responses to GuardDuty or Security Hub findings, where the value is auditable, retryable, least-privilege automation.
- **Logging with redaction.** When step input/output may contain sensitive data, execution logging with redaction (and careful CloudWatch log access control) is how you keep the audit trail without leaking secrets.
- **Path selection.** Step Functions suits orchestration of AWS API steps. Direct VPC/EC2 access, custom TLS control, or streaming needs a different pattern (VPC Lambda, EventBridge Pipes, custom APIs).

## Limitations

- Encryption and auth are handled for you, so you get no control over TLS ciphers or session handling. Workloads needing custom TLS behavior must use a different mechanism.
- The execution role is the security boundary, so an over-broad role turns the orchestrator into a powerful pivot if the workflow or its triggers are compromised.
- The HTTP Task depends on the remote endpoint being correctly TLS-configured and on credentials living in an EventBridge connection. Mishandled external secrets undermine the otherwise secure path.
- Execution logging can capture sensitive step input/output, so without redaction and tight log-access controls the logs become a leak point.
- It orchestrates API calls, not raw network access, so it is not a substitute for VPC-level connectivity to EC2 or on-prem systems.
- Transit security says nothing about the data handling inside each invoked service, so at-rest encryption and downstream IAM still have to be correct on Lambda, S3, DynamoDB, and the rest.