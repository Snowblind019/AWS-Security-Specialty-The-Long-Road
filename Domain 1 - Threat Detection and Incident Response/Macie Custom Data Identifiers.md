# Macie Custom Data Identifiers

Macie ships with managed data identifiers for common sensitive data (credit cards, SSNs, AWS secret keys, passport numbers). Custom data identifiers (CDIs) let you detect your organization's own formats that the managed set will not catch — employee IDs, contract numbers, internal tokens, project codenames. A CDI is regex plus optional context rules.

The point of a CDI is org-specific sensitive data. Managed identifiers cover the universal stuff; CDIs cover "sensitive in your world." The context rules (keyword proximity, ignore words) exist to cut false positives, and allow lists are the complementary feature for excluding known-benign matches.

## How it works

- A **CDI** combines: a **regex** pattern, optional **keywords** that must appear within a **maximum match distance** (proximity) of the match, **ignore words** that invalidate a match, and a **minimum match length**.
- The keyword/proximity logic raises precision — e.g. only flag `SC-CONTRACT-[0-9]{6}` when "confidential" or "nda" is nearby.
- **Allow lists** are a separate Macie feature: specific text or a regex of known-benign values to exclude from findings (e.g. a sample value that always appears).
- CDIs run during **S3 sensitive data discovery jobs**; matches produce sensitive-data findings just like managed identifiers. Findings route to **Security Hub** and **EventBridge** for remediation.

Example CDI:

```json
{
  "name": "Contract ID",
  "regex": "SC-CONTRACT-[0-9]{6}",
  "keywords": ["confidential", "contract", "nda"],
  "maximumMatchDistance": 50,
  "ignoreWords": ["example", "test"]
}
```

## Managed identifiers vs CDIs vs allow lists

| | Purpose |
|---|---|
| Managed data identifiers | Built-in detectors for common sensitive data |
| Custom data identifiers | Your own regex + context rules for org-specific formats |
| Allow lists | Exclude known-benign values from findings |

## What gets tested

- CDIs detect organization-specific sensitive-data formats (employee/contract IDs, internal tokens) that managed identifiers miss, using regex plus keyword proximity.
- Keyword proximity (maximum match distance) and ignore words are the knobs for cutting false positives; allow lists exclude known-benign values.
- Macie, and therefore CDIs, is S3-only — not CloudTrail, EBS, RDS, or DynamoDB.
- Findings route to Security Hub and EventBridge to drive remediation (block public access, quarantine, notify).
- CDIs add no extra cost themselves; Macie bills on bytes scanned, so scope discovery jobs to high-risk buckets.

## Limitations

- S3-only; no other data stores.
- Regex-based — unstructured or obfuscated secrets can evade.
- Detection, not prevention; pair with EventBridge/remediation.
- Cost scales with the volume of data scanned.