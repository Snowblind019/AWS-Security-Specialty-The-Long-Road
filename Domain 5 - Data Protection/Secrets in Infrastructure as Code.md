# Secrets in Infrastructure as Code (IaC)

IaC describes infrastructure as code (Terraform, CloudFormation, CDK, Ansible), and its whole value is transparency: every resource written down and versioned. That is exactly what makes secrets dangerous in it, because a hardcoded password, API key, or token becomes just another variable that ends up in Git history, state files, plan output, CI logs, and Lambda metadata. The core tension: IaC wants to describe everything, secrets require opacity, so you must inject just enough for the resource to work without committing the secret. The thing to hold onto: never store secrets in version control, reference them at deploy time from Secrets Manager or SSM Parameter Store instead, and remember that Terraform state stores resolved secret values in plaintext even when the variable is marked `sensitive`, so the state backend itself (encrypted, access-controlled, audited) is a secret-bearing artifact.

## How it works (where secrets leak)

- **Hardcoded in template files.** Cleartext in `.tf`, `.yaml`, `.json`, or `.ts`, committed to Git, copied into PRs and docs, and living forever in history even after removal.
- **Resolved into state files.** Terraform state records actual deployed values, including passwords and keys. `sensitive = true` hides a value from CLI/plan output but it is still plaintext in state, so an unencrypted or public state backend (a misconfigured S3 bucket) leaks everything.
- **Echoed in CI/CD logs.** GitHub Actions, GitLab, or Jenkins can print variables, `terraform plan` can render secrets, and Slack notifications or build artifacts can capture them unless masked.
- **Baked into Lambda environment variables.** IaC that drops secrets into Lambda env vars stores them in the function's configuration metadata, readable by anyone who can describe the function.
- **Leaked via external data sources.** Fetching secrets through `data.external` or scripts can surface them in plan JSON or console output.
- **The fix is deploy-time reference, not embedding.** Reference secrets from Secrets Manager (`data.aws_secretsmanager_secret_version`) or SSM SecureString (`data.aws_ssm_parameter`) so the value is pulled at apply and, ideally, resolved at runtime by the resource rather than materialized into state. CloudFormation uses dynamic references (`{{resolve:secretsmanager:...}}` / `{{resolve:ssm-secure:...}}`) and `NoEcho: true` for sensitive parameters.

## Leak surfaces and controls

| Surface | Risk | Control |
|---|---|---|
| **Template files** | Cleartext in Git history | Never hardcode; pre-commit scanning |
| **Terraform state** | Plaintext even if `sensitive` | Encrypt backend, restrict IAM, version, audit |
| **CI/CD logs** | Echoed variables, plan output | Mask secrets, sanitize plan/artifacts |
| **Lambda env vars** | Readable in function config | Fetch from Secrets Manager at runtime |
| **CloudFormation params** | Logged in events/metadata | `NoEcho: true`, dynamic references |
| **External data sources** | Output in plan JSON | Avoid, or scrub outputs |

## What gets tested

- **Reference secrets, do not embed them.** The correct pattern is storing secrets in Secrets Manager or SSM Parameter Store (SecureString) and referencing them, or using CloudFormation dynamic references, so the secret never lives in the template or repo.
- **`sensitive = true` does not protect state.** Marking a Terraform variable sensitive hides it from CLI output but leaves it plaintext in state. Securing the secret means encrypting and locking down the state backend, a commonly tested subtlety.
- **CloudFormation `NoEcho` and dynamic references.** Preventing a CloudFormation parameter from appearing in logs and console is `NoEcho: true`, and pulling the actual secret at deploy uses dynamic references to Secrets Manager/SSM.
- **State backend is a secret store.** Terraform state in S3 must have SSE, restricted IAM, versioning, and DynamoDB locking, and CloudTrail on access, because it holds resolved secrets. A public state bucket is the classic breach.
- **Detection in the pipeline.** Pre-commit scanning (git-secrets, truffleHog) blocks secrets before they reach Git, and log masking prevents CI from echoing them.
- **Lambda secrets at runtime.** Injecting secrets into Lambda env vars via IaC is weaker than fetching from Secrets Manager at runtime, since env vars sit in readable function config.

## Limitations

- Referencing a secret from Secrets Manager/SSM can still resolve the value into Terraform state, so the state backend remains sensitive and must be protected regardless of how cleanly the secret is sourced.
- `sensitive` and `NoEcho` reduce accidental display but do not encrypt the underlying artifacts, so they are not a substitute for state encryption and access control.
- Git history is permanent. A secret committed and later removed still exists in history and must be rotated, not just deleted.
- Pipeline masking is best-effort. A secret can still leak through an unexpected output path (an error message, a third-party step) unless outputs are tightly controlled.
- Runtime fetching shifts the secret out of the template but adds an IAM and KMS dependency at execution, so misconfigured permissions there re-open the exposure.
- Ownership gaps matter: developers own the IaC while security owns the secrets, and that seam is where hardcoding slips through, so process and detection, not just tooling, are required.