# AWS Encryption SDK

The AWS Encryption SDK is a client-side encryption library that gives you correct envelope encryption without hand-rolling the crypto plumbing. You call `encrypt()` with a key provider and it generates a data key, encrypts your data locally with authenticated encryption (AES-GCM), wraps the data key under one or more master keys, and returns a self-describing ciphertext that carries its own algorithm, wrapped keys, and encryption context. It works across languages (Python, Java, JavaScript, C, .NET) and against KMS, CloudHSM, or external key managers like Vault. Its distinguishing features are multi-master-key wrapping (encrypt one DEK under several keys so any one can decrypt), encryption context (authenticated metadata that must match on decrypt), and streaming for large files. The thing to hold onto: this is client-side crypto, so AWS never sees the plaintext, the ciphertext is portable and self-describing, and the two levers the exam cares about are encryption context (integrity and scoping) and multi-key providers (region resilience and KMS-plus-external decryption paths).

## How it works

- **One call does envelope encryption.** `encrypt()` generates a random DEK, encrypts the data locally with AES-GCM, and wraps the DEK with the configured master key(s). With KMS this is a single `GenerateDataKey` call that returns both the plaintext DEK (used and discarded) and the already-wrapped DEK, so no separate `Encrypt` call is needed to wrap it.
- **The ciphertext is self-describing.** It carries a header with the algorithm, key/provider info (ARNs, IDs), the encryption context, and every wrapped DEK. Any system with access to a matching master key can decrypt it later, and it is portable across Regions, accounts, and even clouds.
- **Decryption reverses cleanly.** The SDK reads the header, uses the configured key provider to unwrap a DEK (calling KMS `Decrypt` for a KMS key), verifies the encryption context matches, then decrypts locally and returns plaintext.
- **Encryption context is authenticated metadata.** A key-value map (for example service, tenant, env) bound into the ciphertext and required to match exactly on decrypt. It provides integrity binding and scoping, and it appears in CloudTrail on KMS calls so you can audit and even condition key policies on it.
- **Multi-master-key wrapping gives resilience.** The same DEK is wrapped under several master keys, so a ciphertext encrypted under a KMS key in one Region plus a Vault key can be decrypted by either. This is the pattern for multi-Region workloads and KMS-plus-external decryption.
- **Data key caching controls cost.** For high-volume workloads the SDK can cache and reuse DEKs within configurable limits, trading a small amount of key isolation for far fewer KMS calls, and streaming lets you encrypt 50 GB files without loading them fully into memory.

## Encryption SDK vs plain client-side KMS

| Aspect | Plain client-side KMS (`GenerateDataKey` yourself) | AWS Encryption SDK |
|---|---|---|
| **Envelope format** | You design it | Standardized, versioned, self-describing |
| **Multi-key** | You build it | Built-in multi-master-key wrapping |
| **Encryption context** | Manual | First-class, enforced on decrypt |
| **Streaming large files** | You implement | Built-in |
| **Key providers** | KMS only unless you code more | KMS, CloudHSM, Vault, custom plugins |
| **DEK caching** | You build it | Built-in with policy limits |

## What gets tested

- **Encryption context for integrity and scoping.** When a scenario needs to bind ciphertext to a tenant/purpose or enforce that a key is only used in a given context, that is the encryption context, which must match on decrypt or the operation fails, and which is auditable and conditionable in KMS.
- **Multi-master-key for cross-Region and hybrid.** Encrypting under multiple master keys so any one can decrypt is the answer for multi-Region resilience or a KMS-plus-external-HSM decryption path. This is a distinguishing SDK capability.
- **Client-side, AWS never sees plaintext.** Like client-side KMS CMK, this keeps AWS out of the plaintext path, but the CMK still lives in KMS, so it does not by itself satisfy "AWS must never hold the key" (that is a custom/external provider).
- **SDK vs SSE.** If the requirement is control over the envelope, portability, streaming, or multi-key, the Encryption SDK beats server-side SSE-S3/SSE-KMS. If simplicity and server-side handling are fine, SSE is simpler.
- **Data key caching for cost.** High call volume against KMS is mitigated with the SDK's data key caching, at a small isolation trade-off.

## Limitations

- You own plaintext DEK hygiene in memory. The SDK cannot protect a DEK from an application that logs it, caches it to disk, or is itself compromised.
- Application compromise defeats it. If the app can decrypt legitimately, an attacker who owns the app can decrypt too, since the SDK will happily unwrap for whoever holds the credentials.
- The CMK still lives in KMS for KMS providers, so this is not a sovereignty solution on its own. Keys fully outside AWS require a custom or external key provider.
- Multi-key misconfiguration is a real risk. Wrapping under the wrong combination of master keys can either widen who can decrypt or lock you out of a decryption path.
- Skipping encryption context weakens the integrity and scoping guarantees, so omitting it forfeits one of the SDK's main benefits.
- Data key caching trades isolation for cost. Overly aggressive caching reuses a DEK across more data than you might want, so cache limits must be set deliberately.