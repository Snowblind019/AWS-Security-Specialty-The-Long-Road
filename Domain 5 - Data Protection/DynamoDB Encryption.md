# Amazon DynamoDB Encryption

DynamoDB encrypts all data at rest and in transit by default, with KMS integration and no way to turn at-rest encryption off. Every item, index, stream, backup, export, and Global Table replication stream is encrypted, and all traffic is TLS 1.2+, all transparent to the application. For security teams the leverage is at the key layer: the choice of KMS key tier decides whether you get CloudTrail visibility into decryptions, custom key policies, and cross-account or cross-Region control. The thing to hold onto: there are three key tiers (AWS-owned, AWS-managed `aws/dynamodb`, and a customer-managed CMK), and only the CMK gives you auditable key usage, scoped key policies, and the cross-Region control that Global Tables and compliance frameworks demand.

## How it works

- **Three key tiers, not two.** The default is an AWS-owned key (no cost, no CloudTrail visibility, no policy control). The AWS-managed key `aws/dynamodb` lives in your account and its use shows in CloudTrail, but you cannot edit its policy. A customer-managed key (CMK) is fully yours: custom key policy, CloudTrail auditing, rotation, and cross-account grants. You switch tiers on the table without disabling encryption.
- **Envelope encryption under the hood.** On write, DynamoDB gets a data key from KMS (encrypted plus plaintext form), encrypts the item with the plaintext DEK, stores the wrapped DEK next to the data, and discards the plaintext DEK. On read it asks KMS to unwrap the DEK and decrypts. With a CMK or `aws/dynamodb`, those KMS calls are logged.
- **At-rest encryption cannot be disabled.** Once a table exists it is encrypted, which prevents accidental plaintext exposure during a config change. The only lever is which key tier.
- **In transit is always TLS 1.2+.** SDK/CLI to service, Global Table cross-Region replication, and Streams to Lambda consumers are all TLS, with no toggle to turn it off.
- **CMK key policy is the access boundary.** For a CMK-encrypted table, the key policy must let the DynamoDB service and the caller's role use `Encrypt`/`Decrypt`/`GenerateDataKey`. Scope it with `aws:SourceVpce` or `aws:SourceArn` conditions and avoid `Principal: "*"`. Denying the role on the key denies data access even if IAM allows the DynamoDB action, which is the extra control layer a CMK buys.
- **Global Tables need the key in every Region.** Replicated data stays encrypted at rest per Region, and each replica Region needs a usable key and a policy allowing DynamoDB there to use it. Misconfigured keys make replication silently fail or throttle, so multi-Region KMS keys are the design answer.

## DynamoDB key tiers compared

| Tier | CloudTrail visibility | Custom key policy | Cross-account / Global Tables | Cost |
|---|---|---|---|---|
| **AWS-owned** | No | No | No | Free |
| **AWS-managed `aws/dynamodb`** | Yes | No | Limited | KMS request cost |
| **Customer-managed (CMK)** | Yes | Yes | Yes | KMS key + request cost |

## What gets tested

- **CMK is the answer for audit and control.** "Who decrypted what and when," scoped key access, cross-account, or a compliance mandate all require a customer-managed key. The AWS-owned key gives no CloudTrail visibility and no policy control, so it fails those requirements.
- **The key policy is a second gate.** Denying a role on the CMK blocks data access even when its IAM policy grants the DynamoDB action. Use this to enforce least privilege and `aws:SourceVpce`-style scoping at the key.
- **Global Tables and cross-Region keys.** Replication failures or throttling trace back to a replica Region lacking access to a usable key. Multi-Region keys or replicated CMKs are the fix.
- **Export to S3 depends on compatible encryption and permissions.** `ExportTableToPointInTime` needs the destination bucket's encryption and policy to allow the export job, and the whole flow is logged across CloudTrail, S3, and KMS. Misconfigured or public destination buckets are a common mistake.
- **At-rest cannot be turned off.** Any "disable encryption" option is wrong. The only decision is the key tier.
- **Encryption alone is not the whole control.** The intended answer usually pairs at-rest encryption with CMK auditing, scoped key policy, and alerting, not encryption by itself.

## Limitations

- The AWS-owned default gives no CloudTrail visibility and no policy control, so it cannot satisfy audit or least-privilege requirements. That forces `aws/dynamodb` or a CMK.
- `aws/dynamodb` adds CloudTrail visibility but not custom key policies or cross-account use, so cross-account and fine-grained scoping still require a CMK.
- Global Table replication is silently sensitive to key setup. A missing or wrong key policy in a replica Region degrades replication without an obvious error.
- Encryption protects confidentiality at rest and in transit, not authorization. IAM plus the CMK key policy still govern who can read items, so misconfigured access is a separate exposure.
- Exports are an easy place to leak data if the destination S3 bucket is unencrypted or public, so the export target's posture matters as much as the table's.
- CMK usage adds KMS request costs on high-throughput tables, so heavy read/write volume against a CMK-encrypted table carries a per-call bill to plan for.