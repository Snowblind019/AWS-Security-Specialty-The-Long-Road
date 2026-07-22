# AWS KMS Multi-Region Keys

Multi-Region keys let you replicate a customer-managed KMS key from a primary Region into replica Regions so the same logical key exists in each, sharing a key ID (though each has its own Region-specific ARN). This solves the problem that a KMS key is normally Region-locked: anything that moves encrypted data across Regions (S3 Cross-Region Replication, DynamoDB Global Tables, cross-Region DR) needs a key that can decrypt in the destination, and without multi-Region keys you would juggle separate independent keys and re-encrypt on the way. The thing to hold onto: multi-Region keys give one logical key with the same key material usable in several Regions for cross-Region workloads, but each replica is still a separate billable resource with its own policy, rotation is managed from the primary, and this is the specific answer whenever a scenario replicates encrypted data across Regions with SSE-KMS or Global Tables.

## How it works

- **You create a primary as multi-Region at creation.** A CMK is flagged multi-Region when created. You cannot convert an existing single-Region key into a multi-Region key, nor convert a multi-Region key back, so it is a design-time decision.
- **`ReplicateKey` creates replicas that share key material.** Replicating into another Region produces a replica with the same key ID and the same underlying key material (so ciphertext from one Region decrypts in another) but a different ARN because the ARN includes the Region. Metadata like description, policy, and tags copy from the primary at replication time.
- **Each replica is a fully functional, independent regional key.** It encrypts and decrypts in its own Region, has its own key policy you can modify separately, and is billed separately. "Same logical key" does not mean "one shared resource," it means shared material with per-Region governance.
- **Rotation is managed from the primary.** Automatic rotation is enabled on the primary and propagates to replicas so they stay aligned. Replicas follow rather than rotate independently.
- **You can promote a replica for DR.** If the primary Region degrades, you promote a replica to primary in another Region and continue with the same key ID. This is what makes multi-Region keys a DR building block for encrypted datasets.

## Multi-Region key properties

| Property | Behavior |
|---|---|
| **Key ID** | Same across primary and all replicas |
| **Key ARN** | Different per Region (Region is in the ARN) |
| **Key material** | Shared, so ciphertext is portable across the Regions |
| **Key policy** | Copied from primary at replication, editable per Region |
| **Rotation** | Managed from the primary, propagates to replicas |
| **Billing** | Each key in each Region billed separately |
| **Conversion** | Cannot convert single-Region to/from multi-Region |

## What gets tested

- **Cross-Region encrypted replication needs the key in the destination.** For S3 CRR with SSE-KMS or DynamoDB Global Tables, the destination Region must have a usable key, and a multi-Region key is the clean answer because the same logical key decrypts in both Regions.
- **Multi-Region key vs separate keys.** When a scenario wants consistent encryption across Regions without re-encrypting or managing independent keys, that is a multi-Region key. Independent per-Region keys force re-encryption on replication.
- **Rotation and some management are primary-only.** Enabling rotation happens on the primary and propagates. A question implying you rotate each replica independently is wrong.
- **Cannot convert existing keys.** If an existing single-Region key now needs multi-Region behavior, you create a new multi-Region key and re-encrypt, you cannot flip the existing one.
- **DR via replica promotion.** Continuity after a Region outage using the same key ID is achieved by promoting a replica to primary.
- **Still separate resources.** Each replica has its own policy and its own bill, so access control and cost are per Region, not global.

## Limitations

- You cannot convert a single-Region key into a multi-Region key or vice versa, so it must be chosen at creation.
- Each replica is billed and governed separately, so replicating to several Regions multiplies both cost and the number of key policies to manage.
- Shared key material is a wider blast radius: compromise or misuse of the key affects every Region it exists in, so the convenience of one logical key concentrates risk.
- Rotation and certain management are centralized on the primary, so losing or degrading the primary Region complicates key administration until a replica is promoted.
- Replica policies can drift from the primary because they are independently editable, so consistent access control across Regions requires deliberate governance.
- Multi-Region keys solve key availability across Regions, not data replication itself. You still configure S3 CRR, Global Tables, or DR tooling to move the data, the key just makes it decryptable at the destination.