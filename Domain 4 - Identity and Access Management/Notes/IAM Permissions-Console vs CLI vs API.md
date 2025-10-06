# IAM Permissions: Console vs CLI vs API  

## What Is This

At first glance, IAM permissions in AWS seem straightforward. You define an action, attach it to a user, role, or group, and the principal is granted or denied access.  
But here’s the catch:  
The same permission can behave differently — or even fail silently — depending on how it's invoked:

- AWS Management Console (web interface)  
- AWS CLI or SDKs (programmatic)  
- Direct API calls (under-the-hood services, automation, abuse)

This leads to:

- Privilege escalation that works only via the console  
- Detection blind spots in automation paths  
- Permissions that look correct but fail for certain methods  
- Unexpected behavior during incident response or red team simulations  

Understanding the execution context of a permission is critical. It’s not just “does this user have s3:PutObject” — it’s “how are they calling it?”

---

## Cybersecurity Analogy

Picture a building with three entrances:  

- Front door (the AWS Console) — full concierge support, sign-in logs, forms, buttons.  
- Side loading dock (CLI) — technical staff who skip the front desk and bring a pallet jack.  
- Secret service tunnel (API calls) — automated robots coming in by blueprint, no small talk.  

Even if you authorize someone to enter Room 301, that doesn't mean every door to Room 301 is accessible the same way.  
Some IAM paths are console-only helpers. Others are raw underlying APIs.

---

Snowy gives Winterday permission to `iam:CreateUser`. From the console, Winterday can create a new IAM user just fine.  
But from the CLI? It fails.  

**Why?**  
The console doesn’t call `CreateUser` directly.  

It might use chained API calls, session tagging, STS proxy assumptions, or even invoke non-obvious APIs under the hood.

---

## Console vs CLI vs API — How They're Different


| Method    | What It Is             | Characteristics                                            |
|-----------|------------------------|------------------------------------------------------------|
| Console   | Web UI interface       | Friendly UI, often invokes multiple APIs behind the scenes |
| CLI/SDK   | Command-line tools / code wrappers | Makes direct API calls, 1:1 with IAM permission granularity |

| API (raw) | STS/HTTPS calls directly | Low-level, scriptable, stealthy if not logged or scoped     |

---

## Why This Matters

- Some IAM permissions are used only by the console (e.g., `iam:ListAccountAliases` is required for login screen customization)  
- Console may invoke multiple actions at once (creating an EC2 instance involves 12+ API calls)  
- CLI/SDK calls may lack context (no browser session, UI session tags, or default region)  
- Raw API abuse is common in breaches, especially through credential theft or signed STS tokens  

---

## Case Study: s3:GetObject

Let’s say a role has this policy:

```json
{
  "Effect": "Allow",
  "Action": "s3:GetObject",
  "Resource": "arn:aws:s3:::snowy-data/*"
}
```

**In the Console:**  
This allows downloading files from the bucket via the web UI  

**In the CLI:**  
Works the same with `aws s3 cp` — but only if AWS CLI v2 is configured with the correct profile and region  

**In the API:**  
Attackers could generate a signed URL, inject it into another session, or use STS credentials with no MFA — unless your policy has conditions that explicitly block anonymous API paths  

---

## Edge Case: IAM PassRole

Example: To let a user launch an EC2 instance with a role, you must grant:

```json
"iam:PassRole"
```

But:

- In the console, this action is abstracted — you select the role from a dropdown  
- In the CLI, you must specify the exact role ARN  
- If your policy doesn’t use a resource condition, an attacker can PassRole to any compatible resource via automation  

---

## Detection Relevance

### Console Behavior:

- Often batches multiple actions — makes reverse engineering harder  
- Uses console-only actions like:  

  - `aws-portal:*`  
  - `iam:ListAccountAliases`  
  - `sso:ListInstances`  

### CLI/API Behavior:

- More direct, more granular  
- Can expose misconfigured wildcards, like:  
  - `s3:*`  
  - `ec2:Describe*`  
- More likely to be abused in red team scenarios or real breaches  

### Detection Tip

Use CloudTrail's `eventSource` and `userAgent` fields to tell where the action came from.

| User Agent            | Source Type         |
|-----------------------|---------------------|
| signin.amazonaws.com  | Console UI          |
| aws-cli/2.15.32       | CLI v2              |
| Boto3/1.26.144        | Python SDK          |
| aws-internal/         | Internal service call|
| curl/7.64.1           | Manual or script abuse|

---

## Real-Life Snowy Scenario

Snowy is debugging why Winterday’s role can’t create a CloudFormation stack from the CLI.  

The role has:

- `cloudformation:CreateStack`  
- `iam:PassRole`  
- `s3:GetObject` (for pulling the template)  

Winterday tries in the CLI — fails with AccessDenied.  

Turns out:

- Console uses `sts:AssumeRoleWithWebIdentity`  
- Winterday's CLI session wasn’t exporting correct session tags  
- The stack’s IAM role had a trust condition requiring `aws:PrincipalTag` that never showed up in the CLI session  

**Conclusion:** Permissions looked right, but failed due to context mismatch between console and CLI.

---

## Summary Table: Key Differences

| Action Type                | Console | CLI  | API         |
|---------------------------|---------|------|-------------|
| Abstracted Multi-Call Flows| ✔️ Yes     | ✖️ No   | ✖️ No          |
| Requires Additional Permissions| 🟣 Sometimes| ✖️ Rarely| ✖️ Rarely    |
| Human-Readable Error Messages| ✔️ Yes   | Minimal| No         |
| Used by Attackers          | Rare    | Common| Very Common |
| Session Context (tags, UI state)| ✔️ Yes| 🟣 Must be manually set| 🟣 Must be manually signed or injected |

---

## Final Thoughts

If you're writing IAM policies or performing incident response and you're not thinking about how the action was executed, you're missing part of the story.  

- Console behavior hides complexity — great for users, dangerous for architects.  
- CLI/API shows the raw edges — often what attackers and automation use.  
- Some permissions only exist to support the console, and you’d never know from CloudTrail alone.

### When designing roles:

- Test in all three contexts  
- Use explicit deny + conditions to scope API use paths  
- Monitor `userAgent` in CloudTrail to catch strange usage patterns

