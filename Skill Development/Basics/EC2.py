import boto3

ec2 = boto3.resource('ec2')
instance_name = 'winter-ec2'
instance_id = None

# Check if an instance with this name already exists (excluding terminated instances)
instance_exists = False
for instance in ec2.instances.all():
    if instance.tags:
        for tag in instance.tags:
            if tag['Key'] == 'Name' and tag['Value'] == instance_name:
                instance_exists = True
                instance_id = instance.id
                print(f"An instance named '{instance_name}' with id '{instance_id}' already exists.")
                break
    if instance_exists:
        break

# Launch a new EC2 instance if one doesn't exist
if not instance_exists:
    new_instance = ec2.create_instances(
        ImageId='ami-068c0051b15cdb816',
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        KeyName='Winter0',
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': instance_name
                    }
                ]
            }
        ]
    )
    instance_id = new_instance[0].id
    print(f"Instance named '{instance_name}' with id '{instance_id}' created.")

# Stop the instance
ec2.Instance(instance_id).stop()
print(f"Instance '{instance_name}-{instance_id}' stopped.")

# Start the instance
ec2.Instance(instance_id).start()
print(f"Instance '{instance_name}-{instance_id}' started.")

# Terminate the instance
ec2.Instance(instance_id).terminate()
print(f"Instance '{instance_name}-{instance_id}' has been terminated.")