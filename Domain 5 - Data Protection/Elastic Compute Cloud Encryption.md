# EC2 Encryption

There is no single "encrypt EC2" switch. What you actually encrypt is a set of distinct surfaces around the instance: EBS volumes (the main one), snapshots and AMIs derived from them, instance store (ephemeral) disks, and traffic in and out, plus whatever lands in CloudWatch and S3. CPU registers, RAM, and network buffers are not encrypted at rest, encryption-in-use is a separate category. The security point is that none of this is automatic beyond EBS defaults you turn on, so a forgotten unencrypted volume or a shared snapshot is how regulated data leaks. The thing to hold onto: EC2 encryption is a collection of per-surface controls (EBS at rest via KMS, snapshots and AMIs inheriting that key, instance store only on Nitro, and in-transit that you enforce yourself), and sharing an encrypted AMI or snapshot across accounts always requires granting the KMS key, not just the resource.

## How it works

- **EBS at rest is the core layer.** Volumes encrypt with AES-256 via KMS (`aws/ebs` or a CMK), transparently and without meaningful performance cost. You cannot flip an existing volume between encrypted and unencrypted, you snapshot, copy with the target encryption state, and restore.
- **Snapshots inherit the volume's key.** A snapshot of an encrypted volume is encrypted, and copying a snapshot lets you re-target a different CMK. Anyone with `ec2:CreateVolume` and access to the snapshot can spin up an instance with that data, so KMS key access is the real last line of defense.
- **AMIs carry encryption from the root volume.** An AMI built on an encrypted root volume is encrypted. You cannot share an encrypted AMI publicly, only to specific account IDs, and those accounts also need `kms:Decrypt` on the key. This is the mechanism behind secure, multi-tenant image pipelines.
- **Instance store encryption depends on Nitro.** Ephemeral NVMe/SSD disks vanish on termination and are only encrypted on Nitro-based instances, where it is automatic at the hardware layer. They are for high-speed temp data, not persistent sensitive storage.
- **In-transit is your responsibility.** AWS does not encrypt instance-to-instance traffic by default. You enforce TLS 1.2+, mTLS in a mesh, EFS-with-TLS, RDS-with-SSL, and put HTTPS-terminating ALB or CloudFront in front of web services, backed by security groups and `aws:SecureTransport` on API endpoints.
- **Governance makes it non-optional.** SCPs can deny unencrypted volume creation, EventBridge can catch `ec2:CreateVolume` without encryption, Config flags unencrypted volumes and snapshots, and CloudTrail logs the KMS and EC2 calls. Default EBS encryption (per Region) closes the human-error gap for new volumes.

## EC2 encryption surfaces

| Surface | How it is encrypted | Key thing to know |
|---|---|---|
| **EBS volume** | KMS AES-256, at creation | No in-place toggle, snapshot-copy-restore |
| **Snapshot** | Inherits volume key, re-key on copy | Access + `ec2:CreateVolume` reconstructs data |
| **AMI** | Inherits root volume encryption | Share to account IDs only, plus `kms:Decrypt` |
| **Instance store** | Automatic on Nitro only | Ephemeral, not for persistent sensitive data |
| **In transit** | TLS/mTLS you configure | Not encrypted by default between instances |
| **Governance** | SCP/Config/EventBridge | Deny-by-default beats per-volume checkboxes |

## What gets tested

- **"EC2 encryption" is really EBS plus derived resources.** The exam expects you to know there is no single instance-level encryption toggle, and that at-rest protection means EBS, snapshots, and AMIs.
- **Sharing encrypted AMIs or snapshots cross-account.** The correct answer grants the target account use of the CMK in addition to sharing the resource, and encrypted images cannot be made public. `aws/ebs` cannot be shared, so this forces a CMK.
- **No in-place encryption of an existing volume.** Remediation is snapshot to encrypted copy to new volume, then swap.
- **Instance store on Nitro.** If a scenario needs encrypted ephemeral local storage, that is a Nitro instance type, automatic at the hardware layer, not a KMS toggle.
- **In-transit is opt-in.** Instance-to-instance encryption requires you to configure TLS/mTLS. AWS does not provide it by default, unlike managed services that enforce TLS.
- **Preventive governance.** Enforcing encryption fleet-wide is an SCP denying unencrypted volume creation plus default EBS encryption, not relying on people to check a box.

## Limitations

- Encryption at rest covers disks and their derivatives, not memory. RAM, CPU registers, and in-flight buffers are not protected, so a live-instance compromise reads decrypted data.
- No in-place conversion between encrypted and unencrypted volumes, so remediation always creates new resources and requires a cutover.
- Default EBS encryption is per Region and only affects new volumes, leaving existing volumes and other Regions untouched.
- Instance store encryption is inconsistent across instance families and only guaranteed on Nitro, so it cannot be assumed as a portable control.
- Cross-account sharing of encrypted AMIs and snapshots fails silently if the KMS key grant is missing, and encrypted images cannot be shared publicly at all.
- In-transit encryption is entirely on you for raw EC2, so an environment that assumes AWS encrypts east-west traffic is exposed until TLS/mTLS is actually configured.