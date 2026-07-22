# Amazon OpenSearch Encryption

Amazon OpenSearch Service, frequently the SIEM or log-analytics layer holding CloudTrail, GuardDuty findings, and VPC Flow Logs, supports three encryption controls: at-rest via KMS, node-to-node between cluster nodes, and in-transit (HTTPS) for clients and Dashboards. Because the data indexed here is exactly the sensitive security telemetry an attacker would want, encryption is baseline rather than optional. The exam-relevant catch is that the two internal controls, at-rest and node-to-node, must be chosen at domain creation and cannot be toggled on an existing domain, so remediation means snapshot and restore into a new domain. The thing to hold onto: at-rest (KMS) and node-to-node are create-time settings you cannot add later, in-transit HTTPS enforcement is configurable, and node-to-node encryption plus HTTPS enforcement are prerequisites for fine-grained access control.

## How it works

- **At-rest encryption is KMS, on by default, set at creation.** It covers indices, the underlying EBS volumes, and automated and manual snapshots, backed by an AWS-managed key or your CMK. It is enabled at domain creation and cannot be added to an existing unencrypted domain later.
- **Node-to-node encryption secures intra-cluster traffic.** TLS between master, data, and ingest nodes stops a rogue or compromised node from sniffing replication and query traffic inside the cluster. Like at-rest, it is a create-time setting that cannot be toggled afterward.
- **In-transit encryption protects client and Dashboards traffic.** HTTPS (TLS 1.2+) secures client-to-cluster calls, OpenSearch Dashboards sessions, and ingestion from Firehose or Lambda. You can enforce HTTPS-only, require a minimum TLS version, and use a custom ACM cert or front Dashboards with an HTTPS ALB.
- **Remediation for the create-time controls is snapshot and restore.** To add at-rest or node-to-node encryption to a domain that lacks it, you snapshot the data and restore into a new domain created with those settings enabled. There is no in-place enablement.
- **These controls underpin fine-grained access control.** FGAC requires node-to-node encryption and HTTPS enforcement to be on, so the encryption settings are a gate for the finer authorization features, not just confidentiality on their own.

## OpenSearch encryption controls

| Control | Protects | When set | Remediation if missing |
|---|---|---|---|
| **At rest (KMS)** | Indices, EBS volumes, snapshots | Domain creation (default on) | Snapshot and restore to a new domain |
| **Node-to-node** | Intra-cluster node traffic | Domain creation only | Snapshot and restore to a new domain |
| **In transit (HTTPS)** | Client, Dashboards, ingestion | Configurable | Enable HTTPS enforcement / min TLS |

## What gets tested

- **At-rest and node-to-node cannot be enabled after creation.** If a scenario has an existing domain missing either, the answer is snapshot and restore into a new domain with the setting enabled, not "turn it on." This is the most tested OpenSearch encryption fact.
- **Node-to-node stops in-cluster sniffing.** Protecting replication and query traffic from a compromised node inside the cluster is node-to-node encryption specifically, distinct from in-transit (which is the client hop) and at-rest (disk).
- **HTTPS enforcement for the client hop.** Requiring TLS for clients and Dashboards, and disabling old TLS versions for compliance, is the in-transit control, configurable on a running domain.
- **FGAC prerequisites.** Fine-grained access control requires node-to-node encryption and HTTPS enforcement, so a question about enabling FGAC implies those settings must already be on.
- **CMK for audit and scoped access.** Using a customer-managed key gives CloudTrail visibility into decrypts and scoped key access over the default key, the usual answer for compliance-driven logging pipelines.
- **The three layers are distinct.** At-rest (disk), node-to-node (inside the cluster), and in-transit (client to cluster) each address a different threat, and a question about one should not be answered with another.

## Limitations

- At-rest and node-to-node encryption are create-time only, so remediating an existing domain requires a snapshot-and-restore migration, not a toggle.
- The three controls cover different surfaces, so enabling at-rest alone still leaves intra-cluster and client traffic exposed unless node-to-node and HTTPS are also handled.
- Node-to-node and HTTPS enforcement are prerequisites for FGAC, so skipping them blocks the finer access controls entirely.
- Encryption protects confidentiality and integrity of the data, not authorization. IAM, resource policies, and FGAC still govern who can query, so misconfigured access remains a separate exposure.
- Custom ACM certs and HTTPS-only enforcement need deliberate configuration, so a default domain may still accept weaker TLS unless you tighten it.
- CMK usage and snapshot activity add KMS request costs, so high-ingest security pipelines carry a key-usage bill alongside the storage.