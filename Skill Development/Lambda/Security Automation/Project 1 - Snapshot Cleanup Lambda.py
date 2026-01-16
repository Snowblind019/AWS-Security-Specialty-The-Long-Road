import boto3
import logging
from datetime import datetime, timezone

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Initialize EC2 client
    ec2 = boto3.client('ec2')

    # Define how old snapshots must be to delete (in days)
    retention_days = 30

    # Get current time (timezone-aware)
    now = datetime.now(timezone.utc)

    # Track what we delete
    deleted_count = 0

    try:
        # Get all snapshots owned by this account
        response = ec2.describe_snapshots(OwnerIds=['self'])

        for snapshot in response['Snapshots']:
            snapshot_id = snapshot['SnapshotId']
            start_time = snapshot['StartTime'] # When snapshot was created
            age_days = (now - start_time).days # Calculate age

            # Check if snapshot is older than retention period
            if age_days > retention_days:
                logger.info(f"Deleting {snapshot_id} - {age_days} days old")

                # Delete the snapshot
                ec2.delete_snapshot(SnapshotId=snapshot_id)
                deleted_count += 1

        logger.info(f"Cleanup complete. Deleted {deleted_count} snapshots.")

        return {
            'statusCode': 200,
            'body': f'Deleted {deleted_count} old snapshots.'
        }
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        return {
            'statusCode': 500,
            'body':f'Error: {e}'
        }