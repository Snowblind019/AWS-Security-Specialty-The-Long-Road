# API Gateway Security

Amazon API Gateway is the managed front door to backend services (Lambda, ECS, EC2, ALB, HTTP endpoints), handling request routing, authorization, throttling, and monitoring so the backend does not have to. The security problem is exposure: a public API Gateway endpoint is internet-facing by default, which makes it a high-value target for unauthenticated-endpoint probing, DDoS, injection, authorization bypass, and CORS abuse. The thing to hold onto: securing API Gateway is layered defense at the edge, identity (who), resource policy (from where), input validation (what), and throttling (how much), and the exam mostly tests which layer solves the stated problem and which API type (REST vs HTTP) even supports the control.

## How it works

- **Authentication and authorization.** Four mechanisms: **IAM / SigV4** (signed requests, internal and service-to-service), **Cognito User Pools** (JWT, web and mobile), **Lambda authorizers** (custom token or request logic, the OAuth/bearer-token path), and **JWT authorizers** (native OIDC/OAuth2, HTTP API only). API keys are for usage tracking and plans, never authentication on their own. Apply authorization per method so a `POST` can be gated harder than a `GET`.
- **Resource policies.** A JSON policy attached to the API itself, like an S3 bucket policy, controlling the source of calls: restrict to a specific VPC endpoint, an account, or a CIDR range. This is the required mechanism to lock a **private REST API** to its interface VPC endpoint. REST APIs only.
- **Input validation.** Attach request models with JSON Schema to reject malformed or oversized payloads before they reach the backend. Enforce required fields, length, pattern. Blocks injection and broken-deserialization payloads at the gateway. REST APIs; VTL mapping templates transform and validate.
- **Throttling, usage plans, quotas.** Account and per-method throttle limits plus burst. Usage plans tie API keys to per-client rate and quota. This is the abuse, credential-stuffing, and cost-exhaustion control. Per-client usage plans are a REST API feature; HTTP APIs do route-level throttling only.
- **TLS in transit.** HTTPS enforced, minimum **TLS 1.2** (1.2 and 1.3 accepted, 1.0/1.1 rejected). Custom-domain certificates come from ACM. **mTLS** (client certificate validation) is available for B2B and is supported on both REST and HTTP custom domains.
- **CORS.** `Access-Control-Allow-Origin: *` lets any site call the API. Scope to trusted origins, limit methods, and do not expose credentials unless required.
- **Private APIs and VPC integration.** A **private REST API** is reachable only through an interface VPC endpoint (no internet path), gated by a resource policy. **VPC Link** proxies to in-VPC targets (NLB for REST, ALB/NLB/Cloud Map for HTTP) without exposing them publicly.
- **Logging and monitoring.** Access logging and execution logging to CloudWatch Logs, X-Ray tracing, CloudWatch metrics (4xx, 5xx, latency, count), CloudTrail for control-plane changes (who redeployed the API), findings routed to Security Hub or a SIEM.
- **WAF.** Attach a Web ACL for managed rule groups, rate-based rules, and geo/CIDR blocking. WAF integrates with **REST API stages** and CloudFront, not with HTTP APIs.

## REST API vs HTTP API (the control-coverage split)

| Control | REST API | HTTP API |
|---|---|---|
| Price per million | $3.50 | $1.00 |
| IAM / SigV4 auth | Yes | Yes |
| Cognito authorizer | Yes | Via JWT authorizer |
| Native JWT authorizer (OIDC/OAuth2) | No (use Lambda to validate) | Yes |
| Lambda authorizer | Yes | Yes |
| Resource policy | Yes | No |
| API keys + usage plans (per-client quota) | Yes | No |
| Request validation / mapping templates | Yes | No |
| WAF integration | Yes | No |
| Private endpoint | Yes (VPC endpoint + resource policy) | No |
| mTLS on custom domain | Yes | Yes |
| Response caching | Yes | No |

## What gets tested

- **Which API type supports the control.** The single most common trap. WAF, resource policies, API keys/usage plans, request validation, private endpoints, and caching are **REST-only**. Native JWT authorizer is **HTTP-only**. If a scenario needs WAF or a per-client quota on an HTTP API, the answer is "use a REST API" or the control does not apply.
- **Lock down where calls originate.** "Only this VPC / account / CIDR can call the API" is a **resource policy**, not an IAM identity policy and not a security group. Identity answers *who*, resource policy answers *from where*.
- **Private API vs regional/edge.** Removing internet exposure entirely means a **private REST API** behind an interface VPC endpoint, paired with a resource policy that names that endpoint. VPC Link is the reverse direction: reaching private backends, not hiding the API.
- **Authorizer selection.** Signed internal calls: IAM/SigV4. Web/mobile users with a JWT: Cognito or a native JWT authorizer. Bespoke token logic or a third-party IdP with custom validation: Lambda authorizer. API keys are never the authentication answer; they are metering.
- **Throttling as the abuse and cost control.** Flood, credential stuffing, or runaway Lambda spend maps to throttling and usage plans first, Shield/WAF second. Shield Standard is automatic; Shield Advanced is the paid tier for high-risk endpoints.
- **Input validation stops injection at the edge.** When the concern is malformed or malicious payloads reaching Lambda, the REST API request-validation model is the gateway-layer answer, ahead of backend code changes.

## Limitations

- HTTP APIs are cheaper but drop resource policies, WAF, API keys/usage plans, request validation, and private endpoints. Cost optimization can silently remove a security control you needed; verify the control exists on the type before recommending it.
- A resource policy restricts source but does not authenticate. It layers over identity auth, it does not replace it. An open method with only a CIDR allow is still unauthenticated within that range.
- Native JWT authorizers validate the token (signature, claims, expiry) but do not do fine-grained per-resource authorization on their own. Method-level scoping still has to be designed.
- Execution (full-lifecycle) logging is verbose and expensive at volume. It doubles CloudWatch ingestion cost, so production usually runs access logging plus ERROR-level execution logging, not full logging everywhere.
- Shield Standard is DDoS protection at the network and transport layer only. Application-layer (L7) flooding and injection still require WAF and throttling; Shield alone is not the answer to a scraping or L7 flood scenario.
- Caching is a REST-only feature billed continuously by GB-hour regardless of hit rate, so it is a cost lever, not a free security or performance win.