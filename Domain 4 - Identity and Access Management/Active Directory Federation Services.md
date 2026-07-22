# Active Directory Federation Services (AD FS)

AD FS is Microsoft's identity-federation service that lets users authenticate with their existing on-premises Active Directory credentials and receive access to external systems (AWS, Salesforce, Microsoft 365) through **claims-based SAML 2.0** single sign-on, with no separate password. In AWS, AD FS is the on-prem **identity provider (IdP)** that federates into IAM roles: users authenticate at AD FS, get a signed SAML assertion, and exchange it for temporary credentials via STS. The thing to hold onto: AD FS is one instance of the general **IAM SAML federation** pattern (the IdP authenticates, AWS trusts a signed assertion, `AssumeRoleWithSAML` returns temporary credentials), so for the exam the mechanics of the SAML trust and role mapping matter more than AD FS itself, and the modern AWS-recommended alternative is **IAM Identity Center**.

## How it works

- **Trust setup (one time).** Create a SAML IdP in IAM from the AD FS metadata, and create IAM roles whose trust policy allows `sts:AssumeRoleWithSAML` for that SAML provider. Metadata and signing certificates are exchanged so AWS can verify assertion signatures.
- **Login flow.** User hits the AD FS portal, AD FS authenticates against Active Directory, and issues a **signed SAML assertion** with claims (NameID, `RoleSessionName`, and the `Role` attribute listing the role ARN and SAML-provider ARN). The browser posts the assertion to the AWS sign-in endpoint, which calls **`AssumeRoleWithSAML`** on STS. STS validates the assertion against the trusted IdP and returns **temporary credentials** for the chosen role.
- **Role mapping.** AD groups map to IAM roles via the SAML Role attribute (for example `CloudAdmins -> AdminRole`, `DevOps -> ReadOnlyRole`), so directory group membership drives AWS permissions. No IAM users are created for these people.
- **Trust-policy conditions.** Scope the role trust with `SAML:aud = https://signin.aws.amazon.com/saml`, and require MFA with `aws:MultiFactorAuthPresent = true` (effective only if the IdP includes the auth-context in the assertion).
- **Session and audit.** Assertions are short-lived; federated sessions appear in **CloudTrail** as `AssumeRoleWithSAML` with the configured role session name. Optionally enable SAML assertion encryption so the assertion stays encrypted in transit and STS decrypts with your uploaded key.
- **Hardening.** Treat AD FS like a domain controller: TLS everywhere, patched and firewalled servers, MFA at the IdP, periodic signing-key/cert rotation with trust updates in AWS, and precise (non-wildcard) role trusts.

## AD FS/SAML federation vs the alternatives

| | IAM SAML federation (AD FS) | IAM Identity Center | IAM OIDC federation |
|---|---|---|---|
| Protocol | SAML 2.0 | SAML/OIDC (built on federation) | OpenID Connect |
| Best for | Existing AD FS, regulated/legacy, single-account granular control | New deployments, multi-account SSO, permission sets | Web/mobile and workloads (GitHub Actions) |
| Multi-account | Per-account role trust | Native across the org | Per-account |
| AWS recommendation | Valid, but plan migration | Recommended default | For OIDC workloads |
| Credentials | Temporary via AssumeRoleWithSAML | Temporary, managed | Temporary via AssumeRoleWithWebIdentity |

## What gets tested

- **SAML federation replaces IAM users for humans.** The best practice is federating workforce users through an IdP, not creating individual IAM users. Credentials never touch AWS and sessions are temporary. AD FS is the on-prem SAML IdP for this.
- **The AssumeRoleWithSAML flow.** Know the chain: IdP authenticates, issues signed assertion, AWS sign-in posts it, STS calls `AssumeRoleWithSAML`, temporary credentials returned. The API and the SAML-provider + role ARNs in the assertion are the tested details.
- **IAM Identity Center is the modern default.** For new or multi-account setups, IAM Identity Center (with an external SAML IdP or AD) is AWS's recommendation, giving centralized permission sets across the org. Direct IAM SAML federation persists for legacy, regulated, or single-account granular cases.
- **Scope the role trust.** `SAML:aud` and MFA conditions plus precise role ARNs prevent any assertion from assuming any role. A wildcard SAML role trust is a top finding.
- **MFA at the IdP.** AWS trusts the IdP's authentication strength, so MFA belongs at AD FS; the `aws:MultiFactorAuthPresent` condition only works if the assertion carries the auth context.
- **The IdP is the crown jewel.** If AD FS is compromised, an attacker mints assertions and gains federated AWS access. Harden and monitor it like a domain controller; this is the single point of federation risk.
- **Audit via CloudTrail.** Federated logins surface as `AssumeRoleWithSAML`; alerting on these events is the standard detection control.

## Limitations

- AD FS is a single, self-managed point of federation. Compromise or outage of the IdP breaks or exposes all federated AWS access, so it carries domain-controller-level risk and operational burden.
- Direct IAM SAML federation is per-account: each account needs its own SAML provider and role trusts, which does not scale to many accounts the way IAM Identity Center permission sets do.
- AWS only trusts the assertion's signature and claims; it does not re-verify the user. Weak IdP authentication (no MFA) weakens the whole chain regardless of AWS-side controls.
- Assertion replay and over-long validity are real risks; assertions must be signed, short-lived, and audience-restricted, and misconfigured expiry or wildcard trusts undermine the model.
- SAML is for browser/workforce SSO. Non-AWS workloads and modern app auth (GitHub Actions, mobile) use **OIDC** federation instead; AD FS/SAML is not the right tool there.
- Certificate and key rotation must be coordinated with AWS trust updates, or a rotated AD FS signing cert breaks federation until the IdP metadata is refreshed in IAM.