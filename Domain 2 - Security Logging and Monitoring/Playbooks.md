# Playbooks & Runbooks Design

The practice of pre-writing incident response as reusable **strategy** documents (playbooks) and step-by-step **execution** documents (runbooks), so responders execute a known process instead of improvising under pressure. In AWS this is concrete: a runbook is often a literal **SSM Automation document**, and it can be wired to EventBridge, Lambda, Step Functions, and Systems Manager Incident Manager for automated response. This is a Preparation-phase deliverable in the IR lifecycle, and the exam tests both the playbook-versus-runbook distinction and the AWS automation primitives underneath.

The mental split is strategy versus execution. A **playbook** answers what, why, and who for an incident type: triggers, severity and escalation, roles, communication plan, tools, containment objectives, and dependencies like legal or PR. A **runbook** answers how, as concrete steps, increasingly automated. In AWS the word "runbook" is the literal name for an SSM Automation document, and the more of a runbook you can automate and trigger straight from a finding, the faster and more consistent the response.

## How it works

- **Playbooks (strategy)**: one per incident type, such as leaked credentials, EC2 malware, S3 data exposure, insider misuse, or DDoS. Each defines triggers, severity and escalation thresholds, roles and responsibilities, the communication plan, the tools and systems involved, containment objectives, and external dependencies. High-level, reusable across environments, and involving some judgment.
- **Runbooks (execution)**: concrete steps that assume someone (or something) is ready to act. In AWS an **SSM Automation document** is a runbook, whether an AWS-managed one or your own, and it can isolate an instance, snapshot volumes, collect memory, rotate keys, or patch.
- **Automation wiring**: the core pattern is a finding from GuardDuty or Security Hub triggering an **EventBridge** rule that invokes **Lambda** (disable an IAM user, revoke sessions, rotate keys), **SSM Automation** (isolate or snapshot), or **Step Functions** (orchestrate a multi-step containment). Security Hub custom actions and automation rules can also trigger response.
- **Systems Manager Incident Manager**: AWS's productized response system. **Response plans** tie runbooks, responder engagement (contacts and escalation), and chat channels to CloudWatch alarms or EventBridge, and drive structured post-incident analysis. This is the AWS-native way to operationalize a playbook plus runbook plus on-call.
- **AWS Security Incident Response (managed service)**: provides managed triage, coordination, and containment for the critical findings, with 24/7 CIRT access, complementing your own runbooks.
- **Governance**: version-control playbooks and runbooks (a repo, not a wiki), test them in game days, link them to tickets, and keep a human in the loop for high-impact actions.

## Playbook vs runbook

| Trait | Playbook | Runbook |
|---|---|---|
| Audience | IR managers, analysts | Tier-1 responders, engineers, automation |
| Scope | High-level, strategic | Low-level, tactical |
| Answers | Why and what | How |
| Format | Flowcharts, tables, SOPs | Steps, AWS CLI, SSM Automation documents |
| AWS embodiment | Incident-type playbook, Incident Manager response plan | SSM Automation document, Lambda, Step Functions |
| Flexibility | Some judgment | Very procedural, often automated |

## What gets tested

- Playbook equals strategy (what, why, who), runbook equals execution (how). In AWS a runbook is literally an SSM Automation document.
- The automated-response pattern is the core exam concept: a GuardDuty or Security Hub finding to an EventBridge rule to Lambda, SSM Automation, or Step Functions. Recognize it in scenario stems.
- Common containment automations map to incident types: isolate EC2 via SSM, disable or rotate IAM credentials and revoke sessions via Lambda, snapshot volumes, and remove S3 public access.
- Systems Manager Incident Manager operationalizes response plans (runbooks plus on-call engagement, escalation, and post-incident analysis). Distinguish it from AWS Security Incident Response, which is the managed triage and CIRT service.
- Playbooks and runbooks are a Preparation-phase deliverable. You build and test them before an incident, not during one.
- High-impact actions should keep a human in the loop rather than fully auto-executing.

## Limitations

- A runbook is only as good as its last test. Untested runbooks fail during a real incident, so exercise them in game days.
- Over-automation is a real risk. Auto-containment on a false positive can take down production, so gate high-impact actions with an approval step (Step Functions approval or Incident Manager engagement).
- Runbooks drift as the environment changes. Version and review them, or they will reference resources that no longer exist.
- They reduce MTTR and mistakes but do not replace judgment for novel incidents that no playbook anticipated.
- Enabling detection mid-incident is too late. Detection coverage belongs in Preparation, not in a runbook step.