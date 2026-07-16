# Amazon CodeGuru

A machine-learning pair of developer tools: CodeGuru Reviewer, a static analyzer that reviews Java and Python in pull requests and repos, and CodeGuru Profiler, a runtime profiler that finds the most expensive methods in a running application. Reviewer is the security-relevant half. It uses ML and automated reasoning to trace data flow from source to sink and flag secrets, injection, unsafe deserialization, resource leaks, concurrency bugs, and insecure AWS SDK usage, mapped against the OWASP Top 10 and AWS internal best practices.

For security work the thing to hold onto has two parts. First, Reviewer is the shift-left SAST answer: catch the vulnerability in the pull request, before it ships. Second, and more important as of 2026, Reviewer is legacy. It went into maintenance mode on November 7, 2025, with no new repository associations, and AWS now points teams to Amazon Inspector Code Security for repository scanning and Amazon Q Developer for code review. Know CodeGuru for what it did, and reach for Inspector Code Security as the current answer.

## How it works

CodeGuru Reviewer:

- **Trigger**: analyzes pull requests or full-repo scans on GitHub, GitHub Enterprise, Bitbucket, or CodeCommit (for associations that already exist). Findings post as line-level PR comments with a severity, an explanation, and a suggested fix.
- **Engine**: ML plus automated reasoning, running data-flow analysis from source to sink across multiple functions to catch issues a line-by-line human review misses.
- **Detects**: hardcoded secrets, SQL injection, unsafe deserialization, unvalidated input, resource leaks, race conditions, and inefficient or unsafe AWS SDK calls. OWASP Top 10 plus AWS best practices.
- **Languages**: Java (most mature) and Python only.

CodeGuru Profiler:

- **Agent**: a low-overhead agent runs inside your Java or Python app on EC2, ECS, EKS, or Lambda and streams data over TLS to the service.
- **Collects**: stack traces and heap summaries only. It does not collect or store your source code.
- **Produces**: flame graphs, hot-method call stacks, and cost-per-method estimates so you can cut CPU, latency, and spend. This is a performance and cost tool, not a security scanner.

Security posture, both halves:

- Least-privilege IAM roles gate who can create, read, or delete CodeGuru resources.
- CloudTrail logs the API calls. Data is encrypted in transit and at rest and processed in-Region.
- Customer source is not used to train the models, and Profiler never captures source at all.

## Amazon CodeGuru vs sibling options

| | CodeGuru Reviewer | Inspector Code Security | Amazon Q Developer | CodeGuru Profiler |
|---|---|---|---|---|
| Analyzes | Source in PRs / repos | Code repos for vulnerabilities and deps | Code in IDE / repos | A running application |
| Type | Static, ML plus automated reasoning | Static vuln and dependency scan | AI code review, secrets, deps | Dynamic performance profiling |
| Status | Maintenance mode (Nov 2025) | Current | Current, in Kiro transition | Active |
| Best for | Legacy SAST on Java / Python | The current code-security answer | Inline review before merge | CPU, latency, and cost hotspots |

## What gets tested

- CodeGuru Reviewer is the ML-plus-automated-reasoning SAST answer for Java and Python: secrets, injection, resource leaks, concurrency, insecure AWS SDK usage, OWASP Top 10, caught in the pull request. But it is legacy: maintenance mode since November 7, 2025, no new repository associations.
- The current successors are Amazon Inspector Code Security for repository vulnerability and dependency scanning and Amazon Q Developer for code review with static analysis and secrets detection. If a scenario asks for code security scanning today, lean Inspector Code Security.
- CodeGuru Profiler is the performance and cost answer, not a security control: hot methods, CPU, latency, and cost per method from a running app. Its agent collects stack traces and heap summaries only, never source code.
- Posture points that do get tested: least-privilege IAM roles, CloudTrail logging of API calls, encryption in transit and at rest, and in-Region processing.
- Do not confuse Reviewer (static, pre-merge, source code) with Profiler (runtime, performance) or with GuardDuty and Inspector (runtime and infrastructure threat and vulnerability detection).

## Limitations

- Reviewer is in maintenance mode: no new repository associations since November 7, 2025, though existing associations still analyze. AWS steers new work to Q Developer and Inspector.
- Java and Python only. Narrow language support.
- Reviewer is pre-merge static analysis. It does not see runtime or infrastructure issues. Profiler is runtime performance, not a security scanner.
- The successor tooling is itself churning: Amazon Q Developer IDE plugins reach end of support April 30, 2027 with AWS steering users to Kiro, though Q Developer in the AWS Console and first-party AWS experiences continue. Prefer Inspector Code Security as the durable security-scanning path.
- Best value inside the AWS ecosystem, weaker outside AWS-native workflows.