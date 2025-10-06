# Active Directory Federation Services (AD FS)

## What Is the Service

Active Directory Federation Services (AD FS) is a Microsoft identity federation solution that allows users from one organization to securely access resources in another, without needing a separate username and password. It enables Single Sign-On (SSO) across security boundaries using claims-based authentication.

Think of AD FS as the glue between your on-premises Active Directory and external services (like AWS, Salesforce, or Office 365) that don’t natively live in your domain, but still need to trust your users.

In AWS, AD FS is often the on-prem Identity Provider (IdP) that federates into IAM roles via SAML 2.0.

---

## Cybersecurity & Real-World Analogy

Imagine Snowy works for a government agency that has its own badge system.  
Now they need to use a vendor’s secure AWS-hosted portal. Rather than issuing new usernames and passwords, they want to use their existing internal AD identities to authenticate users into AWS.

**AD FS is like an automated badge translation booth:**

- Snowy flashes their on-prem badge (AD credentials)  
- AD FS issues a SAML assertion (like a temporary visa)  
- AWS accepts that assertion and grants access to a specific IAM role  

✔️ No extra passwords  
✔️ Centralized user lifecycle management  
✔️ Full auditability on the IdP side  

---

## How AD FS Works (Simplified Flow)

Here’s what happens under the hood when AD FS federates access to AWS:

1. **User logs into the AD FS portal**  
   - Typically via web browser or enterprise SSO dashboard  
2. **AD FS authenticates user via Active Directory**  
   - Validates username/password or smart card login  
3. **AD FS issues a SAML assertion**  
   This contains claims like:  
   - `NameID = Snowy`  
   - `RoleSessionName = Snowy`  
   - `https://aws.amazon.com/SAML/Attributes/Role = arn:aws:iam::111122223333:role/SnowyRole,arn:aws:iam::111122223333:saml-provider/SnowyADFS`  
4. **User is redirected to AWS STS (Security Token Service)**  
   - STS validates the SAML assertion, issues temporary credentials  
5. **User gets federated into AWS** with an IAM role, scoped by the SAML claim

---

## Key Concepts & Terms

| Term               | Description                                                                  |
|--------------------|-------------------------------------------------------------------------------|
| Claim              | A statement about the user (email, group, role, etc.) included in the SAML assertion |
| Relying Party Trust| The external app (e.g. AWS) that AD FS trusts and sends assertions to        |
| Identity Provider (IdP) | AD FS — it authenticates the user and issues the SAML                   |
| Service Provider (SP)   | AWS — it consumes the SAML assertion and grants access                  |
| SAML Assertion     | A signed XML document that proves who the user is and what they can access   |
| STS                | AWS service that exchanges SAML for temporary IAM credentials                 |

---

## Security Design Considerations

| Area               | Best Practice                                                                 |
|--------------------|-------------------------------------------------------------------------------|
| TLS                | All AD FS communications must be encrypted with valid SSL/TLS certs          |
| Hardening          | AD FS servers should be behind firewalls, patched, and monitored             |
| SAML Assertions    | Signed and time-limited (typically 5–15 minutes)                             |
| Role Trusts        | Use precise IAM conditions (e.g., `StringEquals:SAML:aud = AD-FS`)            |
| CloudTrail         | Monitor `AssumeRoleWithSAML` calls                                            |
| IdP Rotation       | Rotate signing keys periodically and update trust in AWS                     |
| Conditional Access | Pair with Azure AD / MFA / device posture checks if hybrid                   |

---

## Common Pitfalls

| Mistake                     | Consequence                                                           |
|-----------------------------|------------------------------------------------------------------------|
| ✖️ No assertion expiration   | Users could replay the SAML assertion indefinitely                    |
| ✖️ Wildcard IAM role trust   | Any SAML assertion can assume any role — very bad                     |
| ✖️ No MFA at IdP            | Weakens the entire chain of trust                                     |
| ✖️ No logging               | Makes forensics impossible in a breach                                |
| ✖️ Using HTTP instead of HTTPS | Credential and token exposure risk                               |

---

## Snowy’s Real-World Example

Snowy’s org uses AD FS with AWS IAM SAML Federation:

- AD FS configured as IdP  
- IAM roles trust SAML provider named `SnowyADFS`  
- Each role has a Condition block like:

```json
"Condition": {
  "StringEquals": {
    "SAML:aud": "https://signin.aws.amazon.com/saml"
  }
}
```
- The AD FS admin maps Active Directory groups to IAM roles:  
  - `CloudAdmins → arn:aws:iam::123456789012:role/AdminRole`  
  - `DevOps → arn:aws:iam::123456789012:role/ReadOnlyRole`  
- CloudTrail alerts are set for `AssumeRoleWithSAML` events  
- The AD FS signing certificate rotates every 12 months  
- Snowy gets AWS access via:  
  `https://adfs.snowy.org/adfs/ls/IdpInitiatedSignOn.aspx`  

Once authenticated, the SAML assertion sends them into the AWS Console pre‑signed to their role.

---

## Final Thoughts

AD FS is powerful, but fragile if misconfigured.  
It gives your users seamless access to cloud, SaaS, and external systems — but it also creates a single point of federation.

✔️ Harden it  
✔️ Monitor it  
✔️ Pair with MFA  
✔️ Rotate certs  
✔️ Scope your IAM roles precisely

