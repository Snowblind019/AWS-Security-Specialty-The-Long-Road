"""
PROJECT 2: DATABASE-BACKED WEB INFRASTRUCTURE

Objective:
Build a complete network infrastructure where an EC2 instance can securely
communicate with an RDS database cluster in a private VPC.

What this project teaches:
- VPC: Create isolated networks with subnets across availability zones
- Networking: Internet gateways, route tables, security groups
- RDS: Create Aurora Serverless PostgreSQL clusters
- Security: Firewall rules controlling traffic between resources

Services used:
- VPC (networking)
- EC2 (compute)
- RDS (database)
- Security Groups (firewalls)

Skills practiced:
- Network architecture design
- Multi-AZ deployment for high availability
- Security group configuration
- Database cluster creation
- Resource dependencies and creation order

Main operations:
1. Create VPC with custom IP range (10.0.0.0/16)
2. Create 3 subnets across different availability zones
3. Create and attach internet gateway
4. Create route table with internet access
5. Create security groups (EC2 and RDS)
6. Create DB subnet group
7. Create RDS Aurora Serverless cluster
8. Create EC2 instance that can connect to RDS
9. Clean up in reverse dependency order

Real-world application:
- Web application infrastructure
- Secure database deployments
- Multi-tier architectures
- Production-grade networking
"""

import boto3
import time

# Initialize clients
ec2 = boto3.client('ec2')
rds = boto3.client('rds')

# Configuration
PROJECT_NAME = 'wintery-db'
REGION = 'us-west-2'
VPC_CIDR = '10.0.0.0/16'
USERNAME_DB = 'Winter'
PASSWORD_DB = 'Winterday'

# Store resource IDs
resources = {
    'vpc_id': None,
    'subnet_ids': [],
    'igw_id': None,
    'route_table_id': None,
    'sg_ec2_id': None,
    'sg_rds_id': None,
    'instance_id': None,
    'db_subnet_group_name': None,
    'db_cluster_id': None
}

def create_vpc():
    """Create a VPC for our infrastructure"""
    response = ec2.create_vpc(
        CidrBlock=VPC_CIDR,
        TagSpecifications=[
            {
                'ResourceType': 'vpc',
                'Tags':[{'Key': 'Name', 'Value': f'{PROJECT_NAME}-vpc'}]
            }
        ]
    )

    vpc_id = response['Vpc']['VpcId']
    resources['vpc_id'] = vpc_id

    # Enable DNS hostnames
    ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsHostnames={'Value': True})

    print(f"Created VPC: {vpc_id}")
    return vpc_id

def create_subnets(vpc_id):
    """Create 3 subnets in different availability zones"""
    
    # Get available AZs in the region
    azs_response = ec2.describe_availability_zones(  
        Filters=[{'Name': 'state', 'Values': ['available']}]
    )
    azs = [az['ZoneName'] for az in azs_response['AvailabilityZones']][:3]

    subnet_ids = []

    # Create 3 subnets with different IP ranges
    subnet_configs = [
        ('10.0.1.0/24', azs[0]),
        ('10.0.2.0/24', azs[1]),
        ('10.0.3.0/24', azs[2])
    ]

    for i, (cidr, az) in enumerate(subnet_configs, 1):
        response = ec2.create_subnet(
            VpcId=vpc_id,
            CidrBlock=cidr,
            AvailabilityZone=az,
            TagSpecifications=[
                {
                    'ResourceType': 'subnet',
                    'Tags': [{'Key': 'Name', 'Value': f'{PROJECT_NAME}-subnet-{i}'}]
                }
            ]
        )

        subnet_id = response['Subnet']['SubnetId']
        subnet_ids.append(subnet_id)
        print(f"Created Subnet {i}: {subnet_id} in {az}")

    resources['subnet_ids'] = subnet_ids
    return subnet_ids

def create_internet_gateway(vpc_id):
    """Create and attach internet gateway"""
    
    # Create IGW
    response = ec2.create_internet_gateway(
        TagSpecifications=[
            {
                'ResourceType': 'internet-gateway',
                'Tags': [{'Key': 'Name', 'Value': f'{PROJECT_NAME}-igw'}]
            }
        ]
    )

    igw_id = response['InternetGateway']['InternetGatewayId']
    resources['igw_id'] = igw_id

    # Attach to VPC
    ec2.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)

    print(f"Created and attached Internet Gateway: {igw_id}")
    return igw_id

def create_route_table(vpc_id, igw_id, subnet_ids):
    """Create route table with internet access"""
    
    # Create route table
    response = ec2.create_route_table(
        VpcId=vpc_id,
        TagSpecifications=[
            {
                'ResourceType': 'route-table',
                'Tags': [{'Key': 'Name', 'Value': f'{PROJECT_NAME}-rtb'}]
            }
        ]
    )

    route_table_id = response['RouteTable']['RouteTableId']
    resources['route_table_id'] = route_table_id
    
    # Add route to internet gateway
    ec2.create_route(
        RouteTableId=route_table_id,
        DestinationCidrBlock='0.0.0.0/0',
        GatewayId=igw_id
    )

    # Associate route table with all subnets
    for subnet_id in subnet_ids:
        ec2.associate_route_table(RouteTableId=route_table_id, SubnetId=subnet_id)

    print(f"Created Route Table: {route_table_id}")
    return route_table_id

def create_security_groups(vpc_id):
    """Create security groups for EC2 and RDS"""
    
    # EC2 Security Group
    response_ec2 = ec2.create_security_group(
        GroupName=f'{PROJECT_NAME}-ec2-sg',
        Description='Security group for EC2 instance',
        VpcId=vpc_id,
        TagSpecifications=[
            {
                'ResourceType': 'security-group',
                'Tags': [{'Key': 'Name', 'Value': f'{PROJECT_NAME}-ec2-sg'}]
            }
        ]
    )

    sg_ec2_id = response_ec2['GroupId']
    resources['sg_ec2_id'] = sg_ec2_id

    # Add SSH rule to EC2 security group
    ec2.authorize_security_group_ingress(
        GroupId=sg_ec2_id,
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'SSH access'}]
            }
        ]
    )

    print(f"Created EC2 Security Group: {sg_ec2_id}")

    # RDS Security Group
    response_rds = ec2.create_security_group(
        GroupName=f'{PROJECT_NAME}-rds-sg',
        Description='Security group for RDS cluster',
        VpcId=vpc_id,
        TagSpecifications=[
            {
                'ResourceType': 'security-group',
                'Tags': [{'Key': 'Name', 'Value': f'{PROJECT_NAME}-rds-sg'}]
            }
        ]
    )

    sg_rds_id = response_rds['GroupId']
    resources['sg_rds_id'] = sg_rds_id

    # Add PostgreSQL rule
    ec2.authorize_security_group_ingress(
        GroupId=sg_rds_id,
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 5432,
                'ToPort': 5432,
                'UserIdGroupPairs': [
                    {
                        'GroupId': sg_ec2_id,
                        'Description': 'PostgreSQL from EC2'
                    }
                ]
            }
        ]
    )

    print(f"Created RDS Security Group: {sg_rds_id}")

    return sg_ec2_id, sg_rds_id

def create_db_subnet_group(subnet_ids):
    """Create DB subnet for RDS"""
    db_subnet_group_name = f'{PROJECT_NAME}-db-subnet-group'

    rds.create_db_subnet_group(
        DBSubnetGroupName=db_subnet_group_name,
        DBSubnetGroupDescription='Subnet group for winter RDS cluster',
        SubnetIds=subnet_ids,
        Tags=[{'Key': 'Name', 'Value': db_subnet_group_name}]
    )

    resources['db_subnet_group_name'] = db_subnet_group_name
    print(f"Created DB Subnet Group: {db_subnet_group_name}")
    return db_subnet_group_name

def create_rds_cluster(db_subnet_group_name, sg_rds_id):
    """Create RDS Aurora Serverless cluster"""
    cluster_id = f'{PROJECT_NAME}-cluster'

    response = rds.create_db_cluster(
        DBClusterIdentifier=cluster_id,
        Engine='aurora-postgresql',
        EngineMode='provisioned',
        EngineVersion='15.4',
        MasterUsername=USERNAME_DB,
        MasterUserPassword=PASSWORD_DB,
        DBSubnetGroupName=db_subnet_group_name,
        VpcSecurityGroupIds=[sg_rds_id],
        ServerlessV2ScalingConfiguration={
            'MinCapacity': 0.5,
            'MaxCapacity': 1
        },
        Tags=[{'Key': 'Name', 'Value': cluster_id}]
    )

    resources['db_cluster_id'] = cluster_id
    print(f"Created RDS Cluster: {cluster_id}")

    # Create DB instance in the cluster
    instance_id = f'{cluster_id}-instance-1'

    rds.create_db_instance(
        DBInstanceIdentifier=instance_id,
        DBInstanceClass='db.serverless',
        Engine='aurora-postgresql',
        DBClusterIdentifier=cluster_id,
        Tags=[{'Key': 'Name', 'Value': instance_id}]
    )

    print(f"Creating DB Instance: {instance_id}")
    print(f"Waiting for RDS cluster to become available (this takes 5-10 minutes)...")

    # Wait for cluster to be available
    waiter = rds.get_waiter('db_cluster_available')
    waiter.wait(DBClusterIdentifier=cluster_id)

    print(f"RDS Cluster is now available!")

    # Get endpoint
    cluster_info = rds.describe_db_clusters(DBClusterIdentifier=cluster_id)
    endpoint = cluster_info['DBClusters'][0]['Endpoint']
    print(f"Database Endpoint: {endpoint}")

    return cluster_id


def create_ec2_instance(subnet_id, sg_ec2_id):
    """Create EC2 instance in the VPC"""
    response = ec2.run_instances(
        ImageId='ami-068c0051b15cdb816',
        InstanceType='t2.micro',
        MinCount=1,
        MaxCount=1,
        SubnetId=subnet_id,
        SecurityGroupIds=[sg_ec2_id],
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [{'Key': 'Name', 'Value': f'{PROJECT_NAME}-instance'}]
            }
        ]
    )

    instance_id = response['Instances'][0]['InstanceId']
    resources['instance_id'] = instance_id

    print(f"Created EC2 Instance: {instance_id}")
    print(f"Waiting for instance to be running...")

    waiter = ec2.get_waiter('instance_running')
    waiter.wait(InstanceIds=[instance_id])

    print(f"EC2 Instance is running!")
    return instance_id


def show_infrastructure_info():
    """Display information about created resources"""
    print("\n" + "="*60)
    print("Infrastructure Summary")
    print("="*60)

    print(f"\n VPC")
    print(f"ID: {resources['vpc_id']}")
    print(f"CIDR: {VPC_CIDR}")

    print(f"\n Subnets:")
    for i, subnet_id in enumerate(resources['subnet_ids'], 1): 
        print(f"Subnet {i}: {subnet_id}")
    
    print(f"\n Security Groups:")
    print(f"EC2: {resources['sg_ec2_id']}")
    print(f"RDS: {resources['sg_rds_id']}")
    
    print(f"\n EC2 Instance:")
    print(f"ID: {resources['instance_id']}")

    print(f"\n RDS Cluster:")
    print(f"ID: {resources['db_cluster_id']}")

    # Get RDS endpoint
    if resources['db_cluster_id']:
        cluster_info = rds.describe_db_clusters(
            DBClusterIdentifier=resources['db_cluster_id']
        )
        endpoint = cluster_info['DBClusters'][0]['Endpoint']
        print(f"Endpoint: {endpoint}")
        print(f"Username: {USERNAME_DB}")
        print(f"Database: postgres (default)")

    print("\n" + "="*60)

def cleanup_all():
    """Delete all resources in correct order"""
    print(f"\n Starting cleanup...")

    # Delete EC2 instance
    if resources['instance_id']:
        print(f"Terminating EC2 instance...")
        ec2.terminate_instances(InstanceIds=[resources['instance_id']])
        waiter = ec2.get_waiter('instance_terminated')
        waiter.wait(InstanceIds=[resources['instance_id']])
        print(f"EC2 instance terminated")

    # Delete RDS cluster
    if resources['db_cluster_id']:
        print(f"Deleting RDS cluster (this takes 5-10 minutes)...")
        
        # Get instance IDs in cluster
        cluster_info = rds.describe_db_clusters(
            DBClusterIdentifier=resources['db_cluster_id']
        )
        instance_ids = [member['DBInstanceIdentifier'] for member in cluster_info['DBClusters'][0]['DBClusterMembers']]

        # Delete instances first
        for instance_id in instance_ids:
            rds.delete_db_instance(
                DBInstanceIdentifier=instance_id,
                SkipFinalSnapshot=True
            )
            print(f"Deleting DB instance: {instance_id}")

        # Wait for instances to be deleted
        time.sleep(30)
        
        # Delete cluster
        rds.delete_db_cluster(
            DBClusterIdentifier=resources['db_cluster_id'],
            SkipFinalSnapshot=True
        )
        print(f"RDS cluster deletion started")

    # Delete DB subnet group
    if resources['db_subnet_group_name']:
        time.sleep(60)
        try:
            rds.delete_db_subnet_group(
                DBSubnetGroupName=resources['db_subnet_group_name']
            )
            print(f"Deleted DB subnet group")
        except Exception as e:
            print(f"DB subnet group: {e}")

    # Delete security groups
    time.sleep(10)
    for sg_id in [resources['sg_rds_id'], resources['sg_ec2_id']]:
        if sg_id:
            try:
                ec2.delete_security_group(GroupId=sg_id)
                print(f"Deleted security group: {sg_id}")
            except Exception as e:
                print(f"Security group: {e}")

    # Detach and delete internet gateway
    if resources['igw_id'] and resources['vpc_id']:
        ec2.detach_internet_gateway(
            InternetGatewayId=resources['igw_id'],
            VpcId=resources['vpc_id']
        )
        ec2.delete_internet_gateway(InternetGatewayId=resources['igw_id'])
        print(f"Deleted internet gateway")

    # Delete route table
    if resources['route_table_id']:
        try:
            ec2.delete_route_table(RouteTableId=resources['route_table_id'])
            print(f"Deleted route table")
        except Exception as e:
            print(f"Route table: {e}")
            
    # Delete subnets
    for subnet_id in resources['subnet_ids']:
        ec2.delete_subnet(SubnetId=subnet_id)
        print(f"Deleted subnet: {subnet_id}")

    # Delete VPC
    if resources['vpc_id']:
        ec2.delete_vpc(VpcId=resources['vpc_id'])
        print(f"Deleted VPC")

    print(f"\n Cleanup complete!")

def main():
    """Main menu"""
    print("\n" + "="*60)
    print("  DATABASE INFRASTRUCTURE PROJECT")
    print("="*60)
    print("\n1. Create full infrastructure")
    print("2. Show infrastructure info")
    print("3. Cleanup everything")
    print("4. Exit")
    
    choice = input("\nEnter choice (1-4): ")
    
    if choice == '1':
        print("\nCreating infrastructure...\n")
        
        # Create VPC
        vpc_id = create_vpc()
        
        # Create subnets
        subnet_ids = create_subnets(vpc_id)
        
        # Create internet gateway
        igw_id = create_internet_gateway(vpc_id)
        
        # Create route table
        create_route_table(vpc_id, igw_id, subnet_ids)
        
        # Create security groups
        sg_ec2_id, sg_rds_id = create_security_groups(vpc_id)
        
        # Create DB subnet group
        db_subnet_group = create_db_subnet_group(subnet_ids)
        
        # Create RDS cluster
        create_rds_cluster(db_subnet_group, sg_rds_id)
        
        # Create EC2 instance
        create_ec2_instance(subnet_ids[0], sg_ec2_id)
        
        # Show summary
        show_infrastructure_info()
        
    elif choice == '2':
        show_infrastructure_info()
    elif choice == '3':
        confirm = input("This will delete EVERYTHING. Continue? (yes/no): ")
        if confirm.lower() == 'yes':
            cleanup_all()
    elif choice == '4':
        print("Goodbye!")
        return
    else:
        print("Invalid choice")
    
    # Run menu again
    main()

if __name__ == "__main__":
    main()