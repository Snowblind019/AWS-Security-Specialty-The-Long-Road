# Amazon Textract

## What Is the Service

Amazon Textract is a fully managed machine learning service that automatically extracts text, handwriting, tables, forms, and structured data from scanned documents, PDFs, and images.

Unlike basic OCR tools that just grab raw text, Textract understands document layout and context. It can detect relationships between labels and values in forms, recognize tabular structures, and parse fields like:

- “Invoice Number”
- “Amount Due”
- “SSN”
- “Date of Birth”
- “Signature Line”

For Snowy’s security team — managing thousands of compliance PDFs, physical SOC logs, vendor NDAs, redacted forensics docs, and scanned paper forms from remote field sites — Textract serves as a **document intelligence engine**, transforming static inputs into searchable, auditable JSON objects that plug directly into pipelines.

It’s not just OCR — it’s **machine-readable evidence extraction at scale**.

---

## Cybersecurity and Real-World Analogy

### Cybersecurity Analogy

Textract is like hiring a junior security analyst who:

- Reads every paper log, contract, or invoice
- Extracts the sensitive fields
- Labels which field is which
- Digitizes them into JSON or CSV
- Flags if something’s missing (like “signature not found”)

Except this analyst:

- Works 24/7
- Reads 10 languages
- Never gets tired
- And costs pennies

Imagine feeding physical breach response forms or paper IAM change logs into a pipeline that auto-extracts and indexes them — **that’s what Textract does**.

### Real-World Analogy

Think of Textract as a **document decoder**.
You drop in a grainy field report scanned by **Winterday** on a clipboard from a DR drill.
Textract reads the handwriting, detects that `"Signed By: Snowy"` is a form field, and outputs structured data that you can:

- Push into an S3 bucket
- Run Athena queries on
- Or cross-check with CloudTrail

---

## What It Actually Does

| Capability             | Description                                                   |
| Analyze Document       | Detect key-value pairs (forms), tables, checkboxes            |
| Analyze Expense        | Specialized API for invoices and receipts                     |

| Handwriting Support    | Detect cursive or print handwriting (in English)              |
| Bounding Boxes         | Coordinates for every word, table, form element               |
| Confidence Scores      | Output includes per-field confidence metrics                  |
| Structure Preservation | Keeps table/form layout in JSON, not just plain text          |

---

## How It Works

### Workflow: PDF Invoice Ingestion for Compliance

- **Winterday** drops a scanned invoice into an S3 bucket
- **EventBridge** triggers a Lambda function
- Lambda calls `StartDocumentAnalysis` (async) or `AnalyzeDocument` (sync)
- Textract processes:
  - Extracts Invoice ID, Vendor Name, Total, Date
  - Detects signature area was blank (optional validation)

```json
Result is a JSON file with:
- Field: “Invoice Number” → Value: “INV-43190”
- Field: “Amount Due” → Value: “$27,310”
- Field: “Signature” → Value: null (not found)
- Output pushed to DynamoDB, Athena, OpenSearch, or QuickSight dashboard for downstream analysis
```
You now have **searchable, queryable, and reviewable compliance records** that originated from PDFs or faxes.

---

## Use Cases in Security, Compliance, and Audit

| Scenario                  | How Textract Helps                                               |
|---------------------------|------------------------------------------------------------------|
| Red Team Exercise Forms   | Extract metadata from physical playbooks, badges, access logs    |
| Signed NDA / Audit Records | Detect signature fields, validate presence, auto-index         |
| Field Security Reports    | OCR and structure mission notes or SOC field reports            |
| IAM Change Forms (paper)  | Extract “Requestor Name”, “Time”, “Change Approved By”          |
| Third-party Vendor Docs   | Parse and structure legal forms for ingest into secure storage  |
| DR Runbooks (scanned)     | Convert to structured JSON to run validation scripts            |
| Forensics Snapshots       | OCR photos of screens, whiteboards, or logs during IR           |

---

## Security & Compliance Relevance

| Concern                   | Mitigation / Relevance                                          |
|---------------------------|------------------------------------------------------------------|
| Sensitive Data Extraction | Textract may extract PII/PHI → use encryption, access control, tagging |
| IAM Permissions           | Use least privilege (`textract:*DocumentText`, not wildcard)    |
| Encryption at Rest        | Output stored in S3 → enforce SSE-KMS or bucket policies        |
| Data in Transit           | All API calls over HTTPS → avoid public buckets                 |
| Redaction Support         | Use Textract + Amazon Comprehend for PII detection/redaction    |
| Audit Readiness           | Digitize and validate paper-based audit artifacts at scale      |

---

## Pricing

| Pricing Element          | Notes                                     |
|--------------------------|-------------------------------------------|
| Detect Document Text     | $1.50 per 1,000 pages                      |
| Analyze Document         | $15.00 per 1,000 pages (forms/tables)     |
| Analyze Expense          | $15.00 per 1,000 pages                    |
| Handwriting              | No extra charge, supported in AnalyzeDocument |
| Storage/Compute          | Pay separately for S3, Lambda, etc.       |

> **Textract has a Free Tier:**
> First 1,000 pages per month for `DetectDocumentText` only.

---

## Snowy’s Real-World Use Case

### Compliance Vault Digitization

- Old paper SOC logs stored in climate-controlled rooms
- Snowy’s team scans them to PDF
- Textract extracts key fields:
  - Who logged in
  - Time
  - Badge ID
  - Terminal ID
- Lambda pipes this into DynamoDB and QuickSight

Now they can:

- Search login records by badge number
- Detect missing fields via confidence score thresholds
- Automate compliance checks without re-reading 10,000 PDFs

---

## Final Thoughts

Amazon Textract is the **machine-readable bridge between physical compliance artifacts and automated cloud workflows**.

It’s not just OCR — it’s **form-aware intelligence extraction** built for security, legal, and audit pipelines.

- Makes paper documents actionable
- Useful in DR, compliance, and red team postmortems
- Pairs well with Comprehend (for redaction), S3 (for storage), and Athena (for querying)

If you’ve got PDFs, photos, receipts, or forms — and you’re still manually parsing them — **Textract turns that bottleneck into an automated document factory.**
