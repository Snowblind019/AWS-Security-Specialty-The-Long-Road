import boto3
import logging
from datetime import datetime, timezone

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    
    # Tag that marks instances for auto-stop
    auto_stop_tag = 'AutoStop'
    auto_stop_value = 'true'
    
    # Track actions
    stopped_instances = []
    already_stopped = []
    skipped = []
    
    # Find instances with AutoStop=true tag
    response = ec2.describe_instances(
        Filters=[
            {
                'Name': f'tag:{auto_stop_tag}',
                'Values': [auto_stop_value]
            }
        ]
    )
    
    # Loop through reservations and instances
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            state = instance['State']['Name']
            
            # Get instance name from tags
            name = 'No Name'
            if instance.get('Tags'):
                for tag in instance['Tags']:
                    if tag['Key'] == 'Name':
                        name = tag['Value']
                        break
            
            # Only stop running instances
            if state == 'running':
                try:
                    ec2.stop_instances(InstanceIds=[instance_id])
                    stopped_instances.append({
                        'instance_id': instance_id,
                        'name': name
                    })
                    logger.info(f"Stopped: {name} ({instance_id})")
                except Exception as e:
                    skipped.append({
                        'instance_id': instance_id,
                        'name': name,
                        'error': str(e)
                    })
                    logger.error(f"Failed to stop {name} ({instance_id}): {e}")
            else:
                already_stopped.append({
                    'instance_id': instance_id,
                    'name': name,
                    'state': state
                })
                logger.info(f"Already {state}: {name} ({instance_id})")
    
    # Summary
    logger.info(f"Completed: stopped {len(stopped_instances)}, already stopped {len(already_stopped)}")
    
    return {
        'statusCode': 200,
        'body': {
            'stopped': stopped_instances,
            'already_stopped': already_stopped,
            'errors': skipped,
            'summary': {
                'stopped_count': len(stopped_instances),
                'already_stopped_count': len(already_stopped),
                'error_count': len(skipped)
            }
        }
    }