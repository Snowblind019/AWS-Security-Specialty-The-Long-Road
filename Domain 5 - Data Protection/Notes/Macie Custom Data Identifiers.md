# Amazon Macie — Custom Data Identifiers (CDIs)  

## What Are CDIs in Macie

By default, Amazon Macie comes preloaded with **managed data identifiers** — built-in detectors for common sensitive data types like:

- Credit cards  
- Names  
- SSNs  
- Passport numbers  
- AWS secrets  

But what if your organization uses **custom formats** that don’t fit those patterns?

Think:

- Internal Employee IDs (`EMP-445377`)  
- Proprietary customer numbers (`ACCT-XYZ-00001`)  
- Confidential project codes (`Project WinterFire`)  

**Custom Data Identifiers (CDIs)** let you define your own rules and tell Macie exactly what to look for — based on:

- Regex patterns  
- Keyword proximity  
- Validation logic  

---

## Cybersecurity Analogy


Think of CDIs like giving your **DLP engine a personalized dictionary of secrets**.

Managed identifiers are the “known risks” (credit cards, SSNs, etc.),  
but CDIs let you **weaponize your knowledge** of what’s sensitive in your world.


Imagine you’re scanning internal documents and come across:

```
CONFIDENTIAL: Blueprint Code - SNOWY-ENG-1091
```

A built-in engine wouldn’t catch that.  
But with a CDI that says:

> Look for `SNOWY-ENG-[0-9]{4}` when near the word **"Blueprint"** or **"Confidential"**


— Macie **flags it instantly**.

---

## How Custom Data Identifiers Work

A **CDI** is a combo of regex + keywords + optional checks:

| **Component**          | **Description**                                                  |
|------------------------|------------------------------------------------------------------|
| **Regex pattern**      | The primary pattern you want to match (e.g. `SNOWY-[0-9]{6}`)    |
| **Keywords (optional)**| Anchor words that must appear nearby to validate the match       |
| **Proximity window**   | Distance (in characters) from the regex match to the keywords    |
| **Ignore words**       | Words that invalidate a match (e.g. "example")                   |
| **Minimum match length**| Optional length filter to reduce noise                         |

Macie applies this logic when scanning S3 objects, and if all conditions match, it generates a **sensitive data finding** just like with any managed identifier.

---

## Example — SnowyCorp CDI

**SnowyCorp** uses internal Contract IDs formatted like: `SC-CONTRACT-987654`.

They don’t want these appearing in:

- Public S3 buckets  
- External email dumps  
- Customer-uploaded PDFs  

Here’s how they build a CDI in Macie:

```json
{
  "name": "SnowyCorp Contract ID",
  "regex": "SC-CONTRACT-[0-9]{6}",
  "keywords": ["confidential", "contract", "nda"],
  "maximumMatchDistance": 50,
  "ignoreWords": ["example", "test"]
}
```

Now, Macie will **only flag this pattern when near sensitive context** — preventing noise and improving true positive rates.

---

## What You Can Do With CDIs

| **Use Case**          | **Example**                                           |
|------------------------|-------------------------------------------------------|
| Internal IDs           | Employee IDs, badge numbers, customer IDs            |
| Project codenames      | Proprietary naming patterns like `BLIZZARD-R6-ALPHA` |
| Token formats          | Custom JWTs, auth tokens (`X-Access-Token: abc-123`) |
| Legal strings          | `"Privileged & Confidential - Case #XYZ123"`         |
| Regex-tuned formats    | Anything that follows a predictable structure         |

CDIs become especially useful for **regulated environments** (HIPAA, GDPR, CJIS, etc.) where “sensitive” is *context-specific*, not always standard.

---

## Where CDIs Are Used

- **S3 Sensitive Data Discovery** — Macie uses CDIs when scanning S3 buckets  
- **Findings** appear in **Security Hub**, **EventBridge**, or **CloudWatch Logs**  
- **Can trigger remediation** — block public access, quarantine bucket, notify teams  

> They do **not** work on CloudTrail logs, EBS, RDS, or DynamoDB — **Macie is S3-only**.

---

## Security Benefits of CDIs

| **Benefit**               | **Description**                                              |
|---------------------------|--------------------------------------------------------------|

| **Tailored DLP**          | Build rules around your proprietary secrets                  |
| **Reduced false positives**| Add context keywords and distance logic                     |

| **Compliance automation** | Prove that your sensitive data is being monitored            |
| **Integration**           | Use EventBridge to trigger alerts or remediations            |
| **Visibility**            | Audit how often and where sensitive data shows up in buckets |

---

## SnowyCorp Workflow Example

1. **Devs upload log archives** to S3  
2. **Macie CDI** detects `SNOWY-TOKEN-[A-Z0-9]{12}` in a zipped file  
3. **Finding sent** to Security Hub  
4. **EventBridge triggers** Lambda that:
    - Removes public access  
    - Tags the object  
    - Notifies `SnowySecOps` Slack channel  

The devs are alerted, and **no secrets leave the org**.

---

## Pricing Note

Custom Data Identifiers do **not add extra cost** by themselves.  
However, **Macie pricing is based on bytes scanned**, so:

- A **wider scan scope = more cost**  
- Use **scoped buckets** and **discovery jobs with filters** to limit cost while targeting high-risk areas

---

## Final Thoughts

**Custom Data Identifiers unlock the real power of Macie.**

It’s not just about “credit cards” and “SSNs” —  
It’s about protecting *your* secrets, in *your* format, across your data lake.

Without CDIs, Macie is **generic**.  
With CDIs, Macie becomes **SnowyCorp’s custom-tailored surveillance system**, constantly sweeping S3 for confidential data leaks that *only you understand*.

