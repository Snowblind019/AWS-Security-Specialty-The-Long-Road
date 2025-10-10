# AWS Lambda@Edge

## What Is Lambda@Edge

Lambda@Edge is an extension of AWS Lambda that allows you to run serverless functions at AWS edge locations, in response to CloudFront events — before the request ever hits your origin server.

It enables real-time, ultra-low-latency logic to be executed close to the user, such as:

- Request rewriting or redirection  
- Header or cookie manipulation  
- Device detection and A/B testing  
- Geo-targeting and localization  
- Security enforcement (token validation, bot detection)

All of this happens at the AWS edge, rather than inside your application servers, allowing you to offload critical logic, reduce latency, and improve scalability.

---

## Cybersecurity Analogy

Think of your application origin as a castle. Normally, every user request has to reach the castle gate before guards can decide whether to let someone in.

Lambda@Edge is like placing intelligent guards at the borders of your kingdom — long before someone even gets near the castle. These guards can:

- Turn away bad actors immediately  
- Redirect messengers based on location  
- Log everything without ever disturbing the inner walls

By evaluating traffic at the perimeter, Lambda@Edge helps you catch threats early, reduce the load on your main defenses, and add agility at the edge.

## Real-World Analogy

Suppose **Blizzard** is delivering updates to players worldwide via CloudFront. They want to:

- Show a different welcome banner for users in Japan  
- Block known bots from scraping patch notes  
- Rewrite URLs for legacy game clients  
- Redirect mobile users to a different domain  

Instead of adding this logic inside the game server or backend API, they attach Lambda@Edge functions to CloudFront.

Now, all this logic is enforced instantly — at the edge, before the request even travels to the origin.

This results in faster responses, lower origin load, and globally consistent behavior.

---

## How Lambda@Edge Works

### 1. Deployment Model

Lambda@Edge functions are deployed to AWS edge locations (via CloudFront) and are triggered automatically by CloudFront request/response events.

You start by writing a regular AWS Lambda function in **us-east-1 (N. Virginia)**, and then replicate it to edge locations by attaching it to a CloudFront distribution.

### 2. Event Triggers

Lambda@Edge can be triggered at four points in the CloudFront request lifecycle:

| **Event Type**    | **Description**                          | **Common Use Cases**                     |
|-------------------|------------------------------------------|-------------------------------------------|
| Viewer Request    | Before CloudFront checks cache           | Auth headers, geo redirects               |
| Origin Request    | After cache miss, before origin fetch    | URL rewrites, header injection            |
| Origin Response   | After origin sends response              | Modify headers, security headers          |
| Viewer Response   | Before content returned to client        | Add cookies, CSP, log injection           |

### 3. Language Support

Lambda@Edge supports **Node.js** and **Python** runtimes.

However:

- Execution time must be under **5 seconds**  
- Function size is limited (zipped package ≤ **1 MB**)  
- **No environment variables allowed**  
- Read-only `/tmp` storage available (**512 MB**)  

These constraints are designed to maintain fast, lightweight edge execution.

### 4. Propagation and Updates

When you associate a Lambda@Edge function with a CloudFront distribution:

- It is replicated to all **global edge locations**  
- Propagating changes can take **several minutes**  
- Rollbacks require redeploying a prior function version  

This is not ideal for high-churn development workflows — it's better suited for stable, production-grade logic that changes infrequently.

---

## Security and Privacy Use Cases

Lambda@Edge plays a crucial role in **security enforcement at the network perimeter**:

- Token or JWT validation before forwarding requests  
- Geo-fencing and blocking specific IP ranges  
- Bot detection using headers and user agent parsing  
- Stripping tracking cookies or sensitive headers  
- Adding security headers like `Content-Security-Policy`, `Strict-Transport-Security`, etc.

Because all this happens *before* traffic reaches your origin, you significantly reduce attack surface and prevent wasteful origin hits.

---

## Compliance and Data Residency

Since Lambda@Edge runs **globally**, it’s important to understand data residency implications:

- The payload of the request (including headers, cookies, and query strings) **may be processed outside your primary Region**  
- If your compliance model restricts data to specific geographies, Lambda@Edge **may violate that boundary**  
- For strict residency requirements, consider **Lambda@Edge + Regional Edge Caches**, or run validation **in-region** instead

Always evaluate where sensitive data is being touched when using edge compute.

---

## Cost Model

Lambda@Edge has its **own pricing**, separate from regular Lambda:

- Charged **per number of invocations**  
- Charged **per duration** of execution time  
- Also charged based on **data transferred** between CloudFront and origin  


While cost per request is small, heavy use cases with millions of hits can lead to noticeable charges — especially if you're doing complex viewer-request logic.

You should:

- Profile performance before enabling  

- Consider caching results aggressively  

- Optimize function logic for brevity and efficiency

---

## Snowy’s Example: Geo-Based Redirects

Let’s say **Snowy** runs a multi-language website with CloudFront.

**Goals:**

- Redirect users in Romania to `/ro/`  
- Add a cookie for language preference  
- Strip out `X-Test-Header` from external bots

**Implementation:**

- Write a **viewer-request Lambda@Edge** function in Python  
- Deploy it in **us-east-1** and attach it to CloudFront  
- Function detects location via `CloudFront-Viewer-Country` header  
- Sends `302 redirect` to `/ro/` if RO is detected  
- Adds a `Set-Cookie: lang=ro` header  
- Removes unwanted headers from request

**Results:**

- Romanian users get **instantly redirected from the edge**  
- **No load** hits Snowy’s origin  
- Logs are clean, consistent, and localized

---

## When to Use Lambda@Edge

**Use Lambda@Edge when:**

- You need to **modify or inspect requests at the edge**  
- You want to **enforce security controls globally**  
- You want to **redirect, rewrite, or localize** content before hitting your origin  
- You need **dynamic behavior** that CloudFront alone can’t do

**Avoid it when:**

- You need **heavy computation** or **long-running logic**  
- You need **instant updates** — edge replication takes time  
- Your use case is **data residency-sensitive**  
- You just need **simple cache control or static content** — use CloudFront behaviors instead

---

## Final Thoughts

Lambda@Edge is a powerful tool for pushing logic to the **outermost perimeter** of your infrastructure — closer to users, faster to execute, and offloading origin traffic entirely.

It lets you treat the edge not just as a CDN, but as a **programmable policy enforcement layer**, capable of delivering rich user experiences, securing traffic, and improving global performance.

In a modern **security-first architecture**, it’s often your **first line of defense** — inspecting, transforming, and deciding on requests before they touch anything sensitive.

Done right, Lambda@Edge adds **speed**, **security**, and **intelligence** to your CloudFront distributions — and unlocks a whole new class of use cases in the edge computing world.

