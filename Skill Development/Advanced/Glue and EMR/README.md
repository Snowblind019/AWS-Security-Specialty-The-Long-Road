# AWS Glue and EMR Gross Profit Calculator

Calculate gross profit from billing data using AWS Glue Data Catalog and Amazon EMR with PySpark.

## What It Does

Joins three CSV datasets (billing transactions, units sold, production costs) to calculate gross profit:
```
Gross Profit = Revenue - (Units Sold × Cost Per Unit)
```

## Architecture
```
S3 CSV Files → Glue Crawler → Glue Catalog → EMR (PySpark) → S3 Reports
```

## Quick Start

### 1. Upload Data
```bash
aws s3 cp sample_data/ s3://your-bucket/ --recursive
```

### 2. Run Glue Crawler
```bash
aws glue create-crawler --name billing-crawler --role AWSGlueServiceRole \
  --database-name dct-billing \
  --targets '{"S3Targets":[{"Path":"s3://your-bucket/"}]}'

aws glue start-crawler --name billing-crawler
```

### 3. Launch EMR & Run Script
```bash
# Create cluster
aws emr create-cluster \
  --name "Billing Analytics" \
  --release-label emr-6.15.0 \
  --applications Name=Spark \
  --instance-type m5.xlarge \
  --instance-count 3 \
  --configurations file://emr_software_settings.json \
  --auto-terminate

# Submit job
aws emr add-steps --cluster-id j-XXXXX \
  --steps Type=Spark,Name="Calculate Profit",\
Args=[s3://your-bucket/gross_profit_calculator.py]
```

### 4. Check Output
```bash
aws s3 ls s3://your-bucket/reports/
```

## Files
```
├── gross_profit_calculator.py    # PySpark script
├── emr_software_settings.json    # Glue integration config
└── Sample Data/
    ├── billing_data_dairy_07_2023.csv
    ├── units_sold_07_2023.csv
    └── production_costs_07_2023.csv
```

## Sample Output

| company_name | item | bill_amount | units_sold | cost_per_unit | gross_profit |
|--------------|------|-------------|------------|---------------|--------------|
| Lone Star Lactose | Artisan Cheese | $3,525 | 900 | $2.50 | **$1,275** |
| Houston Creamery | Organic Milk | $4,050 | 1,500 | $1.50 | **$1,800** |

## How the PySpark Script Works
```python
# 1. Load tables from Glue Catalog
bills_df = spark.table('billing_data')
units_df = spark.table('units_sold')
costs_df = spark.table('production_costs')

# 2. Join all three tables
joined_df = (bills_df
    .join(units_df, bills_df.id == units_df.company_id)
    .join(costs_df, bills_df.item == costs_df.item))

# 3. Calculate gross profit
result = joined_df.withColumn('gross_profit', 
    col('bill_amount') - (col('units_sold') * col('cost_per_unit_usd')))

# 4. Write to S3
result.write.csv('s3://bucket/reports/')
```

## Key Config: emr_software_settings.json

Tells EMR to use Glue as the metastore:
```json
[{
  "Classification": "spark-hive-site",
  "Properties": {
    "hive.metastore.client.factory.class": 
      "com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory"
  }
}]
```

## IAM Permissions Needed

**Glue Crawler**: S3 read, Glue write  
**EMR Cluster**: S3 read/write, Glue read

## Cost Optimization

- Use `--auto-terminate` on EMR clusters
- Use Spot instances for 70% savings
- Compress output with Snappy/Gzip

## Use Cases

- Financial reporting and profit analysis
- Product line performance tracking
- Cost vs. revenue optimization
- Executive dashboards