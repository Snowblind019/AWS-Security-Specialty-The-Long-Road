# VPC Endpoints

## What Is a VPC Endpoint

A **VPC Endpoint** is a secure, private connection between your **VPC** and **AWS services** — without needing to go over the public internet.

By default, when you access AWS services like S3, DynamoDB, or Secrets Manager from inside your **VPC**, the request is **routed through the internet gateway** (even if you’re using AWS **DNS**). That means:

- Traffic leaves your **VPC** and re-enters AWS
- Public **IPs**, **NAT** gateways, and **route tables** get involved
- You’re exposed to the same threats as any internet traffic

A **VPC Endpoint** fixes that.

It creates a **private path** between your **VPC** and the AWS service using the AWS internal network backbone — **no NAT, no public IPs, no internet.**

---

## Cybersecurity and Real-World Analogy

### Cybersecurity Analogy

Imagine you’re a security engineer inside a data center (your **VPC**), and you want to access your file vault (S3) that’s in another part of the secure AWS facility.

You could go out the front door (**internet gateway**), walk around the building (**public internet**), go through 10 cameras, badge in again (**IAM**), and then reach the vault.

Or…

You could use an **internal hallway** with a security-only tunnel between your room and the vault. That’s a **VPC Endpoint** — a **private, internal tunnel** where no outsiders even know you passed through.

### Real-World Analogy

Using a **VPC Endpoint** is like using the **employee-only hallway** in a hospital instead of going outside and re-entering through the **ER** every time you need something from a different floor.

---

## Types of VPC Endpoints

There are **two main types**, plus a third variant:

| **Type**                         | **Use Case**                        | **Service Examples**                        |
|----------------------------------|-------------------------------------|---------------------------------------------|
| **Interface Endpoint**           | Connect to most AWS services        | **SSM**, Secrets Manager, **STS**, **CloudWatch**, etc. |
| **Gateway Endpoint**             | Only for S3 and DynamoDB            | **S3**, **DynamoDB**                         |
| **Gateway Load Balancer Endpoint (GLB)** | Pass traffic through a 3rd-party appliance | Firewalls, inspection, partner services     |

Let’s break them down.

---

### 1. Interface Endpoint

- Elastic Network Interface (**ENI**) in your **subnet**
- Points to a **service endpoint** (like `ssm.us-west-2.amazonaws.com`)
- Private IP address
- You can connect to it via **DNS** (e.g., `ssm.us-west-2.amazonaws.com` will resolve to the **ENI** inside your **subnet**)

Use this for services like:

- Systems Manager (**SSM**)
- Secrets Manager
- **CloudWatch**
- **STS / KMS**
- **ECR / ECS / Inspector / Athena**

**Security benefit:**
You can restrict access using **Security Groups**, **Route Tables**, and **Endpoint Policies**.

### 2. Gateway Endpoint

- Doesn’t use an **ENI**
- Configured in your **route table**
- Only available for **S3** and **DynamoDB**
- Automatically routes traffic through AWS’s backbone without ever touching the internet

Use this for:

- **S3 access** without NAT
- **DynamoDB lookups** in private **subnets**

**Security benefit:**
You can use **Bucket Policies** to restrict access **only from specific VPC Endpoints** (via `aws:SourceVpce` condition key).

### 3. Gateway Load Balancer Endpoint (GLB)

- For routing traffic to **3rd-party inspection appliances** (like firewalls, packet sniffers)
- Tied to a **Gateway Load Balancer**
- Think: deep packet inspection, firewall-as-a-service

---

## Why It Matters for Security & Compliance

| **Feature**                   | **Benefit**                                                        |
|-------------------------------|---------------------------------------------------------------------|
| **No internet exposure**      | Keeps sensitive data and services on the AWS backbone              |
| **No need for NAT gateway**   | Cost savings + tighter control                                     |
| **IAM + Resource Policies**   | Restrict access only **through VPC Endpoints**                     |
| **Interface Endpoint logs**   | Enable **Flow Logs** to monitor usage                              |
| **Centralized architecture**  | Combine with **PrivateLink**, **Transit Gateway**, **VPC Peering** |

---

## Key IAM/Resource Policy Integration

You can **require traffic to use a VPC Endpoint** by writing IAM or resource policies like:

```json
"Condition": {
  "StringEquals": {
    "aws:SourceVpce": "vpce-0abc123456789"
  }
}
```

This ensures that no one from outside the private network can talk to your bucket/service — even with valid credentials.

---

## Flow Example: Private EC2 → S3 Using Gateway Endpoint

1. EC2 instance in **private subnet** with no internet access
2. Tries to access S3 object
3. Route table has entry:
   `Destination: 0.0.0.0/0 → vpce-gateway-s3`

**A.** Traffic goes **directly to S3** over AWS’s internal network
**B.** IAM policy + bucket policy confirms access

✔️ No NAT
✔️ No internet
✔️ Fully private

---

## Flow Example: EC2 → Secrets Manager via Interface Endpoint

- A. EC2 hits `https://secretsmanager.us-west-2.amazonaws.com`
- B. **DNS** resolves to the **ENI** created by the Interface Endpoint
- C. **TLS** terminates privately
- D. Secrets retrieved securely with **IAM** check

---

## VPC Endpoint vs PrivateLink

**VPC Endpoint** uses **PrivateLink** under the hood.
**PrivateLink** is the **core tech** that allows private connectivity to AWS services and 3rd-party SaaS vendors.

| **Concept**     | **Description**                                                      |
|------------------|----------------------------------------------------------------------|
| **PrivateLink**   | The underlying tech for private service connectivity                |
| **VPC Endpoint**  | A “consumer-side” use of **PrivateLink** for AWS-managed services   |

---

## Real-Life Snowy-Style Example

Imagine you’re building a private compliance system in AWS:

- You store logs in **S3**
- Pull secrets from **Secrets Manager**
- Run jobs on **EC2**

All of it must be **air-gapped from the internet**, but still connect to AWS services.

You:

- Use **Gateway Endpoint** for **S3**
- Use **Interface Endpoint** for **Secrets Manager + SSM**
- Write resource policies with `aws:SourceVpce`
- Save $$$ by not needing a **NAT Gateway**

> Now your audit team is happy, your infra is safer, and your **costs go down**.

---

## Final Thoughts

**VPC Endpoints** are a **mandatory building block** of secure, private AWS environments.
If you ever say *“this workload should not touch the internet,”* then a **VPC Endpoint** is part of your answer.

You’ll see it all over real-world security architectures:

- Compliance zones (**HIPAA**, **CJIS**, **FedRAMP**)
- Financial transaction systems
- Zero trust networking (paired with **NACLs + SGs**)
- **S3 exfiltration prevention**
