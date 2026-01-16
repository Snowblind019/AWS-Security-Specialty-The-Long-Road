# SNS and SQS Billing CSV Validator

Automated CSV validation with error handling and retry logic. When API calls fail, SNS notifies via email and queues retry through SQS.

## Architecture
```
S3 Upload → Lambda (Validate + API Call) → Fails? → SNS (email) + SQS → Lambda (Retry)
                                         → Success? → Move to processed/
```

## What It Does

1. CSV uploaded to S3 triggers `BillingBucketParser` Lambda
2. Validates product lines, currencies, amounts, date format
3. Attempts 3rd-party international tax API call
4. **On failure**: Publishes to SNS (email alert) + SQS (retry queue)
5. `RetryBillingParser` Lambda triggered by SQS, retries without API dependency
6. Valid files → `processed/` bucket, invalid → `error/` bucket

## Project Structure
```
├── Billing Bucket Parser/
│   ├── lambda_function.py    # Initial validator with API call
│   ├── event.json            # S3 trigger test event
│   └── template.yaml         # SAM template
└── Retry Billing Parser/
    ├── lambda_function.py    # Retry validator (SQS triggered)
    ├── event.json            # SQS message test event
    └── template.yaml         # SAM template
```

## Quick Start

```bash
# Deploy both functions
cd "Billing Bucket Parser" && sam deploy --guided
cd "../Retry Billing Parser" && sam deploy --guided

# Wire it up
aws sns subscribe --topic-arn <ARN> --protocol email --notification-endpoint you@email.com
aws sns subscribe --topic-arn <SNS_ARN> --protocol sqs --notification-endpoint <SQS_ARN>
```

**Required resources**: S3 buckets (`winterday-billing`, `billing-errors`, `Processed`), SNS topic, SQS queue

**IAM permissions**: S3 read/write, SNS publish, SQS receive/delete

## Validation Rules

- Product line: Bakery, Meat, or Dairy
- Currency: USD, MXN, or CAD  
- Bill amount: positive float
- Date: YYYY-MM-DD format

## Key Code: Retry Message Parsing

```python
# RetryBillingParser extracts bucket/file from SNS message using regex
match = re.search(r"'(.+?)' bucket and file '(.+?)'", message)
bucket = match.group(1)
file = match.group(2)
```

## Use Cases

- Resilient ETL pipelines with 3rd-party API dependencies
- Automated data quality checks with retry logic
- Financial data processing with audit trails