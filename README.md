# AWS Security Specialty: The Long Road

![Status](https://img.shields.io/badge/Status-In%20Progress-yellow)
![Focus](https://img.shields.io/badge/Focus-AWS%20Cloud%20Security-blue)
![Certification](https://img.shields.io/badge/Certification-AWS%20SCS--C03-8A2BE2)
![SDK](https://img.shields.io/badge/SDK-boto3-orange)
![Method](https://img.shields.io/badge/Method-Hands--On-4479A1)

This repository is the record of my road to the AWS Certified Security Specialty (SCS-C03). It has taken three failed attempts, a full rebuild of how I study, and a lot of time spent actually building things instead of just reading about them. What started as a place to document a second attempt became proof of something more useful: that I am willing to be wrong, start over, and keep going until the work is real.

> *"Success is not final, failure is not fatal: it is the courage to continue that counts."*
> — Winston Churchill

---

## Where This Stands Today

- **CCNA:** Passed. Required at work, and it handed me the study method I now use for everything else.
- **boto3 module:** Complete. Fundamentals through event-driven automation, capped with three security projects.
- **SQL:** Learned on the job while building the CloudTrail analyzer, then solidified through fundamentals.
- **AWS Journeys Edge:** Complete. A full subdomain-by-subdomain hands-on pass through the exam, every objective built out by hand in the companion repo, [AWS Journeys Edge](https://github.com/Snowblind019/AWS-Journeys-Edge).
- **Now:** Drilling practice tests, heading into attempt four.

---

## Three Attempts, Three Lessons

Each failure peeled back a layer I did not know was there. The lessons do not repeat, they go deeper.

### Attempt 1, September 2025: I was studying for a test, not for understanding

I had done Maarek's course, Cantrill's deep dives, hundreds of practice questions. I knew the services. The exam still failed me, and not by a little.

The lesson was about the goal itself. I had been preparing to pass an exam, not to understand AWS security, and those are not the same thing. So I threw out the approach: diagrammed services, rebuilt from first principles, and started asking why things work the way they do instead of just what they do.

### Attempt 2, November 2025: Understanding on paper is not the same as building

This one hurt more, because I had done everything "right." I studied differently, went deeper, put in the work. I could explain KMS, diagram GuardDuty, walk through any architecture on a whiteboard.

Then the exam handed me scenarios built on Python automation, Terraform deployments, and SQL log analysis, tools I had read about but never touched. I knew *about* them. I had no idea how to actually *do* any of it. Knowing a thing and being able to build it are two different skills, and I only had the first one.

That is the failure that ended the reading phase and started the building phase.

### Attempt 3, March 2026: Shallow building is not the same as deep building

This was my first crack at the new C03 format, and the strange part is that I walked away happy. I did not guess a single answer, I picked every one with intent, and the score reflected it. Claude's ballpark put me around five questions short of passing, coming from zero AWS knowledge not long before. That is not devastation, that is a target.

The lesson lived in *where* I fell short. My theory was solid, and my Lambda and automation hands-on was genuinely strong because I had poured real project time into it. Everything else was shallow. The C03 questions kept offering two or three answers that were all technically correct, where only one was the *most* correct given the qualifier: most cost efficient, least overhead, fastest, most secure. Picking between them needs the granular, worked-with-it knowledge you only get by building a service yourself, and I only had that for a handful of services.

So the fix was not "study harder." It was "build wider, one service at a time."

---

## The Turn: From Studying to Building

After the second failure I stopped studying for an exam and started training for the job. This is the phase that changed everything.

I began with Python fundamentals, then moved into the boto3 SDK. Early on I made it harder than it needed to be, trying to memorize every line of syntax while also understanding the reasoning behind it. That burned me out fast. Once I accepted that syntax sticks on its own through daily use, and that the real skill is understanding what the commands do and getting comfortable in the documentation, the whole thing opened up.

From there the work built on itself:

- **Guided builds** for S3, EC2, RDS, and VPC, typed out by hand, questioning anything that did not make sense until it did.
- **Mini-projects** tying services together in a single script, first S3 and EC2, then EC2 with RDS and VPC, then all four at once, to see what integration actually looks like.
- **Lambda and event-driven automation:** EC2 backups, S3 validation, VPC cleanup, then six security and cost functions of the kind you would actually deploy. From there, resilient systems: an SNS and SQS pipeline that alerts and retries on failure, and a Glue and EMR job processing billing data at scale with PySpark.
- **SQL**, picked up out of necessity for the CloudTrail work, then rounded out properly through fundamentals afterward.

The phase closed with three capstone security projects, now living in their own portfolio repo, [AWS Security Projects](https://github.com/Snowblind019/AWS-Security-Projects):

| Project | Stack | What it does |
|---------|-------|--------------|
| S3 Security Auditor | boto3 | Scans buckets for public access, missing encryption, and disabled versioning or logging, then sends SNS alerts grouped by severity |
| Security Group Auditor | boto3 | Flags overly permissive rules (0.0.0.0/0) and unused groups, alerting on each finding |
| CloudTrail Log Analyzer | boto3, SQL | Runs Athena queries against CloudTrail logs for root usage, failed auth, IAM changes, and other suspicious activity |

The thing I kept relearning across all of it: memorizing syntax was never the goal. Understanding how services fit together, what event-driven systems look like, and how to build something resilient, that was the goal. Syntax is just the tool you reach for, and the docs are always there.

---

## The Method: One Subdomain at a Time

The CCNA was a work requirement, and passing it did more than check a box. It gave me the exact method attempt three told me I was missing.

Studying for the CCNA, I went objective by objective: take a single subdomain, build it out by hand, break it down, drill it, and only then move on. My first CCNA attempt skipped the hands-on labs because I was lazy, and it cost me. The granular, build-it-yourself pass is what carried me over the line the second time.

That is precisely the gap from attempt three. So I pointed the same method straight at the SCS and worked all the way through it in [AWS Journeys Edge](https://github.com/Snowblind019/AWS-Journeys-Edge):

- Went **domain by domain, then subdomain by subdomain.** No more studying broad and hoping it sticks.
- For each subdomain, **built it out in AWS by hand** rather than reading about it.
- Captured each one as a **CCNA-style lab:** diagrams, CLI walkthroughs, the gotchas that only show up when you actually deploy it, and checkpoint questions to test recall.
- **Documented the reasoning in my own words,** so I own why one approach wins over another when the exam makes me choose between answers that all look right.

That pass is finished. Every subdomain is built, broken down, and documented, which means the depth I was missing on attempt three is finally on the page. All that stands between me and attempt four now is drilling practice tests to pressure-test it.

This was never just exam prep. My goal is to become a Cloud Security Engineer, and my current level is already good enough for a junior role. Going this deep is how a junior becomes a genuinely capable engineer, the kind of depth you cannot fake through theory, only earn by building and breaking things.

---

## Why I'm Still Here

I could have quit after the first failure. I seriously considered it after the second. But brick walls are not there to keep us out. They are there to show how badly we want the thing on the other side, and to stop the people who do not want it enough.

I have wanted this enough to fail three times and keep building. Every failure now just sharpens the drive instead of feeding self-pity. When I saw that third score report, my first thought was not defeat, it was *where could I have done better, and what do I do next.*

I do not have a hard timeline. I have a method that works, proof that it works from the CCNA, and a repo full of the hands-on depth I was missing. By the Will of the Lord, attempt four is the one.

> *"With men this is impossible, but with God all things are possible."*
> — Matthew 19:26

---

## Progress at a Glance

| Track | Status |
|-------|--------|
| Python and boto3 module | **Complete** |
| SQL fundamentals | **Complete** |
| Capstone security projects (x3) | **Complete** |
| CCNA (work requirement) | **Passed** |
| Subdomain hands-on pass (Journeys Edge) | **Complete** |
| Practice tests for attempt 4 | **In progress** |
| SCS-C03 exam | **Attempt 4 ahead** |

**Companion repos**
- [AWS Journeys Edge](https://github.com/Snowblind019/AWS-Journeys-Edge), subdomain-by-subdomain hands-on labs
- [AWS Security Projects](https://github.com/Snowblind019/AWS-Security-Projects), the three capstone auditors and analyzer

---

## Connect with me

- **LinkedIn:** [emilp-profile](https://www.linkedin.com/in/emilp-profile/)