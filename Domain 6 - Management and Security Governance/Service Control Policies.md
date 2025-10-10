# AWS Service Control Policies (SCPs)

## What Is an SCP
An SCP (Service Control Policy) is a guardrail policy attached to an AWS Organization, used to define the **maximum allowable permissions** for accounts inside that organization or organizational unit (OU). Think of it as a permission boundary — but at the **account level**, not just the role/user level.

- It **doesn’t grant permissions** on its own.
- It **limits what IAM policies can grant** inside the account.
- SCP = Guardrails for what IAM can even attempt to do.

**Why this matters:**
- Prevents accidental privilege escalation
- Ensures compliance boundaries (e.g., “No one can create resources in `us-east-1`”)
- Useful for delegated accounts, sandbox accounts, and child OUs
- Critical for multi-account security and central governance (CIS, NIST, PCI-DSS, etc.)

---

## Cybersecurity Analogy
Think of SCPs like a **locked cabinet of permissions** handed to each department (account). Even if someone in the department has a key (IAM permission), they can’t open drawers that are glued shut by the cabinet owner (the organization’s SCP).

> IAM might say:
> “Sure, Snowy can delete an S3 bucket!”

> But SCP says:
> ❌ “No one in this account is allowed to call `s3:DeleteBucket`. Period.”

Even the **root user is bound** by this.
SCPs override all roles, users, and session permissions at the **boundary level**.

## Real-World Analogy
Imagine an **office building** (AWS Org) with multiple departments (accounts). Each department gets a set of keys (IAM policies) for drawers and rooms. But the **building manager installs locks** on the power grid, server room, and exit doors.
Even if a department manager gives someone keys, if the **building-wide locks** say “no,” those keys do nothing.

**SCPs are those top-level locks** — enforced before any role, user, or application gets to do anything.

---

## How SCPs Work

### 1. Only Work Inside AWS Organizations
- SCPs **only apply** to accounts managed under **AWS Organizations**.
- You must enable **All Features** mode (not consolidated billing only).

### 2. Are Attached to OUs or Accounts
You can attach an SCP to:
- An **Organizational Unit (OU)**
- An **individual account**

They **cascade down** from parent → child.

### 3. Control the Maximum Permissions Allowed
- SCPs don’t grant permissions.
- They **filter down** what IAM policies can be evaluated.

### 4. Evaluation Logic: “Allow if Both Say Yes”
> **Final Permission = SCP says "Allow" AND IAM says "Allow"**
> If **either** says “Deny” → access is denied.

### 5. Explicit Deny Always Wins
If an SCP contains `Effect: Deny`, it overrides **everything**, including IAM `Allow`.

---

## SCP vs IAM vs Permission Boundaries

| **Feature**            | **SCP**                | **IAM Policy**         | **Permission Boundary**     |
|------------------------|------------------------|------------------------|-----------------------------|
| **Scope**              | Account / OU           | User / Role / Group    | Role / Session              |
| **Evaluated By**       | AWS Org                | IAM Engine             | IAM Engine                  |
| **Grants Permissions?**| ✖️ No                  | ✔️ Yes                 | ✖️ No                       |
| **Can Restrict Root?** | ✔️ Yes                 | ✖️ No                  | ✖️ No                       |
| **Use Case**           | Org-wide governance     | Access control         | Scoped delegation           |

---

## Common Use Cases

### Restrict Regions
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Deny",
    "Action": "*",
    "Resource": "*",
    "Condition": {
      "StringNotEquals": {
        "aws:RequestedRegion": "us-west-2"
      }
    }
  }]
}
```
> This blocks everything that isn’t in us-west-2, no matter the IAM policy.

### Block Expensive Services
```json
{
  "Effect": "Deny",
  "Action": [
    "ec2:RunInstances",
    "redshift:*",
    "athena:*"
  ],
  "Resource": "*"
}
```

### Prevent IAM Role Creation
```json
{
  "Effect": "Deny",
  "Action": "iam:CreateRole",
  "Resource": "*"
}
```

### Enforce Tagging Standards
```json
{
  "Effect": "Deny",
  "Action": "*",
  "Resource": "*",
  "Condition": {
    "StringNotEqualsIfExists": {
      "aws:TagKeys": ["Environment", "Owner"]
    }
  }
}
```

### Ensure Root Account Can't Be Used
```json
{
  "Effect": "Deny",
  "Action": "*",
  "Resource": "*",
  "Condition": {
    "StringEquals": {
      "aws:PrincipalAccount": "123456789012",
      "aws:PrincipalType": "Account"
    }
  }
}
```

## Best Practices

- Use a “Deny List” model — block specific sensitive APIs or conditions
- Avoid blanket Allow policies — SCPs should restrict, not grant
- Test with delegated admin accounts before enforcing org-wide
-️ Use `Conditions` to limit by region, tag, VPC, IP, MFA status, etc.
- Name policies clearly — e.g., `Deny-ECR-CrossRegion`, `Enforce-Tagging-Standards`

---

## Real-Life Example: Snowy’s Security Governance

Snowy’s company manages:
- A **production OU**
- A **sandbox OU**

For **sandbox**:
- SCP denies:
  - `iam:*`
  - `organizations:*`
  - `ec2:RunInstances`

  - **Cross-region S3**
- IAM roles inside are free to play — but **guardrails are hard-coded**

For **production**:
- SCP allows **only**:
  - Region: `us-west-2`
  - Approved services like **RDS**, **Lambda**, **ECS**

Even if someone adds a **wildcard IAM role**, it will be **ignored** if it conflicts with the SCP.

Snowy’s team gets **CloudTrail logs** showing attempted violations — and tunes the guardrails accordingly.

---

## Final Thoughts

SCPs are the **silent enforcers** of AWS Organizations — often overlooked, but foundational for **serious multi-account governance**.

They don’t replace IAM — they **limit its power**. Think of them as:
- A “**maximum permissions ceiling**”
- A way to **ensure root user restrictions**
- Your **last line of defense** against accidental overreach

---

If you're prepping for interviews or security reviews, expect to be asked:

> **“How do you ensure accounts can’t break out of compliance?”**

With SCPs, you can say:
- Every account has a **least-privilege boundary**
- **Root access is governed**
- **Cross-region risk and sensitive APIs are blocked**
- **No team can over-provision — even accidentally**
