# SSE-KMS

## What Is SSE-KMS

SSE-KMS is Server-Side Encryption with AWS Key Management Service (KMS) keys for Amazon S3 objects. Compared to SSE-S3, which hides the encryption process and keys from you, SSE-KMS opens the door to cryptographic control — logging, IAM enforcement, and contextual conditions.

The flow is simple:

- You upload a file to S3
- AWS encrypts it at rest using a data key
- That data key is generated and encrypted by AWS KMS, using either:
  - An AWS-managed CMK (e.g., `aws/s3`)
  - A Customer-managed CMK (SSE-KMS-CMK) that you create, tag, monitor, and restrict

But here’s where things start to get interesting:

- Access to the object now depends on two things:
  - S3 permissions (`s3:GetObject`, etc.)
  - KMS permissions (`kms:Decrypt`, etc.)

This two-layer model is what allows fine-grained control, data egress protection, cross-account key ownership, and CloudTrail-based alerting on sensitive access.

---

## Cybersecurity Analogy

If SSE-S3 is like storing your files in a locker with TSA’s keys, SSE-KMS is like having your own biometric vault inside the airport.

- S3 holds the data
- But KMS controls whether the vault will even hand over the key
- Even if someone gets access to the file, they can’t decrypt it unless KMS allows it

This separation is crucial in zero-trust, multi-account, and sensitive data architectures.

## Real-World Analogy

Imagine Snowy stores invoices in a locked room (S3). But instead of a generic key, access requires:

- A badge (IAM permission)
- A fingerprint scan (KMS decrypt permission)
- A security camera (CloudTrail)

With SSE-KMS:

- You define the encryption key
- You get to see who used it
- You can revoke access even if the object is still readable in theory

---

## How SSE-KMS Works in S3 Encryption

1. You upload an object with SSE-KMS enabled (header or bucket default)
2. AWS S3 sends a `GenerateDataKey` request to KMS
3. KMS returns:
  - The plaintext data key (used to encrypt the object)
  - The encrypted data key (wrapped by your CMK)
4. S3 stores:
  - The encrypted object
  - The wrapped data key
5. On read, S3 sends the encrypted key to KMS for `Decrypt`, gets the plaintext key, and decrypts the object

You never see the data key. But you control the CMK that governs it.

---

## Headers and Defaults

**Upload Header for SSE-KMS:**

```http
x-amz-server-side-encryption: aws:kms
x-amz-server-side-encryption-aws-kms-key-id: arn:aws:kms:region:acct:key/your-key-id
```

Or just let the **default bucket encryption** do the job.

---

## Types of Keys

| Key Type             | Description                                                                 |
|----------------------|-----------------------------------------------------------------------------|
| `aws/s3` (AWS-managed) | Default KMS key used automatically. No cost. You don’t manage it.          |
| Customer-managed CMK | Full control: key rotation, tagging, aliases, grants, deletion, policy      |

Use customer CMKs when you want:

- Auditable access via CloudTrail
- Key deletion or rotation
- Tag-based or condition-based access enforcement

---

## IAM Permissions

With SSE-KMS, users need both **S3 and KMS permissions**.
Otherwise, you get **silent failures or AccessDenied** errors.

**Example: Upload with SSE-KMS**
Requires:

- `s3:PutObject`
- `kms:GenerateDataKey`

**Example: Download**
Requires:

- `s3:GetObject`
- `kms:Decrypt`

Even if the user has full S3 access, they will fail if the **KMS policy denies them access to the CMK**.

---

## CloudTrail Logging

Every KMS API call is logged in CloudTrail:

- `GenerateDataKey` (on PUT)
- `Decrypt` (on GET)
- `Encrypt`, `ReEncrypt`, `CreateKey`, etc.

This enables:

- **Forensics**: See who decrypted which object and when
- **SIEM correlation**: Tie object access to user behavior
- **Detection engineering**: Alert if `Decrypt` happens in a sensitive region or from an unusual principal

SSE-KMS makes object-level access **auditable**.

---

## Bucket Policy + KMS Policy Combo

You can enforce encryption using both **S3 Bucket Policies** and **KMS Key Policies**.

### Bucket Policy Enforcement:

```json
{
  "Effect": "Deny",
  "Principal": "*",
  "Action": "s3:PutObject",
  "Resource": "arn:aws:s3:::snowy-sensitive-data/*",
  "Condition": {
    "StringNotEquals": {
      "s3:x-amz-server-side-encryption": "aws:kms"
    }
  }
}
```

### KMS Key Policy Example:

```json
{
  "Effect": "Allow",
  "Principal": { "AWS": "arn:aws:iam::123456789012:role/SnowyApp" },
  "Action": [ "kms:Decrypt", "kms:GenerateDataKey" ],
  "Resource": "*"
}
```

Combine both to fully lock down who can upload/decrypt and which encryption context applies.

---

## Ties to SCPs and Org-Wide Control

SSE-KMS shines in **multi-account governance**. Examples:

- SCP enforces `s3:PutObject` must include encryption with a specific CMK
- SCP blocks use of `aws/s3` and forces `arn:aws:kms:...:key/snowy-required-key`
- KMS key is owned in the **Security account**, but used across accounts via **grants**

You can prevent entire OUs from:

- Using the default AWS-managed key
- Uploading unencrypted content
- Decrypting objects without traceable keys

This turns **S3 + KMS into a centralized encryption authority.**

---

## Security Monitoring & Egress Control

With SSE-KMS, you can:

- See `kms:Decrypt` activity in CloudTrail
- Use EventBridge rules to trigger GuardDuty custom findings
- Monitor for suspicious `Decrypt` attempts from unexpected regions/accounts
- Enforce encryption context (e.g., `"aws:EncryptionContext:env": "prod"`)

This makes SSE-KMS ideal for:

- PII, logs, financial data
- DLP pipelines
- Healthcare, government, and regulated workloads

---

## Comparison Table (SSE-S3 vs SSE-KMS)

| Feature                    | SSE-S3           | SSE-KMS                          |
|----------------------------|------------------|----------------------------------|
| Key Type                  | AWS-managed      | AWS-managed or customer CMK      |
| CloudTrail Logs           | ❌ None          | ✔️ Yes (KMS API events)          |
| Key Rotation              | Auto             | Auto or manual                   |
| Fine-Grained Access Control | ❌              | ✔️ KMS IAM/Grants                |
| Revocation Capability     | ❌               | ✔️ (via KMS policy changes)      |
| Encryption Context Support | ❌               | ✔️                               |
| Cost                      | Free             | $1/month per CMK + usage         |

---

## Real-Life Snowy Scenario

Snowy’s team archives customer invoices in S3.

- They set default bucket encryption to SSE-KMS using a CMK
- Only finance roles get access to `kms:Decrypt`
- CloudTrail tracks every decrypt event
- If any rogue principal tries `kms:Decrypt` from a foreign region, **Security Hub** gets a finding

Later, they split accounts for dev/test/prod:

- Same CMK used via cross-account KMS grants
- All access remains centralized
- All actions logged and revocable

This kind of structure only works with **SSE-KMS**.

---

## Final Thoughts

**SSE-KMS is where S3 meets cryptographic intent.**

- It’s not just encryption — it’s *governed encryption*
- You get **control**, **visibility**, and **forensic trails**
- You can **scope**, **revoke**, **monitor**, and **detect misuse**
- It’s how you turn *data at rest* into **auditable, accountable assets**

---

Use SSE-KMS when:

- You care about data egress
- You want encryption context or tags
- You need to enforce key separation by tenant, region, or environment
- You want to correlate `GetObject` to a `kms:Decrypt` in CloudTrail
