# AWS Direct Connect

AWS Direct Connect (DX) is a dedicated, private physical network link from an on-premises data center, colocation facility, or office into the AWS network, terminated by a cross-connect at a DX location. Unlike a VPN over the public internet, it is a private fiber path, giving lower and more consistent latency, higher bandwidth, predictable throughput, and reduced data-transfer-out cost. The thing to hold onto, and the single most tested point: **private is not the same as encrypted**. Direct Connect does not encrypt traffic in transit by default, so its security value is path isolation and consistency, and encryption has to be added on top with MACsec (Layer 2) or an IPsec VPN over the link (end to end).

## How it works

- **Connection types.** A **dedicated connection** is a physical 1, 10, or 100 Gbps port provisioned from AWS at a DX location. A **hosted connection** is provisioned through an AWS Partner and offers sub-port capacities (50 Mbps to 25 Gbps depending on partner).
- **Virtual interfaces (VIFs).** Logical 802.1Q VLANs on top of the connection. **Private VIF** reaches private VPC resources (EC2, RDS) via a virtual private gateway or Direct Connect gateway. **Public VIF** reaches AWS public endpoints (S3, DynamoDB) over the DX path instead of the internet. **Transit VIF** reaches multiple VPCs through a Transit Gateway (via a Direct Connect gateway) for multi-account hybrid.
- **Routing.** BGP throughout: you control advertised prefixes, ASNs, and local-preference tags. This is also the risk surface, so route filtering and prefix control matter.
- **MACsec encryption.** IEEE 802.1AE Layer 2 encryption between your edge device and the AWS device at the DX location. It is near line-rate, point-to-point (hop-by-hop, encrypted on send and decrypted at the next hop), and supported on **dedicated 10 and 100 Gbps** connections at select PoPs, and since mid-2025 on supported partner interconnects. Encryption modes: `should_encrypt` (default, allows cleartext if MKA fails), `must_encrypt` (link drops if encryption fails), `no_encrypt`.
- **IPsec over DX.** For end-to-end encryption, or on hosted connections and 1 Gbps links that do not support MACsec, run a **Site-to-Site VPN over a public or transit VIF**. This gives an IPsec-encrypted private path (DX plus VPN).
- **SiteLink.** Connects two or more DX locations so traffic flows between your own sites across the AWS global backbone without touching an AWS Region. Requires BGP, supports private and transit VIFs, and supports MACsec where the port and PoP do.
- **Resilience.** Direct Connect Resiliency Toolkit, multiple connections, and LAGs for aggregation. A LAG aggregates bandwidth but does not by itself add path resilience.

## DX encryption and connectivity options compared

| Option | Layer / scope | Encrypts? | Use when |
|---|---|---|---|
| DX alone (private VIF) | Private path, no crypto | No | Consistent private reach to VPC, encryption not required or done at app layer |
| DX + MACsec | L2, edge-to-DX-device, hop-by-hop | Yes (in the link) | Dedicated 10/100 Gbps at a MACsec PoP, near line-rate needed |
| DX + IPsec VPN (public/transit VIF) | L3, end-to-end | Yes (end to end) | Hosted/1 Gbps links, or true end-to-end requirement |
| Internet VPN (no DX) | L3 over public internet | Yes | Light/occasional traffic, no DX presence |
| SiteLink | Site-to-site over AWS backbone | MACsec-dependent | Connect your own DX locations, bypass Regions |

## What gets tested

- **DX is not encrypted by default.** The classic trap. A scenario that says "we use Direct Connect so data in transit is protected" is wrong. Private path, yes; confidentiality, no, until MACsec or IPsec is added. If the requirement is encryption in transit, the answer names one of those, not DX itself.
- **MACsec vs IPsec-over-DX.** MACsec is Layer 2, near line-rate, dedicated 10/100 Gbps only, and only encrypts the single hop to the DX location (not end-to-end past the AWS device). IPsec over a VPN gives end-to-end encryption and works on hosted connections and lower speeds where MACsec is unavailable. Pick MACsec for high-bandwidth link encryption; pick IPsec-over-DX for end-to-end or when MACsec is not supported.
- **VIF selection.** Reach private VPC resources: private VIF. Reach S3/DynamoDB without the internet: public VIF. Fan out to many VPCs via Transit Gateway: transit VIF. Questions map the destination to the VIF type.
- **DX + VPN combo.** "Private, consistent, and encrypted" is DX for the path plus Site-to-Site VPN for the encryption, over a public or transit VIF. Recognize this as the standard regulated-hybrid answer.
- **What DX does and does not defend.** It removes public-internet exposure (DDoS surface, ISP variability) but does not provide encryption, IAM, or application security. It complements those controls, it does not replace them.
- **SiteLink for site-to-site.** When the need is data between two on-prem locations over AWS's backbone with no Region involved, that is SiteLink, not a Region-hosted Transit Gateway hairpin.

## Limitations

- No encryption in transit by default. This is the headline caveat; treating "private" as "secure" is the design error the exam probes.
- MACsec is constrained: dedicated 10/100 Gbps only, select PoPs (and supported partner interconnects), and it is hop-by-hop, so it protects the link to the DX device, not end-to-end into AWS. For end-to-end you still need application-layer TLS or IPsec.
- Hosted connections and 1 Gbps dedicated connections do not support MACsec; their only in-transit encryption option is an IPsec VPN over the VIF.
- BGP is the control plane and the risk surface. Without prefix filtering and route control, a misadvertisement can create a backdoor path between on-prem and AWS; DX does not police your routing for you.
- Provisioning is slow and physical. Cross-connect and colocation setup take weeks and carry facility fees separate from the AWS port charge, so DX is not a quick or low-commitment option like a VPN.
- A LAG increases bandwidth but not resilience. Real redundancy needs diverse connections/locations per the Resiliency Toolkit, not link aggregation alone.