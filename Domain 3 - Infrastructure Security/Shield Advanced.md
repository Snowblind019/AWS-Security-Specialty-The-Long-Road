# AWS Shield Advanced

AWS Shield Advanced is the paid tier of AWS's managed DDoS protection, adding to the automatic, free Shield Standard: L3/L4/L7 detection and mitigation, near-real-time attack visibility, 24/7 access to the Shield Response Team (SRT), DDoS cost protection, and automatic application-layer mitigation via WAF. Shield Standard is on by default for all customers and handles common network/transport (L3/L4) floods; Shield Advanced is for high-value, internet-facing workloads that cannot afford downtime. The thing to hold onto: Shield Standard is automatic and L3/L4 only, while Shield Advanced is an opt-in subscription that adds L7 protection, human response, cost reimbursement, and cross-account management, and the exam tests exactly where that Standard-to-Advanced line falls and which resource types are eligible.

## How it works

- **Subscription.** A flat $3,000/month per organization (payer), a **1-year commitment**, plus data-transfer-out usage fees. You then explicitly add protections to individual resources; subscribing alone does not protect anything.
- **Protected resource types.** CloudFront distributions, Route 53 hosted zones, Global Accelerator standard accelerators, ELB (ALB/CLB), and Elastic IPs (protecting EC2 and NLB via the EIP). You enroll each resource.
- **L3/L4/L7 mitigation.** Beyond Standard's network/transport coverage, Advanced adds application-layer (L7) protection, customizable detection thresholds tuned to your traffic baseline, and advanced routing that shifts attack traffic away from the app.
- **Automatic application-layer mitigation.** Shield Advanced can create and apply WAF rules in your web ACL to mitigate an L7 DDoS with no manual intervention (or run them in count-only mode first). This adds a rule group consuming 150 WCUs to the protection's web ACL.
- **Shield Response Team (SRT).** 24/7 DDoS experts who triage, find root cause, and apply custom mitigations on your behalf during an attack. Using the SRT requires **Business or Enterprise Support**.
- **Proactive engagement.** With Route 53 **health checks** associated with a protected resource, the SRT contacts you directly when a health check goes unhealthy during a detected event. Without health checks, proactive engagement does not work and you must notice the attack and open a case yourself.
- **Cost protection.** Reimburses DDoS-driven scaling charges (EC2, ELB, CloudFront, Global Accelerator, Route 53) when the resource was protected before the attack. L7 protection is included for up to 50 billion WAF requests/month per payer.
- **Multi-account and grouping.** **Firewall Manager** centrally applies Shield Advanced policies across an org (with the known exception that FMS Shield policies do not cover Global Accelerator or Route 53 hosted zones). **Protection groups** treat multiple resources as one unit for detection tuning. A delegated admin manages Shield across accounts.
- **Visibility.** CloudWatch attack metrics, the Shield console diagnostics, and a global threat-environment dashboard.

## Shield Standard vs Shield Advanced

| | Shield Standard | Shield Advanced |
|---|---|---|
| Cost | Free, automatic | $3,000/mo per org, 1-yr commit + DTO |
| Layers | L3/L4 | L3/L4 + L7 |
| Enrollment | Automatic | Explicit per resource |
| SRT access | No | Yes (needs Business/Enterprise Support) |
| Automatic L7 (WAF) mitigation | No | Yes |
| Cost protection | No | Yes (if protected pre-attack) |
| Custom thresholds / metrics | No | Yes |
| Multi-account (Firewall Manager) | No | Yes (not GA/Route 53 policies) |

## What gets tested

- **Standard vs Advanced boundary.** Automatic, free, L3/L4 is Standard. The scenario justifies Advanced only when it needs L7 protection, SRT, cost protection, custom detection, or multi-account governance. "We need protection against HTTP floods and a bill guarantee" is Advanced.
- **Advanced does not auto-protect.** After subscribing you must add protections to each resource (or use Firewall Manager). "Subscribed but a resource was still hit unmitigated" usually means it was never enrolled.
- **Proactive engagement needs Route 53 health checks.** The SRT only reaches out automatically when a health check tied to the protected resource fails. No health check means no proactive contact.
- **SRT requires Business/Enterprise Support.** A common trap: Shield Advanced alone is not enough to engage the SRT; the support tier is a prerequisite.
- **Eligible resource types.** CloudFront, Route 53, Global Accelerator, ELB, and EIP (for EC2/NLB). Something not fronted by one of these (a raw resource with no EIP) cannot be directly protected.
- **L7 mitigation is WAF-based.** Shield Advanced's application-layer defense works by placing WAF rules in your web ACL, so WAF is the enforcement mechanism; Shield orchestrates it.
- **Cost protection is conditional.** Reimbursement applies only if the resource was protected before the attack started; enrolling mid-attack does not retroactively qualify.

## Limitations

- Expensive and committed: $3,000/month per org with a 1-year term plus DTO fees, so it fits high-value targets, not every workload. Fronting apps with CloudFront and using Route 53 is a cheaper baseline mitigation on its own.
- Protection is opt-in per resource; nothing is covered until enrolled, and cost protection requires pre-attack enrollment.
- SRT access depends on Business or Enterprise Support, and proactive engagement depends on configured Route 53 health checks; without both, response is manual.
- Only specific resource types are eligible (edge/LB/EIP/DNS). Backends without one of those front doors are not directly protectable.
- Firewall Manager Shield Advanced policies do not cover Global Accelerator or Route 53 hosted zones, so those must be protected directly rather than via org policy.
- It defends availability against DDoS; it is not WAF for general web exploits, not a firewall, and does not replace least privilege, encryption, or Network Firewall. The automatic L7 mitigation still relies on WAF rules and WCUs in your web ACL.