# AWS WAF (Web Application Firewall)

AWS WAF is a Layer 7 web application firewall that monitors and filters HTTP/S requests to your applications based on rules, protecting against common web exploits (SQL injection, XSS), bad bots, credential stuffing, and malicious or high-risk sources. It attaches in front of specific AWS resources, not an EC2 instance directly: CloudFront, ALB, API Gateway, AppSync, Cognito user pools, App Runner, and Amplify. It inspects HTTP method, URI, query strings, headers, cookies, and body. The thing to hold onto: WAF is application-layer, request-by-request filtering bound to a **web ACL** on a specific resource, so the exam tests when WAF (L7 web exploits) is the answer versus Shield (DDoS), Network Firewall (VPC traffic), or a security group (IP/port), and the scope rule that a CloudFront web ACL is global while ALB/API Gateway web ACLs are regional.

## How it works

- **Web ACL.** The container you associate with a protected resource. It holds rules and rule groups and a default action (allow or block) for requests that match nothing.
- **Rule types.** IP set match, geo match, string/regex match on any request component, size constraint, **rate-based** rules (auto-block sources over a threshold), and SQLi/XSS match statements. Rules are evaluated in **priority order** and processed until a terminating action fires.
- **Actions.** `Allow`, `Block`, `Count` (log without blocking, for tuning), plus **CAPTCHA** (interactive puzzle) and **Challenge** (silent JS browser check). CAPTCHA/Challenge only apply to `GET text/html`, not POST or CORS preflight.
- **Managed rule groups.** AWS-maintained sets: Common Rule Set (OWASP-style), SQLi, Known Bad Inputs, Amazon IP Reputation, Anonymous IP, and paid add-ons: **Bot Control** (common and targeted bots), **Account Takeover Prevention (ATP)** for login flows, and **Account Creation Fraud Prevention (ACFP)** for signup. Mix managed with custom rules; you can override individual managed-rule actions.
- **Rate-based rules.** The standard answer to brute force, scraping, and L7 floods. Default aggregation is client IP, but you can key on forwarded IP (X-Forwarded-For), a header, cookie, query arg, URI path, or a custom combination, and scope-down to a path.
- **WCU (Web ACL Capacity Units).** Every rule has a WCU cost; a web ACL has 1,500 WCUs before extra request fees or a quota increase. Complex rule groups consume capacity fast, so WCU budgeting matters.
- **Body inspection cap.** WAF inspects only the first part of the body (default 8 KB on CloudFront, 16 KB elsewhere), so oversized bodies can bypass content rules unless you raise the limit (at extra cost).
- **Visibility.** Per-request logging to CloudWatch Logs, S3, or Kinesis Firehose, plus CloudWatch metrics and sampled requests.
- **Centralization.** **Firewall Manager** applies WAF policies org-wide; **Shield Advanced** includes WAF on protected resources and uses it for automatic L7 DDoS mitigation.

## WAF vs the other filtering layers

| | WAF | Shield (Std/Adv) | Network Firewall | Security group |
|---|---|---|---|---|
| Layer | L7 HTTP/S | L3/L4 (Std), +L7 (Adv) | L3-L7 VPC traffic | L3/L4 |
| Inspects | Requests (URI, headers, body) | Traffic volume/patterns | Packets, domains, Suricata | IP/port |
| Attaches to | CloudFront/ALB/API GW/AppSync/Cognito/App Runner | Edge/LB/EIP/Route 53 | VPC via routing | ENI |
| Stops | SQLi, XSS, bots, L7 floods (rate rules) | DDoS | Egress, east-west, IDS/IPS | Reachability |

## What gets tested

- **WAF for web exploits, not DDoS or IP/port.** SQLi, XSS, bad bots, and application-layer request filtering are WAF. Volumetric DDoS is Shield; VPC/egress/domain filtering is Network Firewall; IP/port allow is a security group. Match the layer to the threat.
- **Scope: CloudFront is global, ALB/API Gateway is regional.** A CloudFront web ACL is created in the global (us-east-1) scope; ALB, API Gateway, and AppSync ACLs are regional in the resource's Region. "Why won't my ACL attach to the CloudFront distro from eu-west-1" is the scope rule.
- **Rate-based rules for brute force/scraping/L7 flood.** Auto-blocking sources over a threshold, optionally keyed on a header or scoped to the login path, is the WAF answer for credential stuffing and scraping.
- **CAPTCHA/Challenge for automation.** Separating humans from bots on sensitive actions is CAPTCHA (interactive) or Challenge (silent), applied to GET HTML requests, often after Bot Control filters the obvious ones.
- **Managed rules for baseline, then tune with Count.** Start with AWS managed rule groups plus IP reputation, run new rules in **Count** mode to avoid false positives, then switch to Block. This tuning workflow is a frequent best-practice question.
- **Fraud/bot add-ons for account abuse.** Credential stuffing on login is **ATP**; fake-account creation on signup is **ACFP**; scraping/inventory bots are **Bot Control**. Scope them to the relevant path to control cost.
- **WAF + Shield Advanced for L7 DDoS.** Shield Advanced's automatic application-layer mitigation places WAF rules in your web ACL, so WAF is the enforcement mechanism for L7 DDoS.

## Limitations

- L7 HTTP/S only, and only on supported front-end resources. It cannot protect raw TCP/UDP, backend VPC traffic, or a bare EC2 instance; those need Network Firewall or security groups.
- Body inspection is capped (8 KB CloudFront / 16 KB regional by default), so large payloads can evade content rules unless the limit is raised at extra cost.
- WCU limits (1,500 per web ACL) constrain rule complexity; heavy managed groups can exhaust capacity and trigger overage fees or quota requests.
- Pricing compounds across web ACL, per rule, per million requests, and add-on groups (Bot Control, ATP, ACFP), with fraud tiers reaching very high per-request rates, so rules must be scoped and tuned.
- WAF reduces but does not eliminate attacks and can false-positive; rules need Count-mode monitoring and ongoing tuning, and it does not replace IAM, encryption, or input validation in code.
- It is not a DDoS service on its own; volumetric protection is Shield, and WAF's L7 flood defense (rate-based rules, Shield Advanced automation) complements rather than replaces it.