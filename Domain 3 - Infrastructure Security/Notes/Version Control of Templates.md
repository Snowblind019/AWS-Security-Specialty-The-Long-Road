# Version Control of Templates

## What It Is

**Version control** for Infrastructure-as-Code (**IaC**) templates refers to storing and managing **Terraform**, **CloudFormation**, or **CDK** templates in a **source-controlled repository** like Git. Each change is tracked, documented, reviewed, and auditable — just like application code.

### Why this matters for security:

- Prevents unauthorized or accidental changes
- Enables peer review and security audits before deploy
- Maintains historical context and rollback options
- Supports change tracking for compliance and incident response
- Enables consistent pipelines across teams, accounts, and environments

> It’s not just about code hygiene — it’s about *infrastructure governance*.

---

## Cybersecurity Analogy

Imagine if your company updated firewall rules by hand, no records, no approvals — and someone opened port 22 to the world.
No audit trail. No rollback. No accountability.

Version control makes it so *every security-affecting change* is reviewed, logged, and reversible.

## Real-World Analogy

Let’s say **Winterday** is editing a legal contract in Word, saving over the same file each time. **Blizzard** has no idea what changed or why. There’s no trail — just chaos.

Now imagine it’s in Google Docs: version history, comments, approvals.

> That’s Git for your templates. Transparency. Accountability. Control.

---

## Security Benefits of Template Versioning

| **Benefit**              | **Description**                                                         |
|--------------------------|-------------------------------------------------------------------------|
| **Change Accountability** | Every commit has an author, timestamp, and diff                         |
| **Peer Review**           | PRs allow security team to block risky configs                          |
| **Rollback Support**      | Easy to revert to a known-safe version                                  |
| **CI/CD Auditability**    | Pipelines can enforce checks on every commit                            |
| **Compliance Alignment**  | Helps meet SOC 2, ISO 27001, **HIPAA** controls                         |
| **Separation of Duties**  | Developers write templates, security reviews, CI/CD enforces            |
| **Diff-based Alerting**   | GitHub Actions / **CodePipeline** can alert on **IAM/SG** changes       |

---

## How to Implement Secure Version Control of **IaC**

### 1. Store All **IaC** in Git

- **Terraform** (`.tf`)
- **CloudFormation** (`.yaml`, `.json`)
- **CDK** (`.ts`, `.py`, etc.)

> Use **GitHub**, **GitLab**, **CodeCommit**, or **Bitbucket**.

### 2. Use Branching + Pull Requests

- `main` branch is production
- **Devs** use feature branches
- All merges go through Pull Request + Review

**Snowy’s** rule:

> *No one merges to prod without a review, ever.*

### 3. Enforce Reviews for Sensitive Changes

Use diffs and GitHub **codeowners** to flag:

- `iam:*`
- `0.0.0.0/0` ingress
- `s3:PutBucketAcl`
- Disabling encryption or logging

Use bots or actions to auto-warn or auto-block.

### 4. Track Template Versions in Deployments

Inject Git commit **SHA** or tag into:

- **Terraform** variables
- **CloudFormation** metadata
- **SSM** Parameters

So that when an issue happens, you can correlate:
> “Template v1234 created this resource on Sep 26th at 3:01pm.”

### 5. Automate CI/CD Pipelines

**Examples:**

- **Terraform** Plan + Apply via GitHub Actions
- **CloudFormation** via **CodePipeline**
- **Lint → Validate → Scan → Deploy**

**Stages:**

1. Run **linter** (`tfsec`, `checkov`, `cfn-lint`)
2. Validate syntax
3. Security scan
4. Manual or auto-approval deploy
5. Post-deploy drift check

### 6. Tag Everything with Template Version

Enforce tags like:

```hcl
Tags = {
  IaCVersion = "v1.4.7"
  CreatedBy  = "Terraform"
  Environment = "Dev"
}
```

Helps with:

- Inventory analysis
- Cost visibility
- Incident response

---

## Snowy’s Git Flow Example

Let’s say **Snowy** wants to change the `main.tf` to allow EC2 logging to a new S3 bucket:

- Creates `feature/logging-s3-update` branch
- Pushes commit → opens PR
- Reviewer sees: `s3:PutObject` granted, bucket is private, logging enabled
- PR is approved → merge to `main`
- GitHub Action runs `terraform plan`, `terraform apply`
- Commit **SHA** `abc123` is tagged on the deployed resource

> 1 week later, there’s a weird access log. They trace it to commit `abc123`, roll back to `abc122`, and issue resolved.

---

## Final Thoughts

Templates aren’t just “code” — they’re the blueprint for your security perimeter.

Without version control, you’re flying blind.
With it, you have **traceability**, **repeatability**, and **accountability**.

> If you **can’t track who changed what**, then you **can’t secure your cloud**.
