# JWT (JSON Web Token)

A JWT is a compact, self-contained token that carries signed claims between parties, used for authentication, authorization, and session validation. It is three base64url-encoded JSON parts joined by dots: a header, a payload of claims, and a signature. The signature (HMAC with a shared secret, or RSA/ECDSA with a private key) provides integrity and authenticity, so any party holding the right key or the issuer's public key can verify the token without calling back to the issuer. That statelessness is why JWTs underpin OAuth2 and OIDC and show up throughout AWS: Cognito issues them, Identity Center uses them for OIDC SSO, and API Gateway can validate them directly. The critical, constantly tested point is that signed is not encrypted. The thing to hold onto: a JWT's payload is readable by anyone who has the token, the signature only stops tampering, and the token is valid until it expires because there is nothing to revoke.

## How it works

- **Structure.** `header.payload.signature`, each base64url JSON. The header names the algorithm (`alg`) and type; the payload holds claims; the signature is computed over the encoded header and payload.
- **Signing and verification.** HMAC uses one shared secret to both sign and verify; RSA/ECDSA sign with a private key and verify with the matching public key, typically fetched from the issuer's JWKS endpoint. The `kid` header selects which key in the JWKS to use, which is how key rotation works.
- **Claim validation.** After the signature checks out, the verifier must validate claims: `exp` (not expired), `nbf` (already valid), `iss` (expected issuer), and `aud` (this token is for my app). Skipping `iss`/`aud` accepts tokens meant for someone else.
- **Standard claims.** `iss`, `sub`, `aud`, `exp`, `iat`, `nbf`, `jti`, plus custom claims like roles, email, or tenant ID.
- **In AWS.** Cognito returns ID and access tokens as JWTs; API Gateway offers a Cognito authorizer and a JWT authorizer (HTTP APIs) that verify signature, `iss`, and `aud`; ALB can authenticate via OIDC; Identity Center federates over OIDC.

## JWT vs opaque session token

| Feature | JWT | Opaque / session token |
|---|---|---|
| Stateless | Yes, self-contained | No, needs a server-side session store |
| Self-verifiable | Yes, via signature | No, must look up the session ID |
| Scalable across services | Ideal for distributed systems | Limited without a shared cache |
| Revocable | No, valid until expiry unless external logic | Yes, delete the session |
| Typical use | OAuth2, OIDC, APIs | Traditional server-rendered web apps |

## What gets tested

- **Signed is not encrypted.** The payload is base64url, not ciphertext, so anyone with the token can read every claim. Never put secrets in it. If payload confidentiality is required, that is JWE, a separate encrypted format.
- **Validate signature and claims.** A common vulnerability is checking the signature but not `aud` and `iss`, which lets a valid token from another application or issuer through. Always verify audience and issuer alongside expiry.
- **Reject `alg` tricks.** `alg: none` must be refused, and the verifier must pin the expected algorithm rather than trusting the header. Otherwise an RS256-to-HS256 confusion attack lets an attacker sign a token using the public key as an HMAC secret.
- **Verification uses JWKS for asymmetric tokens.** Federated setups use RS256/ES256 with a public JWKS endpoint, and the `kid` header maps to the correct key, which is also how rotation is handled without breaking existing tokens.
- **JWTs cannot be revoked mid-life.** They are stateless and valid until `exp`, so revocation needs a denylist or a key rotation, which is why the real controls are short lifetimes plus refresh-token rotation. This is the same limitation seen in Cognito, where revocation covers refresh tokens only.
- **ID token vs access token.** In OIDC the ID token proves identity (its `aud` is the client) and the access token authorizes API calls (it carries scopes). Authorizing an API off the ID token is a planted error.
- **API Gateway authorizers.** A JWT/Cognito authorizer validates the token before the request proceeds and can pass claims to the backend, replacing a session store with stateless token verification.

## Limitations

- **No pre-expiry revocation.** Being stateless is the strength and the weakness: a stolen token works until it expires unless you maintain a blocklist or rotate signing keys. Short TTLs are the mitigation.
- **Not encrypted by default.** Confidentiality of claims depends on TLS in transit and on not putting sensitive data in the payload; the token at rest is fully readable.
- **Bearer semantics.** Whoever holds the token can use it, so theft equals impersonation for the token's lifetime. Binding techniques (mTLS, sender-constrained tokens) and short lifetimes reduce the window.
- **Clock dependence.** `exp` and `nbf` rely on synchronized clocks, so verifiers need a small leeway for skew or valid tokens get rejected.
- **Security lives in the verifier.** A lax validator, one that accepts `alg: none`, skips `aud`/`iss`, or trusts the header's algorithm, is the weak point, not the token format itself.
- **Token bloat.** Many claims make tokens large, which can bump against header and cookie size limits in real deployments.