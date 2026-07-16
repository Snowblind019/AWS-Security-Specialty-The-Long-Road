# SSM Session Manager Logs

**Session Manager** (a capability of AWS Systems Manager) gives keyless, portless, bastion-less interactive shell access to EC2, on-premises, and edge instances through the **SSM Agent** and **IAM**, with no inbound ports, SSH keys, or jump hosts. Its **logging** captures what happened inside each session (commands and full shell output) to **CloudWatch Logs** and/or **S3**, optionally KMS-encrypted. In the exam it is the secure-remote-access answer and the in-session audit trail, and it is the complement to CloudTrail, not a replacement for it.

The mental split is access versus record, and CloudTrail versus session logging. Session Manager replaces SSH and bastions with IAM-gated, encrypted, logged access. **CloudTrail** records that a session was started and by whom. **Session Manager logging** records what was typed and returned inside it. They are two different logs, and you need both for the full picture.

## How it works

- **Access model**: the SSM Agent on the instance, plus an instance profile (typically `AmazonSSMManagedInstanceCore`), makes an outbound TLS connection to Systems Manager. A user starts a session with `ssm:StartSession`. No inbound port 22 or 3389, no SSH keys, no bastion.
- **Logging destinations**: configured in the account and Region-level **Session Manager preferences**: CloudWatch Logs, S3, or both, with optional **KMS encryption of the session data end to end**. Logs capture start and end time, the IAM principal, instance ID, commands, and full shell output when enabled.
- **IAM**: `ssm:StartSession`, `ssm:TerminateSession`, and `ssm:ResumeSession`, scoped by instance tags or by session document. The `ssm:SessionDocumentAccessCheck` condition enforces that a caller may only use session documents they have access to, which is a privilege-escalation guardrail. The instance role also needs permission to write to the log destination.
- **Enforcing logging**: logging is set in the account and Region-level preferences, which apply to every session, so you enforce it there and then restrict who can modify preferences or use custom documents. It is not enforced per session through `SessionDocumentAccessCheck`.
- **Analysis**: CloudWatch Logs Insights over the CloudWatch destination, Athena over the S3 destination, metric filters or Lambda to alert on risky commands, and correlation with CloudTrail, GuardDuty, and Security Hub.
- **Accountability options**: Run As runs the session as a specific OS user, and a restricted session document can allow only specific commands.

## CloudTrail vs Session Manager logging

| Layer | Captures | Destination |
|---|---|---|
| CloudTrail | The API event: session started, resumed, or terminated, by whom, and when | CloudTrail (S3, CloudWatch) |
| Session Manager logging | In-session activity: commands typed and shell output returned | CloudWatch Logs and/or S3 |

## What gets tested

- Session Manager is the keyless, portless, bastion-less secure-access answer. No inbound 22 or 3389, no SSH keys, IAM-gated. That reduced attack surface is the headline benefit and the usual answer to "give admins shell access without opening ports or managing keys."
- CloudTrail versus session logging is the pivot: CloudTrail shows that X started a session at time T, while Session Manager logging shows what was done inside it. To see in-session commands you need session logging, not CloudTrail alone.
- Log destinations are CloudWatch Logs, S3, or both, with optional KMS encryption of session data, all configured in the account and Region-level Session Manager preferences.
- Enforce logging through those preferences (account-wide), not per-session IAM, and restrict who can change preferences and which session documents can be used.
- Prerequisites are the SSM Agent, an instance profile, and log-write permissions. No agent or role means no session and no logs.
- Scope access by instance tags in the IAM policy, and use Run As for per-user OS-level accountability.

## Limitations

- Off by default. You configure the destination, the IAM permissions, and the preferences.
- It only captures Session Manager activity, not SSH, SCP, or RDP done outside it, so restrict those paths to get full coverage.
- Port-forwarding session types have no shell transcript to log. Command and output logging applies to interactive shell sessions.
- Secrets typed into a shell are captured in the transcript. Mitigate with KMS encryption, tight log-access controls, and restricted-command documents.
- It needs the SSM Agent and connectivity to Systems Manager endpoints, which means VPC endpoints when the instance has no internet path.