# AWS Verified Access

AWS Verified Access is a Zero Trust Network Access (ZTNA) service that gives users secure, **VPN-less** access to internal corporate applications and resources. Instead of granting network-level access, it evaluates every request against policy using **user identity and device posture** before allowing the connection to reach the app, and continuously re-evaluates active sessions. It started with HTTP/HTTPS apps and now also covers **non-HTTP protocols (TCP, SSH, RDP)**, so databases, EC2 fleets, git repos, and SAP can use the same identity/device checks. The thing to hold onto: Verified Access is per-request, per-application zero-trust authorization at the edge of your app, replacing the "connect to the network then reach everything" VPN model, so the exam reaches for it when the requirement is fine-grained, identity-plus-device access to internal apps without a VPN.

## How it works

- **Instance.** The top-level resource that scopes trust providers, groups, and endpoints.
- **Trust providers.** External signals evaluated per request: **identity** providers (IAM Identity Center or any OIDC IdP, Okta, Ping, Cognito, Auth0) and **device** trust providers (CrowdStrike, Jamf, JumpCloud) supplying real-time device posture.
- **Groups.** Logical collections of endpoints that share a base access policy, so similar apps inherit one policy.
- **Endpoints.** One per application. HTTP/S endpoints map to an ALB or ENI; **TCP endpoints** onboard persistent resources (RDS, databases); **network endpoints** onboard groups of ephemeral resources by IP/port with automatic DNS. Non-HTTP access uses a lightweight **Connectivity Client** so users keep native tools (SQL Workbench, PuTTY).
- **Cedar policies.** Access decisions are written in the **Cedar** policy language, evaluating identity claims (user/group/email), device posture, and context (allow only verified emails on compliant managed devices, etc.). Group policy plus optional per-endpoint rules.
- **Continuous verification.** It evaluates each new connection and keeps monitoring active ones, **terminating** a session when it stops meeting policy (for example device falls out of compliance).
- **Setup essentials.** Needs an **ACM certificate** matching the app domain and a public hosted domain, with **CNAME** records mapping app domains to the Verified Access endpoint so all requests route through it.
- **Logging.** Detailed access logs capture the trust context evaluated per request, for audit and troubleshooting (a Cedar/group-name mismatch is the usual "access denied").

## Verified Access vs other remote-access options

| | Verified Access | Client VPN | Site-to-Site VPN | Bastion + SSH |
|---|---|---|---|---|
| Model | Per-request ZTNA, per app | Network tunnel to VPC | Network to VPC | Jump host |
| Grants | Access to one app if policy passes | Broad network reach | Broad network reach | Host, then network |
| Signals | Identity + device posture, continuous | User auth at connect | PSK/cert at connect | SSH key |
| VPN client | None (browser or connectivity client) | OpenVPN client | N/A | SSH client |
| Protocols | HTTP/S + TCP/SSH/RDP | IP | IP | SSH/RDP |
| Best for | Zero-trust app access, work-from-anywhere | Legacy broad access | Network-to-network | Ad-hoc host access |

## What gets tested

- **VPN-less zero-trust app access is Verified Access.** "Give employees access to internal apps based on identity and device posture without a VPN, evaluated per request" is Verified Access. A VPN grants network reach; Verified Access grants access to a specific application only if policy passes.
- **Identity plus device posture.** The differentiator is combining an identity trust provider with a device trust provider, so access requires an authenticated user on a compliant device. Identity-only or network-only controls are weaker answers.
- **Continuous verification and session termination.** Unlike a VPN that authenticates once at connect, Verified Access re-checks active sessions and cuts them when posture fails. This is the "revoke access mid-session if the device becomes non-compliant" answer.
- **Non-HTTP support.** For SSH/RDP/database (RDS, EC2, git, SAP) zero-trust access, Verified Access now covers TCP endpoints via the Connectivity Client, replacing a separate bastion or VPN for those too.
- **Cedar policies.** Access logic is Cedar, evaluating identity and device attributes. A denied-access troubleshooting scenario usually points at the Cedar policy or a group-name mismatch from the IdP.
- **ACM + DNS routing.** It requires an ACM cert and CNAME records routing app domains through the endpoint; certificate or DNS misconfiguration is the common setup failure.
- **Verified Access vs Verified Permissions.** Verified Access controls user access to whole applications (ZTNA at the front door). **Amazon Verified Permissions** is Cedar-based fine-grained authorization *inside* an application (who can do what to which resource). Both use Cedar but solve different layers.

## Limitations

- It authorizes access to applications you onboard as endpoints; it is not a general network VPN and does not give broad subnet reach. Each app is an endpoint with its own policy.
- Setup requires an ACM certificate, a public hosted domain, and CNAME routing, so misconfigured certs or DNS block access; it is more involved than flipping on a VPN.
- Policy evaluation adds latency per request, and unhealthy trust providers slow or break access, so trust-provider availability matters.
- Device posture depends on integrating a supported device trust provider; without one you get identity-only checks, not full zero trust.
- It secures access to the app, not the app's own internal authorization; in-app fine-grained decisions are Verified Permissions, and it does not replace WAF (L7 exploit filtering) or IAM for AWS API access.
- Pricing is per-application-hour plus data processed (HTTP/S) or endpoint-hours plus per-connection (non-HTTP), so many onboarded apps accrue cost; it is Region-scoped and not available everywhere.