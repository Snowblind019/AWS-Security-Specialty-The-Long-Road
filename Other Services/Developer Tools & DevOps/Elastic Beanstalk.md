# AWS Elastic Beanstalk

## What Is the Service

Elastic Beanstalk is AWS’s fully managed **Platform-as-a-Service (PaaS)** offering. It lets developers deploy and scale web applications without managing the underlying infrastructure.

You upload your code (Java, Python, Node.js, PHP, Ruby, Go, .NET, etc.), and Beanstalk:

- Provisions compute (typically EC2)  
- Sets up load balancers (ALB/ELB)  
- Configures auto scaling groups  
- Deploys your app  
- Monitors health  
- Handles rolling updates or blue/green deploys  

Beanstalk sits in that sweet spot between **raw IaaS** (like EC2) and **abstracted services** (like Lambda or App Runner).

### Why it matters from a security perspective:

- It automates infrastructure — but that infrastructure still needs to be audited, isolated, patched, and monitored.  
- It uses EC2 instances, VPCs, IAM roles, ALBs, and S3 buckets behind the scenes — all of which must be hardened.  
- The defaults may not be secure. You need to customize and control the environment to meet your threat model.

---

## Cybersecurity Analogy

Imagine a developer wants to ship an internal web tool. Instead of giving them full control of your data center (rackspace, firewall access, DNS changes), you hand them a secure deployment appliance: plug in your code, and it handles everything.

But here’s the catch: that appliance still opens a port to the outside, still needs OS patches, and still sits in your network.  
**Beanstalk is convenience infrastructure. But convenience doesn’t mean secure by default.**

## Real-World Analogy

Think of Beanstalk as AWS handing you a **pre-built bakery**. You just bring your cake recipe and ingredients (your code). The ovens, counters, and storefront get set up automatically.

But you’re still responsible for:

- Locking the front door (**IAM**, security groups)  
- Keeping the food safe (**app secrets**, OS hardening)  
- Not serving raw eggs (vulnerable dependencies)  
- Cleaning up messes (log rotation, patching)  

**AWS gives you the building. You secure what happens inside.**

---

## How It Works (Under the Hood)

When you deploy an app via Beanstalk, it builds the following components automatically:

| **Component**    | **Details**                                                               |
|------------------|---------------------------------------------------------------------------|
| Environment Tier | Web Server (EC2 + ALB) or Worker Tier (EC2 + SQS queue)                   |
| Platform         | Prebuilt AMIs (Amazon Linux, Windows) with runtimes and nginx/Apache     |
| Compute          | Auto Scaling Group of EC2 instances                                       |
| Load Balancer    | ALB or ELB configured per environment                                     |
| S3 Bucket        | Used to store deployment artifacts and logs                               |
| RDS (optional)   | Can provision a database, but Beanstalk does not manage its lifecycle     |
| IAM Roles        | One for EC2 instances, one for Beanstalk itself                           |
| Logs & Metrics   | Integrated with CloudWatch (if enabled)                                   |

You can deploy using:

- ZIP file (CLI, SDK, Console)  
- Git push via CodePipeline  
- Terraform or CloudFormation wrappers  
- CI/CD systems that call Beanstalk APIs directly  

All infrastructure lives **inside your account**, which means you can (and must) **customize VPCs, subnets, IAM roles, and KMS keys**.

---

## Security Considerations

Elastic Beanstalk environments can be hardened, but you must take action — the defaults are not secure enough for production.

| **Security Area**     | **Best Practice**                                                                 |
|------------------------|-----------------------------------------------------------------------------------|
| VPC Networking         | Deploy into private subnets with NAT gateways for outbound traffic only           |
| Security Groups        | Lock down ALB to specific IPs or VPN CIDRs; restrict EC2 inbound traffic          |
| EC2 Instance Role      | Attach least privilege IAM role (no admin access to S3, DynamoDB, etc.)           |
| OS Patching            | Use Elastic Beanstalk managed updates, or bake AMIs yourself                      |
| App Secrets            | Load from Secrets Manager or SSM Parameter Store — never in code                  |
| Logs                   | Enable CloudWatch Logs integration; stream logs from `/var/log/eb-engine.log`     |
| ALB Settings           | Force HTTPS, disable weak ciphers, use WAF if exposed                             |
| RDS Handling           | Use external RDS, not Beanstalk-provisioned (it gets deleted on teardown)         |
| Encryption             | Use KMS to encrypt volumes, environment variables, and deployment artifacts       |
| Auditability           | Log changes via CloudTrail + EventBridge + SNS notifications                      |

---

## Vulnerabilities and Risks

- If you don’t isolate the EC2 instances, an attacker can pivot from your app container to the underlying host.  
- If you expose your ALB without WAF or Shield, it becomes an attack vector (XSS, path traversal, bot abuse).  
- If you deploy using plaintext secrets (env vars or config files), they can be leaked on disk or through logging.  
- If you use default Beanstalk RDS integration, deleting the app deletes the DB.  
- If you don’t manage app-layer auth, any public URL can become an entry point.  

**Beanstalk handles the “how do I deploy” — not “is my app secure.”**

---

## IAM Integration

Elastic Beanstalk creates two key IAM roles:

| **Role Name**                     | **Purpose**                                      |
|----------------------------------|--------------------------------------------------|
| aws-elasticbeanstalk-ec2-role    | Attached to EC2 instances for S3, logs, etc.     |
| aws-elasticbeanstalk-service-role| Used by Beanstalk service to manage infra        |

These roles can (and should) be customized:

- Limit access to only required services  
- Attach customer-managed KMS permissions  
- Use `kms:ViaService` conditions to limit misuse  
- Rotate secrets using IAM + Secrets Manager bindings  
- Disable metadata v1 and enforce IMDSv2 for EC2s

---

## Visibility and Monitoring

| **Source**                       | **What You Get**                                                         |
|----------------------------------|---------------------------------------------------------------------------|
| CloudTrail                       | Tracks environment creation, config changes, IAM calls                    |
| CloudWatch Logs                  | Captures app logs, instance logs, Beanstalk deployment engine logs       |
| AWS Config                       | Tracks resource drift, insecure config changes                            |
| CloudWatch Metrics               | Environment health, instance CPU, ALB metrics                             |
| Elastic Beanstalk Health Dashboard | App-level health checks and alarms                                    |

You can:

- Forward logs to S3 for retention  
- Trigger alerts from EventBridge when environments enter degraded or failing states

---

## Pricing Model

**Beanstalk itself is free** — you only pay for the underlying resources:

| **Resource**     | **Example Cost (varies by region)**                |
|------------------|----------------------------------------------------|
| EC2 Instances     | Per hour/per second usage                          |
| Load Balancer     | $ per hour + per GB processed                      |
| S3 Bucket         | Storage and PUT/GET requests                       |
| CloudWatch Logs   | Charged by ingestion and retention                 |
| RDS (if used)     | Fully billed as a separate service                 |

There’s no charge for:

- Beanstalk orchestration  
- Environment versions  
- Application versions  

But costs can skyrocket if you don’t monitor:

- Auto Scaling policies  
- Idle environments left running  
- Unused EBS volumes or snapshots

---

## Real-Life Example: Snowy’s Internal CI App

You’ve built an internal CI dashboard in Flask for your NOC team. You want easy deployment but full control of networking and security.

So you:

- Upload the app via `eb deploy`  
- Place it in a private VPC, behind a VPN-only ALB  
- Inject all secrets from Secrets Manager using environment variables  
- Use CloudWatch Logs to stream audit info to your Security account  
- Trigger blue/green deploys via GitHub Actions  
- Use Config Rules to enforce that no EC2 instance is public  
- Rotate deployment KMS key monthly, using `kms:KeyRotationEnabled` Config rule  

**Result**: You get DevOps velocity and audit-ready security posture.

---

## Final Thoughts

Elastic Beanstalk is perfect for:

- Legacy apps that need lift-and-shift deployment  
- Teams that want platform automation without losing visibility  
- Workloads that require full-stack control (EC2 + ALB + VPC)  
- DevSecOps workflows that combine automation + auditing + IAM  

But it’s not **“secure by default.”**

- Encrypt everything  
- Control ALB access with WAF and SGs  
- Audit every deploy and role assignment  
- Separate dev/staging/prod environments using tags + SCPs  
- Use external secrets and external RDS  
- Treat it like raw infrastructure with convenience scaffolding
