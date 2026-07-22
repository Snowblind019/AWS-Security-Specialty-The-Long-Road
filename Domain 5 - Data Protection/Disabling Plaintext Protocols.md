# Disabling Plaintext Protocols (FTP, Telnet, HTTP)

Plaintext protocols move credentials and data over the wire with no encryption, so anyone in the traffic path can read, alter, or replay them. FTP (21), Telnet (23), unencrypted HTTP (80), and bare SMTP (25) are the usual offenders, and each has an encrypted replacement (SFTP/FTPS, SSH or Session Manager, HTTPS with TLS 1.2+, SMTP with STARTTLS). In AWS the work is partly network-level (deny the ports at security groups and NACLs) and partly policy-level (force encrypted transport where a port block does not reach, above all S3). The thing to hold onto: blocking the port stops the protocol at the network edge, but for managed services like S3 the real enforcement is a bucket policy denying requests where `aws:SecureTransport` is false, and redirect-to-HTTPS at the ALB or CloudFront closes the client-side gap.

## How it works

- **Deny the ports at security groups and NACLs.** Security groups (stateful, per-ENI) deny inbound and outbound on 21, 23, and 80 for the workloads that should never speak them, and NACLs (stateless, per-subnet) give a broader subnet-level backstop. This removes the plaintext path at the network layer.
- **Force HTTPS on S3 with `aws:SecureTransport`.** A port block does not apply to S3, so the control is a bucket policy that denies any request where `aws:SecureTransport` is false. This is global: it applies to console, CLI, SDK, and every tool, and it is the single most tested S3 in-transit control.
- **Redirect HTTP to HTTPS at the edge.** Set the ALB port 80 listener to redirect to 443, and set the CloudFront viewer protocol policy to HTTPS-only or redirect-HTTP-to-HTTPS, so a client cannot complete a plaintext connection even if it tries.
- **Replace Telnet and prefer keyless shell.** Block port 23 and, where possible, avoid inbound SSH (22) entirely by using SSM Session Manager, which gives IAM-gated, logged, zero-inbound shell access with CloudTrail session records.
- **Root out FTP.** Port 21 open on an EC2 instance means legacy `vsftpd`/`proftpd`. Remove the package and migrate transfers to SFTP/SCP (SSH-based) or HTTPS with signed URLs.
- **Detect and alarm on legacy ports.** VPC Flow Logs surface connections on 21, 23, and 80 for CloudWatch alarms, and GuardDuty flags unusual ports and traffic to known-bad hosts. This catches drift and backdoors after the initial cleanup.

## Enforcement by surface

| Surface | Plaintext risk | Enforcement |
|---|---|---|
| **EC2 admin access** | Telnet (23) | Block 23, use SSH or SSM Session Manager |
| **EC2 file transfer** | FTP (21) | Remove FTP daemon, use SFTP/SCP/HTTPS |
| **Web / API front door** | HTTP (80) | ALB or CloudFront redirect to HTTPS |
| **S3 access** | `http://` requests | Bucket policy deny on `aws:SecureTransport=false` |
| **Email transport** | Bare SMTP (25) | Enforce STARTTLS |
| **Detection** | Any legacy port | VPC Flow Logs alarms plus GuardDuty |

## What gets tested

- **S3 in-transit enforcement is `aws:SecureTransport`.** The correct answer for "require encryption in transit to a bucket" is a bucket policy denying requests where `aws:SecureTransport` is false, not a security group (which does not apply to S3) and not just enabling TLS on clients.
- **Port block vs policy.** Network-reachable services (EC2 protocols) are handled by security groups and NACLs. Managed services (S3) need policy conditions. Mixing these up is a common distractor.
- **Redirect vs deny at the edge.** ALB listener redirect and CloudFront HTTPS-only/redirect are how you stop clients connecting over HTTP to your front door. Deny is for ports you never want, redirect is for the web path you want upgraded.
- **Session Manager over Telnet/SSH.** When the goal is removing inbound plaintext admin access and getting logged, IAM-gated access, Session Manager beats both Telnet and open SSH.
- **STARTTLS for SMTP.** Securing email transport is STARTTLS on 25 (or submission over 587/465), not simply blocking mail.

## Limitations

- Security groups and NACLs cannot enforce transport encryption on S3 or other managed API endpoints. Those require policy conditions like `aws:SecureTransport`.
- A `aws:SecureTransport` deny protects transport only. It does not encrypt the object at rest, and it does not stop a TLS-using but otherwise unauthorized caller, so it layers with SSE and IAM, it does not replace them.
- Redirecting HTTP to HTTPS still exposes the initial plaintext request line before the upgrade, so for the strictest cases HTTPS-only (reject, not redirect) is preferable to redirect.
- Blocking ports does not remove installed plaintext daemons. A reopened port or a rule change re-exposes them, so removing the FTP/Telnet software is the durable fix.
- STARTTLS is opportunistic and can be stripped by an active MITM unless enforced, so for regulated mail flows you want enforced TLS, not just STARTTLS availability.
- Detection via Flow Logs and GuardDuty is after the fact. It catches drift but does not by itself prevent a plaintext connection, so it complements the preventive controls rather than replacing them.