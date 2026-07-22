# Amazon S3 via VPC Gateway Endpoint

An S3 gateway VPC endpoint routes S3 traffic from your VPC over the AWS private network via a route-table entry, so private-subnet workloads reach S3 without a NAT gateway or internet gateway. It is free (no hourly or per-request charge), which makes it both a cost win over NAT and a security win: paired with an `aws:SourceVpce` bucket policy condition, it becomes a data-perimeter control that guarantees a bucket is only reachable through your endpoint, which blocks exfiltration to arbitrary buckets or from the internet. Gateway endpoints exist only for S3 and DynamoDB. The thing to hold onto: the gateway endpoint gives private routing plus the `aws:SourceVpce` perimeter and eliminates NAT cost, but it does not encrypt traffic (TLS still comes from S3/HTTPS and is enforced separately with `aws:SecureTransport`), and it cannot span Regions.

## How it works

- **It is a gateway endpoint, added to route tables.** You create the S3 endpoint and attach it to the relevant route tables, which adds a route for the S3 prefix list to the endpoint target. S3-bound traffic then stays on the AWS backbone. Gateway endpoints are S3/DynamoDB only, distinct from interface (PrivateLink) endpoints.
- **DNS is unchanged.** The S3 endpoint name resolves as normal and AWS reroutes it internally, so no application code changes are needed.
- **`aws:SourceVpce` builds a data perimeter.** A bucket policy that denies requests whose `aws:SourceVpce` does not match your endpoint ensures the bucket is only reachable through that endpoint, not from the internet and not from other networks or accounts. This is the exfiltration-prevention control.
- **It removes NAT cost and exposure.** Without the endpoint, a private-subnet instance reaches S3 via NAT, paying per-GB processing and data transfer plus the NAT hourly charge, and exposing an egress path. The gateway endpoint is free and keeps traffic internal.
- **Visibility layers on top.** VPC Flow Logs show subnet-to-S3 traffic, CloudTrail data events log object-level access, and Config can detect when a bucket loses its endpoint restriction.
- **It does not encrypt.** The endpoint controls routing and the perimeter, not encryption. TLS comes from S3's HTTPS endpoints and the SDK default, and enforcing it still requires an `aws:SecureTransport` deny.

## Gateway endpoint: what it provides

| Capability | Provided by the endpoint | The actual mechanism |
|---|---|---|
| **Private routing (no NAT/IGW)** | Yes | Route table entry, free |
| **Data perimeter** | Via policy | `aws:SourceVpce` deny in bucket policy |
| **Encryption in transit** | No | `aws:SecureTransport` + S3 HTTPS |
| **Cost savings** | Yes | Eliminates NAT per-GB and hourly charges |
| **Cross-Region** | No | Endpoint, VPC, and bucket must share a Region |

## What gets tested

- **`aws:SourceVpce` for the data perimeter.** Restricting a bucket so it is only reachable through your VPC endpoint (blocking internet and cross-account access, and preventing exfiltration) is the `aws:SourceVpce` condition, preferred over fragile source-IP approaches.
- **Gateway endpoint eliminates NAT for S3.** Reaching S3 privately from a private subnet without NAT cost is the free S3 gateway endpoint. This is both the cost and the security answer.
- **The endpoint does not enforce TLS.** Encryption in transit is a separate `aws:SecureTransport` control. Do not answer "the VPC endpoint encrypts the traffic."
- **Gateway vs interface endpoint.** S3 uses a free gateway endpoint from within a VPC. Interface (PrivateLink) endpoints for S3 exist for on-prem or cross-VPC access and are billed. DynamoDB also uses a gateway endpoint.
- **Same-Region constraint.** The endpoint, VPC, and bucket must be in the same Region, so cross-Region access needs a different approach.
- **Exfiltration containment.** If malware on an instance should not be able to send data to an attacker-controlled bucket, `aws:SourceVpce` plus endpoint policies scoping reachable buckets is the containment control.

## Limitations

- The gateway endpoint provides no encryption, so relying on it for encryption in transit is wrong. TLS must be enforced with a policy condition.
- It only covers S3 and DynamoDB and only works from within the VPC via route tables, so on-prem or cross-VPC private S3 access needs an interface endpoint.
- It cannot span Regions, so the endpoint, VPC, and bucket must share a Region.
- The `aws:SourceVpce` perimeter is only as good as its coverage. A bucket without the condition, or a workload with an alternate egress path (public subnet with IGW), can bypass the intended perimeter.
- The endpoint scopes network access but does not replace IAM and bucket policies, so authorization still depends on those being correct.
- Endpoint policies can restrict which buckets and actions are reachable through the endpoint, but a permissive endpoint policy weakens the containment, so it must be scoped deliberately.