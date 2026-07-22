# Private Communication Path: EC2 to Private API Gateway

When EC2 instances in a private subnet need to call an API Gateway API without any public internet exposure, the pattern is a private API Gateway reached through an interface VPC endpoint. The request resolves to a private IP inside your VPC, travels over the AWS backbone rather than the internet, and is TLS 1.2+ enforced end to end, while you keep all of API Gateway's features (authorizers, throttling, caching, Lambda/Step Functions integration). What makes a private API actually private is not just the endpoint, it is the combination of the interface endpoint, a resource policy that scopes who can invoke, and optionally a VPC endpoint policy. The thing to hold onto: a private API Gateway needs an interface VPC endpoint plus a resource policy allowing that endpoint (the resource policy is required, not optional, for private APIs), TLS 1.2+ is mandatory with no HTTP fallback, and access is gated by both network isolation and IAM/resource policy.

## How it works

- **The API is deployed as private, not public.** A private API is only reachable through an interface VPC endpoint (`execute-api`), so there is no public DNS path to invoke it. This is the endpoint-type decision made on the API.
- **An interface VPC endpoint gives it a private IP.** The `execute-api` interface endpoint places ENIs with private IPs in your subnets. EC2 resolves the API's DNS name (with private DNS enabled) to that endpoint and connects internally.
- **A resource policy is mandatory for private APIs.** A private API requires a resource policy that allows invocation from the specific VPC endpoint (`aws:SourceVpce`) or VPC. Without it, or with the wrong condition, calls are denied. This is the control that binds the API to your endpoint.
- **Traffic stays on the AWS backbone with enforced TLS.** Requests never traverse the public internet, and API Gateway enforces TLS 1.2+, rejecting HTTP. There is no plaintext fallback.
- **Authorization layers on top.** IAM auth, Lambda authorizers, or JWT/Cognito validate the caller, and a VPC endpoint policy can additionally restrict which APIs that endpoint may reach. mTLS is available but requires a custom domain name and has constraints, so it is not automatic.
- **Observability is built in.** CloudWatch access logs, execution logs, and X-Ray give you the audit and tracing for the private path.

## Access-control layers for a private API

| Layer | Role |
|---|---|
| **Endpoint type = private** | Removes any public invocation path |
| **Interface VPC endpoint** | Private IP entry point inside the VPC |
| **Resource policy (required)** | Allows invocation from the specific VPCE / VPC |
| **VPC endpoint policy (optional)** | Restricts which APIs the endpoint can call |
| **IAM / Lambda authorizer / JWT** | Authenticates and authorizes the caller |
| **TLS 1.2+ (enforced)** | Encrypts transport, no HTTP fallback |

## What gets tested

- **Private API needs both the interface endpoint and a resource policy.** The interface endpoint provides the private path, but the resource policy scoping to `aws:SourceVpce` is what actually permits (or denies) access. A private API with no resource policy is inaccessible, and one with a wrong policy is a common misconfiguration.
- **Private vs public endpoint type.** If the requirement is no internet exposure and VPC-only access, the answer is a private API with a VPC endpoint, not a public API behind other controls.
- **TLS is mandatory, no HTTP.** API Gateway enforces TLS 1.2+ and there is no plaintext option, so "encryption in transit" is inherent here, unlike ALB-to-target which is opt-in.
- **VPC endpoint policy for endpoint-level restriction.** Limiting which APIs a given endpoint may reach is the VPC endpoint policy, distinct from the API's own resource policy.
- **mTLS needs a custom domain.** Client-certificate mutual TLS on API Gateway requires a custom domain name and is not just a checkbox, so a scenario demanding mTLS implies that setup.
- **Backbone routing, not NAT.** A private API over an interface endpoint keeps traffic internal without needing a NAT gateway, unlike calling a public API from a private subnet.

## Limitations

- A private API is unreachable without the correct resource policy scoping it to the VPC endpoint, so the resource policy is a required, easy-to-get-wrong piece, not an optional hardening step.
- It is not publicly consumable by design, so external clients need a different pattern (public API, or fronting via other services).
- Interface VPC endpoints have an hourly and per-GB cost, and each adds ENIs, so many private APIs across many VPCs carry endpoint cost and management.
- mTLS requires a custom domain name and additional configuration, so it is not available out of the box on the raw private endpoint.
- Private DNS resolution must be enabled and correctly configured, or the API's name will not resolve to the interface endpoint and calls fail or leak to a public path.
- Network isolation plus TLS secures the path, but authorization still depends on IAM, resource, and authorizer configuration, so a permissive resource policy or missing authorizer undermines the private setup.