import boto3

s3 = boto3.resource('s3')
bucket_name = 's3-bucket-crud1234'

# Check if the bucket exists, create if it doesn't
all_my_buckets = [bucket.name for bucket in s3.buckets.all()]
if bucket_name not in all_my_buckets:
    print(f"{bucket_name} bucket does not exist. Creating now...")
    s3.create_bucket(Bucket=bucket_name)
    print(f"{bucket_name} bucket has been created.")
else:
    print(f"{bucket_name} bucket already exists. No need to create a new one.")

# Upload files to the bucket
file_1 = 'file_1.txt'
file_2 = 'file_2.txt'
s3.Bucket(bucket_name).upload_file(Filename=file_1, Key=file_1)
s3.Bucket(bucket_name).upload_file(Filename=file_2, Key=file_2)

# Read and print file contents from bucket
obj = s3.Object(bucket_name, file_1)
body = obj.get()['Body'].read()
print(body)

# Update file_1 with contents from file_2
s3.Object(bucket_name, file_1).put(Body=open(file_2, 'rb'))
obj = s3.Object(bucket_name, file_1)
body = obj.get()['Body'].read()
print(body)

# Cleanup: Delete files and bucket
s3.Object(bucket_name, file_1).delete()
s3.Object(bucket_name, file_2).delete()
bucket = s3.Bucket(bucket_name)
bucket.delete()