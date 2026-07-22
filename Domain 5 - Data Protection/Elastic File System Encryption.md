# Amazon EFS Encryption

Amazon EFS is AWS's managed NFS file share, mountable across many EC2 instances, containers, and Lambda functions at once, which is exactly what makes its encryption story matter: a shared filesystem is a horizontal attack surface where one compromised node can read everything on the volume. EFS encryption covers both ends, at rest via KMS (AES-256, set at creation) and in transit via TLS on the NFS mount, but the two behave differently: at-rest is chosen when the file system is created and cannot be added later, while in-transit is opt-in per mount and easy to forget. The thing to hold onto: at-rest encryption is a create-time decision (remediation means recreate and migrate), in-transit TLS must be explicitly requested with the `-o tls` mount option and the Amazon EFS client, and encryption protects against disk-level and wire-level threats but not against a compromised OS user, which is where IAM mount policies, security groups, and POSIX permissions take over.

## How it works

- **At rest is KMS, chosen at creation.** Enabling encryption at file-system creation encrypts file content, metadata, and directory names with envelope encryption (a per-object data key wrapped by the `aws/elasticfilesystem` key or your CMK). It is transparent on access and cannot be turned on for an existing unencrypted file system.
- **Remediation is recreate and migrate.** To encrypt existing unencrypted data you create a new encrypted file system and copy the data over (for example with AWS DataSync or a backup restore). There is no in-place toggle.
- **In transit is TLS, opt-in per mount.** Encryption in transit uses TLS 1.2 between the client and the mount target, but only when you mount with `-o tls` using the Amazon EFS mount helper (`amazon-efs-utils`). A default `nfs4` mount without that flag moves data in plaintext across the VPC.
- **Access is a three-part gate on top of encryption.** IAM controls mounting via `elasticfilesystem:ClientMount`/`ClientWrite`/`ClientRootAccess`, security groups restrict NFS (2049) to known sources, and POSIX permissions govern file-level access inside the mount. Encryption does not replace any of these.
- **CMK adds control and auditing.** A customer-managed key gives you a scoped key policy, automatic rotation, and CloudTrail visibility into every decrypt, so you can see who read what and enforce `kms:Decrypt` per role. Denying a role on the CMK blocks reads even when NFS and IAM would allow the mount.

## EFS encryption at rest vs in transit

| Dimension | At rest | In transit |
|---|---|---|
| **When set** | File-system creation only | Per mount, at mount time |
| **How** | KMS AES-256, envelope encryption | TLS 1.2 via `-o tls` + EFS mount helper |
| **Default** | Off unless selected at creation | Off unless you add the flag |
| **Remediation** | Recreate and migrate data | Remount with TLS |
| **Protects against** | Disk theft, snapshot/copy exposure | Sniffing, MITM on the NFS stream |

## What gets tested

- **At-rest encryption cannot be added after creation.** If a scenario has an existing unencrypted EFS that now needs encryption, the answer is create a new encrypted file system and migrate, not "enable encryption on the file system."
- **In-transit TLS is opt-in.** Protecting the NFS stream requires mounting with `-o tls` and the Amazon EFS client. Do not assume TLS is on by default, and a standard NFS mount is plaintext.
- **IAM mount policies control who can mount.** Restricting mount access from other instances or a rogue container is `elasticfilesystem:ClientMount`/`ClientWrite` in IAM plus security groups, not encryption. Encryption stops disk and wire reads, IAM stops the mount.
- **CMK for audit and scoped decrypt.** When the requirement is visibility into who decrypted or per-role key control, that is a customer-managed key with CloudTrail, over the default `aws/elasticfilesystem` key.
- **Encryption does not stop a compromised OS user.** A root-level compromise on a mounting instance reads the decrypted files, so encryption is layered with POSIX permissions and least-privilege IAM, it is not sufficient alone.
- **Security group scoping for NFS.** Limiting port 2049 to specific instance sources prevents arbitrary VPC hosts from mounting, complementing the IAM mount policy.

## Limitations

- No in-place at-rest encryption. Encrypting existing data means a new file system and a migration, with the cutover that implies.
- In-transit encryption is not automatic and depends on the Amazon EFS mount helper plus the `-o tls` flag, so a plain NFS mount silently sends data in cleartext.
- Encryption protects data on disk and on the wire, not from a compromised OS user on a mounting instance, who reads through the decrypted mount.
- Because EFS is shared across many nodes, one weak instance with mount access can read the whole volume, so IAM mount scoping and security groups do more for blast radius than encryption does.
- CMK-heavy, high-throughput read workloads generate many KMS operations, so key request costs scale with access volume even though encryption itself is free.
- POSIX permissions still apply and are not overridden by encryption, so misconfigured file permissions expose data regardless of the encryption state.