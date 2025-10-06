# Service-Linked Roles (SLRs)

## What Is a Service-Linked Role

A **Service-Linked Role (SLR)** is a special kind of IAM role that is **created and managed automatically by AWS services** — not by you.

It allows AWS services to perform actions on your behalf within your account. But instead of telling customers to manually create IAM roles (which leads to misconfigurations), AWS **predefines the trust policy, permissions, and naming**.

In short:

- The AWS service **creates the role for itself**
- It **assumes the role automatically**
- It uses that role to **interact with other AWS resources in your account**
- You can **see the role, view the policy, and audit it**, but **you can't modify the trust policy**

**Why this matters:**
If you don’t understand SLRs, you risk:

- Deleting or modifying roles that break production services
- Failing to audit IAM correctly (thinking _“who created this?”_)
- Missing delegated permissions during incident response

---

## Cybersecurity Analogy

Imagine your data center has an outsourced HVAC system.
You gave the HVAC company their own secure keycard, but instead of letting them go anywhere, you install a **contractor-only elevator**.

That elevator is a **Service-Linked Role**:

- It's locked to just that vendor
- You know when it’s used
- You can’t rewire it or give it to someone else
- But if you remove it, the whole system stops working

## Real-World Analogy

Picture **Winterday** deploying **Elastic Load Balancing (ELB)**.

When he enables **access logging**, ELB needs permission to write logs to S3. But instead of telling him to create an IAM role and paste in a policy, AWS automatically spins up:

```bash
aws iam create-service-linked-role \
  --aws-service-name elasticloadbalancing.amazonaws.com
```

Each AWS service that supports SLRs has a **specific service name** and a **fixed trust policy**.

---

## 1. Trust Relationship

You **can’t edit this**. It’s locked to a specific service. Example:

```json
{
  "Effect": "Allow",
  "Principal": {
    "Service": "elasticloadbalancing.amazonaws.com"
  },
  "Action": "sts:AssumeRole"
}
```

This prevents lateral movement or abuse — **only ELB can assume this role**.

## 2. Permissions Policy

This is where the actual actions are defined. For example:

- `s3:PutObject` into a logging bucket
- `acm:RenewCertificate` for managed certs
- `cloudwatch:PutMetricData` for telemetry

You can **see and audit this policy** — and this is where you control the scope of what AWS services can do.

---

## Visibility and Lifecycle

- SLRs are **tagged** with `aws:servicename`
- You can use the **IAM Console**, **CLI**, or **Access Analyzer** to list them
- They are **named predictably**, for example:
  - `AWSServiceRoleForElasticLoadBalancing`
  - `AWSServiceRoleForAutoScaling`
  - `AWSServiceRoleForEC2Spot`

**To delete:**

```bash
aws iam delete-service-linked-role --role-name AWSServiceRoleForElasticLoadBalancing
```

> **But be warned** — the service may break if you do this.

---

## Use Cases and Detection Implications

| **Use Case**                   | **Service Using SLR**                   | **Permissions Used**                                      |
|--------------------------------|-----------------------------------------|------------------------------------------------------------|
| ELB Access Logging             | `elasticloadbalancing.amazonaws.com`    | `s3:PutObject` to log bucket                               |
| Auto Scaling lifecycle hooks   | `autoscaling.amazonaws.com`             | `sns:Publish`, `sqs:SendMessage`, etc.                     |
| CloudWatch Agent on EC2        | `ec2.amazonaws.com` via SSM-managed     | `cloudwatch:PutMetricData`, `logs:PutLogEvents`           |
| ACM Certificate Renewal        | `acm.amazonaws.com`                     | `acm:RenewCertificate`, `iam:GetServerCertificate`         |
| ECS Task Telemetry (ECS Exec) | `ecs.amazonaws.com`                     | `ssm:StartSession`, `logs:CreateLogStream`, etc.          |

These roles often have **cloud-impacting powers**, so during incident response, knowing how they work can help answer:

- “Was this role abused?”
- “Did this role access S3 unexpectedly?”
- “Which service owns this permission chain?”

---

## SLRs vs Regular IAM Roles

| **Feature**             | **Service-Linked Role**      | **Regular IAM Role**               |
|-------------------------|------------------------------|-------------------------------------|
| **Created by**          | AWS service                  | You                                 |
| **Trust Policy**        | Fixed, service-specific      | Fully customizable                  |
| **Use Case**            | AWS service automation       | General-purpose delegation          |
| **Name Prefix**         | `AWSServiceRoleFor*`         | Anything you define                 |
| **Lifecycle Tied To**   | The AWS service              | Manual                              |
| **Modifiable?**         | Only permission policy       | Yes (both trust + permission)       |

---

## Real-Life Snowy Scenario

You're investigating why **ALB access logs** suddenly stopped showing up in S3.

You trace the service path:

- ALB → S3 → no logs
- IAM logs show the role `AWSServiceRoleForElasticLoadBalancing` no longer exists.
- Someone from the infra team deleted it thinking it was unused.

You use:

```bash
aws iam create-service-linked-role \
  --aws-service-name elasticloadbalancing.amazonaws.com
```

...to restore it.

Now logging resumes.
**Lesson learned:** SLRs aren’t optional metadata — they’re critical control paths.

---

## Final Thoughts

**Service-Linked Roles are invisible glue.**
They connect AWS services to each other **safely** by wrapping the **trust boundary around a fixed principal**.

You **can't customize** how the service authenticates — and that’s the point. It **prevents abuse**.

But just because you didn’t create them doesn’t mean you shouldn’t monitor them.

For CloudSec, that means:

- Monitor **creation and deletion** via **CloudTrail**
- Review **permissions attached** to SLRs **periodically**
- Use **Access Analyzer** to see what resources these roles touch
- Don’t **manually modify or delete** unless you know the impact

> SLRs are part of your **IAM surface area** — treat them like **semi-autonomous agents with scoped power**.
