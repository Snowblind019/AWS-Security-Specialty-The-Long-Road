# AWS VPN

AWS VPN securely connects an on-premises network, data center, or another cloud to an Amazon VPC over the public internet using **encrypted IPsec tunnels**. It is the fast path to hybrid connectivity: extend the corporate network into AWS, route selected traffic through AWS, or provide a redundant backup for Direct Connect. There are two families: **Site-to-Site VPN** (network-to-VPC) and **Client VPN** (individual user devices to AWS). The thing to hold onto: a VPN protects data in transit between the two endpoints, nothing more, so its security value is the encrypted tunnel plus routing and segmentation you layer on, and the exam tests IPsec/IKE tunnel options, the CGW/VGW/TGW roles, Site-to-Site vs Client VPN, and where VPN beats or backs up Direct Connect.

## How it works

- **Endpoints.** A **Customer Gateway (CGW)** represents your on-prem device or software (Cisco ASA, Palo Alto, pfSense). The AWS side terminates on a **Virtual Private Gateway (VGW)** (single VPC) or a **Transit Gateway (TGW)** (many VPCs, and required for accelerated VPN).
- **Tunnels.** Each Site-to-Site connection provides **two tunnels** in independent availability zones for HA. Traffic uses IPsec (ESP) with **IKEv1 or IKEv2** (IKEv2 is the stronger default). NAT traversal moves the session from UDP 500 to UDP 4500 when NAT is detected.
- **Crypto options.** Configurable per tunnel: AES-128/256, SHA-1/SHA-2, and Diffie-Hellman groups (2, 14-18, 22-24). Harden by removing weak defaults (drop IKEv1, AES-128, SHA-1, DH2). Dead Peer Detection controls tunnel teardown.
- **Routing.** Static routes or **BGP dynamic routing**. BGP enables automatic failover across the two tunnels and, on a VGW, site-to-site transit via **VPN CloudHub**.
- **Authentication.** Site-to-Site uses a **pre-shared key** by default, or **certificate-based** IKE auth via an ACM Private CA subordinate CA (which also removes the need to pin the CGW's IP). Client VPN authenticates users via **Active Directory, SAML/federation, or mutual certificates**, with authorization rules per network.
- **Accelerated Site-to-Site VPN.** Uses **Global Accelerator** to pull tunnel traffic onto the AWS edge for better performance. It requires **Transit Gateway**, uses separate tunnel IPs, has NAT-T enabled, and is not available over public Direct Connect VIFs.
- **Segmentation and monitoring.** Prefix filtering controls which routes are advertised in/out; route tables, security groups, and NACLs limit what on-prem can reach once inside; CloudWatch tunnel-state alarms, Site-to-Site VPN logs, VPC Flow Logs, and GuardDuty provide visibility.

## VPN options compared

| | Site-to-Site VPN | Client VPN | Accelerated S2S VPN |
|---|---|---|---|
| Connects | On-prem/other cloud to VPC | User devices to AWS | On-prem to VPC via edge |
| Protocol | IPsec (IKEv1/2) | OpenVPN (TLS) | IPsec over Global Accelerator |
| AWS endpoint | VGW or TGW | Client VPN endpoint | TGW only |
| Auth | PSK or certificate | AD / SAML / mutual cert | PSK or certificate |
| HA | 2 tunnels | Managed endpoint | 2 tunnels, edge-optimized |

## What gets tested

- **VPN vs Direct Connect (and as its backup).** VPN is quick, encrypted, internet-based, and cheaper for low bandwidth; use it for migration bridges, dev/test, DR, and initial connectivity. Direct Connect is private fiber with consistent low latency for production, and DX is **not encrypted by default**, so pairing DX with an IPsec VPN is how you get a private *and* encrypted path. VPN is also the standard **Direct Connect failover**.
- **VGW vs TGW termination.** Single VPC to on-prem terminates on a **VGW**. Many VPCs, transit routing, or **accelerated VPN** requires a **TGW**. VGW site-to-site transit needs BGP (CloudHub); static does not transit.
- **Two tunnels for HA.** Every connection has two tunnels; real resilience uses BGP so failover is automatic. A single-tunnel design is the availability gap.
- **Site-to-Site vs Client VPN.** Network-to-network is Site-to-Site (IPsec). Individual remote user laptops are **Client VPN** (OpenVPN/TLS) with AD/SAML/cert auth and per-user authorization rules.
- **Encryption and IKE hardening.** VPN is the answer when the requirement is "encrypt data in transit to on-prem." Harden by enforcing IKEv2, AES-256, SHA-2, and strong DH groups, and by dropping the weaker defaults.
- **Certificate auth to drop IP pinning.** When the CGW has a dynamic IP, certificate-based IKE auth (ACM Private CA) removes the fixed-IP requirement of PSK.
- **Segment what on-prem can reach.** Prefix filters plus route tables, SGs, and NACLs bound the blast radius so a compromised on-prem network cannot reach the whole VPC. VPN gives the pipe, not the segmentation.

## Limitations

- A VPN encrypts only the transit between endpoints; it does not protect data or control access once traffic is inside either network. Segmentation and IAM still apply.
- Throughput and latency ride the public internet and each tunnel is bandwidth-limited (standard ~1.25 Gbps; a large-bandwidth tunnel option up to ~5 Gbps requires TGW/Cloud WAN). Consistent high-throughput, low-latency needs Direct Connect.
- Default tunnel options include weak choices (IKEv1, AES-128, SHA-1, DH2). Leaving defaults is a hardening gap; you must prune them.
- Accelerated VPN only works with Transit Gateway, not a VGW, and not over public Direct Connect VIFs.
- Static routing gives no automatic failover; without BGP, tunnel loss requires manual intervention, and VGW cannot provide TGW-style multi-VPC transit.
- Client VPN is billed per active connection plus an hourly endpoint fee and needs authorization rules configured; an open Client VPN with broad rules is as risky as any flat network.