# Client-Side Encryption with a Custom Key Store or HSM

This is the zero-trust extreme of data protection: you generate keys in hardware you control (CloudHSM, an on-prem HSM, or a third-party key manager like HashiCorp Vault, Thales, or Fortanix), encrypt the data locally in your own application before it ever leaves your environment, and upload only ciphertext to AWS. AWS never sees the key or the plaintext, there is no SSE, no KMS in the decrypt path, and no IAM condition keys governing the crypto. Everything (generation, storage, rotation, logging, availability) is on you. The thing to hold onto: this is client-side encryption where the key custody lives entirely outside AWS's reach, which is distinct from XKS (a server-side SSE-KMS pattern where KMS calls out to your external key store), and the trade you are making is maximum assurance for the total loss of AWS's guardrails, logging, and recovery.

## How it works

- **Key generation happens in your custody.** A CloudHSM cluster, an on-prem or colocated HSM, or an external KMS/Vault produces and holds the key material. AWS has no handle on it.
- **Encryption happens in your application, before upload.** Your code (often via the AWS Encryption SDK or your own crypto libraries) performs envelope encryption with AES-256-GCM or similar, wrapping data keys under your HSM-held master key.
- **Only ciphertext lands in AWS.** S3 or any AWS store receives an opaque binary blob. It cannot tell the object is encrypted, applies no SSE, and holds no key. You can store wrapped-key metadata alongside the object for later decryption.
- **Decryption happens off the AWS control plane.** Your systems fetch the ciphertext, unwrap the data key using your HSM/Vault, and decrypt locally. No AWS API participates, so a compromised AWS credential or a rogue cloud admin cannot read the data.
- **The AWS Encryption SDK standardizes the envelope.** It handles multi-master keyrings (for example an HSM primary plus a backup), structured ciphertext metadata, and DEK wrapping formats, so you are not inventing a serialization scheme. You still write the integration to your Vault/HSM and secure DEK handling in memory.
- **This is not XKS.** XKS (KMS External Key Store) is a server-side model: SSE-KMS keeps working but KMS reaches out to an external key store you host for the wrap/unwrap. That still routes through KMS and produces CloudTrail records. The pattern in this module keeps AWS out of the crypto path entirely.

## Where this sits vs the other encryption models

| Model | Who holds the key | Who does the crypto | AWS in the path |
|---|---|---|---|
| **SSE-S3** | AWS | AWS (server-side) | Fully |
| **SSE-KMS** | AWS KMS (your CMK) | AWS (server-side) | Fully, CloudTrail-logged |
| **XKS (external key store)** | You, outside AWS | AWS server-side, KMS calls your store | KMS orchestrates, logged |
| **Client-side KMS CMK** | AWS KMS | Your app (client-side) | KMS for the data key only |
| **Client-side custom HSM/Vault** | You only | Your app (client-side) | None |

## What gets tested

- **Client-side custom HSM vs client-side KMS CMK.** If the requirement is that AWS must have zero access to keys and zero decrypt path, that is the custom HSM/Vault model. If AWS holding the CMK (with CloudTrail and IAM conditions) is acceptable, client-side KMS is simpler and preferred.
- **This model vs XKS.** "Keys outside AWS but I still want SSE-KMS and CloudTrail logging" is XKS. "AWS is out of the crypto path completely, I encrypt in my app" is client-side custom HSM. Do not conflate them.
- **Sovereignty and Schrems II style mandates.** Requirements that the provider cannot access data or keys, cross-border restrictions, or air-gapped trust boundaries push to this model.
- **The cost of leaving AWS's guardrails.** Choosing this model means accepting no CloudTrail on the crypto, no IAM condition-key enforcement, manual rotation and re-encryption, and no AWS recovery if the key is lost.
- **S3 bucket policies cannot enforce it.** Because encryption is client-side and the key is external, you cannot write an S3 policy that requires or validates this encryption the way you can with SSE-KMS.

## Limitations

- No CloudTrail visibility into encryption or decryption. Your only crypto audit trail is whatever your HSM or Vault logs itself.
- No IAM or KMS condition-key controls over the keys, and no S3 bucket-policy enforcement of the encryption, because AWS never sees the key.
- Manual rotation. Rotating a key means re-encrypting objects yourself, there is no managed rotation.
- No AWS backup or recovery. If your HSM dies or the key is lost, the data is unrecoverable and AWS cannot help by design.
- High complexity and operational burden. You own key availability, DEK handling in runtime memory, integration code, and disaster recovery for the key infrastructure.
- Easy to conflate with XKS, which is a different, server-side pattern. Choosing the wrong one gives you either more AWS involvement than a sovereignty mandate allows, or more operational burden than you needed.