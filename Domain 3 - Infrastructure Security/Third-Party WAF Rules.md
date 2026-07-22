# Third-Party WAF Rules

Third-party WAF rules are managed rule groups authored by security vendors (F5, Fortinet, Imperva, Trend Micro, Cyber Security Cloud, GeoGuard, and others) that you subscribe to through **AWS Marketplace** and plug into an AWS WAF web ACL alongside AWS-managed and your own custom rules. They give ready-made, vendor-maintained protection (OWASP Top 10, CMS-specific rules for WordPress/Joomla/Drupal, emerging CVEs, bot and reputation logic) without writing the detections yourself. The thing to hold onto: for the exam (Task 3.1.4), third-party rule groups are just another **managed rule group** inside a web ACL, so what matters is knowing they are Marketplace-subscribed and vendor-updated, how they sit next to AWS-managed and custom rules in the same ACL, and how you tune/override them, not the specifics of any one vendor.

## How it works

- **Subscription.** You subscribe to a vendor rule group in AWS Marketplace (or from the WAF console), and it becomes available to add to a web ACL. Billing flows through Marketplace at the vendor's price, on top of standard WAF web ACL, rule, and per-request fees.
- **Placement in the web ACL.** A third-party group is added as a **managed rule group** reference with a **priority**. Rules evaluate in priority order across custom rules, AWS-managed groups, and third-party groups in the same ACL, first terminating action wins.
- **What they cover.** Comprehensive OWASP Top 10 protection (SQLi, XSS, command/NoSQL injection, path traversal), application-stack-specific rules (Struts, Tomcat, WebLogic, WordPress, Drupal, Joomla), known-CVE and known-bad-input signatures, and vendor bot/reputation logic. Vendors write and update the rules continuously, so you inherit their threat research.
- **WCU cost.** Like any managed group, a third-party group consumes Web ACL Capacity Units against the 1,500 WCU budget; complex vendor groups can be WCU-heavy.
- **Tuning and override.** You cannot edit the internal rules, but you can override individual rules or the whole group to **Count**, scope-down with a statement (apply only to certain paths), and set the group's action override. Standard practice is to deploy in Count mode, tune against real traffic, then move to Block.
- **Scope and reuse.** The group lives in the ACL's scope (CloudFront global from us-east-1, or regional for ALB/API Gateway/AppSync/App Runner/Cognito), and the ACL can attach to multiple resources in that scope. Firewall Manager can push ACLs (including third-party groups) org-wide.

## Third-party vs AWS-managed vs custom rules

| | Third-party (Marketplace) | AWS Managed Rules | Custom rules |
|---|---|---|---|
| Author | Security vendor (F5, Fortinet, Imperva...) | AWS | You |
| Billing | Marketplace subscription + WAF fees | Free or add-on (Bot Control/ATP/ACFP) | Standard WAF fees |
| Maintenance | Vendor updates | AWS updates | You maintain |
| Editability | Not editable (override/count only) | Not editable (override/count only) | Fully editable |
| Best for | Vendor-specific coverage, CMS/stack, parity with an existing vendor | Baseline OWASP/bad-inputs/reputation | App-specific logic, exceptions |

## What gets tested

- **Third-party rules come from AWS Marketplace.** "Add vendor-maintained WAF protection" or "supplement AWS managed rules with F5/Fortinet/Imperva" is a Marketplace managed rule group subscription added to the web ACL. It is not a separate service and not a custom rule you write.
- **They coexist with AWS-managed and custom rules.** One web ACL can layer custom rules, AWS-managed groups, and third-party groups, ordered by priority. The exam tests that these combine in a single ACL rather than being mutually exclusive.
- **Tune in Count before Block.** You cannot edit vendor rules, but you can override to Count and scope-down to reduce false positives before enforcing. This is the standard managed-rule tuning workflow.
- **Managed vs custom trade-off.** Choose third-party/AWS-managed when you want low-maintenance, continuously updated coverage and less rule-writing; choose custom rules for app-specific logic and exceptions. Managed rules mean managed *content*, not managed *outcomes*, tuning is still yours.
- **WCU budget applies.** Adding heavy vendor groups can approach the 1,500 WCU ceiling, forcing simplification or a quota increase. Watch capacity when stacking multiple managed groups.
- **Firewall Manager for org-wide rollout.** Deploying the same third-party protection across many accounts is a Firewall Manager WAF policy, not per-account manual attachment.

## Limitations

- Vendor rules are opaque and not editable; you can only override, count, or scope-down. Deep customization requires your own custom rules or a programmable WAF outside AWS WAF.
- Managed does not mean tuned. False positives still need ongoing work, testing on real traffic, exceptions, and monitoring, and teams often get stuck in Count mode without the bandwidth to reach stable Block.
- Extra cost: Marketplace subscription fees stack on top of WAF web ACL, per-rule, and per-request charges, and WCU-heavy groups can trigger capacity overages.
- They inspect L7 HTTP/S only, on WAF-supported front ends, and share WAF's body-inspection cap; they do not protect raw TCP/UDP or backend VPC traffic (Network Firewall/security groups) or mitigate volumetric DDoS (Shield).
- Coverage quality depends on the vendor's update cadence and research; a poorly maintained group adds cost and WCU without proportional protection.
- Overlapping AWS-managed and third-party groups can double-cover or conflict, so priority ordering and per-rule overrides must be planned to avoid redundant blocking or WCU waste.