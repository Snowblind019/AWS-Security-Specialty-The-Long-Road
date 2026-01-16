# Lambda Automation

Serverless automation functions built after learning Lambda fundamentals.

## Security Automation

Six Lambda functions for AWS security compliance and cost optimization:

1. **Snapshot Cleanup** - Delete EBS snapshots older than 30 days
2. **Tag Compliance Checker** - Audit EC2 instances for required tags
3. **S3 Public Access Scanner** - Identify publicly accessible buckets
4. **Unused Security Groups** - Find security groups with no attachments
5. **IAM Access Key Auditor** - Flag access keys older than 90 days
6. **Auto-Stop Instances** - Cost optimization via AutoStop tags

**Use cases:** Security compliance auditing, cost optimization, automated remediation

## Learning Labs

Practice exercises from coursework to understand Lambda event patterns:

- **EC2 Backups** - Scheduled snapshot creation
- **RDS CSV Importer** - S3 trigger → Aurora Serverless import
- **S3 CSV Validator** - Real-time validation on upload
- **VPC EIP Cleanup** - Release unassociated Elastic IPs

**Purpose:** Understand S3 event triggers, scheduled events, and Lambda execution patterns

## Key Concepts Learned

- Event-driven architecture (S3 uploads, CloudWatch schedules)
- IAM policies for Lambda execution roles
- Error handling with CloudWatch logging
- Boto3 client vs resource interfaces
- AWS-specific exception handling

## What's Next

These single-function automations led to multi-service architectures in `Advanced/`:
- **SNS/SQS** - Event-driven CSV validation with retry logic
- **Glue/EMR** - Big data processing pipelines

---

**Note:** Learning Labs contain hardcoded values and are for educational purposes.