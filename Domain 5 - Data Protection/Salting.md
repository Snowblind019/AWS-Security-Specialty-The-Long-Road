# Salting — Deep Dive

## What Is Salting

Salting is the process of adding random, unique data to a password before hashing it.
This guarantees that even if two users choose the same password, their stored hashes will be completely different.

In simpler terms:

**Without salt:**
`hash = SHA256(password)`
Snowy and Winterday both use “Snowstorm123” → identical hashes.

**With salt:**
`hash = SHA256(salt + password)`
Each user’s salt is different → unique hashes.

The **salt itself is stored alongside the hash** (not secret), but its uniqueness destroys precomputed attacks like rainbow tables.
Salting doesn’t stop brute force outright — but it forces attackers to brute force each password **individually**.

> Without salting, you’re essentially handing attackers a master key.

---

## Cybersecurity Analogy

Salting is like fitting every door in your building with a **custom lock** even if people have identical keys.
If an attacker makes a copy of one key, they can’t open the rest of the doors because every lock is subtly different.

No mass compromise from one success.

## Real-World Analogy

Imagine you run a vault facility. Customers bring their own passcodes.
If you store those codes “as is,” one cracked code means dozens of vaults are at risk.

Instead, you prepend a random phrase to each code — like `Icicle-4832` or `Frost-9375` — and only your vault system knows the phrase for that vault.
Even if two customers start with the same code, the full stored secret is different.

---

## Common Risks Without Salting

| Scenario                         | Risk Introduced                                  |
|----------------------------------|---------------------------------------------------|
| Multiple users share same password | One cracked hash = compromise across accounts     |
| Leaked hash database              | Rainbow tables instantly crack weak hashes       |
| Same hash reused across apps      | Credential stuffing + breach chaining            |
| Weak hash algorithms + no salt    | Forever exploitable                              |

---

## How Salting Works Step by Step

1. Generate a secure random salt per password (128 bits or more).
2. Combine `salt + password` (order defined by your hashing library).
3. Hash the combination using a strong password hashing algorithm
   (e.g., `bcrypt`, `scrypt`, `Argon2` — **not** raw `SHA256`).
4. Store both the salt and the resulting hash.
5. Verify by recomputing `hash(salt + enteredPassword)` at login.

✔️ Each password is now effectively in its own hash space.
✖️ Precomputed rainbow tables no longer work.
✔️ Attackers must brute force each password individually.

---

## Why Salting Matters for Security

| Drift Scenario         | Risk Introduced                                |
|------------------------|-------------------------------------------------|
| Weak password reused   | Mass compromise                                 |
| Rainbow table attack   | Instant crack of all weak hashes                |
| Hash database stolen   | Breach correlation across systems               |
| Credential stuffing    | Attackers pivot to other services               |

---

## Best Practices for Salting

✔️ Always generate a **unique salt** per password (never reuse or hardcode).
✔️ Use a **cryptographically secure random generator**.
✔️ Combine salting with a **slow password hashing algorithm** like `Argon2`, `bcrypt`, or `scrypt` — `SHA256` alone is too fast.
✔️ Store the **salt and hash together** (salt is not secret).
✔️ Consider adding a **pepper** (an application-wide secret) stored in a secure location (like **AWS Secrets Manager**) for extra protection.

---

## Real-Life Example (Snowy’s Salted Login System)

Snowy designs a user authentication service for a new SaaS app.
He knows compliance and breach resilience matter, so he implements:

- `Argon2id` with 16-byte unique salt per user
- Pepper stored in **AWS Secrets Manager**
- Password hashes + salts stored in **DynamoDB**
- Verification function recomputes `Argon2id(salt + password + pepper)` at login

**Months later**, an attacker breaches the database and steals hashes + salts.

They try rainbow tables — **useless**.
They try brute force — each hash must be cracked **individually**, at `Argon2id` speeds.

Snowy sleeps at night knowing even weak user passwords aren’t instantly compromised.

✔️ Breach damage minimized
✔️ Rainbow tables neutralized
✔️ Audit-ready password storage

---

## Final Thoughts

**Salting is your first line of defense in password storage.**
Without it, you’re effectively publishing an attacker’s cheat sheet.
With it, you force attackers into high-cost, one-by-one brute forcing — buying you time, compliance, and protection at minimal cost.

In AWS or any cloud app:

✔️ Use **unique salts** and **strong hashing libraries** (`bcrypt` / `Argon2`).
✔️ Store **salts with hashes** and consider an app-wide **pepper**.
✔️ Pair with services like **AWS Secrets Manager** and **CloudWatch alarms** for detection of anomalous login activity.

> Salting doesn’t make weak passwords strong,
> but it makes weak storage defensible.
> It’s cheap, easy, and absolutely non-negotiable in modern security engineering.
