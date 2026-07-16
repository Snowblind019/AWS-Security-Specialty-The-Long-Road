# Automated Forensics Orchestrator for Amazon EC2

A self-service AWS Guidance you deploy (CloudFormation and CDK from the AWS Solutions Library), not a managed service, that automates the digital-forensics workflow when a host is flagged as compromised. Originally scoped to EC2, it now covers EC2 and EKS. From the moment a detection fires it triages the resource, captures memory and disk evidence into a separate forensic account, isolates the instance, spins up a forensic workstation to investigate, and records every step for reporting. It stitches Security Hub, EventBridge, Step Functions, Lambda, SSM, EBS snapshots, KMS, S3, and DynamoDB into one orchestrated incident-response pipeline.

This is a pure incident-response artifact and the exam's model answer for automating EC2 forensics. The thing to hold onto is the sequence and why it is ordered that way: detect, then capture volatile memory first and disk second, then isolate, then investigate on a clean forensic host, with every artifact copied into a separate forensic account under its own KMS keys so the evidence survives even if the source account is compromised. Speed, evidence integrity, and separation of duties, automated.

## How it works

- **Trigger**: in the application account, GuardDuty, AWS Config managed rules, or third-party tools detect malicious EC2 or EKS activity (for example an instance querying a low-reputation domain). Findings flow to Security Hub in the security account, which forwards them to EventBridge. A Security Hub custom action (Forensic triage or Forensic isolation) hands the instance ID to a Step Functions workflow.
- **Triage**: Step Functions gets the instance information, decides whether to isolate (from the Security Hub action) and whether to acquire (from tags on the instance), and records triage details in DynamoDB.
- **Acquisition, two flows in parallel**:
  - Memory: a Lambda uses SSM Run Command to run a memory-acquisition document on the host, assuming a role in the application account, and writes the dump to S3 in the forensic account, tagged with OS and kernel metadata. Memory goes first because it is volatile.
  - Disk: a Lambda snapshots the EBS volume, copies the snapshot using KMS keys shared to the forensic account, shares it, then keeps a local re-encrypted copy under forensic KMS keys so the evidence stays intact even if the source account or the shared snapshot is lost.
- **Isolation**: applies a quarantine security group and invalidates the active credential sessions tied to the compromised instance role. If the isolation flag is set, isolation happens regardless of whether acquisition succeeded or errored.
- **Investigation**: an investigation Step Functions state machine launches a forensic instance from a prebuilt forensic AMI (EC2 Image Builder) loaded with your tools, loads the memory image from S3, builds an EBS volume from the snapshot, and attaches it for analysis via SSM documents. Results and task state land in DynamoDB.
- **Reporting**: process notifications via SNS, with DynamoDB holding the record of every step, which is the chain-of-custody trail.

## Automated Forensics Orchestrator vs sibling options

| | Automated Forensics Orchestrator | Amazon Detective | Amazon GuardDuty | Manual / DIY runbooks |
|---|---|---|---|---|
| Role | Orchestrate acquisition, isolation, investigation | Analyze and visualize findings | Detect threats | Whatever you script |
| Memory / disk capture | Yes (SSM memory dump, EBS snapshot) | No | No | If you build it |
| Isolation | Yes (security group plus credential invalidation) | No | No | Manual |
| Best for | Automated EC2 / EKS forensics at SOC scale | Root-cause investigation of findings | Continuous detection | Small scale, full control |

## What gets tested

- It is a deployable Guidance, not a managed service. Know it as the reference pattern for automated EC2 and EKS forensics, and know the components it wires together.
- The trigger chain: detection (GuardDuty, Config, or third-party) to a Security Hub finding to EventBridge to a Step Functions orchestration, with Security Hub custom actions (Forensic triage, Forensic isolation) driving it.
- Order of volatility: capture memory first (SSM Run Command dumping to S3), then disk (EBS snapshot), because memory is the perishable evidence.
- Cross-account evidence custody: artifacts land in a separate forensic account, and disk snapshots are copied and re-encrypted with forensic-account KMS keys so evidence survives even if the source account is compromised or the shared snapshot is deleted. This is the chain-of-custody and evidence-integrity point.
- Isolation equals a quarantine security group plus invalidating the instance role's active credential sessions. Gotcha: instances sharing that IAM role are also affected when the credentials are invalidated.
- Investigation runs on a purpose-built forensic instance from a hardened forensic AMI (EC2 Image Builder), keeping analysis off the compromised host. DynamoDB holds the state and task records.

## Limitations

- Not a managed service. You deploy and maintain it, including building and updating the forensic AMI.
- Memory acquisition depends on SSM: the target needs the SSM Agent and a working SSM path, so a badly compromised or unreachable host may not cooperate.
- Isolation by credential invalidation hits every instance sharing the compromised role, so shared roles widen the blast radius of isolation.
- Multi-account setup (application, security, forensic) with cross-account roles and shared KMS keys is required, and that complexity is real.
- It orchestrates the plumbing, but you still supply the forensic tooling in the AMI and interpret the results.