import boto3
import time

rds = boto3.client('rds')

# Configuration
username = 'winter0'
password = 'winter012345'
db_subnet_group = 'vpc'
db_cluster_id = 'rds-cluster'
db_instance_id = f'{db_cluster_id}-instance-1'

# Create the DB cluster if it doesn't already exist
try:
    response = rds.describe_db_clusters(DBClusterIdentifier=db_cluster_id)
    print(f"The DB cluster named '{db_cluster_id}' already exists. Skipping creation.")
except rds.exceptions.DBClusterNotFoundFault:
    response = rds.create_db_cluster(
        Engine='aurora-mysql',
        EngineVersion='8.0.mysql_aurora.3.11.1',
        DBClusterIdentifier=db_cluster_id,
        MasterUsername=username,
        MasterUserPassword=password,
        DatabaseName='rds',
        DBSubnetGroupName=db_subnet_group,
        EnableHttpEndpoint=True,  # Enables Data API for serverless queries
        ServerlessV2ScalingConfiguration={
            'MinCapacity': 0.5,  # Minimum ACUs (Aurora Capacity Units)
            'MaxCapacity': 1.0
        }
    )
    print(f"The DB cluster named '{db_cluster_id}' has been created")

    # Serverless v2 requires at least one DB instance in the cluster
    rds.create_db_instance(
        DBInstanceIdentifier=db_instance_id,
        DBInstanceClass='db.serverless',
        Engine='aurora-mysql',
        DBClusterIdentifier=db_cluster_id
    )

# Wait for the cluster to become available before continuing
while True:
    response = rds.describe_db_clusters(DBClusterIdentifier=db_cluster_id)
    status = response['DBClusters'][0]['Status']
    print(f"The status of the cluster is '{status}'")
    if status == 'available':
        break
    print(f"Waiting for the DB Cluster to become available...")
    time.sleep(40)

# Modify scaling configuration (demonstrating cluster updates)
response = rds.modify_db_cluster(
    DBClusterIdentifier=db_cluster_id,
    ServerlessV2ScalingConfiguration={
        'MinCapacity': 1.0,
        'MaxCapacity': 16.0
    }
)
print(f"Updated the scaling configuration for DB cluster '{db_cluster_id}'.")

# Cleanup: Delete instance first, then cluster as RDS requires instances to be deleted before the cluster can be removed
try:
    response = rds.delete_db_instance(
        DBInstanceIdentifier=db_instance_id,
        SkipFinalSnapshot=True  # Skip snapshot as I am learning and don't care
    )
    print(f"Deleting DB instance '{db_instance_id}'...")
    
    while True:
        try:
            response = rds.describe_db_instances(DBInstanceIdentifier=db_instance_id)
            status = response['DBInstances'][0]['DBInstanceStatus']
            print(f"Instance status: '{status}'")
            time.sleep(30)
        except rds.exceptions.DBInstanceNotFoundFault:
            print(f"DB instance '{db_instance_id}' has been deleted.")
            break
except rds.exceptions.DBInstanceNotFoundFault:
    print(f"DB instance '{db_instance_id}' does not exist.")

response = rds.delete_db_cluster(
    DBClusterIdentifier=db_cluster_id,
    SkipFinalSnapshot=True
)
print(f"The '{db_cluster_id}' is being deleted.")