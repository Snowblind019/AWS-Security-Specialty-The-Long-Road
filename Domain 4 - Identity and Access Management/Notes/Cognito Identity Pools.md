# Cognito Identity Pools

## What It Is

An Identity Pool in Amazon Cognito allows federated identities (from Cognito User Pools, SAML IdPs, social providers, or even unauthenticated guest access) to assume temporary AWS credentials using STS (Security Token Service).  
These credentials are used to access AWS services like S3, DynamoDB, AppSync, IoT, etc., based on IAM roles.  

This is not authentication.  
Identity Pools are about **authorization** and AWS-level access, not login forms or password resets. That’s User Pool territory.

---

## Cybersecurity And Real-World Analogy

**Cybersecurity Analogy**  
User Pool is the guard checking your identity at the gate. Identity Pool is the guard saying:  
“Okay, based on who you are, here’s your temporary badge. This only works in Building A, for the next hour.”  

It’s a just-in-time IAM role mapping system, triggered after someone has proven their identity.

**Real-World Analogy**  
A concert:

- The ticket scanner confirms your identity (User Pool)  
- Then a staff member hands you a wristband for backstage access — that wristband is only good for 1 hour and only lets you into certain areas (Identity Pool + IAM Role)

---

### 1. Create the Identity Pool
You define:

- What types of identities are accepted (Cognito User Pool? Facebook? Google? SAML?)  
- Whether to allow unauthenticated (guest) access  
- One or more IAM roles to map identities to  

### 2. Client Authenticates Elsewhere
The user signs in through a User Pool, Google, Facebook, or SAML.  
You receive an ID Token or access token.

### 3. Token Sent to Identity Pool
The client app calls `GetId` and `GetCredentialsForIdentity`.  
The Identity Pool validates the token and maps the user to an IAM role.

### 4. Temporary AWS Credentials Are Issued
The user now receives:

- Access Key ID  
- Secret Access Key  
- Session Token  

These are scoped to the IAM role and expire (typically within 1 hour).

---

## Federation Sources Supported

| Identity Type         | Token Format                  |
|-----------------------|------------------------------|
| Cognito User Pool      | Cognito ID Token (JWT)        |
| SAML IdP              | SAML Assertion                |
| OpenID Connect (Google, Facebook, etc.) | OIDC Token  |
| Unauthenticated       | No token (just request access)|

---

## IAM Role Mapping Options

You map identities to IAM roles in 3 main ways:

| Mapping Type       | Description                                                                 |
|--------------------|-----------------------------------------------------------------------------|
| Default Role       | All users get the same IAM role                                              |
| Rules-Based Mapping| You define logic based on token claims (e.g., email domain, group, IdP provider)|
| Token-Based Role   | The identity token contains a custom:role claim that determines the role (must be allowed explicitly)|

**Danger zone:**  
If misconfigured, this mapping can:

- Grant users too much power (overprivileged IAM role)  
- Allow attackers to assume elevated roles if `custom:role` is not locked down  

---

## Security Benefits

✔️ Short-lived credentials from STS reduce blast radius  

✔️ No permanent IAM users for end-users  
✔️ Scoped, role-based access to AWS resources  

✔️ Supports multi-tenancy and fine-grained access  
✔️ Clean separation between identity system and authorization layer  

---

## Security Pitfalls

✖️ Default IAM roles are often too permissive  
→ Many apps assign all users the same role without using proper claims filtering  

✖️ Custom role mapping from tokens must be explicitly locked down  
→ Never trust client-side `custom:role` unless validated in mapping rules  

✖️ No built-in audit visibility for which identity assumed what  
→ You only see `AssumeRoleWithWebIdentity` in CloudTrail, not “Blizzard from SAML” unless you log it separately  

✖️ Unauthenticated guests can request credentials  
→ Common misconfig: Identity Pool with unauth access enabled + default role = open door  

✖️ No automatic revalidation of revoked tokens  
→ Once an identity is mapped and credentials are issued, those credentials are good until they expire — even if the source token is revoked  

---

## When You’d Use An Identity Pool

| Use Case                        | Why Use It                                                          |
|--------------------------------|---------------------------------------------------------------------|
| S3 file uploads from mobile app | Issue temporary S3 PutObject permission based on login              |
| IoT device provisioning         | Anonymous guest gets IoT connect credentials from Identity Pool      |
| AppSync or DynamoDB             | Grant users temporary access based on login source                  |
| Federated SSO (Okta, Google Workspace) → AWS | Let external identities access AWS SDK calls securely |

---

## Example Role Mapping Flow

- User logs in via Google → gets ID token  
- Token is sent to Identity Pool  
- Identity Pool says:  
“This is a Google user from domain wintercorp.com”  
Mapping rule: if domain == wintercorp.com, use IAM Role WinterdayReadOnly  
- Identity Pool calls `AssumeRoleWithWebIdentity`  
- Temporary credentials are returned  
- User uploads image to S3 (if allowed)

---

## CloudTrail Relevance

Look for:

- `AssumeRoleWithWebIdentity` → proves Identity Pool issued AWS access  
- `GetId` and `GetCredentialsForIdentity` → when apps requested STS creds  

Use CloudTrail event attributes (`principalId`, `userIdentity.sessionContext`) to correlate access back to the originating token.

---

## Best Practices For Identity Pools

- Use rules-based role mapping instead of default roles  
- Lock down token-based roles in mapping rules  
- Disable unauthenticated identities unless truly needed  
- Monitor `AssumeRoleWithWebIdentity` in CloudTrail  
- Enforce IAM least privilege on mapped roles  
- Use short session durations (1 hour or less)  

---

## Final Thoughts

Cognito Identity Pools are often misunderstood and misused — but when configured carefully, they allow fine-grained, scoped, time-limited AWS access for federated users without needing permanent IAM credentials.

Think of it this way:  
**User Pools = who you are**  
**Identity Pools = what you’re allowed to touch in AWS**

They’re not mandatory for every app, but they shine when you need:

- Temporary S3/DynamoDB access from frontend apps  
- Secure federation to AWS services  
- Just-in-time IAM role assumption for third-party identities

