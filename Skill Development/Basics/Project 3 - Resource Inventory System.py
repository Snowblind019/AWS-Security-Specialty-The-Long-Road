"""
PROJECT 3: AWS RESOURCE INVENTORY SYSTEM

Objective:
Create an automated inventory system that scans all AWS resources, generates
detailed reports, saves them to S3, and tracks changes over time.

What this project teaches:
- Describe operations: Query existing resources across all services
- Data aggregation: Combine information from multiple AWS services
- JSON handling: Structure and save data
- Change tracking: Compare current state with historical data
- Reporting: Generate human-readable summaries

Services used:
- EC2 (describe instances, VPCs, subnets)
- S3 (store reports)
- RDS (describe clusters)
- All services from Projects 1 & 2

Skills practiced:
- Describe vs Create operations
- Working with complex nested data structures
- File I/O (reading and writing JSON)
- List comprehensions for data extraction
- Set operations for comparison
- Timestamp management

Main operations:
1. Create S3 bucket for inventory reports
2. Scan all EC2 instances (ID, name, type, state, IPs)
3. Scan all S3 buckets (name, creation date, object count)
4. Scan all VPCs (ID, name, CIDR, subnet count)
5. Scan all RDS clusters (ID, engine, status, endpoint)
6. Generate JSON report with metadata
7. Save report locally and upload to S3
8. Compare with previous reports to detect changes
9. Display summary of all resources

Real-world application:
- Cloud asset management
- Compliance auditing
- Cost tracking and optimization
- Change detection and alerting
- Infrastructure documentation
"""

import boto3
import json
from datetime import datetime
import os

# Initialize clients
ec2 = boto3.client('ec2')
s3 = boto3.client('s3')
rds = boto3.client('rds')

# Configuration
BUCKET_NAME = 'winterday-inventory-bucket'
REGION = 'us-west-2'

def create_inventory_bucket():
    """Create S3 bucket for inventory reports"""
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

def inventory_ec2_instances():
    """Get information about all EC2 instances"""
    print("Inventorying EC2 instances...")
    
    response = ec2.describe_instances()
    
    instances = []
    
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            # Extract instance name from tags
            name = 'N/A'
            if 'Tags' in instance:
                for tag in instance['Tags']:
                    if tag['Key'] == 'Name':
                        name = tag['Value']
                        break
            
            instance_info = {
                'InstanceId': instance['InstanceId'],
                'Name': name,
                'InstanceType': instance['InstanceType'],
                'State': instance['State']['Name'],
                'LaunchTime': instance['LaunchTime'].strftime('%Y-%m-%d %H:%M:%S'),
                'PrivateIpAddress': instance.get('PrivateIpAddress', 'N/A'),
                'PublicIpAddress': instance.get('PublicIpAddress', 'N/A')
            }
            instances.append(instance_info)
    
    print(f"Found {len(instances)} EC2 instances")
    return instances

def inventory_s3_buckets():
    """Get information about all S3 buckets"""
    print("Inventorying S3 buckets...")
    
    response = s3.list_buckets()
    
    buckets = []
    
    for bucket in response['Buckets']:
        bucket_name = bucket['Name']
        
        # Count objects in bucket
        try:
            objects_response = s3.list_objects_v2(Bucket=bucket_name)
            object_count = len(objects_response.get('Contents', []))
        except Exception:
            object_count = 0
        
        bucket_info = {
            'BucketName': bucket_name,
            'CreationDate': bucket['CreationDate'].strftime('%Y-%m-%d %H:%M:%S'),
            'ObjectCount': object_count
        }
        buckets.append(bucket_info)
    
    print(f"Found {len(buckets)} S3 buckets")
    return buckets

def inventory_vpcs():
    """Get information about all VPCs"""
    print("Inventorying VPCs...")
    
    response = ec2.describe_vpcs()
    
    vpcs = []
    
    for vpc in response['Vpcs']:
        vpc_id = vpc['VpcId']
        
        # Get name from tags
        name = 'N/A'
        if 'Tags' in vpc:
            for tag in vpc['Tags']:
                if tag['Key'] == 'Name':
                    name = tag['Value']
                    break
        
        # Count subnets in this VPC
        subnets_response = ec2.describe_subnets(
            Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
        )
        subnet_count = len(subnets_response['Subnets'])
        
        vpc_info = {
            'VpcId': vpc_id,
            'Name': name,
            'CidrBlock': vpc['CidrBlock'],
            'State': vpc['State'],
            'IsDefault': vpc['IsDefault'],
            'SubnetCount': subnet_count
        }
        vpcs.append(vpc_info)
    
    print(f"Found {len(vpcs)} VPCs")
    return vpcs

def inventory_rds_clusters():
    """Get information about all RDS clusters"""
    print("Inventorying RDS clusters...")
    
    response = rds.describe_db_clusters()
    
    clusters = []
    
    for cluster in response['DBClusters']:
        cluster_info = {
            'DBClusterIdentifier': cluster['DBClusterIdentifier'],
            'Engine': cluster['Engine'],
            'EngineVersion': cluster['EngineVersion'],
            'Status': cluster['Status'],
            'Endpoint': cluster.get('Endpoint', 'N/A'),
            'MasterUsername': cluster['MasterUsername'],
            'DatabaseName': cluster.get('DatabaseName', 'N/A'),
            'ClusterCreateTime': cluster['ClusterCreateTime'].strftime('%Y-%m-%d %H:%M:%S')
        }
        clusters.append(cluster_info)
    
    print(f"Found {len(clusters)} RDS clusters")
    return clusters

def generate_inventory_report():
    """Generate complete inventory report"""
    print("\nStarting inventory scan...\n")
    
    # Collect all inventory data
    ec2_instances = inventory_ec2_instances()
    s3_buckets = inventory_s3_buckets()
    vpcs = inventory_vpcs()
    rds_clusters = inventory_rds_clusters()
    
    # Create report
    report = {
        'ReportMetadata': {
            'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Region': REGION,
            'TotalResources': len(ec2_instances) + len(s3_buckets) + len(vpcs) + len(rds_clusters)
        },
        'EC2Instances': ec2_instances,
        'S3Buckets': s3_buckets,
        'VPCs': vpcs,
        'RDSClusters': rds_clusters
    }
    
    return report

def save_report_to_file(report):
    """Save report to local JSON file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'inventory_report_{timestamp}.json'
    
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nSaved report to: {filename}")
    return filename

def upload_report_to_s3(filename):
    """Upload report to S3"""
    s3_key = f'inventory-reports/{filename}'
    
    s3.upload_file(filename, BUCKET_NAME, s3_key)
    print(f"Uploaded to S3: s3://{BUCKET_NAME}/{s3_key}")
    
    return s3_key

def display_report_summary(report):
    """Display a summary of the inventory report"""
    print("\n" + "="*60)
    print("INVENTORY REPORT SUMMARY")
    print("="*60)
    
    metadata = report['ReportMetadata']
    print(f"\nReport Date: {metadata['Timestamp']}")
    print(f"Region: {metadata['Region']}")
    print(f"Total Resources: {metadata['TotalResources']}")
    
    print(f"\nEC2 Instances: {len(report['EC2Instances'])}")
    for instance in report['EC2Instances']:
        print(f"{instance['Name']} ({instance['InstanceId']}) - {instance['State']}")
    
    print(f"\nS3 Buckets: {len(report['S3Buckets'])}")
    for bucket in report['S3Buckets']:
        print(f"{bucket['BucketName']} - {bucket['ObjectCount']} objects")
    
    print(f"\nVPCs: {len(report['VPCs'])}")
    for vpc in report['VPCs']:
        print(f"{vpc['Name']} ({vpc['VpcId']}) - {vpc['SubnetCount']} subnets")
    
    print(f"\nRDS Clusters: {len(report['RDSClusters'])}")
    for cluster in report['RDSClusters']:
        print(f"{cluster['DBClusterIdentifier']} - {cluster['Status']}")
    
    print("\n" + "="*60)

def list_previous_reports():
    """List all previous inventory reports in S3"""
    try:
        response = s3.list_objects_v2(
            Bucket=BUCKET_NAME,
            Prefix='inventory-reports/'
        )
        
        if 'Contents' not in response:
            print("No previous reports found")
            return []
        
        reports = []
        print("\nPrevious inventory reports:")
        for i, obj in enumerate(response['Contents'], 1):
            key = obj['Key']
            last_modified = obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S')
            size = obj['Size']
            
            print(f"{i}. {key} ({size} bytes) - {last_modified}")
            reports.append(key)
        
        return reports
        
    except Exception as e:
        print(f"Error listing reports: {e}")
        return []

def compare_with_previous(current_report):
    """Compare current inventory with most recent previous report"""
    print("\nChecking for changes...")
    
    try:
        # Get list of previous reports
        response = s3.list_objects_v2(
            Bucket=BUCKET_NAME,
            Prefix='inventory-reports/',
            MaxKeys=2  # Get current and previous
        )
        
        if 'Contents' not in response or len(response['Contents']) < 2:
            print("No previous report to compare with")
            return
        
        # Get the second-most recent report (first is current)
        previous_key = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)[1]['Key']
        
        # Download previous report
        s3.download_file(BUCKET_NAME, previous_key, 'previous_report.json')
        
        with open('previous_report.json', 'r') as f:
            previous_report = json.load(f)
        
        # Compare EC2 instances
        current_ec2_ids = {i['InstanceId'] for i in current_report['EC2Instances']}
        previous_ec2_ids = {i['InstanceId'] for i in previous_report['EC2Instances']}
        
        new_instances = current_ec2_ids - previous_ec2_ids
        removed_instances = previous_ec2_ids - current_ec2_ids
        
        print("\nChanges detected:")
        
        if new_instances:
            print(f"New EC2 instances: {len(new_instances)}")
            for instance_id in new_instances:
                print(f"{instance_id}")
        
        if removed_instances:
            print(f"Removed EC2 instances: {len(removed_instances)}")
            for instance_id in removed_instances:
                print(f"{instance_id}")
        
        if not new_instances and not removed_instances:
            print("No changes in EC2 instances")
        
        # Clean up
        os.remove('previous_report.json')
        
    except Exception as e:
        print(f"Could not compare with previous report: {e}")

def cleanup_all():
    """Delete inventory bucket and all reports"""
    print("\nStarting cleanup...")
    
    try:
        # Delete all objects in bucket
        response = s3.list_objects_v2(Bucket=BUCKET_NAME)
        
        if 'Contents' in response:
            for obj in response['Contents']:
                s3.delete_object(Bucket=BUCKET_NAME, Key=obj['Key'])
                print(f"Deleted: {obj['Key']}")
        
        # Delete bucket
        s3.delete_bucket(Bucket=BUCKET_NAME)
        print(f"Deleted bucket: {BUCKET_NAME}")
        
        # Delete local JSON files
        for file in os.listdir('.'):
            if file.startswith('inventory_report_') and file.endswith('.json'):
                os.remove(file)
                print(f"Deleted local file: {file}")
        
        print("\nCleanup complete!")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")

def main():
    """Main menu"""
    print("\n" + "="*60)
    print("  AWS RESOURCE INVENTORY SYSTEM")
    print("="*60)
    print("\n1. Setup (Create S3 bucket)")
    print("2. Generate and save inventory report")
    print("3. List previous reports")
    print("4. Generate report with change tracking")
    print("5. Cleanup everything")
    print("6. Exit")
    
    choice = input("\nEnter choice (1-6): ")
    
    if choice == '1':
        create_inventory_bucket()
        
    elif choice == '2':
        report = generate_inventory_report()
        display_report_summary(report)
        filename = save_report_to_file(report)
        upload_report_to_s3(filename)
        
    elif choice == '3':
        list_previous_reports()
        
    elif choice == '4':
        report = generate_inventory_report()
        display_report_summary(report)
        filename = save_report_to_file(report)
        upload_report_to_s3(filename)
        compare_with_previous(report)
        
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