"""
PROJECT 1: AUTOMATED BACKUP SYSTEM

Objective:
Create an automated system that backs up EC2 log files to S3, manages old backups,
and provides cleanup functionality.

What this project teaches:
- EC2: Create instances, wait for running state, find by tags, terminate
- S3: Create buckets, upload files, list objects, delete objects and buckets
- File operations: Create local files, read directories
- Time-based filtering: Delete backups older than X days

Services used:
- EC2 (compute instances)
- S3 (storage)

Skills practiced:
- Basic AWS resource creation
- File management and uploads
- Lifecycle management (retention policies)
- Error handling with try/except

Main operations:
1. Create S3 bucket for backups
2. Create EC2 instance
3. Simulate log files locally
4. Upload logs to S3 with timestamps
5. List all backups
6. Delete backups older than 7 days
7. Clean up all resources

Real-world application:
- Automated backup systems
- Log archival
- Disaster recovery
"""

import boto3
import os
from datetime import datetime, timedelta
import json

# Initialize clients
ec2 = boto3.client('ec2')
s3 = boto3.client('s3')

# Configuration
BUCKET_NAME = 'winterday-backup-snowbank'
INSTANCE_NAME = 'winter-instance'
REGION = 'us-west-2'
BACKUP_RETENTION_DAYS = 7

# Creating the bucket
def create_backup_bucket():
    """Create S3 bucket for backups"""
    try:
        s3.create_bucket(
            Bucket=BUCKET_NAME,
            CreateBucketConfiguration={'LocationConstraint': REGION}
        )
        print(f"Created bucket: {BUCKET_NAME}")
    except s3.exceptions.BucketAlreadyOwnedByYou:
        print(f"Bucket {BUCKET_NAME} already exists")
    except Exception as e:
        print(f"Error creating bucket: {e}")

# Creating the instance
def create_ec2_instance():
    """Create EC2 instance for backup testing"""
    response = ec2.run_instances(
        ImageId='ami-068c0051b15cdb816',
        InstanceType='t2.micro',
        MinCount=1,
        MaxCount=1,
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [{'Key': 'Name', 'Value': INSTANCE_NAME}]
            }
        ]
    )

    instance_id = response['Instances'][0]['InstanceId']
    print(f"Created EC2 instance: {instance_id}")

    # Wait for instance to be running
    print(f"Waiting for instance to start...")
    waiter = ec2.get_waiter('instance_running')
    waiter.wait(InstanceIds=[instance_id])
    print(f"Instance is running")

    return instance_id

def get_instance_id():
    """Find our EC2 instances by name tag"""
    response = ec2.describe_instances(
        Filters=[
            {'Name': 'tag:Name', 'Values': [INSTANCE_NAME]},
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )

    if response['Reservations']:
        return response['Reservations'][0]['Instances'][0]['InstanceId']
    return None

def simulate_log_files():
    """Create fake log files locally (simulating EC2 logs)"""
    os.makedirs('temp_logs', exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create 3 fake log files
    for i in range(3):
        filename = f'temp_logs/app_log_{timestamp}_{i}.txt'
        with open(filename, 'w') as f:
            f.write(f"Log file created at {datetime.now()}\n")
            f.write(f"Instance: {INSTANCE_NAME}\n")
            f.write(f"Log entry {i}: System operational\n")
        print(f"Created log file: {filename}")

def upload_logs_to_s3():
    """Upload all log files to S3"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_folder = f'backups/{timestamp}/'

    for filename in os.listdir('temp_logs'):
        local_path = f'temp_logs/{filename}'
        s3_key = backup_folder + filename

        s3.upload_file(local_path, BUCKET_NAME, s3_key)
        print(f"Uploaded {filename} to s3://{BUCKET_NAME}/{s3_key}")

    print(f"Backup completed to folder: {backup_folder}")
    return backup_folder

def list_all_backups():
    """List all backup folders in S3"""
    response = s3.list_objects_v2(
        Bucket=BUCKET_NAME,
        Prefix='backups/',
        Delimiter='/'
    )

    if 'CommonPrefixes' not in response:
        print("No backups found")
        return []

    backups = []
    print(f"\nAvailable backups:")
    for prefix in response['CommonPrefixes']:
        folder = prefix['Prefix']
        backups.append(folder)
        print(f"  - {folder}")

    return backups

def delete_old_backups():
    """Delete backups older than BACKUP_RETENTION_DAYS"""
    cutoff_date = datetime.now() - timedelta(days=BACKUP_RETENTION_DAYS)

    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix='backups/')

    if 'Contents' not in response:
        print(f"No backups to clean up")
        return
    
    deleted_count = 0
    for obj in response['Contents']:
        if obj['LastModified'].replace(tzinfo=None) < cutoff_date:
            s3.delete_object(Bucket=BUCKET_NAME, Key=obj['Key'])
            print(f"Deleted old backup: {obj['Key']}")
            deleted_count += 1

    if deleted_count == 0:
        print(f"No old backups to delete")
    else:
        print(f"Deleted {deleted_count} old backup files")

def cleanup_all():
    """Delete all resources created by this project"""
    print("\nStarting cleanup...")

    # Delete all S3 objects
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)
    if 'Contents' in response:
        for obj in response['Contents']:
            s3.delete_object(Bucket=BUCKET_NAME, Key=obj['Key'])
            print(f"Deleted s3://{BUCKET_NAME}/{obj['Key']}")

    # Delete bucket
    s3.delete_bucket(Bucket=BUCKET_NAME)
    print(f"Deleted bucket: {BUCKET_NAME}")

    # Terminate EC2 instance
    instance_id = get_instance_id()
    if instance_id:
        ec2.terminate_instances(InstanceIds=[instance_id])
        print(f"Terminated instance: {instance_id}")

    # Delete local temp files
    import shutil
    if os.path.exists('temp_logs'):
        shutil.rmtree('temp_logs')
        print(f"Deleted local temp_logs folder")

    print(f"Cleanup complete!")

def main():
    """Main menu to run different operations"""
    print("\n" + "="*50)
    print("Automated Backup System")
    print("="*50)
    print("\n1. Setup (Create S3 bucket + EC2 instance)")
    print("2. Simulate logs and backup to S3")
    print("3. List all backups")
    print("4. Delete old backups")
    print("5. Cleanup everything")
    print("6. Exit")

    choice = input("\nEnter choice (1-6): ")  # Removed unnecessary f-string

    if choice == '1':
        create_backup_bucket()
        create_ec2_instance()
    elif choice == '2':
        simulate_log_files()
        upload_logs_to_s3()
    elif choice == '3':
        list_all_backups()
    elif choice == '4':
        delete_old_backups()
    elif choice == '5':
        confirm = input("This will delete EVERYTHING. Continue? (yes/no): ")
        if confirm.lower() == 'yes':
            cleanup_all()
    elif choice == '6':
        print("Goodbye!")
        return
    else:
        print("Invalid choice")

    # Run menu again
    main()

if __name__ == "__main__":
    main()