# AWS Certificate Manager (ACM)

ACM is AWS's managed service for provisioning, deploying, and renewing TLS/SSL certificates. It issues Amazon-signed public certificates trusted by browsers, hosts imported third-party certificates, and (through AWS Private CA) backs an internal PKI for service-to-service mTLS. The security win is operational: ACM auto-renews the certificates it issues so a cert never quietly expires on a Friday night and drops your HTTPS listener, and it keeps private keys non-exportable for ACM-issued public certs so the key material never leaves AWS. The thing to hold onto: ACM auto-renews only the certificates it issued (imported certs are your problem to rotate), CloudFront certs must live in `us-east-1`, and Private CA is the separate, paid path for internal trust and revocation.

## How it works

- **Public certificate issuance runs on domain validation.** You request a cert for a domain, then prove ownership by DNS (preferred, scriptable via Route 53) or email. Once validated, ACM issues an Amazon-signed cert and, as long as the DNS validation record stays in place, renews it automatically before expiry.
- **Deployment is integration, not file-copying.** ACM public certs attach directly to ALB and NLB, CloudFront, API Gateway custom domains, and App Runner. You never handle a `.pem`. The private key for an ACM-issued public cert is non-exportable, so it cannot be lifted out and reused off-AWS.
- **CloudFront has a region rule.** Any cert used on a CloudFront distribution, whether ACM-issued or imported, must be in `us-east-1`, because CloudFront is a global edge service that reads certs from that region. Regional services (ALB, API Gateway) use a cert in their own region.
- **Imported certificates are supported but manual.** You can import a third-party cert into ACM and attach it to services, but ACM will not renew it. Expiry tracking and rotation are entirely on you, which is the main reason to prefer ACM-issued certs where possible.
- **Private CA is the internal-trust arm.** AWS Private CA issues internal TLS certs for microservices, internal APIs, and IoT, with you controlling lifetimes, templates, and revocation via CRL/OCSP. This is the piece that enables internal mTLS and zero-trust service meshes, and unlike public ACM it is billed.
- **Lifecycle events are observable.** Issuance, renewal, and expiry surface through EventBridge and CloudWatch, and API calls log to CloudTrail, so you can alarm on an approaching expiry (critical for imported certs) or audit who requested what.

## ACM vs adjacent certificate paths

| Option | Renewal | Key exportable | Use it for |
|---|---|---|---|
| **ACM public cert** | Automatic (while DNS validation holds) | No | HTTPS on ALB/NLB, CloudFront, API Gateway |
| **ACM imported cert** | Manual, you rotate it | Yes (you imported it) | A cert issued outside AWS you must use on AWS |
| **AWS Private CA** | Automatic within the CA | Yes (internal certs) | Internal mTLS, service mesh, IoT, zero-trust |
| **IAM server certs** | Manual, legacy | Yes | Only where a service predates ACM support |

## What gets tested

- **Auto-renewal boundary.** ACM auto-renews certs it issued via valid domain validation. Imported certs do not auto-renew, so if the scenario is a third-party cert expiring, the fix is a manual rotation process or moving to an ACM-issued cert, not "ACM handles it."
- **CloudFront requires `us-east-1`.** A cert in any other region attached to CloudFront is the classic wrong config. Regional services use the cert in their region.
- **DNS vs email validation.** DNS validation is automatable and the preferred answer for scale and unattended renewal. Email validation is fragile and manual.
- **Public vs Private CA.** Browser-trusted, internet-facing endpoints use public ACM certs. Internal-only, mTLS, or zero-trust service-to-service traffic uses Private CA. Do not reach for a public cert on an internal mesh.
- **Non-exportable keys.** ACM-issued public cert private keys cannot be exported. If a requirement is to run the same cert on a non-AWS server (Nginx on-prem), that points to Private CA or an imported cert, not a public ACM cert.

## Limitations

- ACM does not auto-renew imported certificates. That rotation, and alerting on it, is yours to build.
- Private keys for ACM-issued public certs are non-exportable, so you cannot reuse an ACM public cert on infrastructure outside AWS.
- CloudFront only reads certs from `us-east-1`, which trips up multi-region deployments that forget to request or import the cert there.
- Public ACM certs only deploy to integrated AWS services. They are not general-purpose certs you download and install on arbitrary servers.
- AWS Private CA is billed per CA per month plus per issued certificate, so it is not the free default that public ACM certs are.
- Certificate revocation applies to Private CA (via CRL/OCSP). Public ACM certs rely on renewal and short-lived trust rather than a customer-managed revocation workflow.