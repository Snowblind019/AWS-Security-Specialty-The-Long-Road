# Secure Defaults in AWS

A secure default means the safe outcome is what you get when nobody makes a decision. It matters because the failure mode in cloud environments is almost never a deliberate insecure choice, it is an omission: the encryption box nobody checked at 2am, the logging that was going to be enabled later, the public IP that came along with the default subnet. AWS has moved a number of defaults in the right direction, notably S3 Block Public Access and disabled ACLs on new buckets and default object encryption, but the surface is uneven and several consequential settings still default to off. Knowing which is which is only half the work. The other half is that a default you rely on is not a control, because anyone can change it, which is why the real discipline is overriding weak defaults centrally and pinning good ones so they cannot be undone. The thing to hold onto: a secure default protects you from forgetting, an enforced control protects you from someone choosing otherwise.

## How it works

**Know the actual defaults, because the exam and real audits both test the exceptions.**

| Setting | Default state | Secure by default |
| --- | --- | --- |
| S3 Block Public Access on new buckets | Enabled | Yes |
| S3 object ownership and ACLs on new buckets | ACLs disabled, bucket owner enforced | Yes |
| S3 default encryption | SSE-S3 applied to all objects | Yes |
| New custom security group | No inbound, all outbound allowed | Inbound yes, outbound no |
| Default VPC security group | Inbound from itself, all outbound | Partially |
| IAM users and roles | No permissions | Yes |
| DynamoDB encryption at rest | Always on, AWS owned key | Yes |
| Secrets Manager and SQS encryption | Enabled with an AWS managed key | Yes |
| CloudWatch Logs encryption | Service-managed encryption, CMK opt-in | Partially |
| CloudTrail trail | No trail created, only 90-day event history | No |
| CloudTrail data events | Not logged | No |
| EBS encryption by default | Off, per account and Region setting | No |
| RDS encryption at rest | Off unless selected at creation | No |
| KMS customer managed key rotation | Off, opt-in | No |
| Auto-assign public IPv4 in default subnets | On | No |
| Public access to AMIs and EBS snapshots | Not blocked unless enabled | No |
| Session Manager session logging | Off | No |
| VPC Flow Logs | Off | No |
| CloudFront viewer protocol policy | HTTP and HTTPS allowed | No |
| GuardDuty, Security Hub, Config, Macie, Inspector | Off | No |

**Account-level settings flip a weak default once for everything after.** EBS encryption by default, S3 Block Public Access at the account level, instance metadata defaults requiring IMDSv2, block public access for AMIs and snapshots, and VPC Block Public Access are per-account, per-Region toggles rather than per-resource choices. These are the highest-leverage fixes available because they require no policy evaluation and no scanning.

**Declarative policies make those settings permanent across the organization.** Pinning IMDSv2, allowed AMI sources, snapshot public access blocking, and VPC Block Public Access at an OU means the setting holds regardless of who tries to change it and regardless of new API paths.

**SCPs deny the insecure creation path where a condition key exists.** Denying `rds:CreateDBInstance` unless `rds:StorageEncrypted` is true, denying `ec2:RunInstances` when a public IP is requested, denying object writes that do not carry the expected encryption header. This is precise but only as complete as the available condition keys.

**Config rules and conformance packs catch what nothing prevented.** Paired with SSM Automation remediation, they close the loop for resources created before enforcement or through a path the guardrails missed. CIS and PCI conformance packs are effectively pre-packaged inventories of weak defaults.

**Launch templates, hardened AMIs, and IaC modules relocate the default.** If the only way teams provision is a launch template with encryption on, no public IP, IMDSv2 required, and an instance profile attached, the organization's effective default is that template regardless of what the service default is. Service Catalog makes this binding when direct API access is denied.

**Control Tower and organization services set the detection defaults.** An organization trail, delegated administrator auto-enable for GuardDuty and Security Hub, and an organization Config aggregator mean logging and detection are on in every account including future ones, which addresses the largest block of insecure-by-default items in one move.

## Comparison

| Layer | Applies to | Overridable by a builder | Covers resources created before it | Best for |
| --- | --- | --- | --- | --- |
| Account-level setting | Everything in that account and Region | Yes, by anyone with the permission | No | Flipping a weak default cheaply |
| Declarative policy | Every account in scope | No | No | Making the flipped default permanent |
| SCP or RCP | Every API call in scope | No | No | Denying an insecure creation path |
| Config rule with remediation | Live resources | Only by disabling the rule | Yes | Existing fleet and drift |
| Launch template, AMI, IaC module | Resources provisioned that way | Yes, by not using it | No | Making the safe path the easy path |
| Service Catalog | Provisioning requests | No, if direct API is denied | No | Self-service within approved patterns |

## What gets tested

- **Which defaults are actually secure.** New S3 buckets block public access and disable ACLs, and objects are encrypted. RDS encryption, EBS encryption by default, KMS key rotation, CloudTrail trails, and flow logs are not on by default. Questions rely on candidates assuming more is automatic than is.
- **Encryption cannot be added to an existing RDS instance.** An unencrypted instance must be snapshotted, the snapshot copied with encryption, and restored. This is the standard remediation chain and a favored distractor target.
- **Account-level over per-resource.** When the requirement is that all new volumes are encrypted, the answer is EBS encryption by default for the account and Region, not a Config rule and not tagging.
- **Account-level S3 Block Public Access overrides bucket policies and ACLs**, which is why it beats any detective answer when a scenario describes buckets repeatedly being made public.
- **Pinning versus flipping.** If the scenario says the setting keeps getting changed back, the answer moves from an account setting to a declarative policy or an SCP.
- **IMDSv2.** Enforce with the account metadata default, a launch template, a declarative policy, or an SCP condition on `ec2:MetadataHttpTokens`. Detecting existing offenders is a Config rule.
- **Existing resources.** Prevention never fixes what already exists. Complete answers pair a preventive control for the future with Config remediation for the current fleet.
- **Default VPC exposure.** Default subnets auto-assign public IPv4 addresses. Scenarios about unexpectedly reachable instances often trace to the default VPC rather than to a security group.
- **Detection defaults.** GuardDuty, Security Hub, Config, and CloudTrail data events are off until enabled, and the scalable answer is delegated administrator auto-enable across the organization.

## Limitations

- Defaults change over time and vary by Region, service, and console workflow. Institutional knowledge of "the default is secure" ages badly and should be verified rather than assumed.
- A default is not a guarantee. Anyone with the relevant permission can change it, so relying on defaults without an enforcement layer means relying on nobody making a change.
- Account-level settings are per Region, so a Region nobody uses is a Region where the weak default still applies. This is one reason Region restriction is a prerequisite for coherent baselines.
- Preventive controls apply only forward. Every enforcement decision leaves an existing population that needs separate remediation, sometimes destructively, as with RDS encryption.
- Condition key coverage is incomplete, so some insecure defaults simply cannot be denied at the API and must be handled with proactive checks or detection.
- Hardened templates and modules are conventions unless something denies the alternative path, and the console remains the alternative path.
- Secure defaults reduce accidental exposure only. They do nothing about deliberate misuse by an authorized principal, application flaws, or credential compromise.