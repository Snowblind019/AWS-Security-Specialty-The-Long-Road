# Amazon Cognito (Overview)

Amazon Cognito is AWS's managed identity and authentication service for web, mobile, and SaaS apps. It has two components that people constantly conflate, and keeping them straight is the whole game. User pools handle authentication: registration, login, password policy, MFA, federation, and issuing JWTs. Identity pools handle authorization to AWS: they take a proven identity and exchange it, through STS, for temporary IAM credentials that let the client call S3, DynamoDB, and other services. You can use either alone or chain them, and most real designs chain them. On the SCS exam Cognito questions almost always come down to knowing which component does what, how a token flows from login to AWS access, and which misconfiguration opens the door. The thing to hold onto: user pools answer "who are you," identity pools answer "what can you touch in AWS," and an ID token is the bridge between them.

## How it works

- **The user pool authenticates.** You configure login options, password policy, MFA (SMS or TOTP), and Lambda triggers, and Cognito handles registration, sign-in, recovery, and token issuance.
- **The app client is the app's entry point.** The frontend talks to an app client, which runs the auth flow and returns tokens. The ID token carries user claims, the access token authorizes API calls with scopes and groups, and the refresh token renews the other two.
- **The identity pool authorizes to AWS, optionally.** It connects to a user pool, a SAML IdP, or an OIDC/social provider, maps the identity to an IAM role via role-mapping rules, and returns temporary STS credentials.
- **End to end:** the user logs in, the app client returns the three JWTs, the app uses the ID token for profile display and the access token to call APIs behind API Gateway, and if AWS resource access is needed, the app hands the token to the identity pool and gets back scoped STS credentials.

## User pools vs identity pools

| Dimension | User pools | Identity pools |
|---|---|---|
| Question answered | Who are you | What can you access in AWS |
| Function | Authentication | Authorization to AWS resources |
| Output | JWTs (ID, access, refresh) | Temporary STS credentials tied to an IAM role |
| Bridge API | `InitiateAuth` and friends | `AssumeRoleWithWebIdentity` / `AssumeRoleWithSAML` |
| Typical use | Secure login, MFA, federation for an app | Scoped S3/DynamoDB/AppSync access for a logged-in or guest user |
| Needed for AWS access | No, tokens only | Yes, this is the component that yields AWS credentials |

## What gets tested

- **The authN/authZ split is the core idea.** Login, MFA, and JWT issuance are user pools. Temporary AWS credentials are identity pools. A scenario about accessing an AWS service after login points at an identity pool; a scenario about sign-in, MFA, or federation points at a user pool.
- **`AssumeRoleWithWebIdentity` is the bridge in the logs.** When Cognito grants AWS access, this is the STS call that shows up in CloudTrail and ties the identity to the AWS action. It is the reliable signal that an identity pool issued credentials.
- **Protecting API Gateway has two answers.** Use the Cognito user-pool authorizer to validate the access token, or `AWS_IAM` auth backed by identity-pool STS credentials. Know which fits the scenario.
- **Role mapping is a privilege-escalation surface.** Mapping every user to one broad IAM role, or trusting a client-controlled role claim, is the classic overprivilege finding. Rules-based mapping and least privilege are the expected answers.
- **Lambda triggers add custom logic.** Pre sign-up to block banned domains, Pre Token Generation to add claims and scopes. These are the answer for custom signup or authorization logic.
- **CloudTrail visibility is partial.** Cognito management API calls are logged, and identity-pool role assumption appears as `AssumeRoleWithWebIdentity`, but individual user sign-ins are not in default CloudTrail management events. Capturing them requires user-pool advanced security logging or the user-activity logging feature to CloudWatch/S3.

## Limitations

- **Issued JWTs cannot be invalidated mid-session.** A stolen access or ID token is usable until it expires (about an hour by default). Token revocation applies to refresh tokens only, so short access-token TTLs are the mitigation.
- **Refresh tokens are long-lived.** Default 30 days and configurable up to 10 years, so a stolen refresh token keeps minting access tokens until it expires or is revoked. Keep the lifetime tight.
- **Identity-pool role mapping is easy to get wrong.** A single wide-open role, or an unvalidated token-based role claim, turns login into privilege escalation.
- **Callback and redirect URIs are fragile.** Loose or wildcard URIs invite open-redirect, token-leak, and related abuse. They must be exact.
- **Attribution is hard.** Federated SAML users mapped dynamically, plus thin native sign-in logging, make it difficult to answer "who has access to what" without deliberate extra logging and correlation.
- **Correct configuration is nontrivial.** The moment you mix user pools, identity pools, SAML, and IAM role mapping, the secure-by-default assumption breaks down; the hardening controls are opt-in.