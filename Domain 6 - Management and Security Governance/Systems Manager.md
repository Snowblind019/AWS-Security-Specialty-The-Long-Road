# AWS Systems Manager

Systems Manager is a collection of capabilities for operating managed nodes, and its security significance is that it inverts the access model. Nothing connects inbound. The SSM Agent on each node authenticates with an instance profile and reaches out over HTTPS, so administrative access, command execution, patching, and configuration enforcement all happen without a public IP, an open port 22 or 3389, a bastion host, or a distributed SSH key. Access becomes an IAM decision rather than a network one, which means it can be scoped by tag, conditioned on source VPC or MFA, revoked instantly, and logged with attribution to a named principal. It also carries the corresponding risk: a principal with broad Run Command or Session Manager permissions has root on the fleet without ever touching the network, which makes SSM permissions among the most sensitive in an account. The thing to hold onto: SSM converts server access from a network control problem into an IAM and logging problem, which is an improvement only if the IAM and logging are done properly.

## How it works

**The agent plus an instance profile plus a network path.** A node becomes managed when the SSM Agent runs, the instance profile grants `AmazonSSMManagedInstanceCore` or equivalent, and the agent can reach the Systems Manager endpoints. In a private subnet with no NAT, that means interface VPC endpoints for `ssm`, `ssmmessages`, and `ec2messages`, plus `kms`, `logs`, and an S3 gateway endpoint if session encryption and logging are used. Default Host Management Configuration can manage EC2 instances without an instance profile, and hybrid activations extend management to on-premises and other-cloud servers.

**Session Manager replaces SSH and RDP.** Sessions are brokered by AWS, encrypted in transit, and optionally encrypted with a KMS key. Logging to CloudWatch Logs or S3 captures session output, session preferences are held in a document that can enforce logging and KMS for everyone, and Run As maps a session to a specific local user rather than defaulting to a privileged one. Port forwarding and SSH tunneling over Session Manager cover cases that need a real socket.

**Session access is scoped with IAM conditions.** Tag-based conditions on the target instance restrict who may connect to what. `ssm:SessionDocumentAccessCheck` prevents a user from starting a session with an arbitrary document that would bypass the configured preferences. Conditions on source VPC endpoint, source IP, and MFA presence apply as normal.

**Run Command and Automation are the execution surfaces.** Run Command executes a document against a target set defined by instance IDs, tags, or a resource group. Automation runbooks perform multi-step workflows and are the execution engine behind Config auto-remediation and Security Hub custom actions. Both assume roles, so the effective permissions of an automation are those of its role, not the invoker.

**Patch Manager enforces the patching baseline.** Patch baselines define approval rules and exceptions, patch groups associate nodes to baselines through a tag, maintenance windows schedule the work, and patch policies simplify org-wide rollout. Compliance results feed Systems Manager Compliance and can surface in Config and Security Hub.

**State Manager and Inventory hold configuration steady and visible.** Associations enforce desired state on a schedule, Inventory collects installed packages, users, network configuration, and more, which is what makes fleet-wide questions answerable during an incident.

**Parameter Store is configuration storage with an encryption option.** `SecureString` parameters are encrypted with KMS and are available in the standard tier, not just advanced. The advanced tier buys larger values, a higher parameter count, and parameter policies such as expiration and change notification. Access is scoped by parameter path and by IAM conditions, and reads are logged in CloudTrail alongside the KMS decrypt.

**Parameter Store versus Secrets Manager.** Secrets Manager provides managed rotation with Lambda, resource-based policies for cross-account access, and cross-Region replication, at a per-secret cost. Parameter Store provides versioning and KMS encryption with no rotation framework and no resource policy. Database credentials and anything requiring rotation belong in Secrets Manager; configuration values, flags, and AMI IDs belong in Parameter Store.

**Everything is logged.** CloudTrail records `StartSession`, `TerminateSession`, `SendCommand`, `StartAutomationExecution`, `GetParameter`, and the rest, which makes EventBridge rules on sensitive SSM actions a practical detection control.

## Comparison

| Access method | Inbound port required | Credential to manage | Native session logging | Works without public IP or NAT |
| --- | --- | --- | --- | --- |
| Session Manager | None | None, IAM only | Yes, CloudWatch Logs or S3 | Yes, with interface VPC endpoints |
| Bastion host with SSH | Yes, on the bastion | SSH keys | No, requires host-side tooling | Bastion needs reachability |
| EC2 Instance Connect | Yes, port 22 | Ephemeral keys via IAM | No | No |
| EC2 Instance Connect Endpoint | None from the internet | Ephemeral keys via IAM | Connection logs only | Yes |
| Direct SSH over VPN or Direct Connect | Yes, from the private network | SSH keys | No | Yes, private path |

## What gets tested

- **Private subnet connectivity.** A managed node in a private subnet with no NAT requires interface endpoints for `ssm`, `ssmmessages`, and `ec2messages`. An instance that does not appear as managed is almost always missing one of the endpoint, the agent, or the instance profile.
- **Session Manager over bastions.** Any scenario requiring administrative access with no open ports, no key management, and full auditability resolves to Session Manager with logging to CloudWatch Logs or S3.
- **Enforcing session logging.** Configure session preferences with logging and a KMS key, and use `ssm:SessionDocumentAccessCheck` to stop users from starting sessions with their own document, which is the bypass the condition key exists to close.
- **Scoping who can reach which instance.** IAM conditions on instance tags, not security groups, because there is no network path to restrict.
- **Parameter Store versus Secrets Manager.** Rotation, cross-account resource policies, and cross-Region replication mean Secrets Manager. Cost-sensitive configuration storage with KMS encryption means Parameter Store with `SecureString`.
- **Automation as the remediation engine.** Config rules remediate through SSM Automation documents, and Security Hub custom actions invoke them through EventBridge. Recognize Automation as the executor rather than Lambda when a managed document exists.
- **Patch compliance.** Patch baselines plus patch groups plus maintenance windows, reported into Systems Manager Compliance and Security Hub. Inspector finds vulnerabilities; Patch Manager fixes them.
- **Detecting unmanaged or tampered nodes.** The Config rule for instances managed by Systems Manager, plus Inventory, identifies hosts that dropped off the agent.
- **Hybrid and on-premises.** Hybrid activations bring non-EC2 servers under the same IAM-controlled access and patching model.
- **Least privilege on SSM itself.** `ssm:SendCommand` and `ssm:StartSession` on `*` is effectively fleet-wide root. Correct answers scope by resource ARN and tag.

## Limitations

- Depends on the agent. A node with a stopped, outdated, or removed agent is unmanaged and invisible to Session Manager, Patch Manager, and Inventory, and detecting that is a separate control.
- Network prerequisites are non-trivial in private architectures, and the endpoint set is easy to get partially wrong, which produces nodes that are managed for some capabilities and not others.
- Session logging captures terminal output, not intent. It is strong evidence and weak prevention, and interactive shells still allow anything the local user can do.
- Broad SSM permissions are equivalent to administrative access on every targeted host, and they are frequently granted more loosely than the equivalent SSH access would be.
- Automation runbooks execute with their own role, so a permissive automation role is a privilege escalation path for anyone who can start the automation.
- Parameter Store has no rotation, no resource-based policy, and standard-tier throughput limits that surface under load.
- Patch Manager applies vendor patches on a schedule; it does not validate that the patch fixed anything, and Inspector findings remain the measure of vulnerability state.
- Systems Manager is Regional and per account, so fleet-wide operations across an organization require delegated administration or per-account orchestration.