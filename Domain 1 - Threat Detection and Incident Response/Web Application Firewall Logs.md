# AWS WAF Logs

Per-request logging of how a **web ACL** evaluated traffic: the request metadata, every rule group that was evaluated, which rule made the final call, and the terminating action (**ALLOW, BLOCK, COUNT, CAPTCHA, or CHALLENGE**). Each record is a **JSON document**, logging is off by default, and you configure it per web ACL. In the exam it is the **Layer 7** web-request audit trail used for rule tuning, forensics, and proving web-layer protection, and it is deliberately distinct from network-layer VPC Flow Logs.

The one-line role: WAF Logs are one JSON record per request showing the terminating rule and action plus all rule groups evaluated. Its lane is application-layer request logging, not L3/4 flow metadata (VPC Flow Logs) and not the lightweight sampled-requests view. The tested gotcha is the destination: CloudWatch Logs, S3, or Firehose, and whichever you choose, the destination name must start with **`aws-waf-logs-`**.

## How it works

- **Enablement**: a logging configuration on the web ACL. **Three destinations** are supported: **CloudWatch Logs**, **Amazon S3**, and **Amazon Data Firehose** (formerly Kinesis Data Firehose). You pick **one per configuration**, and fan out to more via Firehose. (The old "WAF can only log through Firehose" limitation is gone.)
- **Naming and placement**: the destination name must start with **`aws-waf-logs-`** for all three destination types (log group, bucket, or stream), and it must be in the **same account and Region** as the web ACL. For a **CloudFront (global) web ACL, logging must be in us-east-1**.
- **Record content**: JSON per request with `timestamp`, `action`, `terminatingRuleId` and `terminatingRuleType`, `httpRequest` (`clientIp`, `country`, `uri`, `method`, `headers`, `args`), `ruleGroupList` (all evaluated), `nonTerminatingMatchingRules` (matched but not decisive, as in COUNT), `rateBasedRuleList`, `labels`, CAPTCHA/CHALLENGE response, and `responseCodeSent`.
- **Redacted fields**: strip sensitive parts of the request (for example the `Authorization` or `Cookie` header, a query arg, or the body) from the logs. Redaction does **not** affect request sampling or Security Lake collection.
- **Log filtering**: WAF can log **only requests that meet conditions** (for example only BLOCK actions, or only requests carrying a given label) to control volume. This is native to WAF logging, not just a downstream Kinesis trick.
- **S3 delivery**: files land at roughly 5-minute intervals, compressed, under `AWSLogs/account-id/WAFLogs/Region/web-acl-name/YYYY/MM/dd/HH/mm`.
- **Related but separate**: `GetSampledRequests` gives a lightweight sample of up to 500 requests from the last 3 hours with no logging configuration, useful for a quick look but not a complete record. WAF logs can also be a native **Security Lake** source.

## Destination comparison

| Destination | Best for | Analysis tooling | Notes |
|---|---|---|---|
| CloudWatch Logs | Quick setup, near-term analysis, alarms | Logs Insights, metric filters | Simplest; higher cost at volume |
| S3 | Long-term storage, compliance, bulk analysis | Athena | Cheapest at volume; ~5-min batched, compressed |
| Amazon Data Firehose | Streaming to OpenSearch, Redshift, or a SIEM | Downstream tool | Most flexible; can transform in transit |

## What gets tested

- WAF Logs are the Layer 7 per-request record showing the terminating rule and action and every rule group evaluated. It is the web-application-firewall audit trail, distinct from VPC Flow Logs (Layer 3/4 network metadata) and from packet capture.
- The destinations are CloudWatch Logs, S3, or Firehose, one per configuration. The `aws-waf-logs-` prefix requirement is a classic trap: name the destination without it and WAF will not accept or list it.
- A CloudFront (global scope) web ACL must log in us-east-1. Regional web ACLs log in their own Region.
- `RedactedFields` removes sensitive data (Authorization, Cookie, body) from the logs, and it does not change request sampling or Security Lake collection.
- Log filtering lets you log only BLOCK or only label-matched requests to cut volume. It is a WAF-native capability, not only a Kinesis-side filter.
- Action values include ALLOW, BLOCK, COUNT, CAPTCHA, and CHALLENGE. COUNT mode records matches without blocking, which is the safe way to validate a rule (or an exclusion) before enforcing it.
- Analysis maps to the destination: Athena over S3, Logs Insights over CloudWatch, Firehose out to OpenSearch or a SIEM.
- Do not confuse full logging with `GetSampledRequests`, which is a 3-hour sample requiring no configuration.

## Limitations

- Off by default, one destination per configuration, and the `aws-waf-logs-` naming prefix is mandatory.
- Layer 7 only. It does not cover network-layer traffic (that is VPC Flow Logs) and never captures raw packets.
- High-traffic web ACLs with full request logging generate large volumes and cost. Use log filtering and redaction to keep it in check.
- Delivery is not instantaneous. S3 batches at roughly 5-minute intervals.
- It records enforcement, it does not enforce. Tuning still requires you to act on what the logs reveal, with rule exclusions and COUNT-mode testing.