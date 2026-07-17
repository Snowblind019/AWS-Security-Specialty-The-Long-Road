# AWS STS

Security Token Service is the engine that issues temporary AWS credentials. Instead of long-lived access keys, STS hands out short-lived credentials, an access key ID, a secret access key, and a session token, that carry a role's permissions and expire automatically, typically anywhere from 15 minutes to 12 hours depending on the call. It is the machinery beneath nearly every secure AWS pattern: role assumption, cross-account access, SAML and OIDC federation, role chaining, just-in-time elevation, and the roles that Lambda, EC2, and ECS run as. Whenever a workload or federated user acts without a static key, STS minted the credential. On the SCS exam it shows up as the API family behind federation and cross-account, plus a handful of trust controls (external ID, source identity, session tags) that are frequently tested. The thing to hold onto: STS turns "I am trusted to assume this role" into a scoped, time-boxed session, and the trust policy on the target role is what decides whether it will.

## How it works

- **Temporary credentials are three parts.** Access key ID, secret access key, and session token. All three must be presented; the session token is what marks them as STS-issued and time-limited.
- **The assume-role API family picks the flow.** `AssumeRole` for an AWS principal (same or cross-account). `AssumeRoleWithSAML` for SAML IdP federation. `AssumeRoleWithWebIdentity` for OIDC/web identity (Cognito identity pools, GitHub Actions, EKS IRSA). `GetSessionToken` for an IAM user, mainly to attach MFA. `GetFederationToken` is the legacy federation path.
- **The target role's trust policy gates it.** It must name the allowed principal and the correct action (`sts:AssumeRole`, `sts:AssumeRoleWithSAML`, `sts:AssumeRoleWithWebIdentity`), plus `sts:TagSession` or `sts:SetSourceIdentity` when those features are used.
- **Session duration is bounded by the role.** `DurationSeconds` in the call cannot exceed the role's `MaxSessionDuration` (default 1 hour, up to 12). Role chaining is capped at 1 hour and cannot use the longer maximum.
- **Everything is logged.** CloudTrail records the assume call with the source identity, session name, and external ID, and downstream API calls carry the assumed-role session context, giving auditability across account and federation boundaries.

## The STS API family

| API | Who calls it / identity source | Use case |
|---|---|---|
| `AssumeRole` | An existing AWS principal (user, role, service) | Cross-account and in-account role switching |
| `AssumeRoleWithSAML` | User federated through a SAML 2.0 IdP | Enterprise SSO (AD FS, Okta) into a role |
| `AssumeRoleWithWebIdentity` | OIDC token from a web identity provider | Cognito identity pools, GitHub Actions, EKS IRSA |
| `GetSessionToken` | An IAM user (optionally with MFA) | Temporary creds for an IAM user, MFA enforcement |
| `GetFederationToken` | An IAM user acting as a federation broker | Legacy federation for non-AWS users |

## What gets tested

- **Match the API to the identity.** SAML assertion means `AssumeRoleWithSAML`; an OIDC token (GitHub, EKS, Cognito) means `AssumeRoleWithWebIdentity`; an AWS principal crossing accounts means `AssumeRole`. IAM Roles Anywhere does not use an STS assume call directly; it has its own `CreateSession` endpoint that returns STS credentials.
- **External ID stops the confused deputy.** When a third party assumes a role in your account, they pass a unique `ExternalId` and your trust policy conditions on `sts:ExternalId`. This prevents another of that third party's customers from tricking them into assuming your role. It is a classic exam item.
- **Source identity is the sticky audit trail.** `sts:SetSourceIdentity` stamps an identifier that persists across role chaining and cannot be changed by the assumed session, so `aws:SourceIdentity` ties every downstream action back to the original human.
- **Session tags drive ABAC.** `sts:TagSession` passes principal tags into the session, and transitive tags carry through role chaining, so policies can match `aws:PrincipalTag` to `aws:ResourceTag`.
- **MaxSessionDuration lives on the role.** The caller cannot exceed it, and role chaining is capped at 1 hour regardless. This is separate from MFA, which is enforced with the `aws:MultiFactorAuthPresent` condition and by passing an MFA serial and token code.
- **Regional endpoints are preferred.** Use regional STS endpoints; tokens from the legacy global endpoint may not work in opt-in Regions unless the account is configured for it.

## Limitations

- **No automatic mid-session revocation.** Issued credentials stay valid until they expire even if the role's permissions change. To kill active sessions you attach a deny policy conditioned on `aws:TokenIssueTime` (the revoke-older-sessions pattern), since there is no one-click revoke.
- **Role chaining costs you.** Chaining caps the session at 1 hour, forfeits the role's longer max duration, and drops non-transitive session tags at each hop.
- **`GetSessionToken` is limited.** It is mostly for adding MFA to an IAM user and cannot be used to call most IAM and STS operations within that session.
- **STS trusts the upstream, it does not authenticate it.** For federation, STS relies on the IdP's assertion or token and on your trust policy conditions; a weak IdP or loose trust policy undermines the whole session.
- **Session tag constraints.** There are size and count limits, and the transitive-versus-non-transitive distinction matters when chaining, which is easy to get wrong.
- **Source-note corrections.** There is no `sts:AssumeRoleWithJWT` API; GitHub Actions and Kubernetes use `AssumeRoleWithWebIdentity`, and Roles Anywhere uses its own `CreateSession`. And MFA is not enforced via `sts:TagSession` (that is for session tags); it is enforced with the `aws:MultiFactorAuthPresent` condition key.