# Module Reuse in IaC

Module reuse means teams consume shared, versioned, parameterized components, Terraform modules, CloudFormation nested stacks and registry modules, CDK constructs, or Service Catalog products, instead of writing resource definitions from scratch each time. The security argument is that a control implemented inside a module is written once, reviewed once, and inherited by every consumer, so a hardened S3 pattern with encryption, Block Public Access, access logging, and a deny-insecure-transport policy stops being something twelve teams each remember or forget. It also compresses remediation: fixing a systemic misconfiguration becomes a module release and a version bump rather than a search across every repository. The tradeoff is concentration. A shared module is a supply chain dependency, and whoever can publish to it can change the security posture of every environment that consumes it. The thing to hold onto: reuse turns your security baseline into a dependency, which makes the module's provenance and version pinning as security-relevant as its contents.

## How it works

**A single authoritative source, with restricted publish rights.** Modules live in a private Terraform registry, AWS CodeArtifact, a Git repository, or the CloudFormation registry. The control that matters is who can publish a version, enforced with protected branches, CODEOWNERS review, and signed commits. Read access is broad, write access is narrow.

**Consumers pin to immutable versions.** Semantic versioning gives intent, but a Git tag can be moved, so a commit SHA or a registry version that cannot be overwritten is the stronger pin. Floating references such as a branch name mean the deployed configuration can change without any commit in the consuming repository, which defeats both change control and audit.

**Secure defaults, and no expressible insecure path.** The strongest module design does not offer a variable that disables encryption or opens a security group to the internet. Where an exception is genuinely required, it is a separate module or a documented variable that a scanner and a reviewer both flag, not a quiet boolean.

**Input validation constrains misuse.** Terraform variable validation blocks, preconditions, and typed inputs reject bad values at plan time rather than producing a resource that scanners must catch later.

**Modules are tested and scanned as artifacts in their own right.** Policy-as-code scanning with Checkov, cfn-guard, or Trivy runs against the module repository, and behavioral tests with Terratest or similar assert that the deployed result actually has the properties claimed. Scanning only the consuming repository misses defects in the component every consumer inherits.

**Provider and dependency versions are pinned too.** The Terraform lock file records provider hashes, and nested module dependencies need the same discipline. An unpinned transitive dependency is the same risk as an unpinned module.

**AWS Service Catalog is the account-boundary version of the pattern.** Products are approved templates published into portfolios, shared across an organization or OU, and launched by users through constraints. A launch constraint lets the product provision with a service role, so consumers can create the resources without holding the underlying permissions themselves. This is the answer whenever a scenario pairs self-service with restricted permissions.

**StackSets distribute the same template rather than the same component.** With Organizations integration and automatic deployment, a StackSet applies a baseline stack to every account in an OU including accounts created later. This complements modules: modules standardize what teams build, StackSets guarantee what every account has.

**CDK adds programmatic enforcement.** Constructs are the reusable unit, and Aspects apply cross-cutting checks across a whole construct tree at synthesis time, which is closer to policy enforcement than to reuse.

**Rollout and deprecation are managed deliberately.** A fix in a module protects nobody until consumers upgrade. Dependency update automation, a minimum-version check in the pipeline, and a Config rule detecting the old pattern in deployed resources are the three mechanisms that make a module release into actual remediation.

## Comparison

| Mechanism | Unit of reuse | Enforces use | Auto-applies to new accounts | Consumer needs underlying permissions |
| --- | --- | --- | --- | --- |
| Terraform module | Parameterized resource group | No, convention only | No | Yes |
| CloudFormation nested stack | Child stack | No | No | Yes, or via stack service role |
| CloudFormation registry module | Reusable resource fragment | No | No | Yes |
| CDK construct with Aspects | Code component plus synthesis checks | Aspects can fail the synth | No | Yes |
| Service Catalog product | Approved, constrained template | Yes, when direct API access is denied | Via portfolio sharing | No, with a launch constraint |
| CloudFormation StackSets | Whole stack per account | Yes, administratively deployed | Yes, with automatic deployment | Not applicable |

## What gets tested

- **Self-service with least privilege.** Teams must provision approved infrastructure without permissions to create the resources directly. The answer is Service Catalog with a launch constraint, not a shared Terraform module.
- **Baseline in every account including future ones.** CloudFormation StackSets with Organizations automatic deployment, or Control Tower for the governance layer. Modules do not self-deploy.
- **Guaranteeing the standard is used.** Modules are a convention and can be bypassed by writing raw resources. Any question phrased as "ensure it cannot be done otherwise" resolves to SCPs, RCPs, declarative policies, or Service Catalog with direct API access denied.
- **Version pinning.** Immutable references over floating branches, and pinned provider versions with a committed lock file. Scenarios describing an unexplained configuration change in an unchanged repository point here.
- **Supply chain integrity.** Restricted publish rights, mandatory review, and signed commits on the module repository. A compromised shared module is the fastest path to organization-wide compromise and is worth recognizing as such.
- **Propagating a fix.** Releasing a fixed module version does not remediate deployed resources. The complete answer includes forcing consumer upgrades and using Config rules to find and remediate existing resources built from the old version.
- **Portfolio sharing.** Sharing Service Catalog portfolios through AWS Organizations rather than per-account copies is the scalable answer.
- **Scanning scope.** Scan the module repository itself, not only the repositories that consume it.

## Limitations

- Reuse is voluntary unless something denies the alternative. A module cannot stop anyone from writing the resource by hand.
- Concentrated risk. One malicious or careless module version reaches every consumer that upgrades, which makes publish permissions among the most sensitive in the estate.
- Over-parameterization erodes the benefit. Every escape hatch added to satisfy an edge case becomes the setting somebody uses to disable a control.
- Version sprawl is normal. Environments end up spread across several module versions, so the security posture is the set of deployed versions, not the latest one in the registry.
- Forking under deadline pressure is common, and a forked copy silently stops receiving fixes while still looking like the standard component.
- Modules encode configuration, not runtime behavior. They cannot address credential misuse, application flaws, or anything that happens after provisioning.
- Deployed resources drift regardless of how the module defined them, so drift detection and Config remain required alongside reuse.