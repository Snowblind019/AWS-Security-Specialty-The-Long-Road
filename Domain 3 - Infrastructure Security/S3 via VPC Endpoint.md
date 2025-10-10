# Amazon S3 via VPC Endpoint

## What Is the Service

Amazon S3 via VPC Gateway Endpoints lets you connect to S3 entirely through AWS's private network, without ever touching the public internet. This is critical when you want to:

• Eliminate exposure to the internet
• Avoid NAT Gateway usage and its high per-GB costs
• Enforce tight security boundaries using IAM and S3 bucket policies
• Stay compliant with frameworks like NIST, PCI-DSS, FedRAMP

Without a VPC endpoint, EC2 instances or Lambda functions in private subnets would need to use a NAT Gateway or Internet Gateway to access S3. That’s unnecessary risk and unnecessary cost. With a Gateway VPC Endpoint, you bypass all that and stay fully within AWS's internal routing fabric.
This is a foundational building block for Zero Trust architectures in AWS.

---

## Cybersecurity Analogy

Imagine you’re building a secure archive room inside your company. You need to send employees there to drop off sensitive documents. You have two options:

• Let them go outside the building, walk through a public alley, and re-enter through the archive’s public door
• Or… build a secure, monitored internal corridor directly between your operations floor and the archive room

The VPC Endpoint is that private corridor. It’s shielded from the outside world. You can install surveillance (logs), badge access (IAM), and even door scanners (bucket policies) to control who gets through. No outside risk, no extra exposure.

## Real-World Analogy

You’ve got a warehouse, and forklifts need to send boxes to storage. Without an internal access road, they’d have to go out to the main highway and loop around — burning fuel, facing traffic, and possibly being hijacked.
So you build an internal access tunnel. No toll booths. No highway. No attackers. Just your forklifts, your road, your destination.
That’s the difference between using a NAT Gateway and using a Gateway VPC Endpoint to access S3.

---

## How It Works
### Service Type

S3 Gateway Endpoints are Gateway-type VPC Endpoints — not the Interface type with ENIs. These are only available for S3 and DynamoDB.

### Routing

You create a VPC endpoint for S3 in a region and attach it to one or more route tables.
AWS adds a route:
**Destination:** `pl-68a54001` → **Target:** `com.amazonaws.region.s3`
All traffic destined for `s3.amazonaws.com` (and other S3 regional endpoints) will now be rerouted internally.

### IAM + Bucket Policy Enforcement

You can restrict access to an S3 bucket using `aws:SourceVpce`. Example:

```json
{
  "Effect": "Deny",
  "Principal": "*",
  "Action": "*",
  "Resource": "*",
  "Condition": {
    "StringNotEquals": {
      "aws:SourceVpce": "vpce-1234567890abcdef0"
    }
  }
}
```

This guarantees the request must come through the VPC endpoint — not from the internet, not from another account.

### DNS Behavior

The DNS name `s3.amazonaws.com` doesn’t change. AWS intercepts it and reroutes internally. No code changes needed.

### Visibility and Logging

You can:
• Use VPC Flow Logs to monitor traffic from subnets to S3
• Use CloudTrail Data Events to log object-level access
• Use AWS Config to detect when buckets lose endpoint restrictions

---

## Pricing Models

- No hourly charge for Gateway Endpoints.
- No per-request fees either.
- You only pay the normal S3 costs — PUT, GET, data stored, etc.

If you skip VPC Endpoints and use a NAT Gateway:
- You’ll pay $0.045 per GB for data transfer
- Plus $0.045 per GB for NAT processing
- Plus $0.045/hr for the NAT Gateway itself

It adds up. Especially for apps doing logging, backup, or large object ingestion to S3.

---

## Other Technical Considerations

- Can attach to multiple route tables
- Cannot span Regions — VPC endpoint must be in the same Region as the VPC and S3 bucket
- Works with S3 Access Points, S3 Object Lambda, and cross-account buckets
- Does not support prefix lists for routing (you use the S3 prefix list ID when configuring the route)

---

## Real-Life Example: Snowy’s Backup Pipeline

Let’s say you’re running an EC2 instance inside a private subnet. It runs hourly backups of sensitive logs to S3 (`s3://snowy-logs-prod`).
Before VPC endpoints, that EC2 had to go out through a NAT Gateway. That meant:

- Exposure to the public internet
- VPC Flow Logs couldn’t see the full egress path
- And you were burning $0.09/GB (combined with NAT charges)

Now you build a Gateway VPC Endpoint for S3, attach it to the private route table, and update the bucket policy to only accept requests from `aws:SourceVpce`.

**Result:**
- No internet exposure
- No NAT Gateway charges
- Full visibility into source IPs, IAM roles, and request metadata
- Zero Trust enforced at the network boundary, identity layer, and storage policy

If malware gets onto that EC2 instance, it can’t exfiltrate to another bucket. It’s locked down.

---

## Final Thoughts

VPC Gateway Endpoints for S3 are one of the highest ROI security tools in all of AWS. They’re simple, powerful, and free.

In any serious architecture where EC2, Lambda, or Fargate functions operate in private subnets and need access to S3:

- Use them to block unnecessary internet exposure
- Enforce `aws:SourceVpce` in every bucket policy
- Pair them with CloudTrail, Config, and Flow Logs for end-to-end visibility
- Remove your NAT Gateways if their only job was to reach S3

This is one of those rare services that hits **security**, **cost**, **visibility**, and **performance** all at once — and does it with almost no complexity.
