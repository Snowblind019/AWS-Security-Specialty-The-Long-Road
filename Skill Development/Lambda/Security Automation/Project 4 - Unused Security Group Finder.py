import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    
    # Track findings
    unused_groups = []
    used_groups = []
    
    # Get all security groups
    response = ec2.describe_security_groups()
    
    for sg in response['SecurityGroups']:
        group_id = sg['GroupId']
        group_name = sg['GroupName']
        
        # Skip the default security group as it can't be deleted anyway
        if group_name == 'default':
            continue
        
        # Check if security group is in use
        # Look for network interfaces using this security group
        eni_response = ec2.describe_network_interfaces(
            Filters=[
                {
                    'Name': 'group-id',
                    'Values': [group_id]
                }
            ]
        )
        
        attached_count = len(eni_response['NetworkInterfaces'])
        
        if attached_count == 0:
            unused_groups.append({
                'group_id': group_id,
                'group_name': group_name,
                'description': sg['Description'],
                'vpc_id': sg.get('VpcId', 'EC2-Classic')
            })
            logger.warning(f"Unused: {group_name} ({group_id})")
        else:
            used_groups.append({
                'group_id': group_id,
                'group_name': group_name,
                'attached_to': attached_count
            })
            logger.info(f"In use: {group_name} ({group_id}) - {attached_count} ENIs")
    
    # Summary
    total = len(response['SecurityGroups']) - 1  # Subtract default
    logger.info(f"Scan complete: {len(unused_groups)}/{total} unused")
    
    return {
        'statusCode': 200,
        'body': {
            'total_security_groups': total,
            'unused_count': len(unused_groups),
            'used_count': len(used_groups),
            'unused_groups': unused_groups
        }
    }