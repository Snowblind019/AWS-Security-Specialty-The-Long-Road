# API Gateway Security

## What Is API Gateway Security

Amazon API Gateway is a fully managed AWS service that allows developers to create, publish, secure, and monitor APIs. It acts as the **front door to backend services** — such as Lambda functions, ECS tasks, EC2, or any external web apps.

The security challenge: API Gateways are **public by default**, exposed to the internet unless you configure them otherwise. That makes them **high-value targets** for attackers who:

- Probe for unauthenticated endpoints  
- Launch DDoS attacks  
- Inject malicious payloads (XSS, SQLi, event injection)  
- Attempt authorization bypasses  
- Abuse overly permissive CORS settings  

Whether your API is REST, HTTP, or WebSocket-based, **misconfiguring access policies** or leaving things open to the world can lead to full compromise of backend systems.

---

## Cybersecurity Analogy

Think of API Gateway as the **reception desk at a corporate building**. It controls who gets to enter, where they go, and what they can say.

If the receptionist:

- Doesn’t check ID (no authentication)  
- Allows anyone into the executive floor (no authorization)  
- Doesn’t scan for weapons (no input validation)  
- Leaves the front door open all night (no throttling)  

— then bad actors walk right in.

## Real-World Analogy

Imagine you're running a **customer support call center**. Everyone has to call a main number (API Gateway), and based on what they say, they're routed to different departments (Lambda, EC2, RDS, etc.).
Then your phone lines will get flooded, private info may leak, and internal systems can be abused.  
**API Gateways are the same:** entry control points for your cloud — and without strict rules, they become your weakest link.


---

## How It Works / What to Secure

### 1. Authentication and Authorization  
**Control Who Can Access**


API Gateway supports several authentication methods:

- **IAM-based Auth**  
  Clients sign requests with AWS SigV4 (great for internal APIs)

- **Cognito User Pools**  
  JWT-based auth for web/mobile clients (federated identity, social login)


- **Lambda Authorizers (Custom Auth)**  
  You provide a function that evaluates headers, tokens, etc.

- **API Keys**  
  Not recommended for auth alone — better for usage tracking


**Best Practices:**

- Use **JWT or SigV4** for strong, verifiable auth  
- Avoid using API Keys as the only layer of security  
- Apply **per-method authorization** to restrict sensitive operations (e.g., POST vs GET)  
- Combine with IAM conditions or resource policies (e.g., allow access only from specific VPCs)

### 2. Resource Policies (Per-API)  
**Control Where Calls Can Come From**

You can attach a **resource policy** to your API Gateway, much like an S3 bucket policy.

**Example use cases:**

- Allow only a specific VPC endpoint to call the API  
- Block traffic from certain CIDR ranges  
- Allow only IAM principals from specific AWS accounts  

This adds **network-level access control**, beyond identity.

### 3. Input Validation and Schema Enforcement  
**Protect the Backend**

Define request models and enforce **strict JSON schemas**:

- Validate required fields  
- Enforce length, format, patterns  
- Reject malformed or unexpected payloads before they reach Lambda/EC2  

This blocks:

- Injection attacks  
- Broken deserialization  
- Event injection vulnerabilities  

You can use **mapping templates (Velocity Template Language)** to transform/validate data at the gateway.

### 4. Throttling, Rate Limiting, and Usage Plans  
**Prevent Abuse and DDoS**

Use API Gateway’s built-in throttling controls:

- Default per-method limits (e.g., 1000 RPS, burst of 2000)  
- Custom usage plans tied to API keys  

- Enforce quotas per client  

This stops:


- Credential stuffing  

- Exhaustion attacks  

- Infinite-loop triggers from untrusted clients  


For DDoS:

- Use **AWS Shield Standard** (enabled by default)  
- For high-risk APIs, subscribe to **Shield Advanced**

### 5. HTTPS Enforcement and TLS 1.2+  
**Secure Data in Transit**

- All API Gateway endpoints use **HTTPS by default**  
- TLS 1.2 is the **minimum version allowed** (TLS 1.0/1.1 deprecated)  
- For **private APIs**, use VPC Endpoint connections (PrivateLink) with encryption

Also:

- Don’t allow downgrade attacks by using weak ciphers  
- Always test your endpoint using tools like **SSL Labs**

### 6. CORS Configuration (Cross-Origin Resource Sharing)  
**Don’t Expose APIs to Untrusted Frontends**

APIs often serve web clients that live on different domains. **CORS headers** control who can talk to the API.

**Too permissive CORS settings:**

```http
Access-Control-Allow-Origin: *
```
This means any website can make requests — including malicious ones.

**Best practices:**

- Only allow trusted domains  
- Limit `Access-Control-Allow-Methods`  
- Don’t expose credentials unless needed

### 7. Logging and Monitoring  
**Detect Misuse and Investigate Incidents**

- Enable **Access Logging** in API Gateway (send to CloudWatch Logs)  
- Enable **Execution Logging** (logs full lifecycle of requests)  
- Trace requests using **AWS X-Ray**  
- Monitor with **CloudWatch Metrics** (4xx, 5xx errors, latency, etc.)  
- Correlate with **CloudTrail** to see who deployed or updated APIs  
- Integrate findings into **Security Hub** or your **SIEM** for visibility

### 8. Private APIs + VPC Links (Optional)

For internal APIs, you can make them completely **private**:

- Use **Private API Gateway** (accessible only through VPC endpoints)  
- Or set up **VPC Link** to proxy traffic to services inside your VPC (like ALB)  

This removes **internet exposure entirely**.

---

## Pricing Models

| Component          | Pricing                                         |
|--------------------|--------------------------------------------------|
| REST API (Legacy)  | $3.50/million requests                          |
| HTTP API (Modern)  | $1.00/million requests (lower cost, less features) |
| WebSocket API      | Charged per message                             |
| Data Transfer      | Charged per GB                                  |
| Caching            | Pay per GB-hour (if enabled)                    |
| Access Logs        | CloudWatch log ingestion + storage fees         |
| WAF Rules          | Charged separately per request inspected        |

---

## Real-Life Snowy-Style Example

**Blizzard is building an API-driven financial service.**  
Customers can check their balance, transfer funds, and view transaction history — all via **API Gateway + Lambda + DynamoDB**.

### Mistake Scenario:

- No auth required on `/check-balance`  
- API key reused across all clients  
- No rate limiting  
- Access logs disabled  

**An attacker:**

- Mass-scrapes account data  
- Floods the Lambda with junk calls (costing $$$)  
- Steals sensitive data  

---

### Snowy Fixes This By:

- Enabling **JWT auth via Cognito**  
- Attaching **IAM conditions + per-method auth**  
- Enabling **throttling + WAF rules**  
- Validating input with **strict JSON schemas**  
- Logging every request to **CloudWatch + X-Ray**

Now the gateway is **locked down tight**, and abuse is **visible and actionable**.

---

## Final Thoughts

**API Gateway is one of the most exposed entry points in AWS.**

It’s critical you treat it like a:

- Firewall  
- Load balancer  
- Traffic cop  

Because it **is**.

Your job is to:

- Authenticate and authorize every call  
- Validate every input  
- Monitor every request  
- Rate-limit every client  

When **properly hardened**, API Gateway becomes a powerful, secure abstraction layer.  
When **neglected**, it becomes your biggest blind spot.

