# Amazon Cognito App Clients

An App Client is the per-application configuration object attached to a Cognito User Pool. A user pool by itself is just a directory of users; the app client is what lets a specific frontend, mobile app, or backend service actually authenticate against it. It defines which auth and OAuth2 flows are allowed, whether a client secret is required, which token types are issued and how long they live, and where Cognito redirects after sign-in and sign-out. In OAuth/OIDC terms the app client is the relying-party registration between your app and the user pool acting as IdP. On the SCS exam it matters because the app client is the trust boundary between application and identity provider, and the common exam traps are all misconfigurations here: secrets embedded in frontend code, wildcard redirect URIs, and refresh tokens that live too long. The thing to hold onto: one user pool, many app clients, each app client is an independently scoped set of rules for how one app is allowed to get tokens.

## How it works

- **The user pool starts empty of clients.** To authenticate any app against it you create at least one app client, and each app gets its own so their trust levels stay isolated.
- **Each client has a Client ID, and optionally a Client Secret.** The ID identifies the client; the secret, when present, makes it a confidential client used in server-side flows.
- **The client controls the token contract.** ID, access, and refresh token lifetimes, allowed OAuth2 grant types, allowed scopes, callback and logout URLs, whether token revocation is enabled, and which custom auth flows are permitted.
- **Apps integrate the Client ID three ways:** the Cognito SDKs (SRP and direct auth APIs), the Hosted UI via redirect, or a raw OAuth2 grant flow against the pool's domain.
- **Tokens come out of the flow as JWTs.** The ID token carries identity claims (OIDC), the access token carries scopes for authorizing API calls, and the refresh token is used to mint new ID and access tokens without re-login.

Token lifetime defaults, all configurable:

| Token | Default | Configurable range |
|---|---|---|
| ID token | 1 hour | 5 min to 1 day |
| Access token | 1 hour | 5 min to 1 day |
| Refresh token | 30 days | 1 hour to 10 years |

## Public vs confidential clients

| Dimension | Public client | Confidential client |
|---|---|---|
| Client secret | No secret | Has a client secret |
| Where it runs | SPA, mobile app, anything on the user's device | Backend service, server-to-server |
| Recommended flow | Authorization Code with PKCE | Authorization Code, or Client Credentials for machine-to-machine |
| Why | Secret cannot be protected in code the user can inspect | Secret can be stored server-side and used to authenticate the client |
| Risk if misused | Embedding a secret here leaks it | Exposing the secret in any client-side asset defeats it |

## What gets tested

- **Public client means no secret; confidential means a secret.** A secret in a mobile app or SPA is a wrong answer every time, because anything shipped to the user's device can be extracted. Public clients use PKCE to protect the Authorization Code flow instead of a secret.
- **Know the OAuth2 flows.** Authorization Code (plus PKCE for public clients) is the secure default. Implicit is legacy and returns tokens in the URL fragment, so treat it as the insecure option. Client Credentials is machine-to-machine with no user and no ID token.
- **User Pools versus Identity Pools is the big distinction.** App clients live on user pools, which handle authentication and issue JWTs. Identity pools do authorization: they exchange a token for temporary AWS IAM credentials via STS. If a scenario needs temporary AWS access to S3 or DynamoDB, that is an identity pool, not an app client setting.
- **Use the right token for the right job.** The access token carries scopes and is what authorizes API calls; the ID token is about identity and should not be used as an API authorizer. Mixing them up is a planted error.
- **Token revocation must be enabled to kill sessions.** JWTs are self-contained and valid until expiry, so you cannot invalidate an already-issued access or ID token mid-life. Enabling revocation lets you invalidate refresh tokens on logout, which is why short access/ID token TTLs matter for sensitive apps.
- **Redirect URIs must be exact.** Wildcard callback URLs are an open-redirect and token-leak risk; the exam wants precise, registered URIs.
- **Advanced security features** (compromised-credential detection, adaptive authentication, MFA) are configured at the pool and client level and are the answer for scenarios about credential stuffing or risky sign-ins.
- **Auditing is in CloudTrail.** `CreateUserPoolClient`, `UpdateUserPoolClient`, `AdminInitiateAuth`, `InitiateAuth`, and `RevokeToken` events carry the `client_id` and `auth_flow`, which is how you trace anomalous or brute-force login behavior back to a specific client.

## Limitations

- **Issued JWTs cannot be revoked before expiry.** Revocation only invalidates refresh tokens, and only when the feature is enabled. Access and ID tokens stay valid for their full TTL no matter what, so a stolen token is usable until it expires. Short TTLs are the mitigation.
- **A client secret is not a control for public clients.** It cannot be hidden in frontend or mobile code, so it provides no real protection there. PKCE is the correct mechanism for those clients.
- **Long refresh token lifetimes are a standing liability.** A 10-year refresh token equals a near-permanent session if stolen, so lifetime must match the app's real session and risk model.
- **App clients are scoped to a single user pool.** One client cannot span pools; each pool needs its own client configuration.
- **Implicit flow exposure.** Because it returns tokens in the URL fragment, tokens can leak through browser history, referrers, and logs. It is deprecated in favor of Authorization Code with PKCE.