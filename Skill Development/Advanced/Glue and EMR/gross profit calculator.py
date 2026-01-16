from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# Initialize Spark session with Hive support for table access
spark = SparkSession.builder.appName('data_processing').enableHiveSupport().getOrCreate()
spark.sql("use `dct-billing`")

# Load and filter source tables to remove invalid records
bills_df = spark.table('dct_billing_processed_1').filter(col('id').isNotNull())
unit_sold_df = spark.table('units_sold').filter(col('company_id').isNotNull())
production_costs_df = spark.table('production_costs').filter(col('cost_per_unit_usd').isNotNull())

# Join billing data with units sold and production costs
# Drops redundant columns after each join to keep schema clean
joined_df = (
    bills_df.join(unit_sold_df, bills_df.id == unit_sold_df.company_id)
    .drop('company_id')
    .join(production_costs_df, bills_df.item_sold == production_costs_df.item)
    .drop(bills_df.item_sold)
    .drop(unit_sold_df.item_type)
)

# Calculate gross profit: revenue minus total production costs
gross_profit_df = joined_df.withColumn('gross_profit', (joined_df.bill_amount - (joined_df.units_sold * joined_df.cost_per_unit_usd)))

# Select final columns for report output
gross_profit_df = gross_profit_df.select('id', 'company_name', 'item', 'bill_amount', 'units_sold', 'cost_per_unit_usd', 'gross_profit')

# Write results to S3 as CSV with headers
gross_profit_df.write.option('header', 'true').csv('s3://dct-billing-data-lake-x/reports/gross_profit_output')