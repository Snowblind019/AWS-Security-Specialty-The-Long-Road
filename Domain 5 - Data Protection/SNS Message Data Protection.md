# SNS Message Data Protection

A per-topic **data protection policy** on Amazon SNS that scans message **payloads in real time** for sensitive data (PII and PHI) using **managed and custom data identifiers**, then **audits**, **de-identifies**, or **denies** it. It is the sensitive-data-detection concept you know from Macie, applied to messages moving through a pub/sub topic rather than objects sitting in S3. This is a data-in-transit and data-leakage control for the messaging layer. One caveat up front, because it decides questions: **SNS message data protection is closed to new customers as of April 30, 2026.** Existing users keep it, new builds need an alternative.

The mental model is three operations across two directions. The operations are **Audit** (log without stopping the flow), **De-identify** (mask or redact without stopping the flow), and **Deny** (block the publish or the delivery). The directions are **Inbound** (evaluated on Publish) and **Outbound** (evaluated on delivery to a subscription). Same data-identifier vocabulary as Macie, but for messages in motion.

## How it works

- **Policy shape**: one data protection policy per topic, **standard topics only** (no FIFO), version `2021-06-01`, with a list of statements. A policy can hold multiple deny and de-identify statements but **only one audit statement**.
- **Data identifiers**: **managed** identifiers cover 25-plus common PII and PHI types (names, addresses, SSNs, credit card numbers, prescription and national drug codes), and **custom** identifiers are your own regex (max **10** per policy, regex up to 200 characters). Detection uses machine learning plus pattern matching, in real time. Managed and custom identifiers can be mixed in one statement.
- **Statement fields**: `DataDirection` (Inbound for Publish requests, Outbound for notification deliveries), `Principal` (specific accounts, roles, or users, or `*`), `DataIdentifier` (the identifier ARNs to scan for), and `Operation`.
- **Audit**: samples messages (`SampleRate` an integer up to **99**, never 100) and logs matches to a **FindingsDestination** and non-matches to a **NoFindingsDestination**, each targeting CloudWatch Logs, Firehose, or S3. It does not interrupt the flow. The CloudWatch log group must use the `/aws/vendedlogs/` prefix.
- **De-identify**: **MaskConfig** replaces the sensitive characters with a chosen character, or **RedactConfig** removes the data entirely. It does not interrupt the flow. On **Inbound**, the payload is sanitized before it enters the topic, so every subscriber receives the same modified message. On **Outbound**, it applies per subscription, so different subscribers can receive different treatment.
- **Deny**: blocks the **Publish** request (inbound) or fails the **delivery** (outbound) when sensitive data is present, returning a **403 AuthorizationError**.
- **Ordering and principals**: on an inbound message, de-identify runs after audit. The two enforcement principals are the **Publish API principal** (inbound) and the **Subscription principal** that called Subscribe (outbound).

## The three operations

| Operation | Effect | Interrupts the flow? | Key config |
|---|---|---|---|
| Audit | Logs findings and non-findings | No | SampleRate up to 99, destinations to CloudWatch Logs / Firehose / S3, one per policy |
| De-identify | Masks or redacts the matched data | No | MaskConfig (character) or RedactConfig (remove), inbound or outbound |
| Deny | Blocks publish or fails delivery | Yes | None, returns 403 AuthorizationError |

## What gets tested

- SNS Message Data Protection is the answer for detecting, masking, or blocking sensitive data (PII/PHI) in SNS message payloads in real time. It reuses the same managed and custom data identifiers as Macie, but operates on messages in transit through a topic, not S3 at rest.
- Three operations map to three verbs. Audit logs without stopping, De-identify masks or redacts without stopping, Deny blocks the publish or delivery. Choose by whether the requirement is observe, sanitize, or block.
- Direction changes the outcome. Inbound acts on Publish, so an inbound de-identify sanitizes the payload before it enters the topic and every subscriber gets the cleaned version. Outbound acts on delivery, so it can differ per subscriber or principal.
- Standard topics only, one policy per topic, and only one audit statement (multiple deny and de-identify are allowed).
- Audit is sampled up to 99 percent, never 100, and needs findings destinations (CloudWatch Logs, Firehose, S3). Remember the `/aws/vendedlogs/` log-group prefix.
- Availability trap: closed to new customers as of April 30, 2026. For a new architecture this is likely no longer the intended answer, so know it exists and note the change.

## Limitations

- Closed to new customers from April 30, 2026. Existing users continue, but new designs must reach for another control.
- Standard topics only, no FIFO.
- It inspects the payload, it is not encryption. Pair with SNS server-side encryption (KMS) for data at rest and TLS for transport.
- Audit is sampled, so it is a monitoring signal, not proof that every message was inspected, and only one audit statement is allowed per policy.
- Custom identifiers are capped at 10 per policy with regex length limits.
- Scope is per topic. This is topic-level protection, not org-wide DLP.