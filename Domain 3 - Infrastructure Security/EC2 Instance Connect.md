# EC2 Instance Connect

EC2 Instance Connect (EIC) is a way to SSH into EC2 instances without long-lived key pairs. On each connection it generates a one-time SSH key, pushes the public key to the instance through the AWS API where it stays valid for about 60 seconds, and lets IAM decide who is allowed to connect. You drive it from the browser console or the CLI. A companion resource, the EC2 Instance Connect Endpoint, extends this to instances in private subnets with no public IP and no bastion host.

For infrastructure security EIC replaces two liabilities at once: the sprawl of distributed .pem keys and the bastion host sitting on a public subnet. The thing to hold onto: access is gated by IAM and by security groups, the keys are ephemeral, and every connection is logged in CloudTrail, so you get identity-based, audited, keyless SSH with no standing credentials and, with the endpoint, no internet exposure.

## How it works

- **Ephemeral keys**: each connection generates a one-time SSH key pair and pushes the public key to the instance with the SendSSHPublicKey API, valid for roughly 60 seconds. Nothing long-lived is stored or distributed.
- **IAM authorization**: the right to connect is an IAM action, ec2-instance-connect:SendSSHPublicKey (and ec2-instance-connect:OpenTunnel for the endpoint). Scope it by instance tags, and restrict the target OS user with the ec2:osuser condition.
- **The agent**: base EIC needs the ec2-instance-connect package on the instance, which is preinstalled on recent Amazon Linux and Ubuntu images.
- **EC2 Instance Connect Endpoint (EICE)**: a tunnel resource you create in a subnet that reaches instances privately, with no public IP, no bastion, and no internet gateway or NAT. It supports SSH and RDP (any TCP through open-tunnel), and all traffic stays on the AWS network.
- **Two security groups with the endpoint**: the endpoint has its own security group, and the instance's security group must allow SSH or RDP from the endpoint's group. IAM says who, the security groups say what path.
- **Auditing**: SendSSHPublicKey and OpenTunnel are logged in CloudTrail with the user, time, client IP, and target instance, so you get an SSH access trail without building key logging.

## EC2 Instance Connect vs sibling access options

| | EC2 Instance Connect (plus Endpoint) | Session Manager (SSM) | Bastion host | Key-pair SSH |
|---|---|---|---|---|
| Auth | IAM plus ephemeral SSH keys | IAM plus SSM agent | SSH keys | Long-lived key pair |
| Inbound port 22? | Yes, but only from the endpoint SG (none from internet with EICE) | None | Yes, to the bastion | Yes |
| Private subnet, no bastion? | Yes, via EIC Endpoint | Yes, via SSM endpoints | N/A (it is the bastion) | No |
| Audit | CloudTrail (SendSSHPublicKey, OpenTunnel) | CloudTrail plus full session logs to S3 / CloudWatch | Whatever you build | None at the AWS layer |
| Best for | Real SSH, SCP, port forwarding, keyless, no bastion | Keyless shell and automation, zero inbound | Legacy pattern | Avoid at scale |

## What gets tested

- EIC provides keyless SSH: it pushes a one-time SSH public key to the instance via SendSSHPublicKey, valid about 60 seconds, with IAM controlling who can connect. No long-lived key pairs.
- Distinguish EC2 Instance Connect (the keyless-SSH feature, needs the EIC agent and a network path to port 22) from the EC2 Instance Connect Endpoint (a tunnel resource that reaches instances in private subnets with no public IP, no bastion, no internet gateway or NAT).
- Access is gated by IAM (SendSSHPublicKey, and OpenTunnel for the endpoint) and by security groups, and both must allow. You can scope IAM by instance tags and by OS user.
- Every connection is logged in CloudTrail (SendSSHPublicKey, OpenTunnel), giving user, time, client IP, and target instance without you building SSH logging.
- With the endpoint, the instance security group allows SSH or RDP from the endpoint's security group, and traffic never leaves the AWS network, so there is no inbound from the internet.
- Compare to Session Manager, which needs no open port 22 at all and logs full session content. Pick EIC when you need real SSH (SCP, port forwarding); pick Session Manager for keyless shell with zero inbound.

## Limitations

- Base EIC needs the ec2-instance-connect package on the AMI, preinstalled on recent Amazon Linux and Ubuntu but not on every image.
- EIC still uses SSH on port 22 (or RDP on 3389). It narrows who can reach the port, but the protocol path exists. Session Manager opens no inbound port at all.
- Keys are short-lived, so this is interactive access, not a way to hand out standing credentials.
- The endpoint is created per subnet, adds its own security group to manage, and you pay for data transfer through it.
- A broad SendSSHPublicKey or OpenTunnel grant (for example Resource *) over-grants SSH. Scope by tags and OS user.
- It controls the connection, not what the user can do once on the host. Host-level user and sudo management is still yours.