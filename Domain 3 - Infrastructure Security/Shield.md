# AWS Shield Standard

AWS Shield Standard is the free, always-on DDoS protection tier that AWS applies automatically at the edge to every customer. It defends against the common volumetric and state-exhaustion attacks that live at Layers 3 and 4 (SYN floods, UDP reflection, NTP and DNS amplification) and it does so with no opt-in, no configuration, and no tuning. The catch is that it only intercepts traffic on services that route through the AWS edge or network layer, so an app sitting on a raw EC2 public IP gets nothing until you front it. The thing to hold onto: Shield Standard is automatic L3/L4 availability protection at the edge, it stops nothing at the application layer (that is WAF and Shield Advanced), and it only protects the specific fronting services that let AWS see the traffic first.

## How it works

- **It runs at the edge, not on your instance.** Traffic to CloudFront, Route 53, Global Accelerator, and the elastic load balancers passes through AWS-managed infrastructure where Shield inspects it before it reaches your origin. This edge position is the whole reason it can absorb volumetric floods.
- **Detection is signature and anomaly based.** A global sensor network watches packet rates, source patterns, and known DDoS signatures across AWS, then flags SYN floods, DNS query floods, and reflection or amplification traffic.
- **Mitigation is automatic and silent.** When an attack is detected, Shield deploys drops, filters, and rate limits inline. There is no console to watch, no rules to write, and by design no per-customer dashboard on the Standard tier.
- **Coverage follows the fronting service, not the account.** You are protected wherever your traffic enters through a supported edge or load-balancing service. Expose a workload directly on an EC2 public IP and it sits outside that intercept path.
- **Scope is strictly L3/L4.** It handles the network and transport layers. Anything that is a valid-looking HTTP request (application-layer floods, credential stuffing, checkout-API abuse) passes straight through to be handled by WAF or Shield Advanced.

## Shield Standard vs the rest of the DDoS/app stack

| Layer / control | What it handles | Where Shield Standard sits |
|---|---|---|
| **Shield Standard** | Automatic L3/L4 DDoS at the edge | Always on, free, no config |
| **Shield Advanced** | Deeper L3-L7 detection, WAF auto-mitigation, cost protection, SRT | Paid opt-in above Standard |
| **AWS WAF** | L7 request filtering: rate-based rules, injection, bad bots | You configure it; Standard does not touch L7 |
| **Fronting service** | CloudFront / Route 53 / GA / ELB puts traffic on the edge | Prerequisite for Standard to see traffic at all |

## What gets tested

- **L3/L4 vs L7 boundary.** If the scenario is an HTTP flood, credential stuffing, or API abuse, Shield Standard is the wrong answer and WAF (or Shield Advanced) is right. Standard only covers network and transport layer floods.
- **Automatic vs opt-in.** Standard is on for everyone with zero setup. Advanced is the paid tier you enable for deeper detection, the Shield Response Team, and DDoS cost protection.
- **Coverage requires a fronting service.** A public EC2 instance with no CloudFront, ALB/NLB/CLB, Route 53, or Global Accelerator in front is not meaningfully protected. The exam tests whether you know Standard needs the traffic on the edge.
- **No visibility on Standard.** If the requirement is DDoS metrics, attack diagnostics, or notification, that is Shield Advanced, not Standard.

## Limitations

- No application-layer protection. HTTP floods and any attack made of valid-looking requests pass through untouched.
- No dashboards, no attack reports, no alerts, and no access to the Shield Response Team. Those all belong to the Advanced tier.
- Protection is confined to CloudFront, Route 53, Global Accelerator, and the elastic load balancers. Raw EC2 public IPs and unsupported entry points fall outside it.
- No DDoS cost protection. If an attack scales your resources, the Standard tier does not absorb the resulting bill the way Advanced does.
- You cannot tune it. There are no thresholds, rules, or knobs to adjust, so where Standard's automatic mitigation is not enough you must move up to Advanced plus WAF.