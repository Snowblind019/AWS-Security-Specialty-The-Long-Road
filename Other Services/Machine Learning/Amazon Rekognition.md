# Amazon Rekognition

## What Is the Service

Amazon Rekognition is AWS’s deep learning–based computer vision service that can analyze images and videos to detect objects, scenes, people, activities, inappropriate content, faces, and text. It’s fully managed, requires no machine learning expertise, and integrates with S3, Kinesis Video Streams, Lambda, and more.

For Snowy’s security team, Rekognition enables automated visual intelligence workflows — spotting tailgaters at data centers, detecting unbadged personnel, flagging license plates, tracking intrusions across footage, and even redacting faces for privacy compliance.

It’s not just about surveillance — it’s about building automation on top of visual data to reduce manual review, respond faster, and prove compliance.

---

## Cybersecurity and Real-World Analogy

### Cybersecurity Analogy

Rekognition is your automated SOC analyst — but for images and video:

- Sees a feed and detects who is present
- Flags anomalies (e.g., no badge, unfamiliar face)
- Extracts license plate or document text in screenshots
- Redacts sensitive visual elements (PII, faces)

It’s like extending your GuardDuty coverage to the physical world.

### Real-World Analogy

Imagine a data center where **Blizzard** walks through the mantrap.

Rekognition checks:

- Does Blizzard’s face match the badge?
- Did someone tailgate behind them?

- Was that door supposed to be accessed at 3:00 AM?

Rekognition logs all this and can trigger alarms — or send a Slack alert to Snowy’s team.

---

## What It Actually Does

| Capability                  | Description                                                  |
|-----------------------------|--------------------------------------------------------------|
| Face Detection              | Detect faces in images/video, bounding boxes, landmarks      |
| Face Comparison             | Compare one face to another — 1:1 verification               |
| Face Search                 | Search for a face in a collection — 1:N matching             |
| Text in Image               | Detect printed text (OCR) in images (e.g., license plates)   |
| Object & Scene Detection    | Cars, trees, people, bags, etc.                              |
| Celebrity Detection         | Flag known public figures (used in entertainment)            |
| Content Moderation          | Detect nudity, violence, suggestive content                  |
| Person Pathing (video)      | Track a person frame by frame                                |
| Protective Equipment Detection | Detect hardhats, vests, masks, etc.                        |
| Custom Labels               | Train your own object detector (e.g., weapons, brand logos)  |

---

## How It Works

### Real-World Security Pipeline: Physical Intrusion Detection

- **Cameras** record entrances (Kinesis Video Stream)
- **Rekognition Video** processes stream in near-real-time:
  - Detects person entry
  - Compares detected face against known employee faces (Face Collection)
  - If face not matched:
    - Lambda sends alert to SecurityHub or SNS topic
    - Optionally calls EventBridge → PagerDuty/Slack
    - Optionally stores cropped face in S3 + DynamoDB record

Now Snowy’s team has **searchable visual logs** of who entered, when, wearing what, and whether they were authorized.

---

## Security & Compliance Use Cases

| Use Case                | Description                                                    |
|-------------------------|----------------------------------------------------------------|
| Tailgating Detection    | Detect two people entering behind one badge scan               |
| Badgeless Access        | Flag anyone without hard hat / ID badge / vest                |
| Unauthorized Access Review | Post-incident video search for intruders                    |
| PII Redaction           | Blur faces before storing images for compliance               |
| License Plate Capture   | Extract plate numbers from parking lot images                 |
| Document Leak Detection | Spot exposed whiteboards or IDs in photos                     |
| Policy Enforcement      | Hard hat or PPE compliance at construction zones              |
| Security Automation     | Integrate with Lambda/EventBridge to trigger alerts           |
| Deepfake / Celebrity Detection | Detect abuse or identity misuse in public content       |

---

## Integration Pattern (Typical Security Architecture)

- **Kinesis Video Stream**: Live camera feeds
- **Rekognition Video**: Stream analysis
- **Rekognition Image**: Point-in-time snapshots
- **S3**: Stores cropped faces, matched images, thumbnails
- **Lambda**: Decision logic (alert, block, tag)
- **DynamoDB**: Face match logs
- **EventBridge**: Alarm routing
- **SecurityHub**: Findings + visibility

All within AWS — no external model hosting required.

---

## IAM + Security Controls

| Control           | Details                                                                 |
|-------------------|-------------------------------------------------------------------------|
| IAM Permissions   | Lock down to specific actions: `rekognition:CompareFaces`, `DetectLabels`, etc. |
| PII Risks         | Faces = biometric data → apply encryption, audit logs, and retention controls |
| S3 Encryption     | Always use SSE-KMS when storing cropped images or metadata             |
| Face Collections  | Secure with tagging, separate per environment/account, apply access control |
| Data Retention    | Define lifecycle policies for image deletion                           |
| Auditability      | Use CloudTrail for all Rekognition API calls                           |
| Compliance        | HIPAA eligible (with BA), FedRAMP, GDPR if properly configured         |

---

## Pricing Overview

| Pricing Tier       | Image                            | Video            |
|--------------------|----------------------------------|------------------|
| Label Detection    | $1.00 per 1,000 images           | $0.12/min        |
| Face Detection     | $1.00 per 1,000 images           | $0.12/min        |
| Face Search        | $1.00 per 1,000 images           | $0.12/min        |
| Compare Faces      | $1.00 per 1,000 images           | N/A              |
| Text in Image      | $1.00 per 1,000 images           | N/A              |
| Custom Labels      | Training = $1/hr<br>Inference = $4.00 per 1,000 images | N/A |
| Streaming Video Archive (Kinesis) | Billed separately per GB/hr | N/A        |

> **Free Tier:** 5,000 images per month for first 12 months.

---

## Real-World Snowy Scenario

### Data Center Physical Access Audit

**Winterday** accidentally triggered a security event: access to the server rack outside of scheduled hours.

- Rekognition Video reviews the feed:
  - Detects time, confirms **no badge** on Winterday
  - Face compared against employee collection = match
  - Entry classified as **low risk** → marked for audit only

Meanwhile, **Blizzard** left a laptop visible in the secure cage.

- Rekognition detects open laptop + no operator nearby
- Lambda triggers alert → Slack message → Jira ticket auto-created

Now the SOC team has **visual alerts tied to IAM activity**, linking physical behavior to account usage in real time.

---

## Final Thoughts

Amazon Rekognition is more than face detection — it’s a **scalable visual security platform** for AWS-native infrastructures.

With the ability to **see**, **understand**, and **act** on visual data, it bridges a key gap between **cybersecurity and physical security**.
