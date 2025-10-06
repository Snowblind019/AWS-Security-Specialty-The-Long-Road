# Amazon EFS — Security

## What Is Amazon EFS

Amazon Elastic File System (EFS) is a fully managed, elastic, POSIX-compliant network file system that can be mounted to multiple EC2 instances across Availability Zones (AZs) in an AWS Region. It offers shared, concurrent access — similar to a NAS (Network Attached Storage) in traditional data centers — and automatically grows/shrinks as files are added or removed.

It’s ideal for:

- Lift-and-shift Linux apps needing shared storage  
- Big data workloads with concurrent writers/readers  
- Container-based apps (ECS, EKS)  
- Home directories, build pipelines, and developer environments  

But from a security and compliance perspective, what matters most is how the data is accessed, shared, encrypted, and monitored — especially in multi-tenant or regulated environments.

---

## Cybersecurity and Real-World Analogy

**Cybersecurity Analogy:**  
Imagine EFS like a shared drive in your organization that everyone can mount and access. You want to control:

- Who can mount it  
- What permissions they have (read/write/delete)  
- Where the data is encrypted (on disk and in transit)  
- How you track access  

Without proper controls, one compromised EC2 could leak the entire shared file system.

**Real-World Analogy:**  
EFS is like a company’s central file server. It scales infinitely, lets multiple users access the same data, but it needs:

- User authentication  
- Access permissions  
- Locks and alarms on sensitive folders  
- Backup plans  

EFS does all that — with AWS-native controls.

---

## How Amazon EFS Works

| **Component**        | **Description**                                                                 |
|----------------------|----------------------------------------------------------------------------------|
| Mount Targets         | Each AZ gets a mount target (ENI), so EC2 instances in any AZ can mount via NFS |
| Protocols             | Uses NFSv4.1 or NFSv4.2                                                          |
| Throughput & Perf     | Bursting model by default; can be provisioned                                   |
| Availability          | Data is replicated across multiple AZs automatically                            |
| Durability            | Designed for 99.999999999% (11 9s) durability                                    |

**Access Points** are great for containers (e.g., in ECS/EKS) that need scoped and isolated access to only certain directories in a shared file system.

---

## Audit Logging and Monitoring

While EFS doesn’t natively log file-level access like S3, you can still gain visibility:

- Enable **CloudTrail** for EFS API activity (e.g., creation, deletion)  
- Use **VPC Flow Logs** to monitor traffic to/from mount targets  
- Monitor **KMS key usage** via CloudTrail  
- Pair with **AWS Config** to track encryption state, permissions, and compliance  

For deeper audit trails:  
Mount EFS to EC2 and use OS-level tools (e.g., `auditd`, CloudWatch Agent) to monitor file access.

---

## Snowy’s Example: EFS for Secure Build Pipelines

Snowy builds a CI/CD system where:

- Jenkins agents run on EC2 in multiple AZs  
- Each agent mounts EFS to read/write build artifacts  
- EFS is encrypted at rest using a **CMK with strict key policies**  
- **Access Points** are defined so each agent writes to a unique directory  
- The `efs-utils` package enforces **encryption in transit**  
- **Security Groups** restrict EFS mount targets to only trusted EC2s  
- All EFS changes are versioned and backed up with **AWS Backup**  

This gives Snowy’s build system a shared, secure, scalable backend without managing any storage servers or worrying about capacity planning.

---

## Final Thoughts

Amazon EFS is powerful — but shared access brings shared risk. That’s why **encryption, access controls, and auditing are non-negotiable** in production.

Use EFS when:

- You need shared, concurrent file access  
- Your apps expect POSIX file semantics  
- You want elastic capacity with high durability  
- You need to run legacy Linux workloads or stateful containers  

Avoid EFS when:

- You’re building stateless microservices (use S3 or EFS OneZone)  
- You don’t need concurrent access (EBS might be enough)  
- You need granular access logging (use S3 with CloudTrail)  
