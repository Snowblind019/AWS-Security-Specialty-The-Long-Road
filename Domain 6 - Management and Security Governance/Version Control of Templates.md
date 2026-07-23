# Version Control of Templates

Keeping CloudFormation, Terraform, and CDK definitions in Git means every change to the security perimeter has an author, a timestamp, a diff, a reviewer, and a revert path. That is the baseline claim, and it is worth stating precisely because the security value comes from properties of the repository rather than from the mere fact of using one. A repository where anyone can force-push to main, where the deploy identity is a long-lived access key in a CI secret, and where nothing links a deployed resource back to a commit provides traceability in theory and none in practice. The properties that matter are enforced review, protected history, a federated deployment identity with no standing credentials, and a stamped link from resource to commit so an incident can be traced from a CloudTrail event to the change that caused it. The thing to hold onto: Git tells you who authored a change, CloudTrail tells you which identity applied it, and you need both plus a deliberate link between them.

## How it works

**Protected branches carry the enforcement.** Required pull request reviews, CODEOWNERS entries routing IAM, security group, KMS, and logging changes to the security team, no force push, no deletion, no self-approval, and no administrator bypass. Without these, the review process is a suggestion.

**Commit and tag integrity.** Signed commits and signed or protected tags stop history from being rewritten or a release tag from being moved to different content. This matters because a mutable tag is a common way a supposedly pinned deployment silently changes.

**The deployment identity is federated, not stored.** CI systems assume an IAM role through OIDC with a trust policy scoped to the repository, branch, and environment, so there is no long-lived key to leak. Separate roles per environment, with production behind an approval gate, is the standard separation.

**Attribution has to be engineered.** CloudTrail records the pipeline role, not the human who opened the pull request. Setting the role session name to the workflow run or actor, or using `sts:SourceIdentity` so the value propagates through role chaining and cannot be changed by the assumer, is what makes CloudTrail answer "who" rather than "which pipeline."

**Deployed resources carry their provenance.** Stamping the commit SHA and template version into resource tags, CloudFormation stack metadata, or an SSM parameter is what lets an investigation move from a suspicious resource to the exact change that created it, in seconds rather than by archaeology.

**Pipelines run a fixed sequence.** Lint and validate, policy-as-code scan, IAM Access Analyzer custom policy checks on any permission change, plan or change set, approval where required, apply, then post-deploy drift detection. Each stage is a gate, and the gates are only real if a failure blocks the merge or the deploy.

**Artifacts and modules are stored immutably.** Pipeline artifacts in S3 with versioning, KMS encryption, and restricted access, shared modules in a registry or CodeArtifact with immutable versions, and consumers pinned to a specific version or commit rather than a branch.

**Secrets never enter the repository, and history is permanent.** Pre-commit and server-side secret scanning catch most attempts, but once a credential is committed it is recoverable regardless of later deletion, so the only correct remediation is rotation.

**Note the platform change.** AWS CodeCommit is closed to new customers, so current designs assume an external Git provider integrated with CodePipeline, CodeBuild, or a third-party runner rather than a CodeCommit repository.

## Comparison

| Record | Answers | Retention | Covers changes made outside the pipeline |
| --- | --- | --- | --- |
| Git history | Who authored and approved the intended change, and why | Repository lifetime | No |
| CloudTrail | Which identity called which API, when, from where | 90 days in event history, longer in a trail | Yes |
| AWS Config timeline | What the resource configuration was at any point | As configured | Yes |
| CloudFormation stack events | What the stack operation did and whether it failed | Stack lifetime | No |
| Drift detection | Where live state no longer matches the template | Point in time, on demand | Detects them, does not attribute |
| Resource tags with commit SHA | Which commit produced this resource | Resource lifetime | No |

## What gets tested

- **CI credentials.** OIDC federation to an IAM role with a trust policy scoped by repository and branch, never an IAM user with long-lived access keys stored in the CI system.
- **Least privilege on deployment.** A CloudFormation service role, or a scoped deploy role with a permissions boundary, so the pipeline principal does not itself hold the resource permissions.
- **Attribution through role chaining.** `sts:SourceIdentity` is the answer when a scenario requires the original human identity to remain visible in CloudTrail across assumed roles, since the session name alone can be set by the assuming principal.
- **Separation of duties.** Author, approver, and deployer as distinct identities, enforced by branch protection and a manual approval action for production.
- **Correlating an incident to a change.** Resource tags carrying the commit SHA, plus CloudTrail for the API call and Config for the configuration timeline. Git alone cannot prove what was deployed.
- **Secrets in history.** Rotate the credential. Rewriting history or deleting the file is not remediation.
- **Rollback reality.** Reverting a commit and redeploying is a new change with its own risk, and stateful resources may be replaced rather than restored. Change sets exist to surface exactly that before it happens.
- **Artifact integrity.** S3 versioning, KMS encryption, and restrictive policies on the artifact bucket, since a pipeline artifact store is a direct path to production.
- **Detecting out-of-band change.** Drift detection and Config, not the repository, because Git has no visibility into console activity.
- **CodeCommit availability.** Recognize that new designs do not start from CodeCommit.

## Limitations

- Git records intent, not reality. It proves what was approved, never what is currently running, which is why drift detection and Config are not optional companions.
- History is permanent in both directions. It preserves the audit trail and it preserves leaked secrets.
- Branch protection is only as strong as its bypass rules, and administrator override is the most common quiet exception.
- The pipeline identity is frequently the most privileged principal in the account and the least reviewed, since it needs broad permissions to deploy everything.
- Review quality is unmeasurable. An approved pull request proves someone clicked approve, not that anyone understood the IAM diff.
- Reverting infrastructure is not symmetrical with reverting code. Deletions, replacements, and data loss make rollback a decision rather than a button.
- None of this constrains the console. Everything in this module is bypassed by an administrator making a change directly, which is why organization-level guardrails remain the backstop.
- Version control provides evidence and process, not enforcement. It does not prevent a bad configuration, it records who agreed to it.