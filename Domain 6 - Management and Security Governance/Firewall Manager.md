# AWS Firewall Manager

AWS Firewall Manager centrally defines protection policies and pushes them across every account, Region, and VPC in an organization, then keeps them applied. It creates and owns the underlying resources, so a Web ACL, a Network Firewall endpoint, a DNS Firewall rule group association, or a replicated security group exists because a policy says it must, and reappears if someone deletes it. The security problem it solves is coverage rather than capability: WAF, Shield Advanced, Network Firewall, and DNS Firewall are all perfectly good on their own, and all of them are useless on the one load balancer a team stood up last week in an account nobody is watching. Firewall Manager makes protection a property of the organization scope and the resource tag rather than of an engineer's memory, and it applies automatically to accounts and resources created after the policy was written. The thing to hold onto: Config tells you a resource is unprotected, Firewall Manager makes it protected and keeps it that way.

## How it works

**Three prerequisites, all commonly tested.** AWS Organizations with all features enabled, AWS Config enabled in every account and Region in scope, and a designated Firewall Manager administrator account registered from the management account. Config is not optional: Firewall Manager depends on it to discover and evaluate resources, so a policy showing no in-scope resources usually means Config is off somewhere.

**Administration is delegated and can be partitioned.** The recommended pattern is a dedicated security tooling account rather than the management account. Multiple administrators are supported, each given an administrative scope limited to specific accounts, OUs, Regions, or policy types, which lets a network team own Network Firewall while an application security team owns WAF.

**Policy scope is expressed three ways.** By organizational unit or explicit account include and exclude lists, by resource type, and by resource tags including exclusion tags. This combination is what allows "all ALBs in the Prod OU except those tagged for a known exception" to be a single policy.

**Policy types cover distinct protections.**

- **AWS WAF.** Associates a managed Web ACL with ALBs, API Gateway stages, CloudFront distributions, AppSync, Cognito user pools, and App Runner. Policies define first and last rule groups, leaving a middle section accounts may populate with their own rules, and can retrofit existing Web ACLs rather than replacing them.
- **Shield Advanced.** Enrolls in-scope resources into Shield Advanced protection organization-wide, which is otherwise a per-resource action nobody performs consistently.
- **Security group policies, in three distinct forms.** A common security group policy replicates a primary group into member accounts and associates it with in-scope resources. A content audit policy evaluates existing rules against allowed or denied rule sets, or against FMS managed audit rule groups, and flags or removes violations such as unrestricted access on 22 or 3389. A usage audit policy finds unused and redundant security groups and can delete them.
- **AWS Network Firewall.** Deploys firewall endpoints and rule groups, in a distributed model with endpoints per VPC, a centralized model routing through an inspection VPC, or by importing existing firewalls.
- **Route 53 Resolver DNS Firewall.** Associates rule groups with VPCs to block command and control domains, domain generation algorithm patterns, and other threat intelligence lists.
- **Network ACL policies.** Manage and enforce network ACL entries across accounts.
- **Third-party firewalls.** Palo Alto Cloud NGFW and Fortigate CNF deployed through the same policy mechanism.

**Remediation is a per-policy switch.** Automatic remediation makes Firewall Manager create, associate, and restore protections, and revert non-compliant changes. Without it the policy is monitor only and produces compliance findings but changes nothing. Expect scenarios that hinge on which mode was chosen.

**Drift is self-healing when remediation is on.** Deleting a Firewall Manager managed Web ACL or detaching it causes Firewall Manager to restore the association on its next evaluation. Resource cleanup, if enabled, removes protections from resources that fall out of scope.

**Findings integrate outward.** Compliance status is available in the Firewall Manager dashboard, can be published to AWS Security Hub, and can drive SNS notifications and EventBridge automation.

**Region behavior matters.** Policies are created per Region and evaluate resources in that Region. Global resources, meaning CloudFront distributions and Shield Advanced protections for global accelerators and CloudFront, are managed from us-east-1.

## Comparison

| Service | Role | Deploys protections | Auto-covers new accounts and resources | Scope |
| --- | --- | --- | --- | --- |
| AWS Firewall Manager | Central enforcement of network and edge protections | Yes, creates and restores them | Yes | Organization, by OU, tag, resource type |
| AWS Config | Detects non-compliant configuration, can remediate via SSM | No, evaluates only | Yes, if recorders are deployed | Per account and Region, aggregatable |
| Security Hub | Aggregates and scores findings | No | Yes | Organization, reporting only |
| Service control policies | Denies API actions | No | Yes | Organization, permission ceiling |
| AWS Control Tower | Landing zone baseline and OU-scoped controls | Only the controls it defines | Yes | Organization structure |
| WAF, Shield, Network Firewall directly | The protection itself | Per resource, manually | No | Single account and Region |

## What gets tested

- **The Config prerequisite.** A policy reporting zero in-scope resources, or an account showing as not protected, points to AWS Config not being enabled in that account or Region. This is the most common Firewall Manager troubleshooting question.
- **Firewall Manager versus Config.** "Detect security groups allowing 0.0.0.0/0 on 22" can be either. "Ensure they are corrected automatically across all accounts including future ones" is Firewall Manager with a content audit policy and automatic remediation.
- **Firewall Manager versus SCP.** SCPs cannot create a Web ACL or attach a firewall. Any requirement to apply a protection rather than deny an action is Firewall Manager.
- **Automatic coverage of new resources.** Wording such as "any new ALB must immediately be protected" is the signature of a Firewall Manager policy rather than a pipeline check or a Config remediation.
- **The three security group policy types.** Know which one replicates a group, which one audits rules, and which one cleans up unused groups. Questions test the distinction directly.
- **Deployment models for Network Firewall.** Centralized inspection VPC versus distributed per-VPC endpoints is a cost and blast-radius tradeoff that appears in architecture scenarios.
- **Global resources.** CloudFront and global Shield protections are managed from us-east-1. Answers that create the policy in the workload Region are wrong for those resource types.
- **Delegated administrator.** Register a dedicated security account, not the management account, and use administrative scope when different teams own different policy types.
- **Monitor versus remediate.** If the scenario says teams need time to review before enforcement, the answer is a monitor-only policy first, then enabling remediation.
- **Cost.** Firewall Manager itself carries no charge. The orchestrated services do, and Shield Advanced in particular is a substantial fixed organizational commitment, which is often the reason a scenario limits its scope.

## Limitations

- Hard dependency on AWS Config across the estate, which brings its own recording cost and its own deployment problem.
- Supports a fixed set of policy types and resource types. Protections outside that list are not centrally enforceable this way.
- Policies are Regional, so organization-wide coverage means a policy per governed Region plus us-east-1 for global resources.
- Automatic remediation is powerful and blunt. Replacing or reverting security group rules and deleting unused groups can break workloads, which is why monitor-only exists as a first phase.
- Firewall Manager owns the resources it creates. Local teams editing them directly will see changes reverted, which is the intended behavior but a real operational friction point.
- Evaluation is periodic rather than instantaneous, so there is a window between a resource appearing and the protection being applied.
- It deploys and enforces protections, it does not inspect traffic itself and it does not tune rules. A badly configured Web ACL enforced everywhere is still a badly configured Web ACL.
- It does nothing for identity, data protection, or host-level security. It is the network and edge enforcement layer only.