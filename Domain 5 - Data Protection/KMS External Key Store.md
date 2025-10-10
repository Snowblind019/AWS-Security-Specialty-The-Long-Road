# AWS KMS External Key Store (XKS)

## What Is the Service

AWS KMS External Key Store (XKS) is a specialized feature that allows you to use encryption keys stored entirely outside of AWS infrastructure — such as in your on-premises HSM, private key manager, or a sovereign cloud key control system.

Unlike CloudHSM or CKS, where AWS may still run the hardware or communicate directly with your key material:  
In XKS, AWS KMS never sees your key material. Ever.

KMS delegates all crypto operations to an external proxy that you host and control, which in turn talks to your external key manager. KMS just acts as a passthrough — enforcing IAM and key policies, then sending requests to your system.

**Why this matters:**

- You can meet stringent compliance rules that prohibit AWS (even logically) from touching or storing the keys.
- You get the AWS KMS user experience — IAM integration, CloudTrail, SSE-KMS, etc. — but the crypto happens 100% outside AWS.
- This is the BYOK (Bring Your Own Key) model, elevated to HYOK (Host Your Own Key).

---

## Cybersecurity Analogy

Imagine you let AWS KMS act like a bouncer at a vault door, verifying who can enter.  
But the vault itself is in your building, not theirs.  

So when someone wants to encrypt something:
- The bouncer checks their badge (IAM + KMS policy)
- Then calls your building’s security team
- Your team walks into your vault, locks/unlocks the container, and returns the result to the requester

AWS handles authorization, but **you handle the actual encryption/decryption**.

## Real-World Analogy

Think of AWS KMS like a concierge desk in a hotel.  
Normally, you give them the room key, and they handle it.  

But in XKS, you say:  
**“Nope. You’re just allowed to verify IDs. If someone needs the key, you send a request to my assistant back home, and they decide whether to unlock the door.”**  
It’s trustless key custody with full workflow integration.

---

## How It Works

Let’s walk through the components and architecture.

### 1. External Key Manager (EKM)

You must have a key manager you already operate:
- On-prem HSM (e.g., Thales, Entrust)
- Sovereign or hybrid cloud KMS

- Vendor-managed keys

This manager stores the key material and performs all cryptographic ops.

### 2. XKS Proxy

- You deploy and operate an XKS proxy that sits between AWS and your key system.
- It receives REST API calls from AWS KMS, then translates them to your EKM's native format.
- It must be highly available, low latency, and secure.

### 3. KMS External Key Store Setup

- You register the proxy in your AWS account and associate it with an external key store in KMS.
- You create KMS CMK stubs that refer to keys in your external system — but store no material.

### 4. Runtime Flow (Encrypt/Decrypt/etc.)

Here's how an **Encrypt** call works:

1. A user (or AWS service like S3) calls Encrypt using your XKS CMK  
2. AWS KMS:
   - Verifies IAM
   - Checks grants / key policy
   - Logs to CloudTrail
3. KMS sends a signed HTTPS request to your XKS proxy  
4. XKS proxy:
   - Authenticates the request
   - Talks to your EKM
   - Performs encryption
   - Returns ciphertext back to KMS
5. KMS relays ciphertext to the requester  

> At no point does AWS possess, cache, or see the key.

---

## Pricing Model

XKS pricing is the same as standard KMS in terms of API calls.

| Resource               | Billing Scope             |
|------------------------|---------------------------|
| XKS CMK usage          | Per KMS API call          |
| Proxy infrastructure   | You operate + pay for     |
| External key manager   | You license + manage      |

There is **no extra charge** for defining an XKS in KMS — but you carry all the infrastructure costs and complexity.

---

## Use Cases

XKS is not for everyone — it’s designed for:

- Highly regulated industries: banking, defense, law enforcement  
- Sovereign key control mandates: GDPR, Schrems II, European Data Residency  
- Internal governance that forbids KMS or CloudHSM usage  
- Multi-cloud or hybrid systems that centralize key custody in one vault

You might already use an on-prem HSM and want AWS services to encrypt data using it — without moving the key.

**Example Scenarios:**

- A German bank must comply with BSI and BaFin requirements that prohibit key storage outside national boundaries  
- A U.S. federal agency requires FIPS 140-2 Level 3 hardware with key custody off-cloud  
- A healthcare org wants central key lifecycle control for workloads across AWS, Azure, and GCP

---

## Comparison Table


| Feature                | AWS KMS (default) | Custom Key Store (CKS) | External Key Store (XKS) |
|------------------------|-------------------|-------------------------|---------------------------|
| **Key location**       | AWS-managed HSM   | Your CloudHSM (in AWS)  | On-prem / external infra  |

| **Key material in AWS?** | ✔️ Yes           | ✔️ In AWS VPC           | ✖️ Never                  |
| **Control plane**      | KMS               | KMS                     | KMS                       |
| **Data plane (crypto)**| KMS HSM           | CloudHSM                | Your system via proxy     |

| **Rotation**           | ✔️ AWS-managed    | ✖️ You manage           | ✖️ You manage             |
| **IAM integration**    | ✔️ Yes            | ✔️ Yes                  | ✔️ Yes                    |

| **CloudTrail logs**    | ✔️ Yes            | ✔️ Yes                  | ✔️ Yes                    |
| **AWS integrations**   | ✔️ Full           | ✔️ Full                 | ✔️ Some limitations       |
| **Setup complexity**   | Low               | Medium                  | High                      |
| **Compliance fit**     | General workloads | FIPS 140-2 / Custody    | Sovereign + External      |

---

## Real-Life Example: Winterday Bank

**Winterday Bank** operates a central Thales Luna HSM cluster in its EU datacenter.  
It already handles key custody for Azure, GCP, and internal services.

To bring AWS into the mix:

- They deploy an XKS proxy that connects to the HSM  
- Configure an External Key Store in AWS KMS  
- Define CMKs in KMS that reference keys in the HSM  
- When storing encrypted data in S3, AWS routes encrypt/decrypt requests through the proxy  

**Result:**  
All of AWS’s services now obey Winterday’s key custody rules — without violating data sovereignty or zero trust encryption models.

---

## Final Thoughts

KMS XKS is **not just another key store** — it’s a statement of **absolute control**.

If you:

- Cannot allow your keys to enter AWS  
- Already operate an enterprise key manager  
- Need full transparency and control for compliance  
- Want to integrate AWS-native features without compromising custody  

**Then XKS is the ultimate tool.**

But it comes at a cost: **you manage everything** — uptime, security, scaling, latency.  

It’s not for casual use.

