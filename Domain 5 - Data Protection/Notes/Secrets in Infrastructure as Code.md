# Secrets in Infrastructure as Code (IaC)

## What Are Secrets in IaC
In Infrastructure as Code (IaC), you define cloud resources — like VPCs, EC2 instances, IAM roles, etc. — using code instead of clicking in the console.  
But here’s where the trouble starts.

Often, you need to inject sensitive values into the infrastructure:

- API keys  
- Database passwords  
- Access tokens  
- OAuth secrets  
- Encryption keys  
- S3 access credentials  
- SMTP or third-party integration keys  

If you’re not careful, these secrets end up hardcoded in Terraform files, CloudFormation templates, CDK stacks, or `ansible-vars.yaml`. And once they’re there?

- They get pushed to GitHub.  
- They get emailed.  
- They get logged.  
- They get leaked.  

And boom — one mistake and an attacker has root access to your infrastructure.  
The IaC model is powerful — but treats secrets like just another variable unless you explicitly protect them. That’s the danger.

---

## Cybersecurity Analogy
Imagine IaC is your robot assistant that builds out your entire datacenter for you.  
You give it instructions: “Provision a database, launch some servers, set up networking.”

Now let’s say you write in your instruction book:  
**“Here’s the password to the vault — it’s `hunter2`. Write it on a Post-It and tape it to the door.”**

That’s what it’s like hardcoding a secret into Terraform or CloudFormation.

The robot follows orders — and blindly leaves sensitive credentials embedded in the final product:

- In environment variables  
- In metadata  
- In logs  
- In state files  

And anyone with access to the IaC repo, or to the S3 backend holding Terraform state, can extract those secrets.

## Real-World Analogy
Let’s say **BlizzardTeam** is using Terraform to deploy a web app.  
Here’s a simplified `terraform.tf` snippet:

```hcl
resource "aws_db_instance" "main" {
  engine         = "postgres"
  username       = "blizzardadmin"
  password       = "MySuperSecretPassword123!"
  ...
}
```

Looks innocent. But this is bad — like **very** bad.

That password is:

- Now in version control history  
- Stored in Terraform state files  
- Possibly echoed in logs or plan previews  
- Shared with every teammate who clones the repo  

Now imagine they commit this to a public GitHub repo by accident.  
Or their CI/CD pipeline prints out the variables.  
Or their state backend (S3 bucket) is misconfigured.  
Now that database? **Wide open.**

---

## How It Works

### 1. Hardcoded in Code Files
- Stored in cleartext in `.tf`, `.yaml`, `.json`, `.ts`, etc.  
- Accidentally committed to version control  
- Copied into PRs, emails, docs  

### 2. Stored in State Files
- Terraform keeps a `.tfstate` file tracking actual deployed resource values  
- That includes real values for passwords, keys, etc.  
- Even if you use `variable = sensitive`, it shows up in the state  
- If stored in S3 or local disk, it must be encrypted and access-controlled  

### 3. Exposed via Logging
- CI/CD systems like GitHub Actions, GitLab, Jenkins might echo variables  
- `terraform plan` output might print secrets  
- Slack notifications, CloudWatch logs, and artifacts might catch sensitive info  

### 4. Environment Variables
- Many teams pass secrets into IaC via env vars  
- But if not scrubbed, they leak into env dumps, logs, Lambda config  

### 5. External Data Sources
- Fetching secrets with `data.external` or scripts can lead to:  
  - Output exposure  
  - Logging into Terraform console  
  - Accidentally outputting secrets in plan JSON or CloudFormation templates  

---

## Real AWS Example — The SnowyCorp Secrets Incident

SnowyCorp had a Terraform file that deployed:

- A Lambda function  
- An RDS database  
- A CloudFront distribution  

In one PR, a dev added:

```hcl
environment {
  variables = {
    DB_PASSWORD = "SnowySuperSecret!"
  }

}
```

Later:

- This was committed and merged  
- CI pipeline echoed the variable during deployment  
- Terraform state was stored unencrypted in an open S3 bucket  

**Result:**

- A random external security researcher found the S3 bucket  
- Downloaded `terraform.tfstate`  
- Extracted the `DB_PASSWORD`  
- Logged into the prod RDS database  
- Dumped 8 months of logs and internal PII  

**After that, SnowyCorp:**

- Rotated all credentials  
- Moved to Secrets Manager  
- Added detection on public S3 buckets  
- Enforced pre-commit hooks with `git-secrets`  
- Audited all Terraform outputs and logs  

---

## How to Fix It

- Never hardcode secrets into `.tf`, `.yml`, `.json`, `.ts`, `.py`, etc.  
- Use AWS Secrets Manager or SSM Parameter Store to securely store secrets  
- Pass secrets into IaC using:
  - `terraform-provider-secretsmanager`  
  - `data "aws_ssm_parameter"` (with `secure_string`)  
  - `data "aws_secretsmanager_secret_version"`  
- Mark variables as `sensitive = true` — this hides them in CLI output, but not in state  
- Encrypt all state files:
  - Use server-side encryption (SSE) on S3 buckets  
  - Enable bucket versioning  
  - Restrict IAM roles to read-only access  
  - Audit access via CloudTrail  
- Use remote backends with locking:
  - S3 + DynamoDB for Terraform to avoid race conditions and accidental overwrites  
- Set up `git-secrets` or `truffleHog`:
  - Pre-commit hook to scan for secrets before code hits Git  
  - Block if regex matches common patterns (AWS keys, passwords, JWTs)  
- Scrub your pipelines:
  - Sanitize `terraform plan` output  
  - Mask secrets in GitHub Actions or GitLab CI logs  
  - Don’t echo unfiltered outputs in Slack or artifacts  
- Limit scope of secrets:
  - One secret per use case  
  - Rotate regularly  
  - Use IAM condition keys (like `SourceVpc`, `SourceArn`) to scope down access  

---

## Other Explanations

- **Sensitive vars still go into state**: Even if you mark a variable as `sensitive = true`, it only hides from CLI/UI. It’s still plaintext in the state file unless you encrypt it.  
- **CloudFormation is just as guilty**: If you inject secrets into parameters and deploy, the templates and metadata may log them. Use `NoEcho: true` for sensitive parameters.  
- **Secrets in Lambda env vars**: Many teams use IaC to deploy Lambda functions and drop secrets into environment variables — these are stored in Lambda config metadata and are readable if an attacker gets access.  
- **Overlapping responsibilities**: Developers own IaC, but secrets often belong to Security or DevSecOps. That gap leads to ambiguity and oversights.  

---

## Final Thoughts

Secrets in IaC are one of the most common — and quietest — security threats in cloud-native environments.

- They don’t cause outages.  
- They don’t show up on dashboards.  
- They just sit there — waiting to be copied, exposed, or stolen.  

The problem isn't IaC itself. It's that IaC was designed for **transparency** — to describe every part of your infra — and secrets, by nature, require **opacity**.

You have to inject just enough info for the compute to work — **without giving away the kingdom**.

If you're serious about cloud security, your policy must be:

> **“No secrets live in version control. Period.”**

- Encrypt everything.  
- Log access.  
- Rotate regularly.  
- Automate detections.  

Treat your `terraform.tfstate` like a password manager file — **because it is**.

