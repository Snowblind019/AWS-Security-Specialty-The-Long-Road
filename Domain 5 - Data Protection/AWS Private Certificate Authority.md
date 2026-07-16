# AWS Private Certificate Authority

A managed private certificate authority for issuing internal X.509 certificates — the cases public CAs won't or shouldn't cover: internal TLS, mutual TLS between services, code signing, device identity, and certificate-based user authentication. The certificates it issues are trusted only within your own PKI, not by public browsers.

The pairing to keep straight is Private CA vs ACM. ACM issues and auto-renews public certificates for free and deploys them to ALB/CloudFront/API Gateway; Private CA stands up your own internal CA hierarchy and issues private certs (for which ACM can still handle lifecycle in general-purpose mode). Public-facing endpoint points to an ACM public cert; an internal/private name or mTLS points to Private CA.

## How it works

- You create a CA as a **root** or **subordinate**. A subordinate can chain to an AWS root or to your existing on-prem/external root by signing its CSR, so Private CA slots underneath an established corporate PKI.
- **Two modes, set at creation and not switchable:**
  - **General-purpose** — any validity period, $400/mo per CA. ACM can issue and auto-renew from it.
  - **Short-lived certificate mode** — certs valid up to 7 days, $50/mo per CA, and must be the last CA in the hierarchy. ACM cannot issue from it.
- Per-certificate cost: general-purpose is tiered by monthly volume per Region ($0.75 → $0.35 → $0.001); short-lived is a flat ~$0.058 per cert.
- **Revocation**: CRLs (published to an S3 bucket) and/or OCSP (managed by AWS, billed per request). Short-lived certs sidestep revocation entirely by expiring fast.
- **Cross-account**: share a CA through RAM so member accounts issue certs from one central CA; the certificate is generated locally in the requesting account.
- **Connectors** (Kubernetes, Active Directory, SCEP) let Private CA replace existing enterprise CAs, at no extra charge beyond the CA and the certs.
- The CA private key is generated and stored in an AWS-managed, FIPS-validated HSM; you never handle it. Access is governed by IAM; issuance and management are logged in CloudTrail.

## Private CA vs ACM (public)

| | AWS Private CA | ACM (public) |
|---|---|---|
| Cert trust | Private, internal only | Publicly trusted |
| Cost | $400 or $50/mo per CA + per cert | Free public certs |
| Names | Any internal name (e.g. api.internal) | Must pass domain validation |
| Use | Internal TLS, mTLS, code signing, device ID | Public ALB/CloudFront/API Gateway |
| Renewal | ACM-managed (general-purpose mode) | ACM-managed |

## What gets tested

- Private CA is for private/internal certs. If the scenario is a public website or endpoint, the answer is an ACM public cert, not Private CA.
- Short-lived mode pairs with IAM Roles Anywhere, EKS workloads, and WorkSpaces certificate-based auth: certs expire quickly instead of relying on revocation. The security argument is "expiry over revocation."
- Mode is fixed at creation — you cannot convert general-purpose to short-lived or back.
- ACM cannot issue from a short-lived-mode CA. If a question wants ACM lifecycle management, the CA must be general-purpose.
- Revocation is CRL (S3) or OCSP (managed, billed). Know both exist.
- Centralized PKI across accounts means sharing the CA via RAM, not one CA per account.
- Subordinate CAs can chain under an existing external root, so you keep your corporate root and place AWS underneath it.
- Cost awareness: a CA bills monthly whether or not you issue certs ($400 general-purpose), so leaving an unused general-purpose CA running is a real, testable cost mistake.
- The CA private key lives in an AWS-managed FIPS-validated HSM; access via IAM, audit via CloudTrail.

## Limitations

- Regional service — for multi-Region you run a CA per Region (or share via RAM); certs and CRLs don't span Regions automatically.
- Not publicly trusted; clients must trust your CA chain.
- General-purpose CAs are expensive to idle at $400/mo.
- Short-lived mode is restricted: certs of 7 days or fewer, must be a leaf CA, and no ACM issuance.
- You manage distribution and trust of the CA cert to clients, unless you use a connector.