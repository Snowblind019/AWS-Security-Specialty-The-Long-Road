# AWS Security Specialty – The Long Road

![Status](https://img.shields.io/badge/Status-In%20Progress-yellow)
![Focus](https://img.shields.io/badge/Focus-AWS%20Cloud%20Security-blue)
![Goal](https://img.shields.io/badge/Certification-AWS%20SCS%20--%20Specialty-8A2BE2)
![SDK](https://img.shields.io/badge/SDK-boto3-orange)
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

## Journal Entry – November 2025

Work priorities shifted unexpectedly and pulled my focus elsewhere for the past few weeks. The AWS SCS is on hold for now — not the direction I planned, but sometimes that's how it goes.

Once things settle, I'll be back to finish what I started here. Probably with a clearer head after the break.

The SCS journey isn't over. Just hitting pause.

---

## Journal Entry – December 2025

Work priorities have straightened out and the pause is over.

I'm back now, and I'm actually doing the thing I said I'd do.

I am first learning Python, Terraform, and SQL, and then putting it into practice and building with them.

Projects I will be working on:

- S3 Security Auditor — Python script to scan buckets for public access, missing encryption, disabled logging
- Security Group Auditor — Python script to find overly permissive rules and unused groups
- CloudTrail Log Analyzer — Python and SQL to analyze CloudTrail logs for security events and suspicious activity

This repository will update as I go. No timeline. Just progress.

---

## Journal Entry – December 24th, 2025

I have finished learning Python fundamentals and have started learning the Boto3 SDK now.

I'm a hands-on learner, so I'm having Claude generate scenario-based challenges for me to code based on what I've learned. I write the code and get it graded by Claude. When something doesn't make sense, I ask for explanations and do more practice in that area until it sticks. This approach helps me retain information much better than just learning theory.

I had Claude generate scenarios around networking topics since those are what I work with daily and am most familiar with. I've added them to this repo. I'll continue doing this for all future challenges.

---

## Journal Entry – January 6th, 2026

As of now I've completed three hands-on boto3 projects: an automated backup system, a security group auditor, and database-backed web infrastructure with EC2, RDS, and VPC.

I'll be honest, I was making this harder on myself than it needed to be. While learning these services, I was trying to memorize all the syntax alongside understanding the why behind every line, and it was genuinely tiring me out. Recently I was made aware that memorizing everything upfront isn't a reasonable goal to put on myself, as the syntax will start sticking naturally the more I use it day to day. What I actually needed was to understand how the commands work and what they do, and get comfortable using documentation and searching to figure out how to build what I need.

Once that clicked, I changed my approach. I worked through guided walkthroughs for S3, EC2, RDS, and VPC, typing everything out myself and asking questions on anything I didn't understand until it made sense. After that, I went through three mini-projects to see what it looks like when you tie multiple services together in one script. The first project combined S3 and EC2, the second brought in EC2, RDS, and VPC, and the third tied all four together. I learned so much more this way than I ever did trying to memorize syntax, and I wasn't getting burned out by it.

Now that I have a deeper understanding of how these services work together, I'm moving on to Lambda and automation to automate things like S3 lifecycle events, RDS maintenance tasks, and VPC monitoring. Eventually I want to explore SNS, SQS, and other event-driven services.

This work is also helping with the Security Specialty exam. Both times I've attempted it, there were boto3 related questions I struggled with. Learning all of this is really filling in those gaps, and continuing to build my knowledge will only make that foundation stronger.

I'm genuinely enjoying this journey now. This feels like progress on its own.

---

## Journal Entry – January 15th, 2026

Lambda has been a game-changer for how I think about automation in AWS. I started with the learning labs to understand how Lambda actually works and answer questions like: how do S3 events trigger functions? What does a CloudWatch schedule look like? How do you write IAM policies that give Lambda exactly what it needs? I built functions for EC2 backups, Aurora Serverless CSV imports, real-time S3 validation, and VPC resource cleanup — not because I needed those specific tools, but because they taught me the patterns that show up everywhere.

Once I had the basics down, I moved to security automation, creating six functions that handle real-world compliance and cost optimization scenarios: cleaning up old snapshots, auditing tags, scanning for public S3 buckets, finding unused security groups, flagging old IAM keys, and auto-stopping instances. These weren't just exercises, they're the kind of functions you'd actually deploy in production.

After getting comfortable with single-function automation, I started building more complex systems. The SNS/SQS project implements a resilient CSV validation pipeline so that when an external API call fails, it publishes an SNS alert and queues a retry through SQS. The Glue/EMR project processes billing data at scale using PySpark on EMR clusters, with Glue Data Catalog handling the metadata layer.

I wouldn't say I've mastered Lambda, I still need to reference documentation and search for solutions constantly. But what's different now is that I understand the underlying patterns well enough to know what I'm looking for. I can read the boto3 docs and figure out how to implement what I need instead of feeling lost.

This work has been incredibly valuable in filling major gaps from my Security Specialty exam attempts. Both times I've taken it, there were questions about Lambda automation patterns, event-driven architectures, and service orchestration that I just didn't have the knowledge for. My understanding was all superficial, but having gone deep into it now, I understand these concepts far better. Those questions would look completely different if I took the exam today.

What I'm seeing clearly again is that memorizing boto3 syntax was never the right goal. The actual goal was understanding how these services work together, what the structure of event-driven systems looks like, and how to build resilient architectures. The syntax is just the tool to implement those concepts, something that can be referenced from many places.

All I have left now are three final projects: S3 Security Auditor, Security Group Auditor, and CloudTrail Log Analyzer. After those, I'll be wrapping up this boto3 module.

---

## Journal Entry – January 21st, 2026

I've completed the three final boto3 projects and moved them to a dedicated portfolio repo I named **[AWS Security Projects](https://github.com/Snowblind019/AWS-Security-Projects)**.

The three projects are:

**S3 Security Auditor** - Scans all S3 buckets for misconfigurations (public access, missing encryption, disabled versioning/logging) and sends SNS alerts grouped by severity

**Security Group Auditor** - Scans EC2 security groups for overly permissive rules (0.0.0.0/0 access) and sends individual alerts for each finding

**CloudTrail Log Analyzer** - Uses Athena SQL queries to analyze CloudTrail logs for suspicious activities (root usage, failed auth, IAM changes, etc.)

These projects represent everything I've learned through this boto3 module, from basic S3 operations to more complex serverless architectures with Athena, Glue, and asynchronous query handling. Each project builds on the previous one, getting progressively more complex. The CloudTrail project was particularly challenging because I didn't know SQL when I started it. I learned SQL functions as I needed them, piecing together queries through trial and error in the Athena console. Now that it's finished, I'm going back to properly learn SQL fundamentals through SQLZoo to fill in those gaps and solidify my understanding.

With boto3 wrapped up, I'm shifting focus to SQL fundamentals for the next 1-2 weeks, then moving on to AWS Skill Builder to fill in the theoretical knowledge gaps for the Security Specialty exam. The hands-on work gave me practical implementation skills, now it's time to round that out with the exam-specific content I'm missing.

---

## Journal Entry – February 1st, 2026

So I have been a bit busy these past two weeks and didn't have as much time to put aside for studying SQL as I would have liked, but that's in the past and I have finished learning it. I can now read and understand SQL queries, write basic SELECT statements with WHERE clauses and JOINs, and actually know what I'm looking at when I see database schemas. Nothing fancy, but enough to work with CloudTrail logs and understand what's happening when I need to query data.

Taking a moment to look back and reflect on my learning journey until now, I am truly happy with how I've matured and progressed toward getting this certification. I have come a long way. The bitterness I felt when I failed the first time, the devastation I felt the second time was hard, but I'm honestly grateful for those failures. From them, I learned how to rebound from failure and did deep dives on individual AWS services to actually understand them, delved into learning Python and boto3, picked up SQL, performed mini projects here and there in addition to the three main automation projects, among other things. I can finally see that checkered flag waving at the end of the runway.

Shifting my mindset so I wasn't studying for an exam but for a job really worked wonders for me. Once I pass this exam, I'll be able to back my cert up with confidence that I know how to do the things required of me in a real job.

Now, all I have left before retaking the exam is to use AWS Skill Builder for hands-on labs and practice exams. The labs will reinforce what I've already built with my automation projects, and the practice tests will highlight exactly where I need to focus. Anything I'm weak on, I'll cover with Udemy courses. I'm hoping to retake the exam by the end of February or beginning of March.

With the Lord's help, I will pass this time!

---

## Attempt #3: March 3rd, 2026

Yet another fail under my belt, and I am happy for it!

For the past month, I have been going at studying quite hard. I have utilized AWS Skill Builder, Tutorials Dojo, and Christophe Limpalair's Cybr.com course for studying, and honestly it was pretty smooth. Come exam day, I didn't do as well as I thought I would, to be honest. Surprisingly, this failure didn't make me get depressed as the previous failures have, and because of this I am noticing something about myself that I didn't really realize until now: every failure just fuels my drive for perfection and mastery of this domain instead of leaving me to wallow in self-pity. When I saw the score report, my mind instantly went to where I could have done better on the exam to have passed, and what I can do now to study and learn better.

Something I noticed about my test today that makes me very happy is that I didn't guess my answers as I have on the previous attempts. On the previous attempts, there were a lot of questions I didn't know the answer to, so I would just guess by what sounded most correct. I am happy that this time around, I didn't do any of that, but rather I confidently selected each answer, and actually got a way better score compared to my previous two attempts! Asking Claude to give me a ballpark estimate of how many questions I was away from a passing score, it estimated ~5 questions, which considering I started this whole thing with no AWS knowledge is amazing to hear! Also, it was my first attempt at the new C03 version of the exam, and I honestly like the new question format, they are actually fun.

Recalling my exam, I noticed my biggest weakness. The reality is that I know Lambda and Automation quite well from putting a lot of time into projects, but I kind of neglected mastering hands-on work for every other service on the exam. Theory-wise I am quite decent, but I don't have that low-level knowledge that is more so required for the exam. I don't know if it's this new version of the exam or if I just never noticed it because I guessed a lot of the answers on my previous attempts, but the majority of the questions had 2 or 3 answers that were correct, where one was just more correct compared to the others in regards to what the question required. I struggled a lot on this part throughout the exam. They all made sense, but qualifiers like "most cost efficient", "least overhead", "fastest response", "most secure" and others like them made choosing between the correct answers a bit hard. I am pretty proficient in the obvious stuff, like how Lambda is almost never the answer for least overhead, or how if a service does something natively you don't need to reinvent the wheel like with CloudTrail Lake and Athena. Where I struggled was on the granular stuff that is only learned by working with the services.

Thus, I thought on it, on how I can learn all these granular things, and the Lord illuminated me on a solution. I will use the practice tests provided by Amazon on AWS Skill Builder, and on Tutorials Dojo, and even ask Claude to generate multiple choice questions for me. I will take each of the four answers to a question and go into AWS and build them out to see which ones work and which fail, and thus find the correct answer by actually doing it. After this I plan to document why the wrong answer is wrong and the correct one is correct in my own words, with screenshots from my hands-on building of it, and possibly even diagram the correct answer out via Lucidchart diagrams. This is all to give me that low-level knowledge to choose the more correct answer between multiple correct answers. For this reason, I have created another repo named **[AWS Journeys Edge](https://github.com/Snowblind019/AWS-Journeys-Edge)** in which I will be doing all this documentation.

I feel like this route is not only helpful for the exam but actually for working the job. My career goal is to become a Cloud Security Engineer, and my current skill level is good enough for a junior position, but by delving this much deeper into AWS I am also working on becoming an excellent, fully-fledged engineer, which you can't become through theory knowledge but through the ability to actually create and break things.

I am excited to tackle this! Sadly, I can't put my full attention to it, as I am studying for the CCNA alongside this since I am required to obtain it at work currently. But even then, I will still make time to work on this, delve into the mud here, and gain an even stronger foothold on my 4th attempt so the 3-5 years of hands-on experience AWS recommends for this exam don't apply to me! As Jesus said in Matthew 19:26 **“With men this is impossible, but with God all things are possible.”**

---

## Journal Entry – June 9th, 2026

It's been a few months since my last update, and the SCS has been on the back burner for most of it, but for a good reason.

Right after my third attempt, I had to put my full focus on the CCNA, since it's a requirement at work. I'm happy to say I passed it. Like this journey, it had its own failure and its own retake before I got it done. On top of that, life shuffled my routine for a bit with a vacation and a shift change at work to adjust to, so studying took a back seat. That's all settled now.

But here's the thing: studying for the CCNA didn't just take time away from the SCS. It handed me the exact method I needed for it.

When studying for the CCNA, I started going subdomain by subdomain. I'd take a single objective, build it out hands-on, break it down, then generate my own questions around it and drill until it stuck. On my first attempt I'd skipped the hands-on labs because I was lazy and it cost me. The granular, build-it-yourself approach is what got me over the line the second time.

That's the same gap I called out after my third SCS attempt: I know the theory, but I lack the low-level, hands-on knowledge to confidently pick the "more correct" answer when two or three options all look right. So I'm taking the CCNA study method I used and am pointing it straight at the SCS.

The plan from here:

- Go domain by domain, then subdomain by subdomain — no more studying broad and hoping it sticks
- For each subdomain, build it out in AWS by hand instead of just reading about it
- Generate practice questions for that subdomain, then build out every answer to see what works and what fails
- Document the *why* behind each correct and incorrect answer in my own words, with screenshots and Lucidchart diagrams

This is the **[AWS Journeys Edge](https://github.com/Snowblind019/AWS-Journeys-Edge)** work I set up after attempt three, now with a tighter structure behind it. One subdomain at a time, built by hand, until I own it.

The CCNA proved the method works. Now I run it back for the SCS.

By the Will of the Lord, the 4th attempt is the one.

---

## Current Projects

| Project | Language/Tool | Status | Repository |
|---------|---------------|--------|------------|
| Skill Development | Boto3 | **Complete** | [View](./Skill%20Development) |
| S3 Security Auditor | Boto3 | **Complete** | [View](https://github.com/Snowblind019/AWS-Security-Projects/tree/main/S3%20Security%20Auditor) |
| Security Group Auditor | Boto3 | **Complete** | [View](https://github.com/Snowblind019/AWS-Security-Projects/tree/main/Security%20Group%20Auditor) |
| CloudTrail Log Analyzer | Boto3, SQL | **Complete** | [View](https://github.com/Snowblind019/AWS-Security-Projects/tree/main/CloudTrail%20Log%20Analyzer) |

## Study Progress

| Domain | Title | Status | Notes |
|--------|-------|--------|-------|
| 1 | Threat Detection and Incident Response | **Complete** | [View](./Domain%201%20-%20Threat%20Detection%20and%20Incident%20Response) |
| 2 | Security Logging and Monitoring | **Complete** | [View](./Domain%202%20-%20Security%20Logging%20and%20Monitoring) |
| 3 | Infrastructure Security | **Complete** | [View](./Domain%203%20-%20Infrastructure%20Security) |
| 4 | Identity and Access Management | **Complete** | [View](./Domain%204%20-%20Identity%20and%20Access%20Management) |
| 5 | Data Protection | **Complete** | [View](./Domain%205%20-%20Data%20Protection) |
| 6 | Management and Security Governance | **Complete** | [View](./Domain%206%20-%20Management%20and%20Security%20Governance) |
| 7 | Other Services | **Complete** | [View](./Other%20Services) |

---

## Connect with Me

- **LinkedIn:** [https://www.linkedin.com/in/emilp-profile/](https://www.linkedin.com/in/emilp-profile/)