import json
import boto3
import logging
from botocore.exceptions import ClientError
 
# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
 
def list_hosted_zones(route53_client):
    """List hosted zones in Route 53."""
    try:
        response = route53_client.list_hosted_zones()
        logger.info(f"Listed {len(response['HostedZones'])} hosted zones.")
        return response['HostedZones']
    except ClientError as e:
        logger.error(f"Error listing hosted zones: {e}")
        return None
 
def create_in_addr_arpa_zone(route53_client):
    """Create the in-addr.arpa zone if it does not exist."""
    try:
        # Check if the zone already exists
        existing_zones = route53_client.list_hosted_zones_by_name(DNSName='in-addr.arpa.')
        if existing_zones['HostedZones']:
            logger.info("The in-addr.arpa zone already exists.")
            return existing_zones['HostedZones'][0]['Id']
       
        # Create the in-addr.arpa zone if it doesn't exist
        response = route53_client.create_hosted_zone(
            Name='in-addr.arpa.',
            CallerReference='unique-identifier-for-in-addr-arpa',  # Use a unique reference
            HostedZoneConfig={
                'Comment': 'Created by Lambda for reverse DNS',
            }
        )
        logger.info("Created the in-addr.arpa zone.")
        return response['HostedZone']['Id']
    except ClientError as e:
        logger.error(f"Error creating in-addr.arpa zone: {e}")
        return None
 
def create_ptr_record(route53_client, hosted_zone_id, ip_address, domain_name):
    """Create a PTR record in the in-addr.arpa zone."""
    try:
        reversed_ip = '.'.join(reversed(ip_address.split('.'))) + ".in-addr.arpa."
        response = route53_client.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={
                'Changes': [
                    {
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': reversed_ip,
                            'Type': 'PTR',
                            'TTL': 300,
                            'ResourceRecords': [{'Value': domain_name}]
                        }
                    }
                ]
            }
        )
        logger.info(f"PTR record created for IP: {ip_address} in hosted zone: {hosted_zone_id}")
        return response
    except ClientError as e:
        logger.error(f"Error creating PTR record for IP: {ip_address} in hosted zone: {hosted_zone_id}: {e}")
        return None
 
def lambda_handler(event, context):
    """Main Lambda handler."""
    # Create a Route 53 client (no region needed since Route 53 is global)
    route53_client = boto3.client('route53')
 
    # Create or get the in-addr.arpa zone
    ptr_hosted_zone_id = create_in_addr_arpa_zone(route53_client)
    if not ptr_hosted_zone_id:
        logger.error("Failed to create or find the in-addr.arpa zone.")
        return {'statusCode': 500, 'body': 'Failed to create or find the in-addr.arpa zone.'}
 
    # List hosted zones in the current account
    hosted_zones = list_hosted_zones(route53_client)
    if not hosted_zones:
        logger.info("No hosted zones found in the current account.")
        return {'statusCode': 500, 'body': 'No hosted zones found.'}
 
    for zone in hosted_zones:
        hosted_zone_id = zone['Id']
        domain_name = zone['Name']
        logger.info(f"Processing hosted zone: {domain_name} with ID: {hosted_zone_id}")
 
        try:
            records_response = route53_client.list_resource_record_sets(HostedZoneId=hosted_zone_id)
            record_sets = records_response['ResourceRecordSets']
            logger.info(f"Found {len(record_sets)} records in hosted zone: {domain_name}")
 
            for record in record_sets:
                logger.info(f"Processing record: {record['Name']} of type: {record['Type']}")
               
                # Ensure that 'ResourceRecords' key exists and handle A or AAAA records
                if record['Type'] in ['A', 'AAAA'] and 'ResourceRecords' in record:
                    ip_address = record['ResourceRecords'][0]['Value']
                    logger.info(f"Found {record['Type']} record with IP: {ip_address}")
                   
                    # Create the PTR record in the in-addr.arpa zone
                    response = create_ptr_record(route53_client, ptr_hosted_zone_id, ip_address, domain_name)
                    if response:
                        logger.info(f"PTR record created successfully for {record['Name']}")
                    else:
                        logger.error(f"Failed to create PTR record for {record['Name']}")
                else:
                    logger.info(f"Skipping record of type {record['Type']} or record without 'ResourceRecords' for {record['Name']}")
        except ClientError as e:
            logger.error(f"Error listing record sets: {e}")
            continue
 
    return {
        'statusCode': 200,
        'body': json.dumps('PTR records creation process completed.')
    }
 
