# Private Communication Path: EC2 to S3 (via VPC Gateway Endpoint)

When an EC2 instance in a private subnet needs to reach S3 without traversing the internet, the right mechanism is an S3 gateway VPC endpoint: a route-table entry that sends S3-bound traffic over the AWS private network with no NAT gateway or internet gateway. This keeps the path private and cheap (gateway endpoints are free), and it lets an endpoint policy restrict which buckets and actions are reachable through it. The critical correction to a common myth: a gateway endpoint does not enforce TLS and does not block HTTP. S3 still accepts both HTTP and HTTPS, and the endpoint only controls routing, not encryption. The thing to hold onto: the gateway endpoint gives you a private path plus bucket/action scoping via the endpoint policy, but to guarantee encryption in transit you still add an `aws:SecureTransport` deny (in the bucket policy or the endpoint policy), because private routing is not the same as enforced TLS.

## How it works

- **A gateway endpoint is route-table based and free.** You add the S3 gateway endpoint to the route tables of the relevant subnets. S3 traffic then routes privately over the AWS backbone with no IGW or NAT, lowering both exposure and NAT cost. Gateway endpoints exist for S3 and DynamoDB only.
- **The endpoint does not encrypt or force TLS.** It changes where the traffic goes, not whether it is encrypted. S3's API endpoints accept HTTP and HTTPS regardless of the gateway endpoint, so an HTTP request is not blocked by the endpoint itself.
- **SDKs and CLI default to HTTPS, which is client-side.** In practice most traffic is already TLS because the tooling defaults to `https://s3.<region>.amazonaws.com`, but that is a client default, not endpoint enforcement, and it can be overridden.
- **Enforcing TLS is a policy control.** To actually require encryption, add a deny on `aws:SecureTransport=false` to the bucket policy (and optionally the endpoint policy). That is what rejects plaintext, not the gateway endpoint.
- **The endpoint policy scopes access.** An endpoint policy can restrict which buckets, prefixes, and actions are reachable through the endpoint (for example only your buckets, only Get/Put), giving a data-perimeter control in addition to IAM and the bucket policy.
- **Data-perimeter conditions tie it together.** On the bucket side you can require access to come through your endpoint using `aws:SourceVpce`, ensuring objects are only reachable via the private path and not from arbitrary networks.

## What the gateway endpoint does and does not do

| Concern | Gateway endpoint | The actual control |
|---|---|---|
| **Private routing (no IGW/NAT)** | Yes, this is its job | Route table entry |
| **Encryption in transit** | No, does not enforce TLS | Bucket/endpoint policy `aws:SecureTransport` |
| **Which buckets/actions reachable** | Via endpoint policy | Endpoint policy + IAM + bucket policy |
| **Restrict bucket to the endpoint** | No | Bucket policy `aws:SourceVpce` |
| **Cost** | Free | n/a |

## What gets tested

- **The gateway endpoint does not enforce HTTPS.** This is the key trap. Private routing is not encryption. To require TLS you use `aws:SecureTransport` in a policy. Answering "the VPC endpoint enforces TLS" is wrong.
- **`aws:SecureTransport` for encryption in transit to S3.** Regardless of endpoint, requiring encrypted access is a bucket policy deny on non-TLS requests.
- **`aws:SourceVpce` for the data perimeter.** Restricting a bucket so it is only reachable through your specific endpoint (blocking access from the internet or other networks) uses the `aws:SourceVpce` condition, the correct pattern over fragile source-IP approaches.
- **Gateway vs interface endpoint.** S3 supports a free gateway endpoint (route-table based) and also interface endpoints (PrivateLink, billed, private IP). Gateway is the default for private S3 access from within the VPC, interface endpoints matter for on-prem or cross-VPC access.
- **Public subnet can bypass the endpoint.** If the instance is in a public subnet with an IGW route, or uses a non-regional/global S3 URL that misses the route, traffic can leave the private path. Correct regional URLs and route configuration matter.
- **Endpoint policy for bucket/action scoping.** Limiting what can be done through the endpoint is the endpoint policy, distinct from the bucket policy and IAM.

## Limitations

- The gateway endpoint provides no encryption guarantee, so relying on it for "encryption in transit" is incorrect. TLS must be enforced with a policy condition.
- It only covers S3 (and DynamoDB) and only works from within the VPC via route tables, so on-prem or cross-VPC private access to S3 needs an interface endpoint instead.
- Misrouting undermines it: a public subnet with an IGW route, or global rather than regional S3 URLs, can send traffic around the endpoint, defeating the private path.
- The endpoint policy scopes access through the endpoint but does not replace IAM or the bucket policy, so all three must align for effective least privilege and data-perimeter control.
- Private routing lowers exposure but does not authorize or encrypt on its own, so `aws:SourceVpce` (perimeter), `aws:SecureTransport` (TLS), and IAM/bucket policies (authorization) are still required.
- Because SDK HTTPS is only a client default, a custom client or legacy script could still connect over HTTP unless the bucket policy denies it, so the enforcement cannot be assumed from tooling behavior.