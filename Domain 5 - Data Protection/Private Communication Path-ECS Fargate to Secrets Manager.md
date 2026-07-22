# Private Communication Path: ECS Fargate to Secrets Manager

When a Fargate task fetches a secret (a database password, API token, or TLS material) from AWS Secrets Manager, the call is always TLS. Secrets Manager is an HTTPS-only service that rejects any non-TLS request, so unlike RDS or ALB-to-target, there is no plaintext option to misconfigure: the SDK negotiates TLS 1.2+ automatically. The interesting security decisions here are not about encryption (it is mandatory) but about where the traffic routes and which identity is authorized: an interface VPC endpoint keeps the call off the internet, and the execution role versus task role distinction decides who can read the secret. The thing to hold onto: TLS to Secrets Manager is mandatory and automatic, an interface VPC endpoint (PrivateLink) is what keeps a private-subnet task off the public internet, and injection at container start uses the task execution role while runtime SDK calls use the task role.

## How it works

- **The call is HTTPS-only, no configuration.** Secrets Manager refuses non-TLS connections and enforces TLS 1.2+. Any official SDK (Python, Go, Node, Java) handles negotiation and validation, so developers do not configure TLS and cannot send a secret over HTTP.
- **Two ways a Fargate task gets a secret.** Referenced in the task definition's `secrets` block, the value is fetched at container start using the task execution role and injected as an environment variable or file. Fetched at runtime via an SDK call, the app uses the task role. These are different roles with different permissions.
- **IAM plus the secret's resource policy authorize the read.** The relevant role needs `secretsmanager:GetSecretValue`, and if the secret is encrypted with a customer-managed KMS key, `kms:Decrypt` on that key too. A resource policy on the secret can further scope who may read it.
- **An interface VPC endpoint keeps it private.** For a task in a private subnet, a Secrets Manager interface endpoint (PrivateLink) provides a private IP so the HTTPS call never traverses the internet, with no NAT gateway needed. An endpoint policy can restrict which secrets are reachable through it.
- **Everything is logged.** `GetSecretValue` and related calls land in CloudTrail, giving a full audit trail of which task read which secret and when.

## Fargate-to-Secrets-Manager access model

| Element | Role / control | Note |
|---|---|---|
| **Injection at container start** | Task execution role | `secrets` block in task definition |
| **Runtime SDK fetch** | Task role | App calls `GetSecretValue` itself |
| **Decrypt (CMK-encrypted secret)** | Same role + `kms:Decrypt` | Two-permission gate |
| **Private routing** | Interface VPC endpoint (PrivateLink) | Keeps traffic off the internet |
| **Endpoint scoping** | VPC endpoint policy | Which secrets reachable via the endpoint |
| **Audit** | CloudTrail | Every secret access logged |

## What gets tested

- **TLS is inherent, so the exam angle is routing and IAM.** Secrets Manager is HTTPS-only, so questions focus on private routing (interface endpoint) and which role is authorized, not on enabling encryption.
- **Execution role vs task role.** A secret injected at container start that fails points at the task execution role and its permissions. An app that fails an SDK `GetSecretValue` at runtime points at the task role. Knowing which role each path uses is the tested distinction.
- **Two-permission gate for CMK-encrypted secrets.** Reading a secret encrypted with a customer-managed key needs both `secretsmanager:GetSecretValue` and `kms:Decrypt`. A denied read despite Secrets Manager permission often means the missing KMS grant.
- **Interface endpoint for private-subnet access without internet.** Keeping the call private without a NAT gateway is a Secrets Manager interface VPC endpoint, and an endpoint policy scopes which secrets it can reach.
- **Fetch at runtime, do not bake secrets in.** The secure pattern is fetching from Secrets Manager rather than embedding secrets in the image or plaintext env vars, and letting the app not log them.
- **Secrets Manager vs Parameter Store.** Rotation, generated secrets, and cross-account sharing favor Secrets Manager, which is often why this service is chosen over Parameter Store for the same Fargate flow.

## Limitations

- Encryption in transit is not a decision here, it is enforced, so the security work shifts entirely to IAM, KMS, routing, and secret hygiene.
- The execution-role vs task-role split is easy to get wrong, causing injection or runtime fetches to fail in ways that look like a Secrets Manager problem but are IAM scoping.
- CMK-encrypted secrets add a KMS dependency, so a missing `kms:Decrypt` grant silently blocks reads even when Secrets Manager permissions look correct.
- An interface VPC endpoint is billed hourly plus per GB and adds ENIs, so private routing has a cost, unlike the free S3/DynamoDB gateway endpoints.
- Injected secrets still land in the container's environment or filesystem, so a compromised task or one that logs its inputs exposes them despite mandatory TLS.
- TLS and private routing protect the fetch, not the downstream handling. A secret pulled correctly and then written to a log or passed insecurely defeats the model.