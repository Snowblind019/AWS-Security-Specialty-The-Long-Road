import csv
import boto3
from datetime import datetime

def get_international_taxes(valid_product_lines, billing_bucket, csv_file):
    """Fetch international tax rates from external API (currently unavailable)"""
    try:
        raise Exception("API failure: International Taxes API is currently unavailable.")
    except Exception as error:
        # Alert operations team via SNS when API calls fail
        sns = boto3.client('sns')
        sns_topic_arn = 'arn:aws:sns:us-west-2:522814732220:Winterday2225:3bedf646-9d96-49f5-9498-602777c7da25'
        message = f"Lambda function failed to reach international taxes API for '{billing_bucket}' bucket and file '{csv_file}'. Error: '{error}'."
        sns.publish(
            TopicArn=sns_topic_arn,
            Message=message,
            Subject="Lambda API Call failure"
        )
        print("Published failure to sns topic.")
        raise error

def lambda_handler(event, context):
    s3 = boto3.resource('s3')
    
    # Extract S3 event details: which bucket and file triggered this Lambda
    billing_bucket = event['Records'][0]['s3']['bucket']['name']
    csv_file = event['Records'][0]['s3']['object']['key']
    
    error_bucket = 'billing-errors'
    processed_bucket = 'Processed'
    
    # Download and parse CSV file from S3
    obj = s3.Object(billing_bucket, csv_file)
    data = obj.get()['Body'].read().decode('utf-8').splitlines()
    
    error_found = False
    
    # Business rules for data validation
    valid_product_lines = ['Bakery', 'Meat', 'Dairy']
    valid_currencies = ['USD', 'MXN', 'CAD']
    
    # Validate each billing record against business rules
    for row in csv.reader(data[1:], delimiter=','):
        date = row[6]
        product_line = row[4]
        currency = row[7]
        bill_amount = float(row[8])
        
        # Validate product line
        if product_line not in valid_product_lines:
            error_found = True
            print(f"Error in record {row[0]}: Unrecognized product line: {product_line}.")
            break
        
        # Validate currency code
        if currency not in valid_currencies:
            error_found = True
            print(f"Error in record {row[0]}: Unrecognized currency: {currency}.")
            break
        
        # Validate bill amount is non-negative
        if bill_amount < 0:
            error_found = True
            print(f"Error in record {row[0]}: negative bill amount: {bill_amount}.")
            break
        
        # Validate date format (YYYY-MM-DD)
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            error_found = True
            print(f"Error in record {row[0]}: incorrect date format: {date}.")
            break
    
    # Route file to appropriate bucket based on validation results
    if error_found:
        copy_source = {
            'Bucket': billing_bucket,
            'Key': csv_file
        }
        try:
            s3.meta.client.copy(copy_source, error_bucket, csv_file)
            print(f"Moved erroneous file to: {error_bucket}.")
            s3.Object(billing_bucket, csv_file).delete()
            print("Deleted original file from bucket.")
        except Exception as e:
            print(f"Error while move file: {str(e)}.")
    
    else:
        copy_source = {
            'Bucket': billing_bucket,
            'Key': csv_file
        }
        try:
            s3.meta.client.copy(copy_source, processed_bucket, csv_file)
            print(f"Moved processed file to: {processed_bucket}.")
            s3.Object(billing_bucket, csv_file).delete()
            print("Deleted original file from bucket.")
        except Exception as e:
            print(f"Error while move file: {str(e)}.")