# IAM Credential Reports

An IAM credential report is a downloadable CSV that snapshots the credential state of every IAM user in the account, plus the root user, in one row each. It captures the hygiene facts you need for an audit: whether a password exists and when it was last used, whether MFA is on, whether access keys exist and when they were last used, created, and rotated, and whether any legacy signing certs are active. It is one of the few built-in tools for account-wide credential hygiene, which makes it central to compliance reviews, incident response, and cleaning up legacy accounts that still lean on IAM users instead of federation. On the SCS exam it shows up as the answer for "how do I audit MFA coverage, stale keys, and unused users across the account." The thing to hold onto: it is a point-in-time hygiene snapshot of IAM user (and root) credentials, nothing about roles, federation, or what APIs were called.

## How it works

- **You generate it, then fetch it.** `aws iam generate-credential-report` builds the report; `aws iam get-credential-report` returns it (base64-encoded, so you decode to CSV). The console offers a direct download under the credential report view.
- **It is cached for up to four hours.** A generate call refreshes it at most once every four hours; a get in between returns the last generated copy. Plan around that staleness for automation.
- **One row per IAM user, plus a root row.** The root account appears as its own entry, which is useful for confirming root has MFA and no access keys.
- **Over twenty fields per row**, focused on credential existence, age, rotation, and last-used timestamps.
- **It is automatable.** A Lambda or script can pull the report, parse for keys older than a threshold or users without MFA, and push findings to S3 or Security Hub as a credential-hygiene pipeline.

## Key fields

| Field | Meaning |
|---|---|
| `user` | IAM username (or `<root_account>` for root) |
| `password_enabled` | Whether console password login is set |
| `password_last_used` | Last console sign-in, or N/A |
| `password_last_changed` | Last password rotation |
| `mfa_active` | Whether MFA is enabled |
| `access_key_1_active` / `access_key_2_active` | Whether each key is active |
| `access_key_1_last_used_date` | Last time the key made a call, or N/A |
| `access_key_1_last_rotated` | Key age / last rotation |
| `cert_1_active` | Whether a legacy X.509 signing cert is active |

## What gets tested

- **It covers IAM users and root only.** No roles, no federated or SSO identities, no assume-role or session activity. A scenario needing role usage or federated visibility is not this report; that is Access Advisor or CloudTrail.
- **It answers credential-hygiene questions directly.** Who lacks MFA, which access keys are stale or never used, which keys are past a rotation age, which users have unused passwords, and how many credentials exist overall.
- **Root shows up in the report.** It is a clean way to verify the root user has MFA on and no active access keys, which is a common compliance and exam checkpoint.
- **Know how it differs from the neighbors.** Credential report is user credential state; Access Advisor is service last-used per identity including roles; Access Analyzer is policy reachability; CloudTrail is API-level events. The exam tests picking the credential report specifically for MFA/key-age/unused-user audits.
- **It supports compliance and IR.** For PCI-DSS, SOC 2, and ISO 27001 it is the credential inventory, and in a breach it answers "what credentials existed and which were in use" as a snapshot.
- **The `last_used` and rotation fields drive the findings.** MFA off, active key with N/A last-used, and rotation older than your policy window are the standard risk indicators to flag.

## Limitations

- **Users and root only.** Roles, federated identities, and SSO users are invisible to it, which is a real gap in modern federation-first accounts.
- **Not API-level.** It shows that a key was last used on a date, not which calls were made or from where. That granularity is CloudTrail.
- **Point-in-time.** It is a snapshot, not continuous monitoring, so catching drift means regenerating and comparing over time or automating the pull.
- **Four-hour refresh cap.** You cannot get a fresher-than-four-hours view on demand, so it can lag recent changes.
- **Descriptive, not preventive or detective.** It reveals credential risk but does not stop or detect abuse; acting on the findings is a separate step.
- **Last-used timestamps have edge cases.** Certain activity may not be reflected precisely, so treat N/A and timestamps as strong signals rather than absolute proof of non-use.