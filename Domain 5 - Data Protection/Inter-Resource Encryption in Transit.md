# Inter-Resource Encryption in Transit

Encryption of traffic between resources or nodes within a workload, as opposed to client-to-service TLS. This is Task 5.1.3 territory: EC2/Nitro instance-to-instance, EMR between cluster nodes, EKS pod-to-pod, and SageMaker between distributed-training containers. The exam tests which of these is automatic and which you must turn on.

The mental split is automatic vs configured. Nitro-based EC2 instances encrypt instance-to-instance traffic for free under specific conditions; EMR and SageMaker require an explicit setting; EKS pod-to-pod is not encrypted by default unless your nodes are Nitro instances or you add a service mesh.

## How it works (by service)

- **EC2 / Nitro**: supported Nitro instance types automatically encrypt traffic between instances (AES-256-GCM, no performance hit) when they are in the **same Region**, in the **same VPC or peered VPCs**, and the traffic does **not** pass through an intermediary like a load balancer, NAT, or transit gateway. Otherwise add TLS at the application layer. Cross-Region VPC/TGW peering traffic is automatically bulk-encrypted leaving the Region, and inter-AZ/inter-Region backbone traffic is encrypted at the physical layer.
- **VPC encryption controls** (newer): audit and **enforce** encryption in transit across all traffic within and across VPCs in a Region (monitor mode, then enforce mode). It relies on Nitro hardware encryption; non-Nitro or intermediary-routed resources must move to supported instances, use app-layer TLS, or be excluded.
- **EMR**: in-transit encryption between cluster nodes is enabled via an EMR **security configuration**; you supply TLS certificates (PEM in S3 or a custom certificate provider). Covers the open-source application traffic (Hadoop, Spark, Presto, and so on).
- **EKS**: control-plane-to-node traffic is TLS. **Pod-to-pod traffic is not encrypted by default.** Options: run nodes on Nitro encryption-capable instance types (inter-node traffic encrypted at the hardware layer, with a modern VPC CNI), or add a **service mesh** (Istio, or Cilium/WireGuard) for mTLS. Secrets envelope encryption with KMS is a separate at-rest concern.
- **SageMaker**: set **`EnableInterContainerTrafficEncryption`** on distributed training/processing jobs to encrypt traffic between job containers/nodes. It can increase training time for deep-learning workloads. Pair with network isolation and VPC config.

## Automatic vs configured

| Service | Inter-resource encryption |
|---|---|
| EC2 (Nitro) | Automatic between supported instances, same Region/VPC, no intermediary |
| EMR | Configured: security configuration + your TLS certs |
| SageMaker | Configured: `EnableInterContainerTrafficEncryption` flag |
| EKS pod-to-pod | Not by default: Nitro nodes or a service mesh (mTLS) |

## What gets tested

- Nitro instance-to-instance encryption is automatic but conditional: same Region, same or peered VPC, and no load balancer / NAT / transit gateway in the path. Route through an intermediary and you lose it — fall back to application-layer TLS.
- EMR inter-node encryption is turned on with a security configuration and your own TLS certificates, not automatic.
- SageMaker distributed jobs need the inter-container traffic encryption flag; it is off by default and can slow training.
- EKS pod-to-pod is not encrypted by default; the answers are Nitro encryption-capable nodes or a service mesh for mTLS (App Mesh historically provided this but is being retired).
- VPC encryption controls is the newer way to audit and enforce in-transit encryption across a Region, leaning on Nitro hardware encryption.
- This is distinct from client-to-service TLS (ACM certs on ALB/CloudFront) and from encryption at rest — 5.1.3 is specifically resource-to-resource within a workload.

## Limitations

- Nitro auto-encryption breaks when traffic crosses an intermediary (LB, NAT, TGW) or leaves the stated conditions; it is not a universal guarantee.
- EMR and SageMaker options add setup (certs) or runtime cost (slower training).
- EKS needs deliberate design (Nitro nodes or a mesh) for pod-to-pod; the default is plaintext within the VPC.
- VPC encryption controls enforce mode requires all in-scope resources to support hardware or app-layer encryption first.