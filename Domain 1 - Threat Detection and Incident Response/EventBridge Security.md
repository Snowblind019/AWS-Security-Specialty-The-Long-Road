# EventBridge Security

## What Is EventBridge

Amazon EventBridge is a fully managed **event bus service** that connects application components using events. It allows AWS services, custom applications, and third-party SaaS apps to communicate **asynchronously** via event routing, without direct coupling.

It supports:

- **Event sources**: AWS services, SaaS apps, custom apps  
- **Event buses**: default, custom, partner  
- **Rules**: pattern matchers that route events  
- **Targets**: Lambda, SQS, Step Functions, Kinesis, etc.

### Why security matters:

EventBridge is often **invisible in architectures**. It operates behind the scenes, quietly moving **sensitive data** — user activity logs, transactions, CloudTrail alerts, GuardDuty findings — from one system to another.

Attackers can exploit misconfigured EventBridge setups to:

- Inject fake events (spoofed security alerts, phantom jobs)  
- Exfiltrate data via unmonitored rules/targets  
- Escalate privileges by triggering overprivileged targets  
- Mask lateral movement using internal buses

---

## Cybersecurity Analogy

Imagine EventBridge is your **interoffice mail system**. Employees drop in requests, forms, memos — and mailroom staff route them to the right teams.

But:

- If anyone can drop anything into the system, **fake memos** start circulating  
- If mail is auto-routed to sensitive departments without verification, it’s a **free-for-all**  
- If there's no **audit trail**, you’re blind

> That’s EventBridge without security.

## Real-World Analogy

Let’s say **SnowyCorp** uses a digital ticketing system where anyone can submit service requests that get auto-routed via keywords (e.g., "VPN" goes to IT).

Now imagine:

- An attacker learns the internal format  
- Submits crafted events with "exec" or "finance" tags  
- Events get routed to sensitive internal systems  
- No one realizes this until it's too late

> EventBridge works the same way — and without strict rules, IAM scoping, and monitoring, any app with `PutEvents` permission becomes a potential insider threat.

---

## How It Works / What to Secure

### 1. Event Buses and Scoping

EventBridge has **three bus types**:

- **Default Event Bus**: receives events from AWS services (CloudTrail, EC2, etc.)  
- **Custom Event Buses**: receive events from your own apps/services  
- **Partner Event Buses**: receive events from trusted SaaS partners

**Best practices:**

- Don’t let untrusted producers write to the default bus  
- Use custom buses for separation of environments (dev/test/prod)  
- Attach **resource policies** to custom buses to restrict who can publish  
- Use naming conventions:  
  - `eventbus-prod-payment`  
  - `eventbus-dev-analytics`  

→ This minimizes accidental cross-talk or privilege confusion.

### 2. IAM Permissions (PutEvents, Rule, Target)

The most sensitive permission in EventBridge is:

- `events:PutEvents` — injects events into any bus the principal can access

Other important permissions:

- `events:PutRule` — create new rules  
- `events:PutTargets` — route events to services  
- `events:DeleteRule`, `events:RemoveTargets` — sabotage detection  

**IAM hardening tips:**

- Scope `PutEvents` to **only the bus ARN needed**  
- Scope `PutTargets` to **specific targets** (e.g., Lambda ARNs)  
- Use IAM **condition keys**:  
  - `events:EventBusName`  
  - `events:Source`  
  - `events:DetailType`

### 3. Event Injection and Spoofing Protection

**Threat**: an attacker with `PutEvents` access injects a **fake event** that triggers:

- A Lambda to process payroll  
- A Step Function to escalate privileges  
- A security alert to mask real ones

**Mitigations:**

- Use **strict event pattern matching**:
  - Match on `source`, `detail-type`, `account`, and specific keys in `detail`
- Avoid overly broad patterns:
  ```json
  { "source": [ { "prefix": "" } ] }
  ```
- Validate events **at the target** (e.g., Lambda code should verify schema)  
- Optionally, use **EventBridge Schema Registry** to enforce structure

### 4. Monitoring and Logging

EventBridge does **not natively log every event** — this is a **major visibility gap**.

To monitor activity:

- Enable **CloudTrail**:
  - Logs API calls (`PutEvents`, `PutRule`, `PutTargets`, etc.)
- Enable **CloudWatch Logs** at the target level (Lambda, Step Functions)
- Use **metrics**:
  - `Invocations`
  - `FailedInvocations`
  - `ThrottledRules`
  - `MatchedEvents`
- Set up **alarms**:
  - Sudden surge in `PutEvents`
  - New rules created unexpectedly in prod
  - Spikes in delivery failures

### 5. Cross-Account Access

For centralized architectures (e.g., SecOps account), use **resource policies** on the event bus:

```json
"Condition": {
  "StringEquals": {
    "aws:PrincipalAccount": "123456789012"
  }
}
```

**Best practices:**

- Allow only specific AWS Account IDs  
- Deny all by default  
- Avoid `Principal: *` unless absolutely required

### 6. Targets and Least Privilege

EventBridge can trigger:

- Lambda  
- Step Functions  
- Kinesis  
- SNS / SQS  
- EC2 Automation  
- ECS Tasks  

**Every target needs IAM permissions to do its job — not more.**

Examples:

- Lambda with broad `s3:*` access = exposure risk  
- Step Function that can assume a high-priv role = lateral movement pivot  

Use **least privilege roles** on the targets and **monitor invocation chains**.

### 7. Encryption and Transport Security

- All EventBridge communication is over **TLS 1.2+**  
- Events are **not encrypted at rest**, unless you:
  - Use **Kinesis** (with KMS)
  - Use **SQS/SNS** with KMS  
  - Manually encrypt the data inside the event `detail`

> For highly sensitive data, don’t send secrets in plaintext inside events.

---

## Pricing Models

| Component                    | Pricing                                |
|------------------------------|----------------------------------------|
| **PutEvents**                | $1 per million events                  |
| **Rules (triggered)**        | $1 per million event-matches           |
| **Schema Registry**          | Free for discovery + code binding      |
| **Custom Buses**             | No additional cost                     |
| **Cross-account delivery**   | Same pricing, but data transfer may apply |
| **EventBridge Pipes**        | Charged separately if used             |

> You also pay for downstream targets — Lambda, SQS, etc.

---

## Real-Life Snowy-Style Example

**Winterday** has a **centralized security account** where GuardDuty and CloudTrail events are forwarded from **12 AWS accounts** via EventBridge.

### Attack Scenario:

- A compromised IAM user in a dev account has `events:PutEvents` to the central bus  
- Attacker injects **1,000 fake GuardDuty findings** to mask real ones  
- Ops team drowns in false positives, **misses a real S3 exfiltration**

### Fix:

- Snowy attaches **resource policy** on the central event bus:
  ```json
  "Condition": {
    "StringEquals": {
      "aws:PrincipalTag/SecurityProducer": "true"
    }
  }
  ```
- Adds tight **event pattern matchers**:
  - Only accept events from `"source": "aws.guardduty"`, with known account and region
- Enables **CloudTrail alerting** on new `PutEvents` from unknown accounts  
- **Targets (e.g., Lambda)** verify the payload before acting

> Now even if access is misused, **fake events won’t match**, and **targets won’t act** without validation.

---

## Final Thoughts

**EventBridge is powerful, invisible, and dangerous when misconfigured.**  
It routes sensitive events silently — and if abused, can become a **covert control plane for attackers**.

### Security Priorities:

- Scope `PutEvents` tightly  
- Monitor rule creation/modification  
- Validate events  
- Harden targets  
- Use cross-account policies cautiously  

> Treat EventBridge like a **secured message bus**, not a fire-and-forget notification system.  
> It can be your **security automation backbone** — or your **weakest link**.
