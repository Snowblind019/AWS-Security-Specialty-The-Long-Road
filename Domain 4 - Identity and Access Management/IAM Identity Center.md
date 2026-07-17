# IAM Identity Center (with SCIM and External IdPs)

IAM Identity Center, formerly AWS SSO, is AWS's centralized workforce identity and access hub for multi-account organizations. It decides who can sign into which accounts, what they can do once inside, and which SAML applications they can reach, all from one place. Authentication comes from its own directory or an external IdP over SAML 2.0; user and group provisioning is automated with SCIM; and access is granted through permission sets that become IAM roles in the target accounts, handing out temporary STS credentials. The whole point is to stop provisioning IAM users and roles by hand in every account. On the SCS exam it is the answer for enterprise SSO and least-privilege governance across an Organization, and it is constantly contrasted with self-managed SAML federation. The thing to hold onto: Identity Center is AWS-managed SSO where permission sets become roles and STS issues short-lived credentials, so humans never need IAM users or long-term keys.

## How it works

- **Core objects.** Users and groups (from the built-in directory or synced from an external IdP), permission sets (policy bundles that translate into IAM roles behind the scenes), account assignments (which principal gets which permission set in which account), and the access portal where users sign in and pick an account and role.
- **Identity source is configurable.** The Identity Center directory, an external IdP via SAML plus SCIM, or AWS Managed Microsoft AD. Authentication flows to the chosen source.
- **SCIM automates the lifecycle.** The IdP is the SCIM client and Identity Center is the SCIM server, so onboarding creates the user, group changes sync, and offboarding deactivates access without any AWS-side action.
- **A permission set is a role template.** It bundles managed and inline policies, an optional permissions boundary, and a session duration. When assigned to a group in an account, Identity Center provisions a corresponding IAM role (named with an `AWSReservedSSO` prefix) in that account.
- **Access flow.** The user authenticates at the portal (SAML to the IdP), selects an account and permission set, and STS issues temporary credentials scoped to the provisioned role.

## Identity Center vs self-managed IAM federation

| Dimension | IAM Identity Center | Traditional IAM SAML federation |
|---|---|---|
| Directory | External IdP or the built-in directory | External IdP only |
| Access model | Permission sets assigned to groups across accounts | IAM roles and SAML providers configured per account |
| Provisioning | SCIM, automated | Manual or custom scripting |
| Visibility | One console for all assignments | Spread across every account |
| Credentials | Temporary via STS | Temporary via STS |
| Best fit | Multi-account orgs wanting central SSO and governance | Lightweight, single-account, or legacy setups |

## What gets tested

- **Identity Center is AWS-managed multi-account SSO.** Permission sets become IAM roles, and access is temporary STS credentials, so there are no IAM users for humans. This is the answer for centralizing access across an Organization.
- **SAML authenticates, SCIM provisions.** Keep the split straight: SAML 2.0 carries the login, SCIM 2.0 syncs users and groups and handles deprovisioning. A question about automatic onboarding and offboarding is SCIM; a question about the login trust is SAML.
- **It contrasts with self-managed federation.** Where AD FS plus IAM SAML providers means configuring trust and roles in each account, Identity Center centralizes that into permission sets and assignments. Pick Identity Center when the scenario stresses scale, central governance, or reducing per-account role sprawl.
- **Identity source options matter.** Built-in directory, external IdP (SAML + SCIM), or AWS Managed Microsoft AD. The scenario's existing directory usually dictates the choice.
- **It supports ABAC.** Attributes from the IdP can be passed as session tags and used in permission-set and resource policies for attribute-based access control.
- **Auditing is centralized.** CloudTrail records sign-ins and role assumptions, and access is always tied to a federated identity, which is the governance and IR benefit the exam highlights.
- **Deprovisioning depends on the IdP.** SCIM removes access when the IdP signals a user is gone, so lifecycle correctness depends on the IdP sending the deactivation.

## Limitations

- **Workforce identities only.** It is for employees and contractors accessing AWS and SAML apps, not customer/app end users (that is Cognito) and not programmatic service credentials (use roles directly).
- **One instance per organization, in one Region.** The Identity Center instance is enabled in a single home Region and is not casually moved, even though it grants access to all accounts and Regions. Organization features require AWS Organizations.
- **SCIM is not instant and not universal.** Sync runs on the IdP's schedule (often tens of minutes), attribute mapping has constraints, and SCIM provisioning requires the IdP to support SCIM 2.0. SAML 2.0 auth is broad, but do not assume every SAML IdP offers full SCIM.
- **Permission sets carry quotas.** There are limits on permission sets per account and related objects, so very large estates need to plan around them.
- **It assigns identity access, it does not replace guardrails.** SCPs, RCPs, and resource-based policies still do their own jobs; Identity Center governs who gets which role, not the org-wide boundaries around them.