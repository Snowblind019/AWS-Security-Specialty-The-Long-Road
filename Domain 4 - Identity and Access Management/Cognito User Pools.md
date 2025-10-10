# Amazon Cognito User Pools

## What Is Cognito User Pools 

Amazon Cognito User Pools is a **fully managed identity directory** in AWS that lets you securely sign up, sign in, and manage users for web and mobile applications.

Think of it as your application’s **auth system-as-a-service** — one that handles:

- User registration and login  
- Password resets and multi-factor authentication (MFA)  
- OAuth 2.0, SAML, OpenID Connect integrations  
- Token issuance (ID token, access token, refresh token)  
- Attribute storage (email, phone, custom fields)  
- Account confirmation flows  
- Email and SMS verifications  

It’s a modern identity system that speaks **JWT**, understands **federated identity**, and is **secure by default** — but only if you configure it properly.

Why it matters: you no longer have to build your own login system from scratch or rely on third-party *SaaS* like Auth0. You can host your own secure, scalable identity *backend* inside AWS — integrated with **IAM**, API Gateway, **AppSync**, and more.

---

## Cybersecurity Analogy

*Cognito* User Pools is like a **high-security access checkpoint.**

It issues **temporary access badges (JWT tokens)**, controls who can enter your application, and enforces things like:

- **2FA on badge pickup** (MFA setup)  
- **Badge revocation rules** (token expiration and blacklisting)  
- **Background checks** (email/phone verification, password strength)  
- **Security desk logs** (*CloudTrail* logs of sign-in activity)

And here’s the thing: if you don’t install cameras (*CloudWatch Logs*), if you let people share badges (token misuse), or you don’t segment access zones (scopes, groups, custom claims), **your checkpoint becomes a liability**.

*Cognito* gives you the tools. **But you build the protocol.**

## Real-World Analogy

Let’s say **SnowyCorp** runs an internal app for employees to file security incident reports.

Instead of maintaining their own login database, Snowy sets up a **Cognito User Pool**.

- The HR team signs up users using email  
- MFA is enforced for everyone  
- App clients use the *Cognito Hosted UI* for login  
- After login, a **JWT** token is issued  
- The token is then attached to all API calls  

If Snowy adds support staff from an external contractor, they federate login using **Google SSO via OpenID Connect** — without creating native users in the user pool.

The **backend (AppSync)** checks token claims like:

- `email_verified`  
- `custom:department`  
- `cognito:groups`  

And enforces authorization with **VTL** templates that map permissions to claims.

All this happens **without touching IAM Users or managing static credentials.**

---

### 1. User Pool
- Stores user identities and attributes (email, phone, custom fields)  
- Handles login, registration, password reset  
- Enforces password policies, email/**SMS** verification  

### 2. App Clients
- Represent *frontend* applications (e.g., web, mobile)  
- Each client has its own settings: token expiration, refresh token validity, etc.  
- Can be marked as public (no secret) or confidential (with client secret)  

### 3. Tokens
- After successful login, *Cognito* issues **3 JWTs**:  
  - **ID Token** — contains user profile info (name, email, etc.)  
  - **Access Token** — used to access APIs, includes scopes  
  - **Refresh Token** — lets the app request new ID/Access tokens  

### 4. Hosted UI
- Optional login page hosted by AWS  
- Supports **OAuth 2.0** flows (Authorization Code, Implicit)  
- Can be customized with your logo/colors  

### 5. Triggers
- Lambda functions that plug into lifecycle events:  
  - *Pre Sign-up* (e.g., prevent signups from banned domains)  
  - *Post Confirmation* (e.g., welcome email)  
  - *Pre Token Generation* (e.g., add custom claims)  
  - *Post Authentication* (e.g., log sign-ins)  

### 6. Federation
- Supports **SAML 2.0, OpenID Connect**, and social logins (Google, Facebook, Apple)  
- Federated identities are **linked to Cognito users with a shared ID**

---

## Pricing Models

*Cognito* User Pools pricing is based on:

| **Tier**       | **Description**                                                                 |
|----------------|----------------------------------------------------------------------------------|
| Free Tier      | 50,000 monthly active users (**MAUs**) — generous for small teams               |
| MAU-Based      | After free tier, charged per 1,000 **MAUs**                                     |
| Federation     | Separate pricing for **SAML/OIDC** users (billed per **MAU**)                    |
| MFA SMS        | Charged separately per message (Amazon **SNS** rates)                           |

**Cost surprise warning:** If you enable **SMS-based** MFA globally and don’t restrict *geos*, you might see a **massive SMS bill.** Use **TOTP** (like Google *Authenticator*) when possible.

---

## Other Explanations / Gotchas

- **Tokens are not revocable** by default. You can set short expiration windows (e.g., 5 min access tokens) or use *Pre Token Generation* triggers to insert session-specific values (e.g., a logout flag).  
- **Refresh tokens last up to 10 years** by default. Set a shorter expiration (like 30 days) unless you *really* need persistence.  
- **Groups ≠ Roles** — *Cognito* User Pool groups are arbitrary strings. You can map them to roles manually in your *backend* or via claims in *Pre Token Generation*.  
- **Don’t store secrets in custom attributes.** Custom attributes are exposed in plaintext via the ID token — *not a secure place to store app secrets*.  
- **Hosted UI is public** unless you configure it tightly — it can be abused if you don’t restrict callback URLs and OAuth scopes properly.

---

## Real-Life Example: Blizzard Developer Portal

Blizzard wants developers to register apps that use their in-game event API. They need:

- Secure user sign-up  
- **OAuth 2.0** with Authorization Code flow  
- Scoped access tokens  
- MFA for admin logins  

**They build:**

- *Cognito* User Pool with App Client  
- *Hosted UI* for login (Authorization Code flow)  
- OAuth scopes like `read:events`, `write:characters`  
- Lambda *Pre Token Generation* trigger to add scopes and tenant IDs  
- *CloudTrail* logging of every login event  
- Custom domain for the Hosted UI (e.g., `auth.blizzard.dev`)  

**They enforce:**

- `cognito:groups = developers, admins, reviewers`  
- Token expiration = 5 minutes  
- Refresh tokens expire after 14 days  
- IP restriction on admin login via Lambda  

Now, devs authenticate securely, and Blizzard’s **backend checks the access token against required scopes** — **no API call is processed unless claims match.**

---

## Final Thoughts

*Cognito* User Pools are powerful — but like **IAM**, they’re only as secure as your implementation.

The biggest mistake teams make is **treating Cognito like a plug-and-play login box**, then forgetting to:

- Harden token lifespans  
- Enforce MFA properly  
- Monitor sign-in activity with *CloudTrail* and *GuardDuty*  
- Limit scopes, groups, and attributes  
- Rotate app client secrets (for confidential clients)  

*Cognito* gives you **OAuth, OpenID Connect, JWT, MFA, user management, federation** — all under one roof.

But unless you secure the roof, the whole house leaks.

If you're going to use *Cognito* for production, treat it like your front gate. Set guards, log entries, limit who gets a key, and monitor the flow.

**Security doesn't end at login. That's just where it begins.**

