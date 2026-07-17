# Amazon Cognito User Pools

A user pool is a fully managed identity directory that handles authentication for web and mobile apps. It does sign-up, sign-in, password resets, MFA, email and phone verification, attribute storage, and federation to SAML, OIDC, and social providers, and on a successful login it issues three JWTs. It replaces building your own login system or leaning on a third-party SaaS, and it plugs into API Gateway, ALB, and AppSync as a token issuer and authorizer. This is the authentication half of Cognito: it proves who a user is and hands back tokens. On the SCS exam the recurring theme is that the pool is only as secure as its configuration, and the tested details cluster around tokens, MFA, federation, and where claims can and cannot be trusted. The thing to hold onto: a user pool authenticates users and issues JWTs; app clients define how each app gets those tokens, and an identity pool is what later trades a token for AWS credentials.

## How it works

- **The pool stores identities and attributes** and owns the account lifecycle: registration, login, password reset, password policy, and email/SMS verification.
- **App clients are the per-app front doors.** Each represents one application, carries its own token settings, and is public (no secret) or confidential (with secret).
- **A successful login yields three JWTs.** The ID token carries identity claims, the access token carries scopes and groups for authorizing API calls, and the refresh token mints new ID and access tokens without re-login.
- **The Hosted UI is an optional AWS-hosted login page** supporting OAuth2 flows, attachable to a custom domain and brandable, but public-facing by default.
- **Lambda triggers hook the lifecycle:** Pre Sign-up (block banned domains), Post Confirmation (welcome flows), Pre Token Generation (inject custom claims and scopes), and Post Authentication (log sign-ins).
- **Federation links external identities to a pool user.** SAML 2.0, OIDC, and social logins are supported, and each federated identity is tied to a Cognito user through a shared identifier.

## The three tokens

| Token | Purpose | Exam-relevant note |
|---|---|---|
| ID token | Identity and profile claims (OIDC) | Do not use it to authorize API calls; it describes the user, it is not an access grant |
| Access token | Authorizing API/resource calls; carries scopes and `cognito:groups` | This is what a backend or API Gateway authorizer should validate for authorization |
| Refresh token | Obtain new ID and access tokens without re-authenticating | Long lifetimes equal long sessions; default 30 days, configurable up to 10 years |

## What gets tested

- **User pool is authentication; identity pool is authorization to AWS.** The pool issues JWTs and proves identity. It does not, by itself, grant access to S3 or DynamoDB. That requires an identity pool exchanging the token for STS credentials.
- **Use the right token.** The access token authorizes API calls via scopes and groups; the ID token is for identity claims only. Authorizing an API off the ID token is a planted mistake.
- **Prefer TOTP over SMS MFA.** SMS is vulnerable to SIM-swap and carries per-message SNS cost that can spike if enabled globally without geo limits. TOTP (authenticator app) is the stronger, cheaper answer. Advanced security features add compromised-credential detection and adaptive/risk-based auth.
- **`cognito:groups` are labels, not IAM roles.** Groups are arbitrary strings. They only translate to AWS permissions through identity-pool role mapping or explicit backend logic, never automatically.
- **Pre Token Generation is how you add claims.** Custom scopes, tenant IDs, and session flags are injected there, which is the answer for scenarios needing extra authorization context in the token.
- **Tokens are not revocable by default.** A JWT stays valid until it expires. The token revocation feature invalidates refresh tokens only; access and ID tokens live out their TTL. Short access-token lifetimes are the control for sensitive apps.
- **Custom attributes are plaintext in the ID token.** Never store secrets in them; anyone holding the token can read them.
- **The Hosted UI is a public surface.** Loose callback URLs and broad OAuth scopes turn it into an open-redirect and token-leak risk, so callback URLs must be exact and scopes minimal.
- **Cognito is an authorizer for other services.** API Gateway has a native Cognito user-pool authorizer, and ALB can authenticate users against a pool. Both validate the token before the request proceeds.

## Limitations

- **No pre-expiry revocation of issued tokens.** Revocation only kills refresh tokens, and only when enabled. Access and ID tokens remain valid for their full lifetime, so short TTLs are the real mitigation.
- **Groups do not map to AWS permissions on their own.** Without an identity pool or backend logic, `cognito:groups` is just a string in a claim.
- **Custom attributes offer no confidentiality.** They ride in the token in the clear and are unsuitable for anything sensitive.
- **Public Hosted UI.** Left loosely configured, it is abusable through wildcard callbacks and over-broad scopes.
- **SMS MFA cost and weakness.** Global SMS MFA without geo restrictions invites both a large bill and SIM-swap exposure.
- **Authentication only.** A user pool grants no AWS resource access by itself; direct AWS SDK access for federated or frontend users needs an identity pool.
- **Secure-by-default is overstated.** MFA, advanced security, short token lifetimes, and monitoring are opt-in. Out of the box the pool leaves several of the tested hardening controls off.