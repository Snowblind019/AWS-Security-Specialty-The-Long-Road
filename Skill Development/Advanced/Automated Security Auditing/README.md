# AWS Security Group Auditor

Automated Lambda function that scans EC2 security groups for overly permissive rules (0.0.0.0/0) and sends SNS alerts when found.

## Architecture
- **EventBridge Scheduler** → triggers Lambda daily
- **Lambda (Python/boto3)** → scans security groups for 0.0.0.0/0 rules
- **SNS** → sends email alerts for findings

## Setup
1. Update `sns_topic_arn` in `lambda_function.py` with your SNS topic
2. Create Lambda with execution role permissions:
   - `ec2:DescribeSecurityGroups`
   - `sns:Publish`
3. Configure EventBridge rule to trigger Lambda on schedule

## What It Does
Iterates through all security groups, checks inbound rules for 0.0.0.0/0, and publishes warnings to SNS when found.

## Potential Enhancements
- Check egress rules
- Flag specific high-risk ports (SSH, RDP, databases)
- Multi-region scanning
- Automatic remediation

---
*Hands-on project from Digital Cloud Training*