# Amazon Application Recovery Controller (ARC)

A set of highly available recovery primitives (formerly Amazon Route 53 Application Recovery Controller) for mitigating **Availability Zone or Region impairments** in multi-AZ and multi-Region applications. ARC is engineered to keep operating when the rest of a Region is having a bad day, which is the whole design point. It spans two domains: **Multi-AZ recovery** (zonal shift and zonal autoshift) and **Multi-Region recovery** (routing control with safety rules, Region switch, and readiness check). For the security exam it sits in the resilience and incident-response area, and the security-relevant piece is that routing controls are IAM-gated, CloudTrail-audited, and guarded by safety rules so failover cannot be forced into an unsafe state under pressure.

The mental split is Multi-AZ vs Multi-Region. Multi-AZ is zonal shift (you manually move traffic off a bad AZ) and zonal autoshift (AWS moves it for you based on its telemetry). Multi-Region is routing controls (highly available on/off switches with safety rules), Region switch (full-stack failover orchestration), and readiness check (a configuration-parity monitor, not a health check). ARC does not react to resource health the way Route 53 health checks or Auto Scaling do. It is the deliberate, resilient control layer you operate on top of them.

## How it works

- **Zonal shift (Multi-AZ, manual)**: temporarily move traffic for a supported resource away from an impaired AZ to healthy AZs in the same Region. Supported resources include **ALB, NLB, EC2 Auto Scaling groups, and EKS**. Shifts are temporary, with an expiration of up to **3 days** (extendable).
- **Zonal autoshift (Multi-AZ, automatic)**: you authorize AWS to shift traffic off an AZ its internal telemetry flags as impaired, and to shift it back when the signal clears. Practice runs validate it, and you pre-scale capacity so a shift completes without waiting on Auto Scaling.
- **Routing control (Multi-Region, manual)**: highly available on/off switches that gate Regional traffic, typically by driving Route 53 health check state. The **cluster** is a data plane of **endpoints in 5 AWS Regions**, and any one endpoint can flip a control, so you can change routing state even while a Region is down. During an event you drive changes through the **data-plane API across all five endpoints, not the console**, because the console can be affected by the same impairment.
- **Safety rules**: **assertion rules** force a set of routing controls to maintain a required state (for example, at least one cell must stay On, so an exhausted operator cannot disable the last healthy Region), and **gating rules** let an overriding control gate changes to others (preventing split-brain, such as both Regions active when you require active-passive).
- **Readiness check (Multi-Region)**: continuously monitors resource quotas, capacity, and routing configuration for **parity across Regions** and surfaces drift. It is explicitly **not** a health monitor and **not** for the failover critical path. It is **closed to new customers as of April 30, 2026**, and AWS directs new designs to Region switch plan evaluation.
- **Region switch (Multi-Region)**: the newer fully managed orchestration for coordinated full-stack failover via declarative recovery plans (scaling compute, switching over databases, shifting DNS), with plan evaluation and automated practice runs.
- **Integrations**: Route 53 health checks, CloudWatch for observability, CloudTrail for an audit trail, and IAM for least-privilege gating of who can flip a control.

## ARC capabilities

| Capability | Domain | Trigger | What it does |
|---|---|---|---|
| Zonal shift | Multi-AZ | Manual | Temporarily move traffic off an impaired AZ (ALB, NLB, EC2 ASG, EKS), up to 3 days |
| Zonal autoshift | Multi-AZ | AWS automatic | AWS shifts traffic off an AZ its telemetry flags as impaired, then back |
| Routing control | Multi-Region | Manual via API | Highly available on/off switches gating Regional traffic, guarded by safety rules |
| Region switch | Multi-Region | Orchestrated plan | Declarative full-stack cross-Region failover (compute, database, DNS) |
| Readiness check | Multi-Region | Continuous | Parity monitor for quota, capacity, and config drift (closed to new customers 4/30/2026) |

## What gets tested

- ARC is deliberate, highly available recovery control, not a health-reactive autoscaler. Its value is that the control path keeps working when a Region is impaired.
- The cluster quorum is a data-plane design, not human approvals. Routing control endpoints live in 5 Regions and any one can flip a control, so state can change during a Regional outage. During an event, use the data-plane API across all five endpoints, not the console.
- Safety rules keep state valid: assertion rules force a set of controls to hold a required state (so you cannot disable the last healthy Region), and gating rules let an overriding control gate others (preventing split-brain when you require active-passive).
- Zonal shift (manual) versus zonal autoshift (AWS-initiated from telemetry) is the Multi-AZ pair. Supported resources include ALB, NLB, EC2 Auto Scaling groups, and EKS, shifts are temporary up to 3 days, and you pre-scale capacity so a shift does not wait on Auto Scaling.
- Readiness check is a parity and drift monitor across Regions, not a health check, and never belongs in the failover critical path. It is closed to new customers as of April 30, 2026, with Region switch plan evaluation as the successor.
- Region switch is the newer answer for coordinated, full-stack multi-Region failover orchestration.
- The security framing is separation of duties and guardrails: routing controls are IAM-gated and CloudTrail-audited, and safety rules enforce invariants so no one can force an unsafe state under pressure. It is not a human voting quorum.

## Limitations

- Readiness check is closed to new customers (April 30, 2026), and even where available it is a parity monitor, never a failover trigger or a health check.
- Do not rely on the console during a Regional event. Drive routing controls through the five-endpoint data-plane API.
- Zonal shift is temporary (up to 3 days) and requires opted-in supported resources plus pre-provisioned capacity in the remaining AZs to absorb the traffic.
- ARC orchestrates and gates recovery, it does not replicate your data or stand up your standby. Cross-Region data sync and standby capacity remain your responsibility.
- Routing control, Region switch, and readiness check are not available in the China Regions or AWS GovCloud (US), though zonal shift and zonal autoshift are.