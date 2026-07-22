# ECS Encryption

Like EC2, "ECS encryption" is not one setting. ECS encrypts nothing on its own, and what people mean is the set of surfaces around a task, each with its own encryption model and its own KMS behavior: EBS volumes (EC2 mode), EFS mounts, container images in ECR, secrets from Secrets Manager or SSM, CloudWatch logs, and task-to-task network traffic. Every layer encrypts at rest through KMS by default or on request, but the actual protection lives in how tightly you scope IAM and the KMS keys, because a broad CMK shared across all secrets, images, and logs turns encryption into theater. The thing to hold onto: at-rest encryption is largely on-by-default per surface, the two settings you must consciously turn on are EFS in-transit and task-to-task TLS, and the real security boundary is per-task IAM plus per-purpose CMKs, not the encryption checkbox.

## How it works

- **EBS volumes (EC2 mode) encrypt at creation via KMS.** Scratch and persistent volumes mounted to ECS-on-EC2 hosts use `aws/ebs` or a CMK, cannot be toggled after creation, and carry encryption into snapshots and AMIs. Enforce it with default EBS encryption, SCPs on `ec2:CreateVolume`, and Config rules.
- **EFS encrypts at rest at creation, but in-transit is opt-in.** At-rest is set when the file system is created. In-transit TLS is separate and must be explicitly enabled via the TLS mount helper (or stunnel). Skip it and container-to-EFS traffic crosses the VPC in plaintext, readable by a compromised node.
- **ECR images encrypt at rest transparently.** Repositories use the `aws/ecr` managed key or a CMK you configure, applied automatically on push and pull. This protects the underlying storage, it does not stop someone with pull permissions from pulling, so private repos plus scoped `ecr:BatchGetImage`/`GetDownloadUrlForLayer` matter more than the encryption itself.
- **Secrets are encrypted at rest and injected just-in-time.** Secrets Manager and SSM SecureString values are KMS-encrypted and decrypted at task start via the execution role, then handed to the container. Security depends entirely on IAM to read the secret, KMS to decrypt it, and the app not logging it to stdout.
- **CloudWatch Logs encrypt at rest, default `aws/logs` or a CMK.** Logs frequently contain stack traces, PII, tokens, or accidentally logged secrets, and any principal with `logs:GetLogEvents` can read them. Sensitive log groups warrant a dedicated CMK and scoped IAM plus resource policies.
- **Task network traffic is not encrypted by default.** Container-to-container, task-to-task, and service-to-service HTTP all move in plaintext unless you enforce TLS, mTLS, or App Mesh with TLS, terminating with ACM certs at an ALB/NLB.

## ECS encryption layers and the setting that matters

| Layer | At rest | The consciously-set control |
|---|---|---|
| **EBS (EC2 mode)** | KMS at creation | Default encryption + SCP enforcement |
| **EFS** | On at creation | In-transit TLS is opt-in, enable it |
| **ECR images** | Automatic (`aws/ecr` or CMK) | Private repos + scoped pull IAM |
| **Secrets (SM/SSM)** | KMS-encrypted | Per-env CMK, scoped IAM, no stdout leak |
| **CloudWatch Logs** | `aws/logs` or CMK | Dedicated CMK + `logs:GetLogEvents` scoping |
| **Task network** | Not encrypted | Enforce TLS/mTLS yourself |

## What gets tested

- **EFS in-transit and task-to-task TLS are the opt-in gaps.** Most ECS encryption surfaces are on by default at rest, so the exam-relevant fixes are enabling EFS in-transit encryption and enforcing TLS/mTLS between tasks. "It's isolated in the VPC" is not encryption.
- **Per-purpose CMKs and scoped IAM over one broad key.** The intended answer scopes decrypt permission per environment and per role, so a compromised task role cannot decrypt every prod secret. One CMK for secrets, images, and logs with broad `kms:Decrypt` is the anti-pattern.
- **Encryption does not stop authorized pulls or reads.** ECR encryption does not prevent someone with pull rights from pulling, and log encryption does not stop a principal with log-read rights. Access scoping, not encryption, is the control there.
- **Secrets injection hygiene.** Reference secrets via the task definition and ensure the app does not log them. A plaintext token in a logged request body defeats the whole chain even with everything encrypted.
- **EBS-in-ECS follows EC2 rules.** No in-place encryption, snapshot-copy-restore to remediate, and default encryption is per Region for new volumes.

## Limitations

- ECS encrypts nothing itself. Every layer is a separate service's encryption model, so a single missed toggle (EFS in-transit, task TLS) leaves a plaintext path in an otherwise "encrypted" system.
- At-rest encryption protects storage, not access. Broad IAM or a broad CMK means an attacker who reaches a task role can still decrypt and read, so encryption without tight scoping is cosmetic.
- Secrets are decrypted into the container at start, so a compromised task or one that logs its inputs exposes them regardless of at-rest encryption.
- Task-to-task traffic has no default encryption, so east-west data is exposed until TLS/mTLS is deliberately configured.
- Sharing one CMK across secrets, images, and logs collapses the blast radius into a single key, so a single over-granted decrypt permission exposes everything.
- CMKs and heavy Secrets Manager or KMS call volume add real cost, so per-purpose keys and frequent secret fetches carry a bill that scales with task count.