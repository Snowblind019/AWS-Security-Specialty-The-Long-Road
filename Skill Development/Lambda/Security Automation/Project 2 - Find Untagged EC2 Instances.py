import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    ec2 = boto3.resource('ec2')

    # Tags that every instance must have
    required_tags = ['Name', 'Environment', 'Owner', 'Project']

    # Track non-compliant = []
    non_compliant = []

    # Check all instances
    for instance in ec2.instances.all():
        instance_id = instance.id

    # Get existing tag keys (or empty list if no tags)
    if instance.tags:
        existing_tags = [tag['Key'] for tag in instance.tags]
    else:
        existing_tags = []

    # Find which required tags are missing
    missing_tags = []
    for tag in required_tags:
        if tag not in existing_tags:
            missing_tags.append(tag)

    # If any tags are missing, add to non-compliant list
    if missing_tags:
        non_compliant.append({
            'instance_id': instance_id,
            'state': instance.state['Name'],
            'missing_tags': missing_tags
        })
        logger.warning(f"{instance_id}: missing {missing_tags}")

    # Summary
    total_instances = len(list(ec2.instances.all()))
    compliant_count = total_instances - len(non_compliant)

    logger.info(f"Scan complete: {compliant_count}/{total_instances} compliant")

    return {
        'statusCode': 200,
        'body': {
            'total_instances': total_instances,
            'compliant': compliant_count,
            'non_compliant': len(non_compliant),
            'details': non_compliant
        }
    }