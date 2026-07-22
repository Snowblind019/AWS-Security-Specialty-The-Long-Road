# Private Communication Path: Lambda to DynamoDB

When a Lambda function reads or writes DynamoDB (order tracking, IoT ingestion, request storage, queues), the call goes through the AWS SDK to DynamoDB's HTTPS endpoint, and the SDK defaults to TLS 1.2+ with no configuration. This is the low-effort end of the encryption spectrum: unlike EC2-to-RDS where you must enable TLS in the client, here the SDK handles negotiation, validation, and cert rotation for you, and DynamoDB is always encrypted at rest as well. The security decisions worth thinking about are IAM scoping, optionally forcing TLS with a policy condition, and private routing for VPC-bound Lambdas. The thing to hold onto: transit encryption is the SDK's HTTPS default (so use the SDK, not raw HTTP calls), at-rest is always on with a KMS key tier you choose, and a VPC-attached Lambda reaches DynamoDB privately through a free gateway endpoint just like S3.

## How it works

- **The SDK defaults to HTTPS.** `boto3`, `aws-sdk-js`, and the others connect to DynamoDB's regional HTTPS endpoint over TLS 1.2+ automatically. You pass no `useSSL` flag, and AWS manages the certs so there is no bundle to rotate.
- **At rest is always encrypted.** DynamoDB encrypts all tables at rest with KMS. You choose the key tier (AWS-owned default, AWS-managed `aws/dynamodb`, or a customer-managed CMK), and only the CMK gives CloudTrail visibility and scoped key control.
- **IAM authorizes every call.** The Lambda execution role needs the relevant DynamoDB actions (`GetItem`, `PutItem`, `Query`, etc.), and if the table uses a CMK, the role also needs `kms:Decrypt`/`GenerateDataKey` on that key. Scope to the specific table ARN, not `*`.
- **Forcing TLS is a policy condition, not a toggle.** To guarantee no plaintext regardless of client, you can deny requests where `aws:SecureTransport` is false in the IAM policy (or a VPC endpoint policy). The SDK default covers normal usage, but the condition is how you enforce it.
- **VPC Lambda reaches DynamoDB via a gateway endpoint.** A Lambda in a VPC uses a DynamoDB gateway VPC endpoint (route-table based, free) to reach DynamoDB privately without a NAT gateway, the same pattern as S3. The endpoint provides private routing, and an endpoint policy can scope which tables and actions are reachable.

## Lambda-to-DynamoDB security model

| Concern | Mechanism | Note |
|---|---|---|
| **In transit** | SDK HTTPS default (TLS 1.2+) | Use the SDK, not raw HTTP |
| **Force TLS** | `aws:SecureTransport` deny in IAM/endpoint policy | Not a service toggle |
| **At rest** | KMS, always on | CMK for audit/scoped access |
| **Authorization** | Execution role, scoped to table ARN | Plus `kms:Decrypt` for CMK tables |
| **Private routing (VPC Lambda)** | DynamoDB gateway endpoint (free) | Endpoint policy scopes tables/actions |

## What gets tested

- **Transit encryption is the SDK default, not a config.** Using the AWS SDK gives HTTPS automatically. The exam-relevant risk is a custom HTTP client bypassing TLS, so "use the SDK" is the safe pattern.
- **Forcing TLS uses `aws:SecureTransport`.** If a scenario requires guaranteeing encryption in transit to DynamoDB regardless of client, that is a policy deny on non-TLS requests, because DynamoDB has no bucket-policy analog and there is no service-level TLS toggle.
- **At-rest key tier for control.** CloudTrail visibility into decryptions and scoped key access require a customer-managed key. The default AWS-owned key gives neither.
- **VPC Lambda private access is a gateway endpoint.** Keeping a VPC-attached Lambda's DynamoDB traffic private without NAT is the free DynamoDB gateway endpoint, mirroring S3.
- **Least-privilege IAM on the execution role.** Scope to the specific table and actions, and include KMS permissions for CMK-encrypted tables, rather than broad `dynamodb:*` on `*`.
- **DynamoDB vs EC2-to-RDS.** This flow is secure-by-default in transit, unlike RDS where the client must opt into TLS. Recognizing which flows enforce TLS and which do not is the tested contrast.

## Limitations

- The HTTPS guarantee comes from the SDK, not the service refusing all plaintext, so a custom or raw HTTP client can undermine it unless an `aws:SecureTransport` condition denies non-TLS.
- There is no bucket-policy equivalent for DynamoDB, so enforcing TLS and data-perimeter conditions lives in IAM and VPC endpoint policies, which must be written deliberately.
- At-rest encryption is always on but the default AWS-owned key gives no CloudTrail visibility or policy control, so audit and scoping require choosing a CMK.
- A VPC-attached Lambda without a gateway endpoint either cannot reach DynamoDB or routes via NAT, adding cost, so private access needs the endpoint configured.
- Encryption in transit and at rest do not authorize access. An over-broad execution role or missing KMS scoping still exposes data to a compromised function.
- DynamoDB Local or a custom proxy changes the picture, since TLS then depends on your setup rather than the managed endpoint's defaults.