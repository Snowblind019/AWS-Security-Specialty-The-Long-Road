# Boto3 Hands-On

## Overview

Hands-on boto3 practice to build practical AWS automation skills. Started with individual service walkthroughs to understand how each service works, then combined them into real-world mini-projects.

---

## Individual Service Scripts

| Service | Script | What It Covers |
|---------|--------|----------------|
| S3 | S3.py | Bucket creation, file upload/download, reading objects, cleanup |
| EC2 | EC2.py | Instance creation, start/stop/terminate, tagging, state checking |
| RDS | RDS.py | Aurora Serverless cluster creation, scaling configuration, instance management |
| VPC | VPC.py | VPC creation, subnets, internet gateways, route tables |

---

## Mini-Projects

| # | Project | Services Used | What It Demonstrates |
|---|---------|---------------|----------------------|
| 01 | Automated Backup System | S3, EC2 | Backup lifecycle management, file uploads, retention policies |
| 02 | Database-Backed Web Infrastructure | VPC, EC2, RDS | Network architecture, security groups, multi-AZ deployment |
| 03 | Resource Inventory System | EC2, S3, RDS, VPC | Describe operations, JSON reporting, change tracking |

---

## Learning Approach

Worked through guided walkthroughs for each service, typing everything out and asking questions until it made sense. Then combined multiple services into mini-projects to see how they work together in practice.

Key realization: memorizing syntax upfront isn't the goal. Understanding what the code does and getting comfortable with documentation is what matters. The syntax sticks naturally with use.

---

## Skills Developed

- boto3 client and resource interfaces
- CRUD operations across AWS services
- VPC networking (subnets, gateways, route tables, security groups)
- RDS cluster and instance management
- Error handling with try/except and AWS-specific exceptions
- Waiters for async resource creation
- Describe operations for inventory and auditing
- JSON handling for reports and data export
