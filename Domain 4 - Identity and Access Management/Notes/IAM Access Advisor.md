# IAM Access Advisor  

## What Is the Service

IAM Access Advisor is a visibility tool in AWS that tells you:  
**"Which AWS services has this IAM identity actually used, and when was the last time?"**

It gives you data-driven insight into the permissions that were granted vs the ones that were actually used — across IAM users, roles, and even groups.  
This is not a simulator, not an analyzer, not a policy writer.  
It’s a *forensics view* of service usage — showing what services an identity has interacted with, and when.

### Why this matters:

Cloud environments tend to accumulate privilege bloat. Roles get created with `*` permissions or full service access "just in case." Over time, no one knows what can be removed safely.

**Access Advisor answers that** — giving you the evidence you need to:

- Remove unused access  
- Enforce least privilege  
- Reduce your attack surface

---

## Cybersecurity Analogy

Access Advisor is like installing a door access log system in your data center.

You already gave people keys (IAM policies), but now you get to see:

- Which doors they actually opened  
- Which doors they’ve never even touched  
- When they last used each one  

So when someone has access to 200 rooms but has only entered 3 of them all year?  
You know it’s cleanup time.

## Real-World Analogy

Imagine you're running a NOC team and Dallas has access to 50 different ticket queues, dashboards, and config tools. But over the last 6 months, Access Advisor shows he’s only used 3 of them. He could *hypothetically* use the others — but he never did.  

So why keep that access?  
This is especially dangerous in AWS — where unused permissions are still attack paths.

---

## How It Works

Access Advisor is built into the IAM console, and it works for:

- IAM Users  
- IAM Roles  
- IAM Groups  

For each entity, it displays:

- Service name (e.g., S3, EC2, KMS)  
- Service last accessed time  
- Whether the entity has permissions to that service  
- How that permission is granted (inline policy, managed policy, group, etc.)

> **Note**: It tracks **service-level access**, not fine-grained API actions.  
You’ll see “has access to S3”, but not whether they called `s3:GetObject` or `s3:DeleteBucket`.

---

### Example Table from Access Advisor (in Console)

| Service | Last Accessed         | Access Via                      |
|---------|------------------------|----------------------------------|
| S3      | 2025-09-01 14:12 UTC  | Customer-Managed Policy         |
| EC2     | Not Accessed          | AWS Managed Policy              |
| RDS     | 2025-08-15 09:03 UTC  | Group-Inherited Inline Policy   |

You can click into each to see how access is granted, and begin trimming anything unused.

---

## Use Cases in Security

### Least Privilege Enforcement
Track down unused services and remove access.

### Post-Incident Review
After a breach or suspicious activity, check what roles were actually used — vs what they *could* have done.

### IAM Role Hygiene
Review temporary roles, Lambda execution roles, or EC2 instance profiles to validate whether they need all that access.

### Contractor / Expiring Access Review
If Winterday leaves the team, you can look at his role and say:  
**“He never used DynamoDB or CloudFormation — cut those out before reassigning.”**

---

## Limitations

- **Service-Level Only**: You don’t get API-level granularity (use CloudTrail for that)  
- **Time-Delay**: Access logs may take up to 4 hours to show up  
- **90-Day Retention**: Data only tracks service access in the past 400,000 minutes (about 90 days)  
- **No SCP Visibility**: It doesn’t show what was blocked by SCPs — only what was allowed and used  
- **No Context of How Access Was Used**: It won’t show tags, conditions, or the calling service (e.g., STS session vs console)

---

## Workflow Example

Let’s say you’re auditing the `SnowyIncidentResponseRole`.

1. Open IAM → Roles → `SnowyIncidentResponseRole` → **Access Advisor** tab  
2. You see that it has access to:  
   - S3: Last used 3 days ago  
   - EC2: Never used  
   - KMS: Last used 60 days ago  
   - RDS: Never used  
3. You check the policies attached — and realize the role has full EC2 and RDS access for no reason  
4. You document the usage with screenshots and propose a revised least privilege policy scoped to:  
   - `s3:GetObject`, `kms:Decrypt`, and minimal STS usage  
Access Advisor doesn’t prevent problems — but it tells you **where the dead weight is**.  

It’s not about blocking attackers after they enter.  
It’s about removing the paths they *could have taken*, but didn’t — before they ever try.

If you’re building secure environments, this is your:

- Cleanup tool  
- Review assistant  
- IAM forensics lens  
- Least privilege enforcer  

It doesn’t go deep like CloudTrail, and it won’t explain *why* something was used — but it answers a simpler question that matters just as much:  
**"What access does this identity have that it doesn't even use?"**

