# AWS Security Specialty – The Long Road

![Status](https://img.shields.io/badge/Status-In%20Progress-yellow)
![Focus](https://img.shields.io/badge/Focus-AWS%20Cloud%20Security-blue)
![Goal](https://img.shields.io/badge/Certification-AWS%20SCS%20--%20Specialty-8A2BE2)
![SDK](https://img.shields.io/badge/SDK-boto3-orange)
![Learning](https://img.shields.io/badge/Learning-Terraform-623CE4)
![Learning](https://img.shields.io/badge/Learning-SQL-4479A1)

---

This repository documents my journey to pass the AWS Certified Security Specialty exam.

It's not the journey I thought it would be.

## Attempt #1: September 15th, 2025

I failed.

Not close. Just... failed.

I thought I was ready. I'd done Stephane Maarek's course, Adrian Cantrill's deep dives, hundreds of practice questions. I knew the services. I understood the concepts. Or at least I thought I did.

The exam proved otherwise.

But that failure taught me something: **I wasn't preparing to understand AWS security. I was preparing to pass a test.** And those aren't the same thing.

So I changed my approach. I started diagramming services. I rebuilt my understanding from first principles. I focused on *why* things work the way they do, not just *what* they do.

I convinced myself that this time, I'd actually learned the lesson.

## Attempt #2: November 4th, 2025

I failed again.

This one hurt more because I'd done everything "right." I'd studied differently. I'd gone deeper. I'd put in the work.

But here's what I missed: **understanding theory isn't the same as being able to implement it.**

I could explain how KMS works. I could diagram GuardDuty's architecture. But when the exam threw me scenarios involving Python automation, Terraform deployments, or SQL-based log analysis — tools I'd heard of but never actually used — I realized my knowledge was still one layer too shallow.

I knew *about* these things. I didn't know how to *do* them.

That's what's changing now.

## What Happens Next

The SCS-C03 exam launches in December. That gives me time — real time — to stop studying for an exam and start training for a career.

Here's the plan:

**Stop reading. Start building.**
- Write Python scripts for security automation
- Deploy infrastructure with Terraform
- Build actual AWS environments and secure them
- Analyze CloudTrail logs with SQL
- Create real projects, not just follow tutorials

**Visual learning that works:**
- Document architectures in plain language
- Build a reference library I can actually use
- (You'll see winter-themed names like Snowy, Winterday, and Blizzard throughout — it's just how my brain organizes examples)

**Go from theory to implementation:**
- Not "what does this service do" → "when would I use this and how would I deploy it"
- Not "what are the features" → "how do I secure this in production"
- Not "can I pass the exam" → "can I do the job"

## Why I'm Still Here

I could have quit after the first failure. I definitely thought about quitting after the second.

But someone once said that brick walls aren't there to keep us out. They're there to show how badly we want something — to stop the people who don't want it badly enough.

I want this badly enough to fail twice and keep building.

> *"Success is not final, failure is not fatal: it is the courage to continue that counts."*  
> — Winston Churchill

This repository started as a way to document my second attempt.  
Now it's proof that I'm willing to do whatever it takes to get this right — even if it means admitting I was wrong, starting over, and failing again before I succeed.

I don't know how long this will take. But I know I'm not stopping until I get there.

By the Will of the Lord, I'll pass the SCS-C03. And when I do, I'll actually be ready for what comes next.

---

## Update – November 2025

Work priorities shifted unexpectedly and pulled my focus elsewhere for the past few weeks. The AWS SCS is on hold for now — not the direction I planned, but sometimes that's how it goes.

Once things settle, I'll be back to finish what I started here. Probably with a clearer head after the break.

The SCS journey isn't over. Just hitting pause.

---

## Update – December 2025

Work priorities have straightened out and the pause is over.

I'm back now, and I'm actually doing the thing I said I'd do.

I am first learning Python, Terraform, and SQL, and then putting it into practice and building with them.

Projects I will be working on:

- S3 Security Auditor — Python script to scan buckets for public access, missing encryption, disabled logging
- Security Group Auditor — Python script to find overly permissive rules and unused groups
- CloudTrail Log Analyzer — Python and SQL to analyze CloudTrail logs for security events and suspicious activity

This repository will update as I go. No timeline. Just progress.

---

## Update – December 24th, 2025

I have finished learning Python fundamentals and have started learning the Boto3 SDK now.

I'm a hands-on learner, so I'm having Claude generate scenario-based challenges for me to code based on what I've learned. I write the code and get it graded by Claude. When something doesn't make sense, I ask for explanations and do more practice in that area until it sticks. This approach helps me retain information much better than just learning theory.

I had Claude generate scenarios around networking topics since those are what I work with daily and am most familiar with. I've added them to this repo. I'll continue doing this for all future challenges.

---

## Update – January 6th, 2025

As of now I've completed three hands-on boto3 projects: an automated backup system, a security group auditor, and database-backed web infrastructure with EC2, RDS, and VPC.

I'll be honest, I was making this harder on myself than it needed to be. While learning these services, I was trying to memorize all the syntax alongside understanding the why behind every line, and it was genuinely tiring me out. Recently I was made aware that memorizing everything upfront isn't a reasonable goal to put on myself as the syntax will start sticking naturally the more I use it day to day. What I actually needed was to understand how the commands work and what they do, and get comfortable using documentation and searching to figure out how to build what I need.

Once that clicked, I changed my approach. I worked through guided walkthroughs for S3, EC2, RDS, and VPC, typing everything out myself and asking questions on anything I didn't understand until it made sense. After that, I went through three mini-projects to see what it looks like when you tie multiple services together in one script. The first project combined S3 and EC2, the second brought in EC2, RDS, and VPC, and the third tied all four together. I learned so much more this way than I ever did trying to memorize syntax, and I wasn't getting burned out by it.

Now that I have a deeper understanding of how these services work together, I'm moving on to Lambda and automation to automate things like S3 lifecycle events, RDS maintenance tasks, and VPC monitoring. Eventually I want to explore SNS, SQS, and other event-driven services.

This work is also helping with the Security Specialty exam. Both times I've attempted it, there were boto3 related questions I struggled with. Learning all of this is really filling in those gaps, and continuing to build my knowledge will only make that foundation stronger.

I'm genuinely enjoying this journey now. This feels like progress on its own.

---

## Update – January 15th, 2025

Lambda has been a game-changer for how I think about automation in AWS. I started with the learning labs to understand how Lambda actually works and answer questions like: how do S3 events trigger functions? What does a CloudWatch schedule look like? How do you write IAM policies that give Lambda exactly what it needs? I built functions for EC2 backups, Aurora Serverless CSV imports, real-time S3 validation, and VPC resource cleanup—not because I needed those specific tools, but because they taught me the patterns that show up everywhere.

Once I had the basics down, I moved to security automation, creating six functions that handle real-world compliance and cost optimization scenarios: cleaning up old snapshots, auditing tags, scanning for public S3 buckets, finding unused security groups, flagging old IAM keys, and auto-stopping instances. These weren't just exercises, they're the kind of functions you'd actually deploy in production.

After getting comfortable with single-function automation, I started building more complex systems. The SNS/SQS project implements a resilient CSV validation pipeline so that when an external API call fails, it publishes an SNS alert and queues a retry through SQS. The Glue/EMR project processes billing data at scale using PySpark on EMR clusters, with Glue Data Catalog handling the metadata layer.

I wouldn't say I've mastered Lambda, I still need to reference documentation and search for solutions constantly. But what's different now is that I understand the underlying patterns well enough to know what I'm looking for. I can read the boto3 docs and figure out how to implement what I need instead of feeling lost.
This work has been incredibly valuable in filling major gaps from my Security Specialty exam attempts. Both times I've taken it, there were questions about Lambda automation patterns, event driven architectures, and service orchestration that I just didn't have the knowledge for. My understanding was all superficial, but having gone deep into it now, I understand these concepts far better. Those questions would look completely different if I took the exam today.
What I'm seeing clearly again is that memorizing boto3 syntax was never the right goal. The actual goal was understanding how these services work together, what the structure of event driven systems looks like, and how to build resilient architectures. The syntax is just the tool to implement those concepts, something that can be referenced from many places.

All I have left now are three final projects: S3 Security Auditor, Security Group Auditor, and CloudTrail Log Analyzer. After those, I'll be wrapping up this boto3 module.

---

## Current Projects

| Project | Language/Tool | Status | Repository |
|---------|---------------|--------|------------|
| Skill Development | Python, Boto3 | 🟪 In Progress | [View](./Skill%20Development) |
| S3 Security Auditor | Python, Terraform | ✖️ Not Started | ✖️ Not Started |
| Security Group Auditor | Python, Terraform | ✖️ Not Started | ✖️ Not Started |
| CloudTrail Log Analyzer | Python, SQL | ✖️ Not Started | ✖️ Not Started |

## Study Progress

| Domain | Title | Status | Notes |
|--------|-------|--------|-------|
| 1 | Threat Detection and Incident Response | ✔️ Complete | [View](./Domain%201%20-%20Threat%20Detection%20and%20Incident%20Response) |
| 2 | Security Logging and Monitoring | ✔️ Complete | [View](./Domain%202%20-%20Security%20Logging%20and%20Monitoring) |
| 3 | Infrastructure Security | ✔️ Complete | [View](./Domain%203%20-%20Infrastructure%20Security) |
| 4 | Identity and Access Management | ✔️ Complete | [View](./Domain%204%20-%20Identity%20and%20Access%20Management) |
| 5 | Data Protection | ✔️ Complete | [View](./Domain%205%20-%20Data%20Protection) |
| 6 | Management and Security Governance | ✔️ Complete | [View](./Domain%206%20-%20Management%20and%20Security%20Governance) |
| 7 | Other Services | ✔️ Complete | [View](./Other%20Services) |

> ✔️ = Complete 🟪 = In Progress ✖️ = Not Started

---

## Connect with Me

- **LinkedIn:** [https://www.linkedin.com/in/emilp-profile/](https://www.linkedin.com/in/emilp-profile/)