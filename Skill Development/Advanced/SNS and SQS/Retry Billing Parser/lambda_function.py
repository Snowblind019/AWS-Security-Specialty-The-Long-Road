import csv
import boto3
from datetime import datetime
import re

def lambda_handler(event, context):
    s3 = boto3.resource('s3')
    
    # Parse SQS message to extract bucket and file information
    message = event['Records'][0]['body']
    match = re.search("for '(.*?)' bucket and file '(.*?)'", message)
    if match:
        billing_bucket, csv_file = match.groups()
    else:
        print(f"Error parsing message: {message}.")
        return
    
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