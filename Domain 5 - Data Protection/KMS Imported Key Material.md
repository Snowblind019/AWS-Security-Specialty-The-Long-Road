# KMS Imported Key Material

A KMS key whose key material you generate yourself and import (origin EXTERNAL, also called BYOK), rather than letting AWS generate it (the default, origin AWS_KMS). Task 5.3.3 is about knowing the difference and when each applies. With imported material you are the source of truth: you keep the copy, you control durability and expiry, and AWS cannot recover it if you lose it.

The distinction the exam wants: AWS-generated key material (default) is simpler — AWS handles generation, durability, and rotation. Imported key material is for when you must generate keys outside AWS for compliance or provenance, or need to control the key's lifecycle (expire it, delete the material on demand). It is not the same as an external key store: with imported material the key still lives and is used inside KMS; with an external key store the material never enters AWS.

## How it works

- Create a KMS key with **origin EXTERNAL**; it starts with no material ("pending import").
- KMS gives you a **wrapping public key (RSA)** and an **import token** (both expire in 24h). You wrap your 256-bit key material and import it.
- After import the material lives in KMS and the key works like any other, with these differences:
  - You can set the material to **expire** on a date (AWS-generated material cannot).
  - You can **delete the imported material on demand**, immediately disabling the key without the 7–30 day key-deletion waiting period; re-import later to restore.
  - **Rotation**: automatic rotation is *not* supported. On-demand rotation *is* supported — you import new material first, then rotate; the key ID/ARN stays the same and KMS retains old material for decryption. (Older guidance said you had to create a new key; that is no longer required.)
  - If your only copy is lost and the material expires or is deleted, the data is **unrecoverable**; AWS cannot regenerate it.
- Historically symmetric only; KMS now also supports importing asymmetric and HMAC key material. Multi-Region keys can use imported material (import the same material into each replica).

## Imported vs AWS-generated vs external

| | Where material is generated | Where it lives / is used |
|---|---|---|
| AWS-generated (AWS_KMS) | AWS | In KMS |
| Imported (EXTERNAL) | You, outside AWS | Imported into KMS, used in KMS |
| External key store (XKS) | You, in your HSM | Stays in your external HSM; never in KMS |

## What gets tested

- Imported key material means you generate the key outside AWS and import it — the answer when there is a compliance or provenance requirement to create keys on your own HSM, or a need to control the key's durability.
- You retain the source copy and own durability: lose it (and let the material expire or be deleted) and the data is unrecoverable. That is the trade for control.
- Imported material can **expire** and can be **deleted on demand** for immediate key disablement (no deletion waiting period). These lifecycle controls are the main reasons to choose it.
- Rotation: no automatic rotation for imported material; use on-demand rotation (import new material, then rotate) or, on older accounts, manual rotation. AWS-generated keys support automatic annual rotation.
- Do not confuse it with an **external key store**: imported material ends up inside KMS; XKS keeps material in your external HSM and KMS never stores it. "Key must never be stored in AWS" points to external key store, not imported.
- The default (AWS-generated) is recommended unless a specific requirement forces import.

## Limitations

- You own key durability — losing your copy can mean permanent data loss.
- No automatic rotation; on-demand rotation requires you to import new material first.
- Import token and wrapping key expire in 24 hours.
- More operational burden than the AWS-generated default.