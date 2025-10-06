# Secrets Management

## What Is Secrets Management

**Secrets Management** is the practice of securely storing, accessing, rotating, and auditing credentials such as:

- API keys  
- Database passwords  
- OAuth tokens  
- SSH keys  
- Certificates  
- Cloud service tokens  
- Encryption keys (KMS/SSL private keys)  

In AWS, this is handled via:

- **AWS Secrets Manager**  
- **SSM Parameter Store** (`SecureString`)  
- **KMS** (for encryption)  
- Optionally: **external tools like HashiCorp Vault**

**Why this matters:**  
Secrets are often the *keys to the kingdom* — a leaked RDS password or access token can lead to full data compromise or infrastructure manipulation.

The most common mistake?

- Hardcoding secrets in:
  - Lambda environment variables
  - GitHub repos
  - Dockerfiles
  - Configuration files

Attackers *actively scan public repos and artifact registries* to harvest secrets.  
You need a centralized, encrypted, access-controlled, **auditable** way to manage them — with fine-grained permissions and rotation policies.

---

## Cybersecurity Analogy

Think of secrets as the **master keys** to every room in a skyscraper.

If you tape the keys to the wall next to the door (hardcoded secrets), or let every intern have a copy (overpermissioned IAM), it’s only a matter of time before the building is breached.

**Secrets management** is your vault — with biometric locks, access logs, key rotation policies, and real-time alerts if someone touches the door.

## Real-World Analogy

Let’s say you run a large restaurant.

Each kitchen station (API, Lambda, container) needs access to specific tools and ingredients (secrets). If you let every chef grab anything from the back room, they’ll:

- Trip over each other  
- Waste resources  
- Maybe grab the wrong item (e.g. prod DB creds in dev)

**Instead**, you:

- Lock ingredients in labeled bins  
- Assign access badges to only the stations that need them  
- Rotate items (e.g. fresh food daily)  
- Monitor who opened what, and when  

AWS gives you this system via **Secrets Manager**, **IAM**, **KMS**, and **audit logs**.

---

## How It Works

### 1. AWS Secrets Manager

Fully managed secrets storage and rotation service:

- Stores **encrypted secrets** (RDS passwords, API keys, etc.)
- Integrated with **KMS** for encryption
- Supports **automatic rotation via Lambda**
- Allows **fine-grained access control via IAM**
- Integrated with **CloudTrail for audit logging**

**Native support for:**

- RDS (MySQL, PostgreSQL, Aurora)  
- Redshift  
- DocumentDB  

**How it’s secured:**

- Secrets are encrypted at rest with a **KMS CMK**
- Access is controlled with **IAM policies**
- Secrets are retrieved **at runtime** by apps using the SDK/CLI
- You can attach **resource policies** to secrets for **cross-account access**

### 2. SSM Parameter Store (`SecureString`)

Alternative to Secrets Manager — often used for:

- Smaller secrets  
- Configuration values  
- Scripts and parameters  

**SecureString type:**

- Encrypted with **KMS**  
- Slower than Secrets Manager for rotation/auditing  
- No built-in rotation feature  
- IAM-controlled  

**Use this when:**

- You need fewer features  
- Want to avoid Secrets Manager costs  
- Already using SSM for config  

### 3. IAM Access Control

Critical for both **Secrets Manager** and **Parameter Store**.  
Use **least privilege IAM roles**:

- Allow `secretsmanager:GetSecretValue` only to the *specific secret ARN*  
- Avoid wildcard access (`*`)  
- Attach IAM conditions:
  - `aws:username`
  - `secretsmanager:SecretId`
  - `secretsmanager:VersionStage`

**Example IAM policy:**

```json
{
  "Effect": "Allow",
  "Action": "secretsmanager:GetSecretValue",
  "Resource": "arn:aws:secretsmanager:us-west-2:123456789012:secret:db-prod-*"
}
```

Use IAM roles for service accounts (`IRSA`) in EKS or **Lambda execution roles** to scope access tightly.

### 4. Rotation

Secrets Manager supports **automatic rotation** via Lambda:

- Create a Lambda with logic to:
  - Rotate DB credentials
  - Update app config (optional)
  - Test the new secret

**Rotation can be:**
- Scheduled (e.g., every 30 days)  
- Triggered manually  
- Managed across accounts  

This **reduces the window of exploitation** if a secret is leaked.

**SSM** has no native rotation — you'd have to build it manually with Lambda + KMS.

### 5. Auditing and Monitoring

AWS provides native observability:

- **CloudTrail**: records all access to secrets (`GetSecretValue`, `PutSecretValue`)  
- **CloudWatch Logs**: capture **rotation Lambda logs**  
- **AWS Config**: can **track changes to secrets**  

- **Security Hub**: pulls findings for **overpermissioned access**

You can set up **GuardDuty** or **custom CloudWatch alarms** to detect:

- Unusual access patterns  
- Access from new IPs  
- Secrets being accessed outside working hours  

### 6. Encryption (KMS Integration)

Secrets in both **Secrets Manager** and **SSM SecureString** are encrypted using **KMS CMKs**:

- Default AWS-managed keys (`aws/secretsmanager`)  
- Or **Customer Managed Keys (CMKs)** for tighter control  

You can:

- Audit access to the KMS key via **CloudTrail**  
- Use **key policies** and **grants** to control decryption  
- Enable **key rotation** for CMKs  
- Set **automatic deletion windows** for retired keys  

> **Important:**  
> Revoking a key without updating the secrets breaks retrieval — **rotate the secret before key deletion**.

### 7. Common Pitfalls to Avoid

| Mistake | Why It’s Dangerous |
|--------|---------------------|
| Hardcoding secrets in code or env vars | Leaks in GitHub, logs, or memory dumps |
| Wildcard access to all secrets | Privilege escalation risk |
| No rotation policy | Stale secrets are easy targets |
| Not using audit logs | Blind to breaches or misuse |
| Sharing secrets across stages (dev/prod) | Risk of cross-environment compromise |
| Decrypting secrets too early (at container startup) | Secrets persist in memory or logs |

---

## Pricing Models

| **Service**           | **Pricing Notes**                                                              |
|-----------------------|---------------------------------------------------------------------------------|
| Secrets Manager       | $0.40 per secret per month + $0.05 per 10K API calls                           |
| SSM Parameter Store   | Free for `String`, paid for `SecureString` with advanced tier                  |
| KMS                   | $1/month per key + API calls                                                   |
| CloudTrail, CW Logs   | Charged separately per GB ingested/stored                                      |

> **Tip:** Rotate secrets on schedule and **cache them securely in memory** (not on disk) to reduce costs.

---

## Real-Life Snowy-Style Example

**SnowyCorp** has a microservices architecture.  
The API Gateway calls a Lambda that:

- Reads a secret from **Secrets Manager**  
- Uses it to connect to an **RDS Aurora cluster**  
- Logs the transaction and closes the connection  

**Bad practice:**

- Secret hardcoded in Lambda env var  
- IAM role allows `GetSecretValue` on `*`  
- Secret rotated manually (once a year)  
- No CloudTrail monitoring  

**Attack scenario:**

- Lambda gets dumped due to a bug  
- Env vars expose the plaintext DB password  
- Attacker uses credentials to exfiltrate customer data  

**Fixed:**

- Secret stored in **Secrets Manager**, encrypted with a **CMK**  
- IAM policy scoped to `arn:aws:secretsmanager:us-west-2:...:secret:prod-rds-1a2b3c`  
- Lambda fetches secret at runtime  
- Rotation every 30 days, with test + verify logic  
- CloudTrail alerts on suspicious access  

**Result:**  
Even if the Lambda is compromised, secrets are not sitting in memory or logs, and access is **audited + limited**.

---

## Final Thoughts

Secrets are the **crown jewels**.  
Treat them like credentials with **expiry dates**, **access boundaries**, and **audit trails** — not static values.

**Secrets Manager** gives you:

- KMS-backed encryption  
- IAM + resource policies  
- Auto rotation  
- Native auditing  

**SSM** gives you a **lightweight alternative** for configs and small secrets.

> **Golden Rule:**  
> You **shouldn’t need to open a secret manually**.  
> Every app should fetch, decrypt, and rotate them automatically — and you should know *when* and *why* each access happens.

