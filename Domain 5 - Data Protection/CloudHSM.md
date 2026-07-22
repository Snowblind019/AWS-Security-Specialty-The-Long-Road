# AWS CloudHSM

AWS CloudHSM is single-tenant, dedicated cryptographic hardware (FIPS 140-2 Level 3 validated HSMs) that runs in your VPC and gives you sole control of the keys. It is the deliberate opposite of KMS: where KMS is managed encryption-as-a-service with AWS operating the backend, CloudHSM hands you the appliance, and AWS staff and services cannot access or decrypt your key material under any circumstances. You provision it, you manage users and roles inside it, you handle backup and rotation, and you own the operational burden that comes with that control. The thing to hold onto: reach for CloudHSM only when a requirement forces sole tenancy, Level 3 validation, key export, or a non-AWS crypto API (PKCS#11, JCE, CNG), and remember that to make KMS-integrated AWS services use those HSMs you front CloudHSM with a KMS custom key store rather than calling the HSM directly.

## How it works

- **Dedicated HSM cluster in your VPC.** Launching CloudHSM provisions physical HSM appliances reserved for you, attached to your VPC via ENIs and clustered across AZs for availability. There is no shared backend, unlike KMS.
- **You own the identity and lifecycle inside the HSM.** You create crypto officers (CO), crypto users (CU), and appliance users/auditors, generate or import keys, and perform operations (encrypt, sign, wrap, tokenize) through the HSM client. AWS only keeps the hardware healthy and provides network reachability.
- **Keys never leave in the clear, but export under policy is possible.** Key material stays in tamper-resistant hardware that can zeroize on physical tampering. Unlike KMS, CloudHSM supports exporting keys under wrapping policy, which is what enables BYOK and hybrid on-prem HSM workflows.
- **Non-AWS crypto APIs are the differentiator.** CloudHSM exposes PKCS#11, JCE, and Microsoft CNG, so it can back a custom certificate authority, custom signing workflows, or non-AWS applications running on EC2 or on-prem that need HSM-backed operations.
- **Integrating with AWS services goes through a KMS custom key store.** AWS services that expect a KMS key (S3, EBS, Redshift) cannot call an HSM directly. You create a KMS custom key store backed by your CloudHSM cluster, and KMS operations are then performed in your HSMs, giving you single-tenant hardware with normal KMS integration.
- **Auditing and backup are yours.** Key usage inside the HSM is not recorded in CloudTrail the way KMS calls are, so you implement HSM-side auditing, and you are responsible for cluster backup and key redundancy.

## CloudHSM vs the key-custody spectrum

| Option | Who holds the HSM | Tenancy | Use it when |
|---|---|---|---|
| **KMS (default)** | AWS | Multi-tenant | Managed encryption, CloudTrail logging, low ops |
| **KMS custom key store (CloudHSM-backed)** | You (CloudHSM in your VPC) | Single-tenant | Need Level 3 single-tenant HSMs but with KMS integration |
| **CloudHSM direct** | You | Single-tenant | PKCS#11/JCE/CNG, custom CA, key export, non-AWS apps |
| **KMS External Key Store (XKS)** | You, outside AWS entirely | External HSM/KMS you run | Keys must live outside AWS and you still use KMS APIs |

## What gets tested

- **CloudHSM vs KMS.** Single-tenant dedicated hardware, FIPS 140-2 Level 3, customer sole control, key export, and non-AWS crypto APIs point to CloudHSM. Managed, automated, CloudTrail-logged, low-cost encryption points to KMS.
- **Making AWS services use CloudHSM.** The correct pattern is a KMS custom key store backed by CloudHSM, not direct service-to-HSM integration. This is a frequent distractor.
- **XKS is external, not CloudHSM.** KMS External Key Store connects KMS to a key manager you host outside AWS. It does not run on CloudHSM. If the requirement is keys physically outside AWS while still using KMS, that is XKS. If it is single-tenant hardware inside AWS, that is a CloudHSM-backed custom key store.
- **Sole-control and sovereignty requirements.** "Prove AWS cannot access the keys," jurisdictional key ownership, or a regulator that demands single tenancy pushes you to CloudHSM.
- **Logging gap.** Operations inside the HSM are not in CloudTrail, so if the scenario needs AWS-native audit of every key use, plain KMS is a better fit than raw CloudHSM.

## Limitations

- No AWS-managed backup or rotation. Cluster redundancy, key backup, and rotation are entirely your responsibility, and losing the credentials means AWS cannot recover the keys.
- No CloudTrail visibility into in-HSM key usage. You must build HSM-side auditing to know how keys were used.
- High cost and high complexity. It is billed per HSM per hour and demands real crypto, networking, and operational expertise, so it is a niche choice rather than a default.
- No direct integration with KMS-based AWS services. Those need a KMS custom key store in front of the cluster.
- XKS is a separate, external mechanism and does not run on CloudHSM, so treating them as the same thing is a mistake.
- Getting it wrong is unforgiving. The same isolation that keeps AWS out also means there is no support path to recover mismanaged keys or a broken cluster.