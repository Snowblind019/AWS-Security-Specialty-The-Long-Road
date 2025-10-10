# JWT (JSON Web Token) 

## What Is a JWT

A **JSON Web Token (JWT)** is a compact, self-contained, cryptographically signed token used to securely transmit information between parties — typically for authentication, authorization, and session validation.

JWTs are:

- **Stateless** — all the info needed is in the token  
- **URL-safe** — can be passed in headers, cookies, or query strings  
- **Signed** (via HMAC or RSA/ECDSA) to prevent tampering

Common in **OAuth2**, **OpenID Connect (OIDC)**, and **serverless APIs**

They're used by:

- **AWS Cognito** and **IAM Identity Center**
- **OIDC identity providers** (Google, Auth0, etc.)
- **Backend apps** for session validation
- **API gateways** for auth checks

---

## Cybersecurity Analogy

Imagine you’re visiting **SnowySec HQ**. At the front desk, they hand you a badge:

- It has your name, permissions, expiry time  
- It’s digitally sealed by Snowy’s admin key  
- You can use it to get into certain rooms  
- But the badge itself carries all the info — no need to ask the desk every time

That’s what a JWT is.  
**Not just a session ID — it’s a portable security envelope, readable and verifiable on its own.**

## Real-World Analogy


- Issued by a trusted authority  
- Contains your identity + claims (e.g., citizenship, visa)  
- Has a signature to prevent forgery  

- Can be read and verified by any border officer — no need to call your embassy  

It’s **self-contained and validatable without phoning home** — perfect for distributed cloud systems.

---

## Anatomy of a JWT

A JWT is made of three parts, separated by dots (`.`):

```
<Header>.<Payload>.<Signature>
```

All three parts are **base64url-encoded JSON**.

### 1. Header

```json
{
  "alg": "RS256",
  "typ": "JWT"
}
```

Tells us:

- `alg`: Algorithm used (HMAC, RSA, ECDSA)  
- `typ`: It's a JWT

### 2. Payload (Claims)

```json
{
  "sub": "user123",
  "iss": "https://auth.snowysec.com",
  "aud": "my-app",
  "exp": 1717261200,
  "email": "blizzard@snowysec.com",
  "role": "admin"
}
```

This is where the action happens. It contains claims like:

- `sub` = subject (user ID)  
- `iss` = issuer  
- `aud` = audience  
- `exp` = expiration timestamp  
- Custom claims like roles, email, tenant ID, etc.

> This data is **readable by anyone** — so don’t put secrets here!

### 3. Signature

```
base64url(header) + "." + base64url(payload) signed with secret or private key
```

- Ensures **integrity**  
- Verifies **authenticity**  
- Prevents **tampering**

If the signature is invalid → **token rejected**

---

## Signing Algorithms

| **Algorithm** | **Type**   | **Notes**                                               |
|---------------|------------|----------------------------------------------------------|

| `HS256`       | HMAC       | Symmetric key — same key used to sign and verify        |
| `RS256`       | RSA        | Asymmetric — private key signs, public key verifies     |
| `ES256`       | ECDSA      | Smaller, faster, more modern                            |


In **federated identity** (e.g., Cognito), you’ll usually see **RS256** with a **public JWKS endpoint** for verification.

---

## Common Claims (JWT Payload)

| **Claim** | **Description**                                  |
|-----------|--------------------------------------------------|
| `iss`     | Issuer — who created the token                   |
| `sub`     | Subject — who the token is about                 |
| `aud`     | Audience — who the token is intended for         |
| `exp`     | Expiration — UNIX timestamp of expiry            |
| `iat`     | Issued At — when it was issued                   |
| `nbf`     | Not Before — when it becomes valid               |
| `jti`     | JWT ID — unique identifier (nonce)              |

You can add custom claims like `email`, `roles`, `org_id`, etc.

---

## JWT in AWS

| **Use Case**         | **JWT Usage**                                                                 |
|----------------------|-------------------------------------------------------------------------------|
| **Amazon Cognito**   | Returns JWTs (`id_token`, `access_token`) after successful auth              |
| **IAM Identity Center** | Uses OIDC + JWTs for federated SSO                                      |
| **API Gateway**      | JWT authorizer can verify tokens and extract claims for access               |
| **Amplify**          | Passes Cognito JWTs to backend apps                                          |
| **IoT / Custom Auth**| JWT used for identity + policy mapping                                       |

---

## Security Considerations

| **Risk**                        | **Mitigation**                                                                 |
|---------------------------------|---------------------------------------------------------------------------------|
| Expired tokens reused           | Always validate `exp`                                                          |
| Weak algorithm chosen           | Never allow `alg: none`; reject unknown `alg`                                  |
| Token stolen = session hijack   | Use HTTPS, short lifetimes, refresh token rotation                             |
| Sensitive data in payload       | Never store secrets — JWT payloads are **not encrypted**                       |
| No revocation mechanism         | Use short-lived tokens + refresh tokens + back-channel tracking                |

>  JWTs are **stateless** — they **can’t be revoked** unless you maintain a **blocklist** or **rotate keys**.

---

## JWT vs Session Tokens

| **Feature**         | **JWT**                                 | **Traditional Session Token**                     |
|---------------------|------------------------------------------|---------------------------------------------------|
| Stateless?          | ✔️ Yes                                  | ✖️ No (requires server/session store)              |
| Scalable?           | ✔️ Ideal for distributed systems         | 🟣 Limited without central cache                   |
| Self-verifiable?    | ✔️ Yes (if signed)                       | ✖️ Must look up session ID                        |
| Revocable?          | ✖️ No (unless external logic)            | ✔️ Easily revoked                                  |
| Used In?            | OAuth2, OIDC, APIs                       | Legacy web apps                                   |

---

## Real-Life Example: API Access with JWT

**SnowySec** builds a backend API with **API Gateway + Lambda**.  
**Blizzard** logs in via **Cognito** → receives a JWT.

JWT contents:

```json
{
  "sub": "blizzard",
  "email": "blizzard@snowysec.com",
  "role": "analyst",
  "exp": 1719870000
}
```

When Blizzard makes a request:

1. API Gateway **verifies the JWT signature** against Cognito's public JWKS endpoint  
2. If valid → **extracts claims**  
3. Passes claims to **Lambda function** as context  
4. Lambda enforces **role-based logic** (analyst can only read logs)

> No session store. No DB hits.  
> **Pure token-based access control.**

---

## Final Thoughts

JWTs are the **cornerstone of modern identity and access** in the cloud.  
They're **fast**, **flexible**, and **self-contained** — perfect for:

- Stateless microservices  
- Multi-account/cloud federated identity  
- API auth  
- Short-lived, verifiable sessions  

But they come with trade-offs:

- Can’t be revoked easily  
- Must be validated thoroughly  
- Don’t confuse “signed” with “encrypted”  

> If you use them right, JWTs give you **Zero Trust**, **federated**, **auditable** access in a clean, modern package.

