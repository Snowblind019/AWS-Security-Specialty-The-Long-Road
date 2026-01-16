import boto3
import logging
from datetime import datetime, timezone

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    iam = boto3.client('iam')
    
    # How old is too old (in days)
    max_age_days = 90
    
    # Track findings
    old_keys = []
    compliant_keys = []
    
    # Get current time
    now = datetime.now(timezone.utc)
    
    # Get all IAM users
    users_response = iam.list_users()
    
    for user in users_response['Users']:
        username = user['UserName']
        
        # Get access keys for this user
        keys_response = iam.list_access_keys(UserName=username)
        
        for key in keys_response['AccessKeyMetadata']:
            key_id = key['AccessKeyId']
            status = key['Status']  # Active or Inactive
            created = key['CreateDate']
            
            # Calculate age
            age_days = (now - created).days
            
            # Build key info
            key_info = {
                'username': username,
                'key_id': key_id,
                'status': status,
                'age_days': age_days,
                'created': created.strftime('%Y-%m-%d')
            }
            
            # Check if key is old and active (inactive keys are less risky)
            if age_days > max_age_days and status == 'Active':
                old_keys.append(key_info)
                logger.warning(f"OLD KEY: {username} - {key_id} - {age_days} days old")
            else:
                compliant_keys.append(key_info)
    
    # Summary
    logger.info(f"Scan complete: {len(old_keys)} old active keys found")
    
    return {
        'statusCode': 200,
        'body': {
            'total_keys': len(old_keys) + len(compliant_keys),
            'old_active_keys': len(old_keys),
            'compliant_keys': len(compliant_keys),
            'max_age_days': max_age_days,
            'findings': old_keys
        }
    }