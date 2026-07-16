# EC2 Image Builder

A managed service that automates building, testing, and distributing hardened, patched machine images, both EC2 AMIs and container images. It runs your build steps on a throwaway EC2 instance using the AWS Task Orchestrator and Executor (AWSTOE), tests the result, and ships it to the accounts and Regions you choose, only if the tests pass.

For infrastructure security it is the golden-image factory, the thing that makes immutable, compliant baselines real. The thing to hold onto: Image Builder produces known-good images from a versioned recipe, applies CIS or STIG hardening components, bakes in OS and package patches, scans for CVEs with Amazon Inspector, and can rebuild automatically when a new critical vulnerability appears. Instead of hand-hardened AMIs that drift, every instance launches from a repeatable, tested, scanned baseline.

## How it works

- **Recipe**: the immutable, versioned definition of an image. A parent (base) image, an ordered list of components, and block device mappings, where you set encrypted EBS with a KMS key. There are image recipes (AMIs) and container recipes (ECR).
- **Components**: the build and test steps, written in AWSTOE YAML: install packages, apply hardening, run validation tests. Use AWS-managed components such as update-linux, CIS Level 1, and STIG hardening, or write your own custom components.
- **Infrastructure configuration**: the EC2 instance Image Builder launches in your account to build and test, with its instance type, subnet, security group, and instance profile. Build in an isolated subnet with a scoped role.
- **Distribution configuration**: where the finished image goes. Which accounts and Regions the AMI is copied to, its launch permissions and tags, or the target ECR repository for containers. Images can be re-encrypted per target with the destination KMS key.
- **Pipeline**: ties the recipe, infrastructure config, and distribution config together with a schedule (cron), a manual run, or an EventBridge trigger. It distributes only if every test passes.
- **Vulnerability scanning**: with Amazon Inspector enabled, the pipeline scans images for OS and language-package CVEs during the build. A Critical or High Inspector finding can fire an EventBridge rule that reruns the pipeline and republishes a freshly hardened image, a continuous remediation loop (ECR enhanced scanning for the container path).
- **Sharing**: share components and recipes across accounts with AWS RAM.

## EC2 Image Builder vs sibling options

| | EC2 Image Builder | Manual AMI (snapshot) | Packer (self-managed) | SSM Patch Manager |
|---|---|---|---|---|
| Model | Automated golden-image pipeline | One-off, click-built | Automated, you run it | Patch running instances |
| Repeatable and versioned | Yes, semantic versions | No | Yes | N/A |
| Built-in hardening and CVE scan | CIS / STIG components plus Inspector | No | You script it | No (patches, not hardens) |
| Distribution | Multi-account, multi-Region | Manual copy | You script it | In place |
| Best for | Immutable, compliant image supply chain | Quick throwaway | Multi-cloud image builds | Keeping live fleets patched |

## What gets tested

- Image Builder automates building, testing, and distributing hardened, patched AMIs and container images. The pipeline is recipe (base image plus components plus block device mappings) plus infrastructure configuration (the build instance) plus distribution configuration (target accounts, Regions, ECR), on a schedule or a trigger. It distributes only if tests pass.
- Hardening: apply AWS-managed CIS Level 1 or STIG hardening components, or start from a Marketplace CIS pre-hardened base image, to get a compliant baseline instead of hand-hardening.
- Patching model: bake updates into the image and redeploy (immutable infrastructure), as opposed to SSM Patch Manager, which patches live instances in place. Know which model a scenario is asking for.
- Vulnerability scanning: Image Builder integrates with Amazon Inspector to scan images for CVEs during the pipeline, and Inspector must be enabled for the account. A Critical or High finding can trigger an EventBridge rebuild for a continuous remediation loop.
- Encryption: use encrypted EBS in the recipe with a KMS key, and re-encrypt per target during distribution.
- Build security: the pipeline builds on an EC2 instance with an instance profile in your account, so scope that role and its subnet. Share components and recipes across accounts with AWS RAM.

## Limitations

- It builds images, it does not patch running instances. Live fleets still need SSM Patch Manager or a redeploy from a new image.
- Builds run on real EC2 instances in your account, which cost money and need a scoped instance profile and network.
- Inspector scanning requires Amazon Inspector enabled for the account, and container CVE gating requires ECR enhanced scanning.
- Golden images go stale. Without a schedule or a CVE-triggered rebuild, a hardened AMI drifts out of compliance as new CVEs land.
- Recipes and components are immutable and versioned, which is good for provenance but means you manage version sprawl.
- Distribution copies AMIs, which consume storage in every target Region and account.