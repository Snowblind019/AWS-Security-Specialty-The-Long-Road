# Scenario: You want to upload a file to S3, but only if it doesn't already exist (to avoid overwriting important data).
# Your Task:


# Create a bucket called winter-backup-test
# Upload a file called important.txt (create it locally first with some content)
# Write code that checks if important.txt already exists in the bucket before uploading
# If it exists, print "File already exists, skipping upload"
# If it doesn't exist, upload it and print "File uploaded successfully"


# Hint: You'll need to list objects in the bucket and check if your filename is in that list.


import boto3
# Specifying what resource (S3 in this case)
s3 = boto3.resource('s3')
bucket_name = 'winter-backup-test'
important = 'important.txt'


# Create the bucket but check if it exists first
all_buckets = [bucket.name for bucket in s3.buckets.all()]
if bucket_name not in all_buckets:
    s3.create_bucket(Bucket=bucket_name)
    
# Get all stuff in the bucket
objects_in_bucket = [obj.key for obj in s3.Bucket(bucket_name).objects.all()]


# Check if the file already exists in the bucket
if important in objects_in_bucket:
    print(f"Fie already exists, skipping upload")
else: 
    s3.Bucket(bucket_name).upload_file(Filename=important, Key=important)
    print(f"File uploaded successfully")
