# AWS KMS Custom Key Store (CloudHSM-backed)

A KMS custom key store (CKS) lets you back KMS keys with your own CloudHSM cluster instead of AWS-managed HSMs, while keeping the entire KMS experience: the same APIs, IAM and key policies, grants, CloudTrail logging, and integration with S3, EBS, RDS, and Lambda. It is the deliberate middle ground between plain KMS (AWS holds the key material) and raw CloudHSM (you hold everything but lose KMS integration): KMS still orchestrates policy and forwards each crypto operation to your HSMs, which perform it with key material AWS cannot see. The thing to hold onto: CKS gives you single-tenant FIPS 140-2 Level 3 custody plus full KMS integration, it is how KMS-based AWS services can use CloudHSM-held keys, and there are two custom-key-store flavors that the exam contrasts, CloudHSM-backed (keys in your CloudHSM inside AWS) and external key store / XKS (keys in a key manager you run outside AWS).

## How it works

- **You run the CloudHSM cluster.** Deployed in your VPC, owned and operated by you (scaling, availability, backups, credentials). Key material lives here and is never visible to AWS personnel or services, only KMS has runtime access to perform operations.
- **KMS links to it as a custom key store.** You configure a CKS in KMS and connect it to the cluster. You then use standard KMS APIs (`CreateKey`, `Encrypt`, `Decrypt`), and behind the scenes KMS routes each operation to your CloudHSM, which does the crypto and returns the result to the calling service.
- **KMS manages, the HSM performs.** Policies, IAM, grants, and CloudTrail all work exactly as with a normal KMS key, but the actual encrypt/decrypt/sign happens in your hardware with your key material.
- **You own the key lifecycle.** You create, delete, and back up keys with CloudHSM tooling. KMS can use them but cannot export them, and it does not automatically rotate them, rotation is manual and your responsibility.
- **It plugs into KMS-integrated services.** Because a CKS key is still a KMS key, SSE-KMS on S3, EBS encryption, RDS, and envelope encryption all work unchanged, just routed through your HSMs. This is the whole reason to use CKS over raw CloudHSM.

## The key-custody spectrum

| Feature | KMS (default) | Custom Key Store (CloudHSM) | CloudHSM only | External Key Store (XKS) |
|---|---|---|---|---|
| **Key custody** | AWS-managed HSMs | Your CloudHSM, in AWS | Your CloudHSM, in AWS | Your key manager, outside AWS |
| **KMS APIs** | Full | Full | None (raw PKCS#11/JCE/CNG) | Full via XKS proxy |
| **Automatic rotation** | Yes | No, manual | No | No |
| **S3/EBS/RDS integration** | Yes | Yes | No | Yes |
| **CloudTrail** | Yes | Yes | No (HSM-side only) | Yes |
| **Best for** | General purpose | Compliance + AWS integration | Full HSM control, non-AWS crypto | Keys must live outside AWS |

## What gets tested

- **CKS is how KMS services use CloudHSM keys.** When a scenario needs S3 SSE-KMS or EBS encryption but with keys in a customer-controlled, single-tenant, Level 3 HSM, the answer is a CloudHSM-backed custom key store, not raw CloudHSM (which has no KMS integration) and not plain KMS (AWS holds the key).
- **CKS vs XKS.** CloudHSM-backed CKS keeps the HSM inside AWS in your VPC. XKS puts the key material in a key manager you host entirely outside AWS. "Keys must never be on AWS infrastructure at all" is XKS. "Single-tenant HSM under my control but inside AWS, with KMS integration" is CKS.
- **No automatic rotation.** Custom key store keys are not auto-rotated by KMS, so rotation is a manual, customer-owned operation. A requirement for AWS-managed automatic rotation rules out CKS.
- **KMS keeps the control plane.** IAM, key policies, grants, and CloudTrail all still apply, which is the advantage over raw CloudHSM where you lose native AWS audit and integration.
- **Compliance/custody driver.** FIPS 140-2 Level 3 with customer custody plus a demand to keep AWS-native workflows is the signal for CKS.

## Limitations

- You operate the CloudHSM cluster, so availability, backups, credentials, and capacity are your responsibility, and a broken or unreachable cluster makes the keys unusable.
- No automatic rotation. Rotation is manual via CloudHSM tooling, unlike default KMS keys.
- High cost and operational maturity required. CloudHSM instances are expensive and the model suits high-compliance organizations, not general use.
- It is single-tenant HSM inside AWS, so it does not satisfy mandates that key material never touch AWS infrastructure at all, that is XKS territory.
- Losing or mismanaging the CloudHSM key material is unrecoverable through AWS, since AWS cannot access or export it by design.
- Every crypto operation depends on the cluster's availability and adds a hop, so latency and the cluster's uptime directly affect the KMS-integrated services relying on it.