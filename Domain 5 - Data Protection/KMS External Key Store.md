# AWS KMS External Key Store (XKS)

XKS lets you use encryption keys that live entirely outside AWS, in your own on-prem HSM or external key manager, while still driving them through the KMS control plane. KMS never sees, caches, or stores the key material: it enforces IAM and key policy, logs to CloudTrail, then forwards each crypto operation over HTTPS to an XKS proxy you host, which relays to your external key manager where the actual encrypt/decrypt happens. This is BYOK taken to HYOK (host your own key), the extreme end of the custody spectrum for organizations that cannot let keys touch AWS even logically. The thing to hold onto: XKS keeps the KMS user experience (SSE-KMS, IAM, CloudTrail, service integration) while the key material and the cryptographic operation stay off AWS entirely, which is exactly what separates it from a CloudHSM custom key store where the HSM sits inside your AWS VPC.

## How it works

- **Your external key manager holds and uses the keys.** An on-prem HSM (Thales, Entrust) or external/sovereign key system stores the key material and performs the crypto. AWS never possesses it.
- **You run the XKS proxy.** A proxy you deploy and operate sits between KMS and your key manager, receiving signed HTTPS requests from KMS and translating them to your EKM's native protocol. It must be highly available and low latency, because every operation depends on it.
- **KMS holds only stubs.** You register the proxy and an external key store in KMS and create KMS key references that point at keys in your external system but contain no material. To KMS they look like keys, but the bytes live outside.
- **Runtime flow keeps AWS as authorizer only.** An Encrypt call (from a user or S3) hits KMS, which verifies IAM, checks grants and key policy, and logs to CloudTrail, then sends a signed request to your proxy. The proxy authenticates it, calls your EKM to perform the operation, and returns the result through KMS to the caller. AWS authorizes, you encrypt.
- **You own everything below the control plane.** Rotation, availability, scaling, latency, and security of the proxy and EKM are all yours. KMS does not rotate XKS keys.

## The custody spectrum, XKS at the far end

| Feature | KMS (default) | Custom Key Store (CloudHSM) | External Key Store (XKS) |
|---|---|---|---|
| **Key location** | AWS-managed HSM | Your CloudHSM, in your AWS VPC | On-prem / external, outside AWS |
| **Key material in AWS?** | Yes | Yes (in AWS) | Never |
| **Who performs the crypto** | AWS KMS HSM | Your CloudHSM | Your EKM via the proxy |
| **Control plane** | KMS | KMS | KMS |
| **Automatic rotation** | Yes | No, you manage | No, you manage |
| **AWS service integration** | Full | Full | Most, with some limits |
| **Setup complexity** | Low | Medium | High |

## What gets tested

- **XKS vs CloudHSM custom key store.** The decisive question is where the key material lives. XKS keeps it entirely outside AWS with crypto performed off-cloud, CKS keeps a single-tenant HSM inside your AWS VPC. "Keys must never enter AWS infrastructure at all" is XKS.
- **Sovereignty and off-cloud custody mandates.** Requirements like data-residency laws, Schrems II, or a regulator forbidding key storage in the cloud point to XKS, because it is the only model where AWS never holds the material.
- **KMS stays the control plane.** Even with keys off-cloud, IAM, key policy, grants, and CloudTrail still apply, so you keep the KMS UX and SSE-KMS integration. That retention of AWS-native features is the reason to choose XKS over pure client-side external crypto.
- **You own availability and rotation.** XKS keys are not auto-rotated, and if your proxy or EKM is down, KMS operations fail. A requirement for AWS-managed rotation or no external dependency rules XKS out.
- **Multi-cloud central custody.** Centralizing key custody across AWS, Azure, and GCP in one external vault is a classic XKS driver.

## Limitations

- You operate the proxy and the external key manager, so their uptime, latency, scaling, and security are entirely your burden, and any outage stops KMS operations that depend on them.
- No automatic rotation. Key rotation is managed in your external system, not by KMS.
- Highest setup complexity and cost of the custody options, appropriate only for organizations with mature security operations and a hard off-cloud mandate.
- Some AWS service integrations have limitations compared with native KMS, so not every KMS-integrated workflow behaves identically under XKS.
- Every operation adds a network hop to your proxy and EKM, so latency and the reliability of that path directly affect the services relying on the keys.
- If your external key manager loses the key material, AWS cannot help recover it, since by design AWS never had it.