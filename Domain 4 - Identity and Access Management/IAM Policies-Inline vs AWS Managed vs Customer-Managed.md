# IAM Policies: Inline vs AWS Managed vs Customer-Managed

## What Is This

When you create IAM identities — users, roles, or groups — you need a way to define what they’re allowed to do. That’s what IAM policies are: they’re the permission blueprints. But in AWS, there’s more than one type of policy — and which one you use affects security, auditability, blast radius, and lifecycle management.

The three types:

- **AWS Managed Policies** – created and updated by AWS
- **Customer-Managed Policies** – written and owned by you
- **Inline Policies** – directly embedded into a specific IAM identity

On the surface, they all control access. But under the hood?
They impact reuse, versioning, policy hygiene, detection, and governance in completely different ways. If you're building secure multi-account environments or trying to detect overprivileged roles, understanding this separation of policy types is foundational.

---

## Cybersecurity Analogy

Imagine you're running a data center:

- **AWS Managed** is like using a generic master key provided by the landlord. It unlocks all common rooms, it’s convenient, but you don’t control it — and the landlord may change the locks without telling you.
- **Customer-Managed** is your team creating a secure, custom master key that only opens the doors you want, with logs tracking every cut and who has one.
- **Inline Policies** are when you take a key, weld it to someone's badge, and never make a copy. That key can’t be reused, audited, or easily revoked at scale — but it’s ultra-specific and tied to just that one person.

## Real-World Analogy
Picture Snowy building access at a NOC.

- All new techs are given a standard access sheet printed by HR (AWS Managed).
- For Dallas, you create a special laminated sheet granting him access to fiber splice rooms only (Customer-Managed).
- Then Nathan gets a one-time Post-it stuck inside his locker giving him single-use access to the rooftop panel (Inline).

Guess which one gets forgotten during audits and ends up as a shadow permission?

---

## How It Works

All three policies define a Statement block with Effect, Action, Resource, and optional Condition.
The real difference is how they’re stored, who controls them, how they’re reused, and what audit metadata exists.

---

### AWS Managed Policies

- Created and maintained by AWS (you can’t edit them)
- Updated without your input
- Same policy is available to every AWS customer
- No version control
- Often overly broad (e.g., PowerUserAccess gives full access except IAM & billing)

**Best for:**

- Quick starts
- Temporary roles
- Service-linked roles (some require them)

**Security Caveats:**

- You don’t control updates. AWS might add new permissions over time.
- You can’t limit the scope via resource tags unless wrapped in SCPs or permission boundaries.

### Customer-Managed Policies

- Created and owned by you
- Stored centrally in your account’s policy namespace
- Attach to multiple roles/users/groups
- You can version, update, document, and automate them
- Show up in IAM Access Analyzer, Security Hub, etc.

**Best for:**

- Production permissions
- Least privilege enforcement
- Detection-friendly governance
- Tag-based delegation and permission boundaries

**Security Caveats:**

- Still need to manage lifecycle (e.g., decommission old versions)

- Still prone to privilege creep if reused too broadly

### Inline Policies

- Embedded directly into a specific user/role/group
- One-to-one relationship
- Not reusable
- Not versioned
- Easy to forget — especially if the user is deleted or replaced
- Don’t show up in list-policies, only visible on the identity itself

**Best for:**

- Short-term delegation (“let Snowy assume this role just for this week”)
- Highly scoped emergency access
- Edge cases like break glass accounts or temp contractors

**Security Caveats:**

- No audit trail for version history
- Easy to lose visibility
- Tools like Access Analyzer or IAM Access Advisor can miss them in rollups

---

## Pricing Models

There’s no direct cost to using any policy type.
But the operational cost (in time, risk, misconfiguration, and audit complexity) is massive:

| Policy Type       | Direct Cost | Operational Risk                     |
|-------------------|-------------|--------------------------------------|
| AWS Managed       | Free        | Medium – risk of AWS changes silently|
| Customer-Managed  | Free        | Low – your version, your guardrails  |
| Inline            | Free        | High – non-reusable, hard to track   |

---

## Real-Life Snowy Scenario

Let’s say Winterday spins up a new Lambda function in a sandbox account and uses `AWSLambdaFullAccess`.
Two months later, that policy gets updated by AWS to include `logs:PutMetricFilter`.
But no one reviewed whether that was safe — and now Snowy’s lambda-role can push filters to any CloudWatch logs and mess with detection.

If it were a **customer-managed policy**, you’d have caught the change in Git or CI/CD.
If it were **inline**, no one else would even know it existed.

---

## Final Thoughts

Choosing between inline, AWS managed, and customer-managed policies isn’t about preference — it’s about control.

In security architecture, you want:

- Reusable but auditable policies → **Customer-managed**
- Easy-to-track permissions with versioning → **Customer-managed**
- Avoid blind spots and orphaned policies → **No inline unless absolutely necessary**
- Don’t fully trust AWS Managed in production — they’re too convenient to question

**Default to customer-managed unless you have a good reason not to.**
Because when things break or get breached, you’ll want to say:
> "We wrote that policy. We know what it does. We know who touched it."

Not:
> "Wait… where did this policy come from? Who added that permission?"
