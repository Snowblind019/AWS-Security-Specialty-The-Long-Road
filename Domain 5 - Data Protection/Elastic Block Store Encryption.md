# EBS Encryption (Amazon Elastic Block Store)

EBS encryption provides transparent AES-256 encryption at rest for EC2 block storage (boot volumes, data volumes, snapshots, and volume clones) plus encryption of the data in transit between the instance and the volume, all managed through KMS. It is transparent to the application and has negligible performance cost, so the security value is simple: a copied snapshot, a volume attached elsewhere, or a downloaded backup is unreadable gibberish without access to the KMS key. The catch that dominates exam questions is that encryption is a create-time property of a volume, you cannot toggle it on an existing unencrypted volume, so the fix is always a snapshot, copy-with-encryption, restore path. The thing to hold onto: EBS encryption is per-volume and set at creation, default encryption is a per-Region account setting that only affects new volumes, and the KMS key policy plus IAM together decide who can actually decrypt and mount.

## How it works

- **Encryption is transparent and KMS-backed.** New encrypted volumes use AES-256 with a data key from KMS, encrypt/decrypt happens inline with no app changes and no meaningful performance hit. You choose the AWS-managed key `aws/ebs` or a customer-managed CMK for scoped policy, auditing, and separation of environments.
- **Encryption is inherited down the chain.** Snapshots of an encrypted volume are encrypted, volumes created from an encrypted snapshot are encrypted, and clones stay encrypted. You do not re-decide encryption at each step, it flows from the source.
- **You cannot encrypt an existing unencrypted volume in place.** The supported path is: snapshot the unencrypted volume, copy the snapshot with encryption enabled (choosing the key), then create a new volume from the encrypted copy and swap it in. The same copy-with-a-different-key step is how you re-key or change the CMK.
- **Default encryption is a per-Region toggle for new volumes only.** Enabling EBS encryption by default applies to every new volume in that Region, but does not retroactively encrypt existing volumes or snapshots. It is set per Region, so a multi-Region account enables it in each.
- **Cross-account snapshot sharing needs a CMK grant.** An encrypted snapshot shared to another account is useless there unless that account is granted use of the CMK. The AWS-managed `aws/ebs` key cannot be shared cross-account, so cross-account flows require a CMK.
- **IAM plus the key policy are the two gates.** IAM controls who can `CreateVolume`, `AttachVolume`, and `CopySnapshot`, while the KMS key policy controls who can decrypt. An attacker who copies a snapshot still needs both the IAM permission and CMK access, and CloudTrail logs the KMS and EBS calls for detection.

## EBS encryption facts at a glance

| Aspect | Behavior | Exam trap |
|---|---|---|
| **When set** | At volume creation | No in-place encryption of existing volume |
| **Existing unencrypted volume** | Snapshot to encrypted copy to new volume | "Just enable encryption" is wrong |
| **Default encryption** | Per-Region, new volumes only | Not retroactive, not global |
| **Snapshots/clones** | Inherit source encryption | Cannot strip encryption by snapshotting |
| **Cross-account share** | Needs CMK grant to the other account | `aws/ebs` key cannot be shared |
| **Re-key** | Copy snapshot with a different CMK | No direct key swap on a live volume |

## What gets tested

- **No in-place encryption.** Encrypting an existing unencrypted volume is snapshot to encrypted copy to restore. This is the single most tested EBS fact.
- **Default encryption scope.** Enabling encryption by default covers new volumes in that Region only. It does not encrypt old volumes and must be enabled per Region.
- **Cross-account snapshot sharing requires a CMK.** Sharing an encrypted snapshot to another account works only if the target account is granted use of the customer-managed key. Default AWS-managed keys cannot cross accounts.
- **Two-gate access.** Reading an encrypted volume needs both IAM permission on the EBS action and access to the KMS key. Denying the role on the CMK blocks decryption even if IAM allows the attach.
- **Encryption inheritance.** You cannot use snapshot-and-restore to remove encryption. Anything derived from an encrypted source stays encrypted, which is often a distractor answer.
- **Detection.** Config rules flag unencrypted volumes and snapshots, and CloudTrail plus CMK logging surface unusual `CreateVolume`, `CopySnapshot`, and `Decrypt` activity.

## Limitations

- Encryption is a create-time property, so remediating an unencrypted volume always means creating a new volume and cutting over, not flipping a switch.
- Default encryption is not retroactive and is set per Region, so relying on it does nothing for volumes and snapshots that already exist or for other Regions.
- The AWS-managed `aws/ebs` key cannot be shared cross-account, which forces a CMK for any cross-account snapshot workflow.
- Encryption protects confidentiality only. It does not stop an authorized-but-malicious principal who has both the IAM permission and CMK access, so key-policy scoping and monitoring still matter.
- CMK usage adds KMS request costs on high-I/O fleets and per-key monthly charges, so many environment-specific keys carry a real bill.
- Encryption does not prevent access to a running instance's mounted filesystem. Malware on a live EC2 reads through the decrypted mount, so EBS encryption defends against offline theft of the volume, not in-guest compromise.