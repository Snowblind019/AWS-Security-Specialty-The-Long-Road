# VPC Endpoints

A VPC endpoint gives resources in your VPC a private path to AWS services (and, via PrivateLink, to other VPCs and SaaS) without traversing the public internet, an internet gateway, or a NAT gateway. By default, calling S3, DynamoDB, Secrets Manager, or KMS from a VPC goes out to the public AWS endpoint; an endpoint keeps that traffic on the AWS backbone with private IPs. The thing to hold onto: endpoints are both a privacy control (no internet path) and an access control (endpoint policies plus `aws:SourceVpce`/`aws:SourceVpc` conditions let you require that a service is reached only through your endpoint), and the exam's core split is gateway (S3/DynamoDB, free, route-table based) versus interface (everything else, PrivateLink ENI, paid).

## How it works

- **Gateway endpoint.** For **S3 and DynamoDB only**. It adds a **prefix-list route** to the route tables you select, pointing that service's prefix list at the endpoint. No ENI, no security group, free, and same-Region/same-VPC only. It cannot be reached from on-premises or another VPC.
- **Interface endpoint (PrivateLink).** An **ENI with a private IP** in your subnet for 100+ services (SSM, Secrets Manager, STS, KMS, ECR, CloudWatch, and so on). Reached by DNS (private DNS makes the normal service hostname resolve to the ENI). Supports **security groups** on the ENI, is billable per-AZ-hour plus per-GB, and can be reached from other VPCs, cross-Region, and on-premises via Direct Connect/VPN.
- **Gateway Load Balancer endpoint.** Steers traffic to third-party inspection appliances (firewalls, IDS/IPS) behind a Gateway Load Balancer. Different purpose from the two data-access types.
- **Resource endpoints (newer).** Reach a specific target (an RDS instance or any TCP target by IP/domain) in another VPC or on-premises without standing up an NLB.
- **Endpoint policies.** Both gateway and interface endpoints support a resource-style **endpoint policy** that restricts which principals, actions, and resources can be reached through that endpoint, an extra layer on top of IAM.
- **Requiring the endpoint.** Bucket/resource/IAM policies can demand traffic arrive via your endpoint with a condition:

```json
"Condition": { "StringEquals": { "aws:SourceVpce": "vpce-0abc123456789" } }
```

`aws:SourceVpc` (any endpoint in a VPC) and `aws:VpcSourceIp` are related keys. This blocks access even with valid credentials unless the call comes through the private path.

## Gateway vs interface endpoint

| | Gateway endpoint | Interface endpoint |
|---|---|---|
| Services | S3, DynamoDB only | 100+ services (SSM, KMS, Secrets Manager, ECR, STS...) |
| Mechanism | Route-table prefix-list entry | PrivateLink ENI + private IP |
| Cost | Free | Per-AZ-hour + per-GB |
| Security group | No | Yes (on the ENI) |
| Endpoint policy | Yes | Yes |
| From other VPCs / on-prem / cross-Region | No | Yes |
| DNS | Route-based (no DNS change) | Private DNS resolves service name to ENI |

## What gets tested

- **Gateway for S3/DynamoDB, interface for the rest.** The default and cheapest way to reach S3 or DynamoDB privately from a VPC is a **gateway endpoint** (free). Everything else, and any S3 access from on-prem or cross-VPC, is an **interface endpoint**. Picking an interface endpoint for high-volume same-Region S3 wastes money.
- **Lock a bucket to the VPC.** "Only allow S3 access through our VPC" is a **bucket policy with `aws:SourceVpce`** (or `aws:SourceVpc`), a top S3-exfiltration-prevention answer. It denies even valid credentials coming from the internet.
- **Endpoint policy vs resource policy.** The endpoint policy restricts what can be reached *through the endpoint*; the bucket/resource policy restricts access *to the resource*. Both can be applied and the exam tests knowing which lever does which.
- **Private DNS for interface endpoints.** So existing SDK calls to the normal hostname resolve to the ENI, enable **private DNS** (and `enableDnsSupport`/`enableDnsHostnames`). "App still hits the public endpoint after creating an interface endpoint" is usually private DNS not enabled.
- **Security groups apply to interface endpoints only.** Gateway endpoints have no ENI and no SG; control them with route tables and endpoint policies. Interface endpoint ENIs are gated by security groups.
- **Endpoints are regional.** A us-east-1 endpoint does not privately reach a service in us-west-2; that traffic goes over the internet unless you use cross-Region PrivateLink. Watch cross-Region assumptions.
- **Remove NAT/IGW dependency.** Private subnets reaching AWS services without a NAT gateway is the endpoint pattern, cutting both internet exposure and NAT cost, a common "air-gapped but still needs S3/SSM" design.

## Limitations

- Gateway endpoints only serve S3 and DynamoDB, only within the same Region and VPC, and cannot be reached from on-premises or peered VPCs. For those cases you need an interface endpoint.
- Interface endpoints cost per-AZ-hour and per-GB and are deployed per AZ for resilience, so multi-AZ coverage multiplies cost; they are not free like gateway endpoints.
- Endpoints are regional and, by default, VPC-local. Cross-Region private access needs cross-Region PrivateLink; do not assume one endpoint covers all Regions.
- Private DNS misconfiguration silently sends traffic back over the public path. The endpoint exists but is bypassed until DNS and VPC DNS attributes are correct.
- Gateway endpoints depend on route-table associations; a subnet whose route table lacks the association follows the default route (often the internet). Coverage is per route table, not automatic VPC-wide.
- Endpoint and `aws:SourceVpce` controls govern the network path and reachability, not identity. They complement IAM and bucket policies; they do not replace least-privilege permissions.