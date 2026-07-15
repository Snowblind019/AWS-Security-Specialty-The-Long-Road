# Nitro Encryption (the AWS Nitro System)

The AWS Nitro System is the hardware and firmware foundation under every modern EC2 instance: dedicated **Nitro cards** that offload networking, EBS, and instance storage, a **Nitro Security Chip** acting as a hardware root of trust, and a lightweight **Nitro Hypervisor** for CPU and memory allocation. "Nitro encryption" is not one feature, it is the set of cryptographic guarantees the system provides across three planes: data at rest, data in transit, and data in use, all anchored by one property: AWS operators have no mechanism to access instance memory or customer data, and that is written into the AWS Service Terms and independently affirmed. In the exam it is the answer to "how is EC2 data protected at the hardware layer without me configuring anything," and to "how do I process sensitive data isolated even from my own instance's root user."

The mental frame is three encryption planes plus one isolation guarantee, split by automatic vs configured. Memory encryption, EBS crypto offload, and instance-to-instance in-transit encryption are automatic or transparent. Nitro Enclaves for data in use, and NitroTPM for boot integrity, are the pieces you deliberately turn on.

## How it works

- **Hardware root of trust and operator isolation**: the Nitro Security Chip validates hardware and firmware integrity, and the design removes any interactive path (no SSH, no login) for AWS staff to reach the host or read instance memory. This is the confidential-computing baseline, not an opt-in.
- **At rest, memory**: instance DRAM is **always encrypted** on modern families, starting with AWS Graviton2, AMD EPYC (Milan), and Intel Xeon Scalable (Ice Lake). Instances using **AMD SEV-SNP** encrypt memory with an instance-specific key. No configuration, no measurable performance cost.
- **At rest, EBS**: encryption is offloaded to the Nitro card using **AES-256** with keys managed through **KMS**, transparent to the guest OS with no performance hit. You enable EBS encryption (and can set an account-level default so every new volume is encrypted), but the crypto itself is handled in hardware.
- **In transit**: supported Nitro instances **automatically encrypt instance-to-instance traffic** with AES-256-GCM under specific conditions (same Region, same or peered VPC, no load balancer / NAT / transit gateway in the path). The full conditions and fallbacks live in the Inter-Resource Encryption in Transit module. Traffic between an instance and its EBS volumes is likewise encrypted.
- **In use, Nitro Enclaves**: isolated, hardened virtual machines carved from a parent instance's own CPU and memory. They have **no persistent storage, no interactive access, and no external networking**, and communicate only over a local **vsock** channel to the parent. The parent instance, including its root user, cannot read the enclave's memory. Up to **four enclaves per instance**, processor-agnostic across Intel, AMD, and Graviton.
- **Enclave attestation and KMS**: the Nitro Hypervisor produces a **signed attestation document** containing the enclave's measurements (hashes and Platform Configuration Registers). Using the Nitro Enclaves SDK, the enclave calls KMS operations (`Decrypt`, `GenerateDataKey`, `GenerateRandom`) with that document attached. KMS validates the measurements against condition keys, then returns ciphertext encrypted to the enclave's public key, so only that enclave can decrypt. Gate with **`kms:RecipientAttestation:ImageSha384`** and **`kms:RecipientAttestation:PCR`** condition keys: PCR0 to PCR2 cover the image and kernel, PCR3 is a hash of the parent's IAM role ARN, PCR8 is the image-signing certificate.
- **NitroTPM**: a TPM 2.0 compliant module for measured boot and sealing secrets to instance state. KMS also supports attestation for NitroTPM.

## Automatic vs configured

| Layer | What is encrypted | Automatic or configured |
|---|---|---|
| Instance memory | DRAM, always-on | Automatic (Graviton2, AMD Milan, Intel Ice Lake and newer) |
| Operator access | No path to instance data at all | Automatic (contractual, hardware-enforced) |
| EBS at rest | Volume data, AES-256 via KMS | Configured (enable; can default account-wide), crypto offloaded to Nitro |
| Instance-to-instance and instance-to-EBS in transit | AES-256-GCM | Automatic under conditions (see Inter-Resource note) |
| Data in use | Isolated enclave memory and CPU | Configured (build enclave, set KMS attestation policy) |
| Boot integrity / key sealing | Measured boot state | Configured (NitroTPM on supported instances) |

## What gets tested

- Nitro is the hardware answer to "how is EC2 data protected without me configuring TLS or disk crypto everywhere." Memory is always encrypted on modern instances, and AWS operators have no mechanism to reach instance memory or data. That guarantee is contractual and independently affirmed, not marketing.
- Nitro Enclaves is the answer whenever the scenario needs sensitive data (PII, private keys, healthcare, multi-party computation) processed in isolation from the parent instance's own admins and applications. Recognize the constraints: no persistent storage, no interactive access, no external networking, vsock only, up to four per instance.
- Enclave plus KMS attestation is the confidential-computing crypto pattern: use `kms:RecipientAttestation:ImageSha384` or `:PCR` condition keys so a KMS key can be used only by an enclave whose measurements match. KMS re-encrypts the response to the enclave's public key. PCR3 ties access to a specific IAM role, PCR8 to a specific signing certificate.
- Do not confuse the roles. Nitro Enclaves isolates and attests processing, it is not a key store: it calls KMS. KMS manages keys. CloudHSM is the dedicated single-tenant HSM. NitroTPM handles boot integrity and sealing. A question that says "isolate processing even from root" is Enclaves.
- AMD SEV-SNP instances use an instance-specific memory encryption key. SEV-SNP and "confidential computing" in a stem point at Nitro.
- Instance-to-instance encryption is automatic but conditional. Route through a load balancer, NAT, or transit gateway and it stops, so you fall back to application-layer TLS. The conditions are the Inter-Resource note's territory.

## Limitations

- In-transit auto-encryption is conditional and breaks the moment traffic crosses an intermediary or leaves the stated conditions. It is not a universal guarantee.
- Enclave isolation is also a constraint: no storage, no networking beyond the vsock channel, and no SSH means you architect around the local socket and cannot shell in to debug. Enclaves are pinned to their parent, cannot migrate, and cannot talk to each other.
- Always-on memory encryption depends on processor generation. Older instance families predate it.
- NitroTPM and enclave attestation add real setup: managing PCR values, KMS condition-key policies, and signing the enclave image file. A wrong PCR or condition either locks the enclave out or widens access more than intended.
- Nitro provides confidentiality and isolation, not detection or remediation. Pair it with the services that watch and respond.