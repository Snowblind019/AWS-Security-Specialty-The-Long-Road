import boto3

def lambda_handler(event, context):
    # Initialize EC2 resource using boto3
    ec2_resource = boto3.resource('ec2')
    
    # Iterate through all Elastic IP addresses in the VPC
    for elastic_ip in ec2_resource.vpc_addresses.all():
        # Check if the Elastic IP is not associated with any instance
        if elastic_ip.instance_id is None:
            print(f"No association for elastic IP: {elastic_ip}. Releasing...")
            # Release the unassociated Elastic IP
            elastic_ip.release()
    
    return {
        'statusCode': 200,
        'body': 'Processed elastic IPs.'
    }