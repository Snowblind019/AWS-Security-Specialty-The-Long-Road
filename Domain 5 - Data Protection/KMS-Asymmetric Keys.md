# AWS KMS: Asymmetric Keys

Asymmetric KMS keys are RSA or ECC public/private key pairs where the private key never leaves KMS and the public key can be freely downloaded, shared, or embedded in clients. They come in two usage types: `ENCRYPT_DECRYPT` (public key encrypts, private key decrypts) and `SIGN_VERIFY` (private key signs, public key verifies). The point is enabling trust across a boundary where the other side should never get KMS access: clients encrypt on-device before uploading, or external partners verify your signatures locally, all without you exporting a private key or handing out decrypt permissions. The thing to hold onto: use symmetric keys for bulk and AWS-service encryption and DEK wrapping, and reach for asymmetric only when you need cross-boundary encryption or public signature verification, and remember that asymmetric KMS keys do not support automatic rotation, unlike symmetric ones.

## How it works

- **You pick usage type and key spec at creation.** `ENCRYPT_DECRYPT` or `SIGN_VERIFY`, and an RSA or ECC spec. A key does one job, you cannot both encrypt and sign with the same key.
- **The public key is distributable, the private key is not.** `GetPublicKey` lets any permitted caller download the public key with no decrypt or sign rights. Only KMS ever performs the private-key operation (`Decrypt` or `Sign`), and the private key is never exportable.
- **Encrypt/decrypt flow.** Clients call `GetPublicKey` once, encrypt locally with the public key (no AWS call per encryption), and your server calls KMS `Decrypt` with the private key to read it. RSA has strict plaintext size caps, so for anything large you use envelope encryption via `GenerateDataKeyPair`.
- **Sign/verify flow.** Your service calls KMS `Sign` with the private key, and anyone holding the public key verifies locally (or via `Verify`) without KMS access. This is how you give external parties verification trust while keeping the signing key inside KMS.
- **Access is IAM plus key policy, logged in CloudTrail.** `kms:Sign` and `kms:Decrypt` are the sensitive permissions to scope tightly, `kms:GetPublicKey` is safe to grant broadly, and grants, conditions, and encryption context wrap around access the same as symmetric keys. Every operation is logged.
- **Rotation is manual.** KMS automatic annual rotation applies to symmetric keys only. For an asymmetric key you rotate by creating a new key pair and distributing the new public key to clients, then retiring the old one. There is no one-click rotation that preserves the public key.

## Symmetric vs asymmetric KMS keys

| Feature | Symmetric | Asymmetric |
|---|---|---|
| **Key material** | AES-256 | RSA or ECC pair |
| **Exportable** | No | Public key only |
| **Operations** | Encrypt, Decrypt, GenerateDataKey | Encrypt/Decrypt or Sign/Verify (one per key) |
| **Automatic rotation** | Yes | No, manual only |
| **Performance** | Very fast | Slower, especially RSA |
| **Best for** | AWS-service encryption, DEK wrapping, bulk | Cross-boundary encryption, public signature verification |

## What gets tested

- **Asymmetric keys do not auto-rotate.** If a scenario relies on automatic annual KMS rotation, the key must be symmetric. Rotating an asymmetric key is a manual create-and-redistribute process. This is the most tested asymmetric detail.
- **When to choose asymmetric over symmetric.** Encrypting outside AWS without granting KMS access, or letting external parties verify signatures without decrypt access, calls for asymmetric. Bulk encryption, EBS/S3/RDS, and DEK wrapping stay symmetric because asymmetric is slow and size-limited.
- **One usage type per key.** A key is either encrypt/decrypt or sign/verify, not both. A question that needs both requires two keys.
- **Public key distribution is safe, decrypt/sign grants are not.** The exposure risk is over-granting `kms:Decrypt` or `kms:Sign`, not sharing the public key. Scope those with conditions and monitor `Sign`/`Decrypt` volume.
- **RSA size limits push to `GenerateDataKeyPair`.** Directly encrypting large data with an RSA public key fails on size, so envelope encryption with a data key pair is the pattern.
- **Private key never leaves KMS.** Requirements that the signing or decryption key must never be exportable or exposed on an instance point to KMS asymmetric keys over homegrown crypto.

## Limitations

- No automatic rotation. Rotating an asymmetric key means generating a new pair and redistributing the public key, with the client-side coordination that implies.
- One operation per key. You cannot use the same asymmetric key for both encryption and signing, so multi-purpose designs need multiple keys.
- Slow and size-limited. RSA in particular is far slower than symmetric AES and caps plaintext size, making asymmetric a poor fit for bulk or high-throughput encryption.
- The private-key operations still run in KMS, so decrypt and sign are subject to KMS request limits and cost, and heavy signing volume adds latency and bill.
- Security depends on scoping `kms:Sign` and `kms:Decrypt`. A broad grant on those undermines the whole model even though the public key is harmless to share.
- It solves cross-boundary trust, not bulk confidentiality. For encrypting large volumes you still fall back to symmetric keys and envelope encryption.