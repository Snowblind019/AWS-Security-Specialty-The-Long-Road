# Private Communication Path: VPC PrivateLink / Interface Endpoints

PrivateLink connects a consumer VPC to a service (an AWS service, a SaaS provider, or a custom service in another account) over the AWS backbone with no internet, NAT, or IGW, by placing an interface endpoint (an ENI with a private IP) in your subnets. It is the standard way to consume AWS services privately from a private subnet and to expose an internal service across accounts without VPC peering or public IPs, which makes it a staple of regulated and multi-account architectures. The nuance the exam probes: PrivateLink provides private connectivity, it does not itself add encryption. TLS comes from the service on top (AWS service endpoints like KMS and Secrets Manager are HTTPS-only, so those are always encrypted, but a custom service behind an NLB is only encrypted if you configure TLS on it). The thing to hold onto: PrivateLink is private routing plus per-endpoint access control (security groups, endpoint policy, and the provider's acceptance), encryption depends on the service layered on top, and unlike VPC peering it is one-directional (consumer to service) and non-transitive.

## How it works

- **An interface endpoint puts a private IP in your VPC.** The endpoint is an ENI mapped to the target service. Consumers resolve the service name (with private DNS) to that private IP and connect without any public path.
- **Traffic stays on the AWS backbone.** No NAT, no IGW, no public IP. This reduces exposure and is why regulated environments favor it, but "private" describes the network path, not the payload encryption.
- **Encryption is the service's, not PrivateLink's.** AWS service endpoints (KMS, Secrets Manager, and most others) enforce HTTPS/TLS, so those calls are always encrypted. For a custom service you expose behind an NLB, PrivateLink carries whatever you run, so you must terminate TLS on the service to encrypt it.
- **Access control is layered.** Security groups on the endpoint ENI restrict source/port, an endpoint policy restricts which resources or actions are reachable through it, and on the provider side a service access (acceptance) policy controls which consumer accounts may connect at all.
- **It is consumer-to-service and non-transitive.** PrivateLink exposes a single service to consumers, it does not create general VPC-to-VPC reachability. You cannot route VPC A to VPC B to VPC C through it, that is Transit Gateway territory.
- **Everything is auditable.** Endpoint usage and the underlying API calls appear in CloudTrail, and interface endpoints are billed per hour and per GB (unlike the free S3/DynamoDB gateway endpoints).

## PrivateLink vs peering vs NAT/IGW

| Feature | PrivateLink | VPC Peering | NAT / IGW |
|---|---|---|---|
| **Stays private** | Yes | Yes | No (public IPs) |
| **Transitive routing** | No (point-to-service) | No | n/a |
| **Encryption** | Service-dependent (AWS services enforce TLS) | Optional, yours to configure | Optional |
| **Multi-account exposure** | Excellent, one service at a time | Works but broad and harder to scale | Not ideal |
| **Access control** | SG + endpoint policy + provider acceptance | Route tables + SG | SG only |

## What gets tested

- **PrivateLink is private routing, not automatic payload encryption.** For AWS services the service enforces TLS, but for a custom service behind an NLB you must configure TLS yourself. Answering "PrivateLink encrypts the traffic" for a custom service is wrong.
- **PrivateLink vs peering for exposing one service across accounts.** Sharing a single internal service to other accounts without giving broad network reachability is PrivateLink. Peering connects whole VPCs and is broader and non-transitive.
- **Consuming AWS services from a private subnet without internet.** Interface endpoints (PrivateLink) let a private-subnet workload reach services like KMS or Secrets Manager with no NAT. For S3 and DynamoDB specifically, the free gateway endpoint is the usual choice, interface endpoints matter for on-prem or cross-VPC.
- **Endpoint policy and provider acceptance.** Restricting what an endpoint can reach is the endpoint policy, and controlling which consumers may connect to a provider service is the provider's acceptance/access policy. These are distinct controls.
- **Non-transitive, point-to-service.** PrivateLink does not give A-to-B-to-C routing. Transitive, any-to-any connectivity is Transit Gateway.
- **Cost model.** Interface endpoints bill per hour and per GB, so many endpoints across many VPCs add up, unlike the free gateway endpoints.

## Limitations

- PrivateLink provides connectivity, not encryption, for custom services. A service behind an NLB is only encrypted if you terminate TLS on it, so "private" is not "encrypted" by itself.
- It is one-directional and non-transitive: the consumer reaches the service, not the reverse, and it cannot chain VPCs. Broad or transitive connectivity needs peering or Transit Gateway.
- Interface endpoints are billed hourly and per GB and consume ENIs, so at scale they carry real cost and IP consumption, unlike free gateway endpoints.
- Private DNS must be configured correctly or the service name will not resolve to the endpoint, and traffic may fall back to a public path.
- Network-layer privacy does not replace application-layer security. Authentication, authorization, and rate limiting on the service are still yours to implement.
- The provider controls acceptance, so a misconfigured or overly permissive service access policy can expose the service to unintended consumer accounts.