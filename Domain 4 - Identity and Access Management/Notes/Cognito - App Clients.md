# Amazon Cognito

## What It Is

An App Client in Amazon Cognito is like a login portal configuration for your app.  
It defines how users can interact with your User Pool — what flows are allowed, whether refresh tokens are issued, how long tokens last, which OAuth grants are supported, and whether secret-based validation is required.

Each frontend/mobile/backend app that needs to authenticate users must be configured as an App Client. This isn’t just for UI apps — even your API clients may be App Clients.

**TL;DR:** App Clients are the configuration objects that tell Cognito:

- Who’s allowed to sign in  
- What kind of tokens they can get  
- Whether they need a client secret  
- Whether refresh tokens are allowed  
- Which OAuth2 flows (Auth Code, Implicit, etc.) are supported  

---

## Cybersecurity And Real-World Analogy

**Cybersecurity Analogy**  
Think of App Clients like the entry points to your login system. Each client has a unique identifier (and optionally a secret), and defines how users from this client can interact with your identity provider.

It’s like configuring trust relationships in OAuth/OIDC between a relying party (your app) and the identity provider (Cognito User Pool).

**Real-World Analogy**  
Imagine your building has multiple entrances:

- Front Door (Web App)  
- Side Door (Mobile App)  
- Emergency Door (Admin CLI)  

Each door has rules: who can enter, what kind of badge they get, and how long it lasts.  
Those rules per entrance are the App Client settings.

---

## How It Works

When you create a Cognito User Pool, it’s empty.  
To interact with it, you must create one or more App Clients.

Each App Client:

- Has a unique Client ID  
- Optionally has a Client Secret (used in confidential flows)  
- Controls:
    - Token expiration durations (ID, access, refresh)  
    - OAuth2 settings (redirect URIs, grant types)  
    - Whether client secret is required  
    - Whether token revocation is supported  
    - Whether signing out invalidates refresh tokens  
    - Whether advanced security is enforced  
    - Custom authentication flow settings  

You can then integrate this Client ID into your frontend/mobile/backend apps using:

- Cognito SDKs  
- Hosted UI redirect URLs  
- OAuth2 grant flow  

---

## Types Of App Clients

| Type                | Description    | Typical Use                             |
|---------------------|----------------|-----------------------------------------|
| **Public Client**     | No secret       | Mobile apps, SPAs                       |
| **Confidential Client**| Has client secret| Backend services, secure server-to-server apps |

> Use a client secret only when it can be stored securely — e.g., backend server or API — not in frontend/mobile code.

---

## Common Settings

| Setting                | Explanation                                                 |
|------------------------|-------------------------------------------------------------|
| Generate Client Secret | Enables confidential client (OAuth2 standard)               |
| Enable Sign-in API     | Allows InitiateAuth, AdminInitiateAuth                       |
| Enable Token Revocation| Allows logout/refresh token invalidation                     |
| Allowed OAuth Flows    | Authorization Code, Implicit, Client Credentials             |
| Allowed OAuth Scopes   | openid, email, profile, custom scopes                        |
| Callback URLs          | Where Cognito redirects after login                          |
| Logout URLs            | Where to redirect after logout                               |
| Token expiration settings| How long tokens last (ID, access, refresh)                |

### Token Expiration Defaults (Unless Changed)

| Token        | Default Expiry | Configurable?   |
|--------------|---------------|-----------------|
| ID Token     | 1 hour         | ✔️              |
| Access Token | 1 hour         | ✔️              |
| Refresh Token| 30 days        | ✔️ (1h to 10y)  |

> Make sure token durations match your app’s session handling model.  
> Long refresh tokens = long sessions = more risk if stolen.

---

## Security Best Practices

- Use client secrets only in secure environments  
- Enable refresh token revocation if you’re using long-lived sessions  
- Set short token TTLs for sensitive apps  
- Avoid redirect URI wildcards (like `*`)  
- Avoid exposing App Client secrets in mobile or frontend code  
- Use separate App Clients for different trust levels (e.g., Admin vs Public UI)  
- Name clients clearly (e.g., Snowy-WebApp-Client, Snowy-CLI-Admin)  

---

## When To Use Multiple App Clients

You’ll want to define different App Clients for:

- Separate platforms (web vs mobile vs CLI)  
- Different login methods (OAuth2 vs SRP vs custom auth)  
- Varying token TTLs or refresh settings  
- Apps with/without MFA  
- Testing vs production environments  

Each App Client is logically isolated and can use different callback URLs, secrets, flows, and token settings — even if they all point to the same User Pool.

---

## AWS CLI & SDK Examples

```bash
aws cognito-idp create-user-pool-client \
  --user-pool-id us-west-2_ABC123 \
  --client-name SnowyWebApp \
  --generate-secret \
  --allowed-o-auth-flows user_password auth_code \
  --allowed-o-auth-scopes email openid profile \
  --callback-urls https://app.snowy.io/login/callback
```

---

## CloudTrail Visibility

App Client actions show up in logs like:

- CreateUserPoolClient  
- UpdateUserPoolClient  

- DeleteUserPoolClient  

- AdminInitiateAuth (when login starts using this client)  
- RevokeToken and InitiateAuth events  

You’ll also see the `client_id` and `auth_flow` in these logs, useful for tracing weird login behavior or brute-force attempts.

---

## Final Thoughts

App Clients are not just configuration checkboxes — they define the security perimeter between your application and your identity provider.  
They are your OAuth clients, your token factories, and your sign-in gatekeepers.

Use them intentionally.  
Configure them clearly.  
Name them cleanly.  
Protect their secrets.

