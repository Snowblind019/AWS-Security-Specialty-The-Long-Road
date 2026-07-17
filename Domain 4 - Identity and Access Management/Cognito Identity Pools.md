# Amazon Cognito Identity Pools

An identity pool exchanges a proven identity for temporary AWS credentials. It takes a federated identity, from a Cognito user pool, a SAML IdP, an OIDC or social provider, or even an unauthenticated guest, and maps it to an IAM role, then has STS issue short-lived credentials scoped to that role. Those credentials let the client call AWS services directly: S3, DynamoDB, AppSync, IoT, and so on. This is not authentication. Identity pools do authorization at the AWS layer, which is the opposite side of the coin from user pools. On the SCS exam the whole topic hinges on one idea and a handful of dangerous misconfigurations around it. The thing to hold onto: user pools answer "who are you," identity pools answer "what are you allowed to touch in AWS," and the bridge between them is an IAM role plus STS.

## How it works

- **You create the pool with its accepted identity types.** Cognito user pool, SAML, OIDC/social, and an explicit choice of whether to allow unauthenticated guest access. You also attach the IAM role or roles that identities can be mapped to.
- **The client authenticates somewhere else first.** It signs in via a user pool, Google, Facebook, or a SAML IdP and receives an ID/access token or SAML assertion. The identity pool never handles the login itself.
- **The client presents the token to the pool.** It calls `GetId` to get an identity ID, then `GetCredentialsForIdentity`. The pool validates the token and resolves which IAM role the identity maps to.
- **STS issues temporary credentials.** Behind the scenes this is `AssumeRoleWithWebIdentity` (for OIDC/social/user-pool identities) or `AssumeRoleWithSAML` (for SAML). The client receives an access key ID, secret access key, and session token, typically valid for about an hour.
- **The client uses those credentials against AWS**, limited to whatever the mapped role's policy permits.

Enhanced versus basic flow is worth knowing: in the **enhanced (simplified) flow**, `GetCredentialsForIdentity` returns credentials and Cognito applies the role mapping for you; in the **basic (classic) flow**, the client gets an OpenID token from Cognito and calls `AssumeRoleWithWebIdentity` itself. Enhanced is the default and the recommended path.

## IAM role mapping options

| Mapping type | How the role is chosen | Risk |
|---|---|---|
| Default role | Every authenticated identity gets the same role | Usually ends up overly permissive; no differentiation between users |
| Rules-based mapping | Logic on token claims (email domain, group, IdP) picks the role | Safe when rules are precise; the recommended approach |
| Token-based (`custom:role`) | A claim in the token names the role to assume | Must be explicitly locked down, or a user who controls the claim escalates privilege |

Guest access sits alongside these: if unauthenticated identities are enabled, callers with no token at all can request the unauthenticated role's credentials.

## What gets tested

- **Identity pool equals authorization and temporary AWS credentials; user pool equals authentication.** This split is the single most tested idea. Any scenario needing temporary access to S3, DynamoDB, or another AWS service from a federated or mobile user is an identity pool answer.
- **The STS calls are `AssumeRoleWithWebIdentity` and `AssumeRoleWithSAML`.** The client-facing calls are `GetId` and `GetCredentialsForIdentity`. Recognizing these in a log or question stem tells you an identity pool issued the access.
- **Lock down token-based role mapping.** A `custom:role` claim that the client can influence is a privilege-escalation path unless the mapping rules validate it. Prefer rules-based mapping and never trust a client-supplied role claim blindly.
- **Default role is the lazy, dangerous choice.** Assigning all users one broad role is the classic overprivilege finding. Least privilege on mapped roles is the expected best practice.
- **Unauthenticated access is an open door if the guest role is broad.** Enabling guest identities plus a permissive default role means anyone can request working AWS credentials. Disable unauth unless the use case genuinely needs it, and keep its role minimal.
- **Issued credentials outlive token revocation.** Once STS hands out credentials, they are valid until expiry even if the source token is revoked. There is no revalidation mid-session, so short session durations are the control.
- **Audit visibility is limited by default.** CloudTrail shows `AssumeRoleWithWebIdentity`, `GetId`, and `GetCredentialsForIdentity`, but not a friendly "this human from this IdP" unless you correlate `principalId` and `userIdentity.sessionContext` or log the token subject separately.

## Limitations

- **No propagation of revoked identity.** The credentials are self-contained STS sessions; revoking the upstream token does nothing until the session expires. Keep sessions to an hour or less for sensitive access.
- **Default-role overprivilege.** The path of least resistance grants everyone the same role, which almost always ends up broader than any single user needs.
- **Client-influenced role claims are a trust boundary.** `custom:role` and similar must be constrained in mapping rules; treating the token as authoritative for role selection is an escalation risk.
- **Guest access is easy to leave wide open.** Unauthenticated identities plus a non-minimal role is a recurring real-world misconfiguration.
- **Thin native attribution.** The federation events do not name the originating human identity on their own, so tracing "who did what" requires deliberate extra logging and correlation.
- **Not always necessary.** Identity pools earn their place only when frontend, mobile, or federated identities need to make AWS SDK calls directly. If the backend holds the AWS credentials, you may not need one at all.