import json
import boto3
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Initialize EC2 client using boto3
    ec2 = boto3.client('ec2')
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        # Create snapshot of the specified EBS volume
        response = ec2.create_snapshot(
            VolumeId='vol-0b20e35b923a2bcb4',
            Description='My EC2 Snapshot',
            TagSpecifications=[
                {
                    'ResourceType': 'snapshot',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': f"My EC2 snapshot {current_date}"
                        }
                    ]
                }
            ]
        )
        logger.info(f"Successfully created snapshot: {json.dumps(response, default=str)}")
    except Exception as e:
        logger.error(f"Error creating snapshot: {e}")

if __name__ == "__main__":
    lambda_handler({}, None)