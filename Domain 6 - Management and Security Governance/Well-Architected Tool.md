# AWS Well-Architected Tool

The Well-Architected Tool is a structured self-assessment: you register a workload, answer a set of best-practice questions across the six pillars of the Well-Architected Framework, and the tool identifies high and medium risk issues and generates an improvement plan linked to AWS guidance. Nothing is scanned. No resource is inspected, no API is called against your environment, and no finding is generated from live state. That is not a defect, it is the category. Config and Security Hub answer whether a resource is configured correctly; the Well-Architected Tool answers whether the architecture was designed with the right controls in mind, including things no scanner can observe, such as whether an incident response plan has ever been exercised, whether threat modeling happens, and whether the team knows where its sensitive data is. For security work it functions as a design review record and a due-diligence artifact. The thing to hold onto: this is the only assessment in AWS driven entirely by what humans assert, which makes it the only one that can cover process rather than configuration.

## How it works

**Workloads and lenses define the scope.** A workload represents a system under review. A lens supplies the question set: the Well-Architected Framework lens covers all six pillars, and specialized lenses exist for serverless, SaaS, machine learning, data analytics, financial services, and more, available through the lens catalog.

**Custom lenses encode organization-specific standards.** A security team can author its own question set with its own risk rules and improvement guidance, publish it with versioning, and share it, which is how an internal architecture standard becomes a repeatable review rather than a document.

**Answers produce risk classifications.** Unselected best practices become high or medium risk issues, and the improvement plan lists them in priority order with links to the underlying guidance. Questions can be marked as not applicable with a reason, which keeps the risk count meaningful.

**Milestones are immutable point-in-time snapshots.** Taking a milestone before a launch and again after remediation is what turns a review into evidence of progress rather than a rolling document with no history.

**Profiles and review templates add context and consistency.** A profile captures business context so questions are prioritized appropriately, and review templates let an organization start every review from a standard configuration rather than from scratch.

**Sharing works across accounts and the organization.** Workloads, custom lenses, profiles, and templates can be shared with specific accounts, IAM principals, or, with trusted access enabled, an organization or OU. This is how a central security team reviews workloads it does not own.

**Trusted Advisor context appears inside reviews.** The tool surfaces relevant Trusted Advisor checks alongside questions, which grounds some answers in observed data rather than pure assertion.

**The API makes it programmable.** Reviews, answers, milestones, and lenses are all accessible through the API and SDK, so review status can gate a deployment pipeline and results can be exported into a risk register or ticketing system.

## Comparison

| Tool | Input | What it assesses | Automated | Output |
| --- | --- | --- | --- | --- |
| Well-Architected Tool | Human answers to structured questions | Architecture and process design | No | Risk issues and an improvement plan |
| Security Hub | Live resource state via controls | Current configuration posture | Yes | Findings and a security score |
| AWS Config | Live resource state via rules | Configuration compliance and history | Yes | Compliance evaluations |
| Audit Manager | Collected evidence mapped to controls | Whether controls can be evidenced | Yes, collection | Signed assessment reports |
| AWS Artifact | AWS auditor reports and agreements | AWS's own compliance | Not applicable | Downloadable attestations |
| Trusted Advisor | Fixed AWS-authored checks | Best practice deviations | Yes, periodic | Colour-coded recommendations |

## What gets tested

- **Self-assessment versus automated evaluation.** Any scenario requiring continuous, automatic detection of misconfiguration is Config or Security Hub. The Well-Architected Tool is the answer when the requirement is a structured architectural review or a design-stage risk assessment.
- **Process controls.** Questions about incident response readiness, threat modeling, or team knowledge have no automated equivalent, and the Well-Architected Tool is the only service that captures them.
- **Custom lenses.** When an organization has its own architecture standard that no AWS lens covers, the answer is authoring a custom lens, not writing Config rules, because the subject matter is design rather than resource state.
- **Milestones.** For demonstrating improvement over time or capturing a pre-launch baseline, milestones are the mechanism. They are immutable, which is what gives them evidentiary value.
- **Organization-wide reviews.** Enable trusted access and share workloads and lenses with the organization or an OU, rather than running disconnected per-account reviews.
- **Pipeline gating.** The API allows a review or a milestone to be a prerequisite in a release process, which is the practical way "no major workload launches without a review" is enforced.
- **Not a compliance certification.** It produces no attestation and satisfies no regulator by itself. Audit evidence is Audit Manager, AWS attestations are Artifact.
- **Cost.** The tool is free, so cost never argues against using it.

## Limitations

- Entirely self-reported. Answers reflect what the team believes or is willing to state, and an optimistic review produces a clean result with no relationship to reality.
- No visibility into resources. It cannot detect drift, cannot confirm an asserted control exists, and will happily record that encryption is enforced in an environment where it is not.
- Point in time. A review ages immediately and only regains value when repeated, which makes review cadence the real control.
- Generates no findings, no alerts, and no enforcement. The improvement plan is a backlog that competes with everything else in the backlog.
- Question sets are broad rather than deep, so a pillar can be answered adequately while a specific serious weakness goes unmentioned.
- Review fatigue is a genuine failure mode. Fifty-plus questions per workload per quarter tends toward copied answers, which quietly converts the process into theatre.
- Custom lenses require ongoing authorship and versioning, and a stale custom lens encodes last year's standard as this year's requirement.
- It informs design and records diligence. It is not a control, and nothing in an environment changes because a review was completed.