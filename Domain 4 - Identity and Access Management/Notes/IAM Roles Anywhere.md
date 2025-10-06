# IAM Roles Anywhere

## What Is IAM Roles Anywhere

IAM Roles Anywhere is a service that lets you securely access AWS resources from outside AWS infrastructure — using X.509 certificates instead of static credentials or access keys.
This is AWS’s answer to a long-standing problem:

> “How do I let on-prem servers, Kubernetes clusters, EC2s in another cloud, or even embedded/IoT devices authenticate to AWS APIs — without using permanent IAM users or long-lived access keys?”

With IAM Roles Anywhere, you can:

- Issue a short-term session token (via STS) for any non-AWS workload
- Use X.509 TLS certificates to authenticate to IAM roles
- Completely avoid static AWS access keys
- Enforce tight identity-based permissions and least privilege

It’s like Instance Profile behavior for things outside AWS.

---

## Cybersecurity Analogy

Imagine a secure warehouse (AWS). Normally, only employees with AWS badges (IAM roles) can enter.
But now you've got trusted third-party delivery trucks (on-prem servers, edge devices) that need temporary access — but you don’t want to give them permanent keys.

IAM Roles Anywhere lets you say:

- “Here’s a certificate signed by our CA”
- “This proves you're trusted”
- “We’ll let you in with temporary scoped access for a short time — and we’re logging everything”

It’s zero-trust in action — you don’t assume anything just because a server is internal. They must present proof, match conditions, and earn trust dynamically.

## Real-World Analogy

Imagine Snowy has a CI/CD runner sitting in a datacenter outside of AWS. It needs to:

- Upload build artifacts to S3
- Trigger a CodeDeploy job
- Maybe rotate a secret in Secrets Manager

**Old way:**

- You create an IAM user
- Generate access key and secret key
- Store it in a vault, worry about rotating it every 90 days

**New way (Roles Anywhere):**

- That runner presents a signed client certificate
- AWS checks if the certificate maps to a trust anchor

No long-term credentials. No IAM users. Fully auditable.

---

## How It Works

The workflow has 5 key components:

1. **Trust Anchor**
   A CA (Certificate Authority) you trust to sign identities
   Can be private (e.g., ACM PCA) or external (e.g., your internal CA or Vault)

2. **Profile**
   Defines the mapping between X.509 certificate principals and IAM roles
   *Example:* Certs signed for `build-agent.prod.snowy.lan` can assume `RoleBuildDeployer`

3. **IAM Role**
   The actual role being assumed
   Must trust the `rolesanywhere.amazonaws.com` service principal
   Session policies and conditions can restrict access further

4. **Signing Certificate**
   Stored securely on the device or server
   Must be signed by the trusted CA

5. **AWS CLI / SDK Integration**
   Use the credential helper (`aws_signing_helper`) to generate credentials on demand
   The helper talks to IAM Roles Anywhere and exchanges the cert for STS credentials

---

## What This Solves

| Problem                             | IAM Roles Anywhere Fixes It? |
|-------------------------------------|-------------------------------|
| Long-lived access keys (risk)       | Yes                           |
| IAM user sprawl                     | Yes                           |
| Secure access from hybrid cloud     | Yes                           |
| Identity-based fine-grain auth      | Yes                           |
| Role chaining / scoped trust        | Yes (via conditions + tags)  |
| Auditable / temporary sessions      | Yes                           |
| MFA / device-bound access           | Yes (if certs are device-bound) |

---

## CLI Example: Secure On-Prem to AWS Flow

```bash
aws_signing_helper credential-process \
  --certificate /path/to/client-cert.pem \
  --private-key /path/to/key.pem \
  --trust-anchor-arn arn:aws:rolesanywhere:us-west-2:111122223333:trust-anchor/abc123 \
  --profile-arn arn:aws:rolesanywhere:us-west-2:111122223333:profile/BuildAgents \
  --role-arn arn:aws:iam::111122223333:role/BuildDeployerRole
```

This will:

- Authenticate the certificate against the trust anchor
- Assume the role `BuildDeployerRole`
- Return an STS token (AccessKey, SecretKey, SessionToken)
- Used by the AWS CLI or SDK as if it's a real IAM principal

---

## Security Benefits

- No static keys to rotate, leak, or forget
- Short-lived credentials (default 1 hour)
- Audit trail via STS and CloudTrail
- Least privilege enforcement via role scoping
- Support for private PKI (device certificates, org-wide certs, etc.)

---

## Security Caveats

- You must protect the private keys of these certificates
- If your CA is compromised, the trust anchor becomes a weakness
- You must enforce session policies, tags, and role boundaries
- Currently limited to X.509 v3 client certificates only
- Still needs role trust policy hardening (e.g., Conditions on cert fields)

---

## Real-Life Snowy Scenario

Snowy’s ops team manages a fleet of IoT sensor hubs in rural fiber closets — offline most of the time, but occasionally connect to push diagnostics to AWS.

**Requirements:**

- No internet-facing credential stores
- No permanent access keys
- Only allow sensors to write logs to one S3 bucket, nothing else

**Solution:**

- Each sensor has a cert signed by Snowy's internal CA
- AWS IAM Roles Anywhere is configured with that CA as the trust anchor
- Each sensor can only assume a role scoped to:
  `s3:PutObject` on `arn:aws:s3:::snowy-logs/sensors/*`

- Session lasts 30 minutes, then expires

Sensors don’t need human intervention, no one rotates keys manually, and CloudTrail logs every interaction by X.509 principal.

---

## IAM Role Trust Policy Example

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "rolesanywhere.amazonaws.com"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "aws:PrincipalTag/DeviceType": "IoTSensor"
        }
      }
    }
  ]
}
```

This means: only clients coming through IAM Roles Anywhere with a valid tag (e.g., from a profile) can assume this role.

---

## Final Thoughts

IAM Roles Anywhere is one of the most powerful but least known AWS security services — because it blurs the line between AWS-native and external access.
It extends IAM best practices to non-AWS workloads in a way that’s:

- Temporary
- Credentialless
- Auditable
- Policy-enforced
- Fully managed by your trust model (via PKI)

If you're running:

- On-prem CI/CD
- Third-party clouds (GCP, Azure, DigitalOcean)
- Edge nodes / remote fiber huts / offline sensors
- Kubernetes clusters outside AWS

Then **IAM Roles Anywhere lets you retire static keys permanently.**
