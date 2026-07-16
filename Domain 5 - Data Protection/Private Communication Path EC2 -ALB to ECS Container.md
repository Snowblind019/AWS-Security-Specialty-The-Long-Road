# Private Communication Path: EC2 / ALB → ECS Container

## What Is This Flow

In this pattern, an EC2-hosted **Application Load Balancer (ALB)** receives incoming traffic and forwards it to an **ECS container**, often part of an internal microservice architecture.

This flow is everywhere: public websites, private APIs, internal dashboards, or backend services talking across a mesh of load balancers.

But here’s the catch: **encryption between ALB and ECS is optional** — it depends entirely on your listener config and target group protocol.

- If your ALB uses an **HTTPS listener**, it can:
  - Terminate TLS (decrypt at the ALB level)
  - Or pass through TLS all the way to the container (via TCP mode)
- If your ALB uses **HTTP**, the downstream ECS connection is **not encrypted**, even if the ECS service is private.

> **Encryption-in-transit here is not guaranteed. It must be explicitly configured.**

---

## Cybersecurity Analogy

Think of ALB as a **receptionist** at a secure office.

If the client shows up and asks to speak in code (TLS), the receptionist can either:

- Decode the message and forward the plain version to an employee (TLS termination), or  
- Leave it encrypted and pass the sealed envelope directly to the employee (TLS passthrough)

Now imagine some offices say:

> “We don’t do secure messages here. Just talk freely in the lobby.”

That’s what happens if you use **HTTP listeners** and **HTTP target groups** — your private messages are being whispered across an open room.

## Real-World Analogy

Let’s say you run a coffee shop. Customers place orders at a **kiosk (ALB)**, and those orders are routed to the **barista (ECS container)**.

- If the kiosk accepts secure online payments, it **decrypts** the payment, logs it, then sends a **plaintext** work order to the barista.
- Alternatively, in a more secure setup, the kiosk **doesn’t decrypt anything** — it just hands off the **encrypted payload** to the barista, who has their own decryption keys.

Same with **ALB → ECS**.  
If you don’t **explicitly secure both ends**, traffic can float around in plaintext.

---

## How It Works

| Component        | Behavior                                                                 |
|------------------|---------------------------------------------------------------------------|
| **ALB Listener** | HTTPS listener uses TLS termination unless configured for passthrough     |
| **Target Group** | Can use HTTP or HTTPS to send traffic to ECS containers                   |
| **ECS Container**| Must expose ports and listen on expected protocol                         |
| **TLS Passthrough** | Possible using ALB + NLB combo or special config (rare)                |

> By default, HTTPS listeners **terminate TLS** at the ALB — meaning the ALB decrypts traffic and forwards plain HTTP to ECS.

This is **okay for public endpoints**, but not ideal for internal services that require strict end-to-end (E2E) encryption.

To go full **E2E TLS**, you need:

- HTTPS listener on ALB  
- TLS listener in the ECS container  
- Target group protocol = HTTPS  

But **this is not enforced by AWS** — **you** must configure it.

---

## Encrypted In Transit: Conditional

**Encrypted if**:

- ALB uses an **HTTPS listener**, **and**
- Target group is set to **HTTPS** or uses **passthrough**

**Not encrypted if**:

## Security Config Options

| Option                         | Effect                                                    |
|--------------------------------|------------------------------------------------------------|
| HTTP Listener → HTTP Targets   | ✖️ No encryption at all                                   |
| HTTPS Listener → HTTP Targets  | TLS terminates at ALB (internal traffic = plaintext)      |

| HTTPS Listener → HTTPS Targets | TLS from client to ALB, then again from ALB to ECS        |
| TLS Passthrough (rare)         | Possible with NLB → ALB chaining or TCP mode (strict E2E) |

> In many orgs, the default is HTTPS at the edge and **HTTP inside** — which **works**, but **isn't truly encrypted throughout**.

---


## Security Considerations

| Risk                        | Mitigation                                                  |
|-----------------------------|--------------------------------------------------------------|

| Plaintext to ECS            | Use HTTPS target groups or implement TLS at the app level    |
| Implicit Trust in ALB       | If ALB is compromised, downstream traffic is exposed         |
| Misconfig of TLS passthrough| Validate certs in containers, use mutual TLS if needed       |
| Lack of Auditing            | Enable ELB access logs + VPC Flow Logs for observability     |

---

## Final Thoughts

This flow — **ALB to ECS container** — is deceptively simple, but **dangerously easy to misconfigure**.

AWS gives you all the tools for TLS enforcement, but it’s **opt-in**.  
**You** decide whether encryption continues beyond the load balancer or stops there.

If you're building **internal microservices** or anything sensitive (auth APIs, admin panels, backend workers), make it a rule:

> **“If the outside is encrypted, the inside should be too.”**

TLS from **ALB → ECS** isn’t overkill — it’s **minimum viable trust**.

