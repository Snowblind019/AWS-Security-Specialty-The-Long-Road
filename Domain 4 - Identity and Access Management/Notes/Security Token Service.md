# AWS STS

## What Is the Service
AWS Security Token Service (STS) is the engine behind temporary credentials in AWS.
Instead of hardcoding long-term access keys (which are risky and difficult to rotate), STS lets you request short-lived credentials that expire automatically. These temporary credentials can assume specific roles, have limited permissions, and are valid for a controlled time window — typically 15 minutes to 12 hours depending on the API used.

STS is foundational to many secure AWS patterns:
- Cross-account access
- Federated identities (SSO, Active Directory, Cognito)
- IAM role chaining
- On-demand privilege elevation (Just-in-Time Access)
- Access delegation for Lambda, EC2, ECS tasks
- Session-based auditing

Without STS, everything would rely on static keys — and static keys get leaked, copied, forgotten, and abused.

---

## Cybersecurity Analogy
Think of IAM user access keys like permanent master keys to a building — risky, overpowered, and often copied.
STS is more like issuing a temporary badge at the front desk. It’s tied to your identity, limited in what doors it can open, and it auto-expires after a few hours. If that badge gets dropped or stolen, the window of abuse is narrow. And if it’s misused, you can trace exactly who it was issued to and why.

## Real-World Analogy
Imagine a secure facility like a data center. Rather than giving engineers a key that works 24/7 forever, they scan their company badge, state their purpose, and are handed a temporary access card good for the next 6 hours — and only for the racks or cages they’re allowed to touch.

That’s STS. It enables just enough access, for just enough time — without permanent doors being left unlocked.

---

## How It Works
AWS STS issues temporary security credentials made up of:
- **Access Key ID**
- **Secret Access Key**
- **Session Token**

These credentials can be generated using different API calls depending on the use case.

- **AssumeRole**
  Used to switch identities — typically for cross-account access. The trusted principal (user, Lambda, EC2, etc.) assumes a target role.

  ```json
  {
    "Action": "sts:AssumeRole",
    "RoleArn": "arn:aws:iam::222222222222:role/ReadOnlyS3",
    "RoleSessionName": "SnowyTempSession"
  }
  ```

  The calling identity gets a temporary session with the permissions of the **ReadOnlyS3** role.

- **GetSessionToken**
  Generates temporary credentials for an IAM user (used rarely, mostly legacy). Can add MFA enforcement.

- **AssumeRoleWithSAML**
  For federated users logging in via SAML-based identity providers (Okta, ADFS, etc.).

- **AssumeRoleWithWebIdentity**
  Used when apps or mobile clients authenticate via OIDC-based IdPs (like Cognito, Google, Facebook). The app exchanges the identity token for a session.

- **AssumeRoleWithJWT**
  Used with IAM Roles Anywhere or newer OIDC flows like Kubernetes and GitHub Actions.

---

## Session Duration and Control
You control session length in the API call (e.g., `DurationSeconds = 3600`). Max session duration depends on the role's trust policy.

For example:
- Default max: 1 hour (3600 seconds)
- Can be increased to 12 hours with a role setting
- Some services (like Cognito Identity Pools) default to shorter durations

You can also enforce:
- MFA with `sts:TagSession` and condition keys like `aws:MultiFactorAuthPresent`
- Session tags for attribute-based access control (ABAC)
- External ID for 3rd-party delegation (e.g., Snowy grants Zayo access to S3 logs)

---

## Security Controls and Considerations

| Feature              | Description                                                                 |
|----------------------|-----------------------------------------------------------------------------|
| **Session Tags**     | Key-value pairs attached to the session for ABAC. Used in fine-grained policies. |
| **External ID**      | Prevents confused deputy attacks. Required when 3rd parties assume roles.   |
| **Source Identity**  | Traces the original calling identity for audit purposes (via CloudTrail).   |
| **MFA Enforcement**  | Used to enforce strong identity verification before granting session.       |
| **MaxSessionDuration** | Controlled in the trust policy of the target role.                        |

---

## CloudTrail Integration
Every STS call is logged in **CloudTrail** — both the API call and any resource access using the temporary credentials.

You’ll see:
- **AssumeRole** call from source identity
- Session name and external ID (if provided)
- Access events tied back to the session

This creates **auditability across identity boundaries** — especially important in cross-account or federated setups.

---

## Pricing Model
STS itself is free. There’s no cost for:
- Calling AssumeRole, GetSessionToken, or federating
- Session tokens issued
- Duration of the session

You’re only charged for the underlying services used during the session (e.g., S3 reads, Lambda invokes, etc.).

---

## Real-Life Example: Snowy’s Multi-Account Engineering Setup
Let’s say you’ve got a **shared services account** for IAM and logging, and multiple **workload accounts** for production apps.

Blizzard is a developer in the engineering org. She authenticates via Okta, which sends a SAML assertion to AWS. STS validates the assertion and issues a temporary credential to assume the **EngineeringDevAccess** role in the workload account.

This role grants only:
- Read access to CodeCommit repos
- Deploy permissions in Dev environment
- Session duration limited to 1 hour
- Requires MFA via Okta

The session tags include:
- `department = engineering`
- `project = SnowstormApp`

Now policies in that account can say things like:

```json
"Condition": {
  "StringEquals": {
    "aws:RequestTag/project": "SnowstormApp"
  }
}
```

So she can only deploy to apps tagged to her project.

At the end of the session, her permissions vanish. No long-term keys. No standing access. And everything is traceable in CloudTrail.

---

## Final Thoughts
AWS STS is the **glue** between identity, permissions, and governance in AWS.

Whether you're building:
- Secure cross-account access
- Federated authentication for workforce or mobile apps
- Temporary escalation workflows for just-in-time access
- Session-aware access controls with ABAC

...you’re using STS behind the scenes.

Security-wise, STS allows for:
- Short-lived credentials that expire
- Auditability across federated boundaries
- Policy enforcement tied to identity, session tags, and MFA
- Complete removal of static access keys from almost all workloads

This is one of the **most foundational services in AWS security**, and mastering its flows is essential for designing safe, scalable, multi-account environments.
