# TLS 1.2+

TLS is the protocol securing data in transit: it encrypts traffic on the wire, authenticates endpoints via certificates, and detects tampering and MITM. The version matters because TLS 1.0 and 1.1 are deprecated and vulnerable to downgrade and cipher attacks (POODLE, BEAST), while only TLS 1.2 and 1.3 meet modern and compliance baselines (PCI DSS, HIPAA, NIST). Across AWS, enforcing TLS 1.2+ is a per-service job at each edge: a security policy on ALB and CloudFront sets the minimum version and ciphers, S3 uses a policy condition, and databases enforce it via parameters. The thing to hold onto: enforcing the TLS floor is choosing a modern security policy on ALB/CloudFront, the S3 lever is `aws:SecureTransport`, API Gateway is already TLS 1.2+ with no downgrade, and "supports TLS" is not "enforces TLS" for databases, where the client or a parameter must require it.

## How it works

- **CloudFront: minimum viewer TLS via security policy.** Set the minimum protocol version (for example TLSv1.2_2021) and an HTTPS-only or redirect viewer policy, with an ACM cert in `us-east-1`. This removes weak protocols and ciphers on the client hop.
- **ALB: HTTPS listener plus a modern security policy.** Choose a TLS 1.2 or TLS 1.3 security policy (for example an `ELBSecurityPolicy-TLS-1-2` or `-TLS-1-3` policy) on the HTTPS listener to set the version floor and cipher suite, and redirect port 80 to 443.
- **S3: `aws:SecureTransport` deny.** A bucket policy denying requests where `aws:SecureTransport` is false blocks all non-TLS access, uniformly across CLI, SDKs, and tools. This is the S3 in-transit control.
- **RDS/Aurora: enforce per engine.** Force TLS with `rds.force_ssl=1` (PostgreSQL) or `require_secure_transport=ON` (MySQL) in a parameter group, and have clients use SSL with the RDS CA bundle (`sslmode=require`/`verify-full`), optionally client certs for mTLS.
- **API Gateway: TLS 1.2+ by default.** It enforces TLS 1.2+ and cannot be downgraded, so the work is attaching an ACM cert to a custom domain, not enabling TLS.
- **Monitoring.** CloudWatch can surface TLS negotiation failures, S3 denials of plaintext requests, and ACM renewal failures, so downgrade attempts and cert problems are visible.

## Enforcing TLS 1.2+ by service

| Service | Mechanism | Note |
|---|---|---|
| **CloudFront** | Minimum viewer TLS security policy | ACM cert in `us-east-1` |
| **ALB / NLB** | HTTPS listener + TLS 1.2/1.3 security policy | Redirect 80 to 443 |
| **S3** | Bucket policy `aws:SecureTransport=false` deny | Applies to all clients |
| **RDS / Aurora** | `rds.force_ssl` / `require_secure_transport` | Client uses RDS CA bundle |
| **API Gateway** | TLS 1.2+ by default | Cannot downgrade |

## What gets tested

- **TLS 1.0/1.1 are non-compliant.** Enforcing TLS 1.2 minimum on ALB/CloudFront via a modern security policy is the answer for PCI/HIPAA and to block downgrade attacks. Legacy policies that permit TLS 1.0 are wrong.
- **S3 in-transit is `aws:SecureTransport`.** Requiring TLS to a bucket is the bucket policy condition, not a security group (which does not apply to S3) or client trust alone.
- **Database TLS is enforced, not assumed.** RDS supporting TLS does not mean it is required. Forcing it is a parameter (`rds.force_ssl`/`require_secure_transport`) plus client SSL config, and validation needs the CA bundle.
- **API Gateway is already TLS 1.2+.** No enabling needed, and it cannot be downgraded, so encryption in transit is inherent there.
- **Cert validation prevents MITM.** Encrypting without validating the server cert leaves a MITM gap, so clients must validate (verify-full), and ACM handles server cert lifecycle and rotation.
- **CloudFront cert region.** The viewer cert must be in `us-east-1`, a recurring misconfiguration.

## Limitations

- Defaults can be permissive: legacy ALB/CloudFront security policies allow TLS 1.0/1.1, so you must explicitly select a TLS 1.2+ policy.
- TLS support is not enforcement, especially for databases, where an unconfigured client connects in plaintext unless the engine forces TLS.
- Encryption without certificate validation still allows MITM, so `verify-full`-style validation and current CA bundles are required, not just enabling SSL.
- Certificate rotation matters: expired certs cause outages or insecure fallbacks, and AWS RDS cert rotation requires updating client trust stores.
- TLS protects the wire, not data at rest or authorization, so it pairs with encryption at rest and IAM rather than standing alone.
- Redirecting HTTP to HTTPS still exposes the initial plaintext request line, so the strictest endpoints reject rather than redirect, and enforcement must cover both hops (viewer and origin) where a CDN or load balancer is involved.