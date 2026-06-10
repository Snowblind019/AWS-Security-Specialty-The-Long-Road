# API Gateway Logs

API Gateway emits two kinds of logs to CloudWatch Logs: access logs (a per-request summary you design) and execution logs (a verbose internal trace for debugging). They show request traffic, caller identity, status, latency, and authorizer context at the API edge. Configured per stage; off by default.

The distinction that matters for security: access logs are a clean, customizable per-request record; execution logs are a deep internal trace that, at full verbosity, can capture request and response bodies and headers — including auth tokens. That makes execution logs both the most useful for debugging and the biggest data-exposure risk.

## How it works

- **Access logs**: one entry per request, in a format you define with `$context` variables (`identity.sourceIp`, `httpMethod`, `resourcePath`, `status`, `requestId`, `authorizer.claims`, `integration.latency`). Output as JSON/CLF/CSV to a CloudWatch Logs group per stage.
- **Execution logs**: verbose step-by-step detail (mapping templates, integration calls, authorizer decisions). Log level is OFF / ERROR / INFO per stage; INFO plus "log full request/response data" captures bodies and headers.
- Delivery is to **CloudWatch Logs**, not S3 directly. From there, subscription filters route to Firehose/Lambda and onward to S3, OpenSearch, Security Lake, or a SIEM.
- API Gateway needs an **account-level CloudWatch Logs role** (ARN set in API Gateway settings) with `logs:CreateLogGroup`, `logs:CreateLogStream`, and `logs:PutLogEvents`. Without it, execution logging will not write.
- REST APIs support both access and execution logs; HTTP APIs support access logs but not execution logs in the same form.

## API Gateway logs vs neighbors

| Source | Captures |
|---|---|
| Access logs | Per-request summary you design (caller, path, status, latency, claims) |
| Execution logs | Verbose internal trace; can include full request/response data |
| CloudTrail | Control-plane: who changed the API configuration |
| WAF logs | Which requests matched or were blocked at the WAF in front of the API |

## What gets tested

- Execution logs not appearing is almost always the missing account-level CloudWatch Logs role. That is the canonical fix.
- Execution logs at INFO with full-data logging capture sensitive payloads, headers, and tokens — a data-exposure risk. Keep the log level minimal in production, restrict and KMS-encrypt the log group, and avoid logging auth material.
- Access logs are per-stage and fully customizable via `$context`; design them to capture caller identity and authorizer claims for incident response.
- Logs land in CloudWatch Logs; route them onward to S3 or a SIEM with subscription filters.
- Correlate API Gateway logs with WAF logs (what the WAF did) and CloudTrail (who changed the API).
- `$context.authorizer.claims` and `$context.identity.sourceIp` answer "who called this, and from where."

## Limitations

- Execution logs are verbose, costly, and can leak sensitive data; use sparingly.
- Requires the CloudWatch Logs role configured at the account level.
- Access log format must be defined by you; nothing is captured by default.
- HTTP APIs do not offer execution logs the way REST APIs do.
- Delivery is near-real-time via CloudWatch, not instantaneous.