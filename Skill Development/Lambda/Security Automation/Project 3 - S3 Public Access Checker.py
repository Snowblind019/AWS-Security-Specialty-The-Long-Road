import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    s3 = boto3.client('s3')

    # Track findings
    public_buckets = []
    private_buckets = []
    errors = []

    # Get all buckets
    response = s3.list_buckets()

    for bucket in response['Buckets']:
        bucket_name = bucket['Name']

        try:
            # Check public access block settings
            public_access = s3.get_public_access_block(Bucket=bucket_name)
            config = public_access['PublicAccessBlockConfiguration']

            # All four settings should be True for fully private
            is_fully_blocked = (
                config['BlockPublicAcls']and
                config['IgnorePublicAcls']and
                config['BlockPublicPolicy']and
                config['RestrictPublicBuckets']
            )

            if is_fully_blocked:
                private_buckets.append(bucket_name)
                logger.info(f"{bucket_name}: private")
            else:
                public_buckets.append({
                    'bucket': bucket_name,
                    'settings': config
                })
                logger.warning(f"{bucket_name}: potentially public!")

        except s3.exceptions.NoSuchPublicAccessBlockConfiguration:
            # No public access bloc = potentially public
            public_buckets.append({
                'bucket': bucket_name,
                'settings': 'No public access block configured'
            })
            logger.warning(f"{bucket_name}: no public access block!")

        except Exception as e:
            errors.append({
                'bucket':bucket_name,
                'error': {e}
            })
            logger.error(f"{bucket_name}: error - {e}")

        # Summary
        total = len(response['Buckets'])
        logger.info(f"Scan complete: {len(private_buckets)}/{total} fully private")

        return {
            'statusCode': 200,
            'body': {
                'total_buckets': total,
                'private_count': len(private_buckets),
                'public_count': len(public_buckets),
                'public_buckets': public_buckets,
                'errors': errors
            }
        }