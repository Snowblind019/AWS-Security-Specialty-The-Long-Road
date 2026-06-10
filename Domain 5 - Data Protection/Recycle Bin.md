# Recycle Bin in AWS (S3 Versioning + Object Lock + MFA Delete)

## What Is the "Recycle Bin" in AWS?

There is no official AWS service called **“Recycle Bin”** — but the concept exists through a combination of:

- **S3 Versioning**
- **S3 Object Lock**
- **MFA Delete**

Think of it as *soft deletion* + *protection against permanent removal*, similar to how your OS Recycle Bin lets you recover deleted files until they’re truly purged.

AWS doesn’t have a single “Recycle Bin” service — instead, you build this functionality using the features below.

---

## Key Components of a Secure Recycle Bin Strategy

| Feature         | Description                                                                       | What It Enables                                  |
|-----------------|-----------------------------------------------------------------------------------|--------------------------------------------------|
| **S3 Versioning** | Stores all versions of an object, including deletes (which become delete markers) | Lets you undelete or restore previous versions   |
| **S3 Object Lock** | Prevents object deletion for a fixed time (compliance or governance mode)        | Ransomware defense, legal hold                   |
| **MFA Delete**   | Requires MFA to permanently delete versions                                       | Extra layer to prevent unauthorized purging      |
| **Lifecycle Rules** | Automatically expire or archive old versions                                    | Retention cleanup                                |

---

## How the Flow Works (Snowy’s Example)

Let’s say **Snowy** has versioning enabled on the `snowy-documents` bucket.

- A file is accidentally deleted → **S3 adds a delete marker**, but the previous versions still exist  
**If Object Lock** was enabled with governance mode, even a rogue internal user couldn’t delete the object early unless they had special permissions.  
**If MFA Delete** is on, then only users with the MFA device can permanently delete an object version.

---

## Security & Compliance Use Cases

| Use Case                  | How It Helps                                                                 |
|---------------------------|------------------------------------------------------------------------------|

| **Ransomware Resilience** | Attackers may try to encrypt or delete your S3 data. Object Lock + Versioning protects the originals. |

| **Accidental Deletes**    | Recycle Bin behavior: just restore previous version                         |
| **Legal Hold / WORM**     | Object Lock (compliance mode) prevents tampering for a set retention time   |
| **MFA-Protected Deletes** | Forces human validation before destructive action                           |

| **Governance Policies**   | Define how long to retain versions before deletion or archival              |

---

## Real-World Analogy

Think of S3 like a **Google Docs history panel**.

- You can see past versions  
- Revert to old states  
- Even block edits entirely during legal review  

But *only if* you turned on:
- `Version History`  
- `File Lock`

If not configured, it’s just like `Shift+Delete` — **permanent loss**.

---

## Gotchas & Caveats

| Concern                         | Explanation                                                                 |
|----------------------------------|------------------------------------------------------------------------------|
| **Versioning increases cost**   | You’re storing every version of every object. Use lifecycle policies to clean up old versions. |
| **MFA Delete is CLI/API only**  | Can’t turn it on in the Console. Very hard to disable — for good reason.    |
| **Object Lock must be pre-set** | Must be enabled when the bucket is created. You *can’t enable it retroactively*. |
| **Requires careful permissions**| Ensure IAM roles/policies don’t allow bypass or privilege escalation        |

---

## Review

- **S3 Delete ≠ Destruction** if versioning is on  
- **Delete marker ≠ real delete** — you can still recover  
- **MFA Delete** and **Object Lock** are separate mechanisms  
- **Object Lock (compliance mode)** is immutable — even for root users  
- **Lifecycle policies** don’t override Object Lock retention windows  
- Use Object Lock for **WORM compliance / ransomware prevention**

---

## Final Thoughts

If you're in **security**, **governance**, or **compliance** — build a Recycle Bin strategy using:

- **S3 Versioning**: for undeletion  
- **Object Lock**: for retention and immutability  
- **MFA Delete**: for strong authorization  

**Combined**, they give you:
- A “time machine”  
- Legal defense  
- Ransomware shield  

All in native AWS — no third-party tooling required.

