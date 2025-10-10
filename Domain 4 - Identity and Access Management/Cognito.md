# Amazon Cognito

## What It Is

Amazon Cognito is AWS’s built-in service for managing user identity and authentication, especially in mobile, web, and SaaS apps.

There are two main components to understand:

| Component     | Purpose                                                                 |
|---------------|-------------------------------------------------------------------------|
| **User Pools**   | Manage user registration, login, password reset, MFA, etc.             |
| **Identity Pools** | Provide temporary AWS credentials to authenticated (or guest) users so they can access other AWS services (e.g. S3, DynamoDB) |

**User Pools = Who are you?**  
**Identity Pools = What can you access in AWS after login?**

---

## Cybersecurity And Real-World Analogy

**Cybersecurity analogy:**  
Think of Cognito User Pools as the login desk at your company — it checks your ID, lets you in, and hands you a badge (JWT token).

Then the Identity Pool is the person who assigns what rooms you’re allowed to go into, translating your badge into temporary door-access codes (STS credentials with IAM roles).

**Real-world analogy:**  
A theme park:

- User Pool is the ticket booth that verifies your purchase and prints your wristband.  
- Identity Pool is the backstage pass system that determines if your wristband also lets you into VIP areas.

---

## How It Works

### 1. User Pool

You create a User Pool with:

- Login options (username, email, phone)  
- Password policies  
- MFA configuration (SMS or TOTP)  
- Triggers/Lambda hooks (pre-signup, post-login, etc.)

Cognito handles:

- Registration, sign-in, verification  
- Account recovery  
- Token issuance (ID token, Access token, Refresh token)

### 2. App Client

- Your front-end app talks to the App Client — which initiates auth flows.  
- Tokens are returned to the app (typically JWTs).  
- **ID Token** has user claims (email, sub, etc.)  
- **Access Token** is used to call User Pool-protected APIs  

- **Refresh Token** is for long-term access

### 3. Identity Pool

- Optionally connects to User Pool, SAML IdP, or OpenID IdP (e.g. Google, Facebook)  
- Maps identities to IAM roles using role mapping rules  
- Returns temporary STS credentials so users can use AWS services

---

## Security Benefits

- Built-in support for MFA, TOTP, device tracking, and secure token refresh  
- No need to manage custom login backends or password databases  
- Built-in token revocation and token expiration  
- Secure federation support (SAML, OpenID Connect, social)  
- Scoped, time-limited AWS access via STS from Identity Pools  

## Security Pitfalls (Yes, Cognito Has Many)

- Tokens cannot be invalidated mid-session by default  
→ If an attacker gets a valid token, it’s valid until it expires (typically 1 hour)

- Refresh tokens can live for 30 days+ unless you rotate manually  
→ If refresh token is stolen, it can continuously regenerate access tokens

- Identity Pool permissions are mapped via IAM roles, so misconfiguration = privilege escalation  
→ Common mistake: mapping all users to a single "wide open" IAM role

- Complicated callback URLs and redirect URIs  
→ Misconfigurations in these = open redirect attacks, SSRF, or token leaks

- Hard to audit programmatically who has access to what  
→ Especially when federated SAML users are mapped dynamically

---

## Use Cases In Security Architectures

| Use Case                       | How Cognito Helps                                                                 |
|--------------------------------|-----------------------------------------------------------------------------------|
| Secure login for mobile apps   | User Pool handles auth securely with TOTP, SMS, password policies                |
| Federated enterprise auth      | Identity Pool integrates with SAML or OIDC to link corporate identities          |
| Temporary access to S3/DynamoDB| Identity Pool gives scoped STS credentials after user login                      |
| Protecting API Gateway endpoints| Use AWS_IAM or Cognito User Pool Authorizer in the gateway                      |
| Custom app logic on signup/login| Use Lambda triggers (e.g., deny users from banned email domains)               |

---

## Cognito And Token Flow

A standard login/token flow:

1. User logs in via UI  
2. App sends credentials to Cognito App Client  
3. Cognito returns:
    - ID Token (user attributes)  

    - Access Token (scopes & groups)  
    - Refresh Token (for re-auth)  
4. App uses:

    - ID Token for frontend profile info  
    - Access Token to call APIs behind API Gateway  

    - Refresh Token to get new tokens after expiration  
5. If using Identity Pool:

    - App exchanges the Cognito ID Token for STS credentials (IAM roles)

---

## CloudTrail & Logging Relevance

Cognito itself doesn’t log individual user logins in CloudTrail — but related services do:

| Event                        | Where to See It                                                      |

|------------------------------|-----------------------------------------------------------------------|
| Token generation             | App/CloudWatch logs if captured                                      |
| Role assumption via Identity Pool | CloudTrail (AssumeRoleWithWebIdentity)                          |
| App client misuse or abuse   | CloudTrail (if tied to API Gateway or Lambda)                        |

> If your app uses Cognito to give STS access to S3, look for `AssumeRoleWithWebIdentity` in CloudTrail as the bridge between the identity and the AWS action.

---

## Final Thoughts

Cognito is a solid middle-tier authentication system for AWS-native apps — not as flexible as Auth0 or Keycloak, but great when:

- You need fast, secure login with minimal setup  
- You want to delegate user identity and MFA management to AWS  
- You want to grant temporary AWS access based on identity  

But it’s **NOT trivial to configure correctly** — especially when mixing User Pools + Identity Pools + SAML + IAM.

If you’re building a modern app in AWS — especially with S3, API Gateway, and Lambda — Cognito can secure your front door without ever writing your own auth system.

