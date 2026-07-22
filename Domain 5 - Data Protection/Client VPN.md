# AWS Client VPN

AWS Client VPN is a managed, endpoint-based OpenVPN service that lets individual users (laptops, remote workers) establish an encrypted TLS tunnel into a VPC and reach private AWS or on-prem resources. It is the remote-access counterpart to Site-to-Site VPN: Site-to-Site connects whole networks, Client VPN connects people. Security-wise the two things that matter are how a user authenticates (certificate mutual auth, Active Directory, or SAML federation) and what they are allowed to reach once connected (authorization rules plus security groups), because the endpoint terminates inside your VPC and a loose authorization rule is a wide-open door into private subnets. The thing to hold onto: Client VPN is per-user encrypted access into a VPC, authentication decides who gets a tunnel and authorization rules decide what that tunnel can reach, and the two are separate controls you must both lock down.

## How it works

- **The Client VPN endpoint is the anchor.** You create an endpoint, give it a client CIDR block (the address pool assigned to connecting users, which must not overlap the VPC or on-prem ranges), and associate it with one or more subnets. Each association creates an ENI in that subnet and enables reachability to that AZ.
- **Authentication picks who gets in.** Three modes: mutual certificate authentication (client and server certs issued via ACM), Active Directory (via AWS Directory Service, supports MFA), and SAML 2.0 federation (via IAM Identity Center or an external IdP for SSO). Federation and AD are how you tie access to corporate identity and enforce MFA.
- **Authorization rules decide what they reach.** After connecting, a user reaches nothing until an authorization rule permits a destination CIDR, optionally scoped to an AD group or SAML group. This is the least-privilege lever: grant access to specific subnets or hosts, not `0.0.0.0/0`.
- **Security groups still apply.** Traffic from the endpoint's ENIs is subject to the security group on the endpoint and the security groups on target resources, so SG rules are a second enforcement layer under the authorization rules.
- **Split-tunnel vs full-tunnel.** Split-tunnel sends only VPC-bound traffic through the tunnel and lets normal internet traffic go out the user's local connection. Full-tunnel routes all user traffic through AWS, which lets you inspect or filter egress but costs more and adds latency.
- **Connection logging gives visibility.** Client VPN can log connection events (who connected, when, from where, connection duration) to CloudWatch Logs, which is your audit trail for remote access.

## Client VPN vs adjacent access paths

| Option | Connects | Auth | Use it when |
|---|---|---|---|
| **Client VPN** | Individual users to a VPC | Cert, AD, or SAML | Remote workers need private access from laptops |
| **Site-to-Site VPN** | Whole on-prem network to VPC | Pre-shared key / cert (IPsec) | Two networks need a persistent encrypted link |
| **Direct Connect** | On-prem to AWS over private line | Physical circuit | Consistent bandwidth/latency, not over internet |
| **Verified Access** | Users to specific apps, no VPN client | IdP + device trust (zero-trust) | Per-app access with identity and posture checks |
| **Session Manager** | Admin to a single instance shell | IAM | Keyless, zero-inbound shell to one host |

## What gets tested

- **Client VPN vs Site-to-Site VPN.** Individual remote users need Client VPN. Connecting an entire branch or data center network to the VPC is Site-to-Site. The word "users" versus "network" is the tell.
- **Authorization rules are how you scope access.** A user connecting but unable to reach a resource, or reaching too much, is fixed by authorization rules (and their group scoping), not by the authentication method. Authentication is who gets a tunnel, authorization is what the tunnel reaches.
- **SAML / IAM Identity Center for SSO and MFA.** When the requirement is corporate identity, single sign-on, or federated MFA for VPN users, that is SAML federation or AD, not mutual certificate auth.
- **Client CIDR must not overlap.** The client address pool cannot overlap the VPC CIDR or on-prem ranges, or routing breaks. This is a common scenario detail.
- **Split-tunnel for egress control.** If the requirement is to inspect or filter all user internet traffic, full-tunnel routes it through AWS. If the requirement is efficiency and only VPC traffic through the tunnel, split-tunnel.
- **Zero-trust per-app access is Verified Access, not Client VPN.** If the scenario wants app-level access with device posture and no VPN client, that points at Verified Access.

## Limitations

- Client VPN gives network-level access into a VPC, so a broad authorization rule (`0.0.0.0/0` to the whole VPC) over-grants. Fine-grained control needs per-CIDR rules scoped to identity groups.
- Mutual certificate authentication has no built-in MFA or central identity. For MFA and corporate SSO you must use AD or SAML federation.
- The client CIDR block cannot overlap the VPC or on-prem address space, and changing it later means recreating the endpoint.
- Each subnet association creates billable ENIs and the endpoint is billed per association-hour plus per connection-hour, so idle or over-provisioned associations cost money.
- It is not a zero-trust, per-application model. Once a user is authorized to a subnet they have network reachability to everything in it that security groups allow, unlike Verified Access which gates per application.
- Connection logging is opt-in. Without it enabled you lose the remote-access audit trail that an incident investigation would need.