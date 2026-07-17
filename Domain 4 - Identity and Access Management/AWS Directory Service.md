# AWS Directory Service

AWS Directory Service is a family of managed directory offerings that give AWS workloads and services a directory to authenticate against, without you standing up and babysitting domain controllers. It is not one product but three distinct options that differ sharply in what they actually are: a real managed Microsoft Active Directory, a proxy to your existing on-prem AD, or a small Samba-based standalone directory. On the SCS exam it is rarely about "how do I run a directory" and almost always about picking the right one for a scenario and understanding where the credentials live, whether on-prem trust is possible, and how MFA and encryption are enforced. The thing to hold onto: the three flavors trade off between real AD features, keeping identity on-prem, and cost, and the exam tests whether you can map a scenario to the correct one.

## How it works

- **AWS Managed Microsoft AD** runs actual Windows Server Active Directory managed by AWS. You get real domain controllers deployed across two AZs in your VPC, with Kerberos, LDAP/LDAPS, Group Policy, schema extension, and fine-grained password policies. It supports one-way and two-way forest trusts with on-prem AD, so users can stay in the on-prem forest while accessing AWS-side resources.
- **AD Connector** stores no directory in AWS. It is a stateless proxy that forwards authentication requests over your VPN or Direct Connect link to on-prem AD. Credentials are validated on-prem and never copied to the cloud, which is the whole point when compliance forbids a cloud copy of the directory.
- **Simple AD** is a Samba 4 directory that looks like a small AD but is not Microsoft AD. It is standalone, cheap, and self-contained, with no on-prem dependency, but it lacks trusts, schema extension, and MFA.
- **Domain controllers live in your VPC.** For Managed Microsoft AD and AD Connector you place them in two subnets across two AZs, and security groups govern the DC traffic. Connectivity planning is part of the design.
- **Seamless domain join** lets EC2 instances (Windows and Linux) join the directory automatically through SSM, so workloads authenticate against the directory without manual join steps.
- **Consumers of the directory** include EC2, RDS for SQL Server, Amazon FSx, WorkSpaces, and IAM Identity Center, which can use Managed Microsoft AD or AD Connector as its identity source.

## The three offerings compared

| Dimension | Managed Microsoft AD | AD Connector | Simple AD |
|---|---|---|---|
| What it actually is | Real managed Windows Server AD | Proxy to on-prem AD, no cloud directory | Samba 4 standalone directory |
| Directory data in AWS | Yes | No, stays on-prem | Yes |
| Trust with on-prem AD | Yes (one-way and two-way forest trusts) | N/A (it is the on-prem AD, proxied) | No |
| Schema extension | Yes | No | No |
| MFA | Yes (RADIUS) | Yes (RADIUS) | No |
| Group Policy / real AD features | Full | Uses on-prem AD's | Limited Samba subset |
| Cross-account sharing | Yes (share within Organization) | No | No |
| Typical fit | Need real AD features or on-prem trust for RDS/FSx/WorkSpaces | Reuse existing on-prem AD without storing a copy in AWS | Small, standalone, cost-sensitive, no on-prem tie |

## What gets tested

- **Match the scenario to the flavor.** On-prem trust required, schema extension, or real Microsoft AD features (RDS SQL Server, FSx, WorkSpaces, Group Policy) point to **Managed Microsoft AD**. A requirement to keep the directory on-prem and store no copy in AWS points to **AD Connector**. A small standalone directory with no Microsoft-specific needs points to **Simple AD**.
- **Only Managed Microsoft AD supports trusts.** Any scenario asking for a trust relationship with an existing on-prem forest rules out AD Connector and Simple AD.
- **AD Connector keeps credentials on-prem.** It validates against on-prem AD over the private link and stores nothing in the cloud, which is the answer when the constraint is "no directory data in AWS" or "authentication must happen against the corporate directory."
- **MFA is RADIUS-based, and Simple AD does not support it.** Managed Microsoft AD and AD Connector integrate an external RADIUS/MFA provider. If a scenario needs MFA on a Directory Service directory, Simple AD is wrong.
- **Managed Microsoft AD is a valid identity source for IAM Identity Center.** When the design centralizes SSO across accounts on top of AD, Managed Microsoft AD (or AD Connector fronting on-prem) is the identity source and Identity Center manages permission sets.
- **LDAPS for encryption in transit.** Managed Microsoft AD supports LDAP over SSL, and this is the expected answer for securing directory queries on the wire.
- **Encryption at rest and logging.** Directory data is encrypted, and Managed Microsoft AD can forward security event logs to CloudWatch Logs for monitoring and alerting.

## Limitations

- **You are not Domain Admin on Managed Microsoft AD.** AWS reserves the Enterprise Admin and Domain Admin roles. You get a delegated OU and admin rights scoped to it, cannot log into the DCs, and cannot install arbitrary software on them.
- **AD Connector is only as available as the link.** It stores nothing, so if the VPN or Direct Connect path to on-prem is down, authentication fails outright. It is also sized (small or large) by directory size and cannot extend the on-prem schema.
- **Simple AD is not real AD.** No trusts, no schema extension, no MFA, no fine-grained password policy, and incomplete support for AD-specific tooling and PowerShell cmdlets. It is de-emphasized for anything beyond small, simple, standalone use.
- **Directory controllers consume VPC capacity.** DCs sit in your subnets across two AZs and depend on correct subnet, routing, and security group configuration; misconfigured connectivity is a common failure mode.
- **Cost scales with edition and MFA.** Managed Microsoft AD Standard versus Enterprise Edition, plus any RADIUS/MFA infrastructure, carries real monthly cost, unlike the much cheaper Simple AD.