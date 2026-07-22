# Encryption in Transit in AWS

Encryption in transit protects data moving between users, services, and Regions from eavesdropping, tampering, and MITM, and in AWS it is almost entirely TLS. It shows up in two directions: north-south (users to AWS via HTTPS on CloudFront, ALB/NLB, API Gateway) and east-west (service to service via App Mesh mTLS, TLS to RDS/DynamoDB, and private paths over PrivateLink). The recurring theme for the exam is that it is not automatic everywhere: some endpoints default to permissive TLS policies or accept plaintext unless you enforce otherwise. The thing to hold onto: for S3 you enforce transit encryption with a bucket policy denying `aws:SecureTransport=false`, for load balancers and CloudFront you pick a strong TLS security policy and terminate with ACM certs, and mTLS (client-certificate auth) is a separate trust-store configuration, not something a public ACM cert provides on its own.

## How it works

- **Load balancers terminate TLS with a chosen security policy.** ALB (L7) and NLB support HTTPS/TLS listeners, and the security policy (for example a TLS 1.3 policy) sets the minimum protocol and cipher suites, removing weak ciphers and downgrade vectors. ALB supports SNI for multiple certs on one listener and mTLS via an uploaded client-CA trust store.
- **CloudFront terminates TLS at the edge.** It serves HTTPS-only content, integrates with ACM for free public certs (which must be in `us-east-1` for CloudFront), and lets you set a minimum viewer TLS version.
- **S3 is enforced by policy, not a port.** All S3 endpoints are HTTPS-capable, but to require encryption you add a bucket policy that denies any request where `aws:SecureTransport` is false. This is the canonical S3 in-transit control.
- **Databases need client-side TLS.** RDS, Aurora, Redshift, and DynamoDB all support TLS, but you enforce it on the client (for example `sslmode=require` for PostgreSQL) using the Region-specific CA bundle, and some engines let you force TLS for all users via a parameter (`rds.force_ssl`).
- **App Mesh does east-west mTLS.** It uses Envoy sidecars to encrypt and mutually authenticate service-to-service traffic via mesh policy, a strong fit for zero-trust microservices, so individual apps do not each build TLS.
- **PrivateLink provides private connectivity, TLS still runs on top.** A PrivateLink interface endpoint keeps traffic on the AWS backbone and off the public internet, which is a network-segmentation and exposure control. It does not by itself replace application TLS: you still terminate TLS at the service endpoint for actual encryption.
- **ACM handles the server certs, mTLS trust is separate.** ACM (and ACM Private CA) issue and auto-rotate the server-side certificates. Client-certificate authentication (mTLS) on ALB or API Gateway is configured with a separate trust store of CA certs you provide (often issued by ACM Private CA), so "ACM does mTLS" is only half the story.

## Where encryption in transit is enforced

| Surface | Mechanism | The thing you must set |
|---|---|---|
| **CloudFront** | TLS at edge, ACM cert in `us-east-1` | Minimum viewer TLS, HTTPS-only |
| **ALB / NLB** | HTTPS/TLS listener + security policy | Strong policy, optional mTLS trust store |
| **S3** | HTTPS endpoints | Bucket policy deny on `aws:SecureTransport=false` |
| **RDS / Aurora / Redshift / DynamoDB** | Client-side TLS | Region CA bundle, `sslmode=require` / `rds.force_ssl` |
| **App Mesh** | Envoy sidecar mTLS | Mesh TLS policy |
| **PrivateLink** | Private path on AWS backbone | Still terminate TLS at the endpoint |

## What gets tested

- **S3 in transit is `aws:SecureTransport`.** The correct control for requiring TLS to a bucket is a bucket policy deny on `aws:SecureTransport=false`, not a security group or a client setting alone.
- **Strong TLS policy on load balancers.** Enforcing a minimum TLS version and modern ciphers is choosing the restrictive ELB/NLB security policy. Legacy policies allow TLS 1.0 and weak ciphers.
- **Database TLS is client-enforced.** Requiring encrypted DB connections means configuring the client with the CA bundle and `sslmode=require`, or forcing it engine-side. TLS support existing does not mean it is enforced.
- **mTLS is a trust-store config, not a plain ACM cert.** Client-certificate authentication on ALB/API Gateway needs a CA trust store (commonly from ACM Private CA). A public ACM server cert alone does not authenticate clients.
- **PrivateLink is private, not automatically encrypted at the app layer.** If the requirement is confidentiality of the payload, you still run TLS to the endpoint. PrivateLink solves exposure and segmentation, not encryption by itself.
- **ACM for automated cert lifecycle.** Preferring ACM over bring-your-own certs is about auto-renewal and integration, and remember the CloudFront `us-east-1` region rule.

## Limitations

- Defaults are not always strict. Legacy TLS security policies permit old protocols and ciphers, so you must explicitly choose a modern policy.
- TLS support does not mean TLS enforcement, especially for databases, where an unconfigured client can still connect in plaintext unless the engine forces TLS.
- PrivateLink does not encrypt payloads on its own. It provides a private network path, and application TLS is still required for confidentiality.
- Public ACM certs cover the server side only. mTLS client authentication needs a separately managed CA trust store, typically backed by ACM Private CA, which is a paid service.
- CloudFront requires its cert in `us-east-1`, a common cross-Region misconfiguration.
- Encryption in transit protects the journey, not the stored bytes. It must be paired with encryption at rest, and it does nothing about an endpoint that is authorized but malicious.