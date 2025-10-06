# IAM Credential Reports  

## What Is the IAM Credential Report

The IAM Credential Report is a downloadable CSV report that gives you a complete snapshot of credential usage and hygiene for every IAM user in your account.

It shows:

- Whether the user has a password  
- When the password was last used  
- Whether MFA is enabled  
- Whether access keys exist  
- When the keys were last used, rotated, or created  

This is one of the few built-in tools for account-wide credential hygiene auditing — especially for older environments that still rely on IAM users instead of federation.  
It’s also essential for compliance audits, security reviews, SOC 2 readiness, and proactive exposure reduction.

---

## Cybersecurity Analogy

Think of IAM Credential Reports like a sanitation inspection log for your cloud.  
Every IAM user is a door into the building. Some have rotating keys, some have no MFA locks, and some haven’t been used in 400 days.

You can’t secure a building if you don’t know who has what kind of access — and this report is your flashlight into the dark corners of credential sprawl.

## Real-World Analogy

Imagine Snowy inherits a legacy AWS account.  
There are 42 IAM users, some created five years ago. No one knows:

- Which ones are still active  
- Whether their access keys are rotated  
- Whether they’re even used  

Running the IAM Credential Report is like pulling their badge records and checking:

- Who last clocked in  
- Who has 24/7 master access  
- Who has lost their badge but is still marked “active”

---

## How It Works

The IAM Credential Report is generated on demand by calling the AWS API or downloading from the console:

```bash
aws iam generate-credential-report
```

```bash
aws iam get-credential-report --output text --query 'Content' \| base64 -d > cred-report.csv
```

You can also just go to **IAM Console → Credential Report → Download**.

The CSV contains one row per IAM user, and includes fields like:

| Field                     | Meaning                          |
|---------------------------|----------------------------------|
| user                     | IAM username                     |
| password_enabled         | true/false                       |
| password_last_used       | Timestamp or N/A                 |
| password_last_changed    | When password was rotated        |
| mfa_active               | true/false                       |
| access_key_1_active      | true/false                       |
| access_key_1_last_used_date | Timestamp or N/A             |
| access_key_1_last_rotated | How old the key is              |
| cert_1_active            | For X.509 certs (legacy use)     |

There are over 20 fields, most of them focused on how credentials were used, when, and whether MFA exists.

---

## What This Is Good For

- Audit user hygiene (e.g., “Do any users lack MFA?”)  
- Detect unused IAM users (“Never signed in, no key usage, remove them.”)  
- Check password policy compliance  
- Spot stale or non-rotated access keys  
- Inventory how many credentials exist in your environment  
- Prepare for PCI-DSS / SOC 2 / ISO 27001 reviews  

---

## What This Does NOT Do

- It does not include roles — only IAM users  
- It does not show federated or SSO identities  
- It does not show session activity or assume-role usage  
- It does not show API-level granularity (use CloudTrail for that)  

This is an IAM user-focused report — which makes it critical for legacy account cleanup or technical debt audits.

---

## Use Case Example: Security Audit Walkthrough

- Downloads the report via the console  

- Filters for `mfa_active == false`  
- Finds 3 IAM users with full admin access and no MFA  

- Filters for `access_key_1_last_used_date == N/A` and `access_key_1_active == true`  
- Finds 4 access keys created >180 days ago that have never been used  

- Flags these users/keys for deletion or MFA enrollment  

**Outcome**:

- 7 security risks eliminated  
- 1 email to Snowy’s boss showing proactive cleanup  
- 1 bullet point in the audit report checked off  

---

## Why This Matters for Detection and Incident Response

During a breach investigation, one of your first questions is:  
**“What credentials existed, and which were in use?”**

If you don’t know:

- Who had active access keys  
- Whether they were used recently  
- Which keys have never been rotated  
- Who didn’t have MFA  

Then you’re flying blind.  
This report gives you a snapshot-in-time to answer those questions quickly — even if the account is 10 years old.

---

## Security Best Practices from the Credential Report

| Risk Indicator                                 | What It Means                    | Mitigation                            |
|------------------------------------------------|----------------------------------|----------------------------------------|
| `mfa_active == false`                          | No MFA for console access        | Enroll MFA immediately                |
| `password_enabled == true` and `password_last_used == N/A` | IAM user with password never used | Consider removing password        |
| `access_key_1_active == true` and last_used == N/A | Key created but never used     | Disable or delete                     |
| `access_key_1_last_rotated > 90 days`          | Key aging, risk of compromise    | Rotate on a schedule                  |
| `cert_1_active == true`                        | Legacy SSL cert still active     | Decommission legacy usage unless needed |

---

## Automated Remediation Example

You can write a Lambda or script to:

- Download the credential report  
- Parse it for access keys older than X days  
- Auto-disable or alert on risky users  
- Log findings to S3 or send to Security Hub  

This becomes part of a **credential hygiene pipeline** — especially powerful in large orgs with many accounts.

---

## Final Thoughts

IAM Credential Reports are one of AWS’s quietest but most powerful visibility tools.  
They don’t prevent incidents.  
They don’t detect abuse.

But they **show you the truth about credential risk** in your environment — and that’s step one in tightening down IAM.

If you're doing governance, incident response, or technical debt audits, this report is not optional — **it's foundational**.

