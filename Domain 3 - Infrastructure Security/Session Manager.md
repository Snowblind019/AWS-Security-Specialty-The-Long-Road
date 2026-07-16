# Session Manager

AWS Systems Manager Session Manager gives you secure, interactive shell access to EC2 instances, on-premises servers, and edge devices through a browser or the CLI, with no inbound ports, no SSH keys, and no bastion host. The SSM Agent on the instance makes an outbound connection to the Systems Manager service, which brokers your session, so nothing has to listen for inbound connections. Access is controlled entirely by IAM, and every session can be recorded.

For infrastructure security this is the answer the exam wants for instance access. The thing to hold onto: zero inbound ports (the security group needs no port 22 at all), zero long-lived keys, IAM-gated who-can-connect, and full session recording of every command and its output to S3 or CloudWatch. It removes the SSH keys, the open port, and the bastion in one move, and it leaves a complete audit trail.

## How it works

- **Outbound-only connection**: the SSM Agent connects out over HTTPS 443 to the Systems Manager service, and your client connects to that service. The instance needs no inbound rule. The path is engineer to HTTPS 443 to Session Manager to the agent.
- **Prerequisites**: the SSM Agent installed and running (preinstalled on Amazon Linux and many AMIs) and an instance profile with SSM permissions (AmazonSSMManagedInstanceCore) so the instance registers as a managed node.
- **IAM access control**: ssm:StartSession governs who can connect, scoped by instance tags. This is the entire access model, and there are no keys.
- **Logging and audit**: CloudTrail logs the StartSession call (who, when, target). Session activity logging streams the full terminal input and output to CloudWatch Logs and S3, optionally KMS-encrypted. This session-content recording is the audit differentiator.
- **Encryption**: session data is TLS 1.2 in transit by default, and you can add KMS encryption end to end and on the logs.
- **RunAs and preferences**: sessions run as ssm-user by default, and RunAs pins a specific OS user. Session preferences (logging destinations, KMS, idle timeout, RunAs) are set per account and Region and can be automated org-wide.
- **Port forwarding**: tunnel a local port to a port on the instance, or to a remote host the instance can reach (for example RDS), over the encrypted SSM channel with no inbound port opened, replacing a bastion or VPN for private services.
- **Private access**: for instances without internet, use interface VPC endpoints (ssm, ssmmessages, ec2messages, plus kms, logs, s3 for encryption and logging) to keep traffic on the AWS network.

## Session Manager vs sibling access options

| | Session Manager | EC2 Instance Connect | Bastion host | Key-pair SSH |
|---|---|---|---|---|
| Auth | IAM, SSM agent (outbound only) | IAM, ephemeral SSH keys | SSH keys | Long-lived key pair |
| Inbound port | None | Port 22 (from endpoint SG with EICE) | Port 22 to the bastion | Port 22 |
| Session-content logging | Yes, full to S3 / CloudWatch | No (connection only) | Whatever you build | None |
| Private subnet, no bastion | Yes, via SSM VPC endpoints | Yes, via EIC Endpoint | N/A (it is the bastion) | No |
| Best for | Keyless audited shell, zero inbound, port forwarding | Real SSH (SCP, port forwarding), keyless | Legacy | Avoid |

## What gets tested

- Session Manager gives shell access with no inbound ports, no SSH keys, and no bastion. The SSM Agent makes an outbound HTTPS connection to the service, so the instance security group needs zero inbound rules. Access is IAM-controlled (ssm:StartSession) and can be scoped by instance tags.
- Prerequisites: the SSM Agent installed and running, and an instance profile with SSM permissions (AmazonSSMManagedInstanceCore). For instances without internet, add interface VPC endpoints (ssm, ssmmessages, ec2messages, plus kms, logs, s3 for encryption and logging).
- Full auditability is the differentiator: CloudTrail logs the StartSession call, and session activity logging streams the entire terminal input and output to CloudWatch Logs or S3, optionally KMS-encrypted. That session-content recording is what EC2 Instance Connect does not give you.
- Port forwarding tunnels a local port to a port on the instance, or to a remote host reachable from it such as RDS, over the encrypted SSM channel with no inbound port opened, replacing a bastion or VPN for private services.
- Sessions run as ssm-user by default, and RunAs pins a specific OS user. Session data is TLS 1.2 in transit and can add KMS encryption end to end.
- Pick Session Manager over EC2 Instance Connect when you want zero inbound and full session logging. Pick EIC when you specifically need native SSH such as SCP or SSH-based tooling.

## Limitations

- Needs the SSM Agent and an instance profile with SSM permissions. An instance missing either will not appear as a managed node.
- The agent needs outbound 443 to the SSM endpoints, or VPC endpoints, so a fully isolated instance with neither cannot be reached.
- Not native SSH. SCP and some SSH-only tooling need port forwarding or a proxy config rather than a plain shell, which is where EIC fits better.
- Session logging is opt-in. Without configuring S3 or CloudWatch session logging you only get the CloudTrail StartSession record, not the commands.
- Access control lives in IAM, so a broad ssm:StartSession (Resource *) over-grants shell access to every instance. Scope by tags.
- It controls the connection and OS identity via RunAs, but host-level sudo and user configuration are still yours to manage.