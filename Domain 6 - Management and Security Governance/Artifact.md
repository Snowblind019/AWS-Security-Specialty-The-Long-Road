# AWS Artifact

AWS Artifact is the self-service portal where AWS publishes its own audit evidence: the signed compliance reports produced by the third-party auditors who assess AWS infrastructure, plus the legal agreements you sign with AWS to unlock regulated workloads. It performs no action on your account, provisions nothing, and evaluates nothing you have built. Its entire security function is to supply the provider half of the shared responsibility model in a form an auditor, a regulator, or a customer's procurement team will accept. When a security questionnaire asks whether the underlying cloud is ISO 27001 certified or SOC 2 attested, Artifact is the authoritative answer, and when a workload touches PHI, the HIPAA BAA accepted through Artifact is the legal precondition that makes the workload permissible at all. The thing to hold onto: Artifact proves AWS did its part, it never proves you did yours.

## How it works

**Two distinct object types.** Reports are read-only artifacts AWS publishes and you download. Agreements are bilateral legal instruments you accept, which changes your account's contractual standing with AWS. Exam questions frequently hinge on which of the two a scenario needs.

**Reports cover provider scope only.** SOC 1 Type II (financial controls), SOC 2 Type II (security, availability, confidentiality), SOC 3 (public summary), ISO 27001, 27017, 27018 and 9001, PCI DSS Attestation of Compliance and responsibility summary, FedRAMP packages for GovCloud and US regions, plus regional frameworks including C5, IRAP, MTCS, ENS and HITRUST. Each states which AWS services are in scope, which is the detail that matters: a service outside the report's scope is not covered by that attestation even though it runs in the same account.

**Most reports are gated behind a confidentiality term.** Downloading a SOC or PCI report requires accepting an NDA term at download time. The accepted term binds distribution, so these documents cannot be posted publicly or handed to arbitrary third parties. SOC 3 exists precisely because it is the version with no such restriction.

**Agreements are accepted per account or per organization.** Individual accounts accept their own agreements. Organization-wide acceptance, which covers all member accounts, can only be performed from the management account by a principal with the relevant Artifact permissions. This is the single most common trap in the agreement portion of the domain.

**Access is IAM-gated like any other service.** Relevant actions include `artifact:GetReport`, `artifact:GetReportMetadata`, `artifact:GetTermForReport`, `artifact:ListReports`, `artifact:AcceptAgreement`, `artifact:DownloadAgreement` and `artifact:TerminateAgreement`. Separating report access from agreement acceptance is a legitimate least-privilege design: compliance analysts get read on reports, legal or a delegated admin gets acceptance rights.

```bash
aws artifact list-reports
aws artifact get-report --report-id <id> --term-token <token> --version 1
```

**Third-party reports are a separate surface.** Artifact also exposes compliance documentation for ISV products sold through AWS Marketplace, which supports vendor risk assessment of software running on AWS rather than AWS itself.

**Agreements can be terminated.** Terminating a BAA removes the contractual coverage but does nothing to the data already stored, which remains your obligation to remediate.

## Comparison

| Service | Whose compliance | Evidence type | Continuous |
| --- | --- | --- | --- |
| AWS Artifact | AWS itself | Third-party auditor reports, signed legal agreements | No, point in time documents |
| AWS Audit Manager | Your workloads | Automatically collected evidence mapped to framework controls | Yes, continuous collection |
| AWS Config | Your resources | Configuration state and rule evaluations | Yes, on change or periodic |
| Security Hub | Your account posture | Findings scored against standards such as CIS and PCI | Yes, aggregated findings |
| AWS Compliance Center | Public reference | Jurisdictional regulatory information | Not applicable |

## What gets tested

- **Artifact versus Audit Manager.** If the question asks for proof that AWS meets a standard, the answer is Artifact. If it asks to demonstrate that your own workload meets a standard, or to assemble evidence for your own audit, the answer is Audit Manager. Audit Manager can pull Artifact into a wider audit package, but it does not replace it.
- **Artifact versus Config and Security Hub.** Config and Security Hub assess resources you own and produce findings. Artifact produces no findings at all. Any scenario mentioning drift, non-compliant resources, or remediation is not Artifact.
- **HIPAA scenarios.** Storing or processing PHI on AWS requires an accepted BAA. The correct sequence is accept the BAA, then restrict the workload to HIPAA eligible services, then apply encryption and access controls. Downloading the HIPAA whitepaper is not sufficient.
- **Organization scope.** Pick management account acceptance when the requirement is that every member account is covered. Member accounts cannot accept an organization agreement on their own behalf.
- **Distribution limits.** When a scenario needs a compliance document shareable with the public or with a party unwilling to sign an NDA, pick SOC 3 rather than SOC 2.
- **Least privilege.** Expect distractor answers granting broad admin to enable a compliance analyst; the correct answer scopes to the specific Artifact read actions.
- **Cost.** Artifact is free, so cost optimization is never a valid reason to choose against it.

## Limitations

- Read-only with respect to your environment. It cannot detect, prevent, alert, or remediate anything.
- Reports are point-in-time attestations with defined audit periods. They go stale, and a report covering an earlier period says nothing about the current one.
- Service scope varies per report. A newly launched service is often absent from the current attestation until the next audit cycle.
- Accepting an agreement changes legal standing only. It applies no technical control, enforces no service restriction, and does not stop you from putting regulated data on an ineligible service.
- NDA-covered reports carry distribution restrictions that constrain how audit packages can be shared.
- It documents the AWS side of shared responsibility exclusively. Customer-side controls, encryption, IAM, logging, network isolation, remain entirely unevidenced by it.