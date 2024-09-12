import json
import boto3
import os
import logging
from botocore.exceptions import ClientError
 
# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
 
def list_hosted_zones(route53_client):
    """List all hosted zones in Route 53."""
    try:
        response = route53_client.list_hosted_zones()
        logger.info(f"Listed {len(response['HostedZones'])} hosted zones.")
        return response['HostedZones']
    except ClientError as e:
        logger.error(f"Error listing hosted zones: {e}")
        return None
 
def create_ptr_record(route53_client, ptr_hosted_zone_id, ip_address, domain_name):
    """Create a PTR record in the in-addr.arpa zone."""
    try:
        # Reverse the IP address for PTR record
        reversed_ip = '.'.join(reversed(ip_address.split('.'))) + ".in-addr.arpa."
       
        # Create PTR record in the target zone (in-addr.arpa)
        response = route53_client.change_resource_record_sets(
            HostedZoneId=ptr_hosted_zone_id,
            ChangeBatch={
                'Changes': [
                    {
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': reversed_ip,
                            'Type': 'PTR',
                            'TTL': 300,
                            'ResourceRecords': [{'Value': domain_name}]  # Domain name as the PTR target
                        }
                    }
                ]
            }
        )
        logger.info(f"PTR record created for IP: {ip_address} pointing to {domain_name}")
        return response
    except ClientError as e:
        logger.error(f"Error creating PTR record for IP: {ip_address}: {e}")
        return None
 
def lambda_handler(event, context):
    """Main Lambda handler."""
    regions = os.getenv('regions').split(',')  # Retrieve multiple regions from environment variables
 
    # Target PTR zone for reverse DNS (in-addr.arpa)
    target_zone_name = 'in-addr.arpa.'
    ptr_hosted_zone_id = None
 
    for region in regions:
        route53_client = boto3.client('route53', region_name=region)
 
        # List all hosted zones
        hosted_zones = list_hosted_zones(route53_client)
        if not hosted_zones:
            logger.info(f"No hosted zones found in the current account for region: {region}")
            continue
 
        # Find the specific PTR hosted zone (in-addr.arpa.)
        for zone in hosted_zones:
            if zone['Name'] == target_zone_name:
                ptr_hosted_zone_id = zone['Id']
                logger.info(f"Found PTR hosted zone: {target_zone_name} with ID: {ptr_hosted_zone_id}")
                break
 
        if not ptr_hosted_zone_id:
            logger.error(f"PTR hosted zone {target_zone_name} not found in region: {region}")
            continue
 
        # Process all hosted zones for PTR record creation
        for zone in hosted_zones:
            hosted_zone_id = zone['Id']
            domain_name = zone['Name']
 
            try:
                # List all resource records in the hosted zone
                records_response = route53_client.list_resource_record_sets(HostedZoneId=hosted_zone_id)
                record_sets = records_response['ResourceRecordSets']
                logger.info(f"Found {len(record_sets)} records in hosted zone: {domain_name}")
 
                for record in record_sets:
                    # Only process 'A' (IPv4) and 'AAAA' (IPv6) records
                    if record['Type'] in ['A', 'AAAA']:
                        ip_address = record['ResourceRecords'][0]['Value']
                        logger.info(f"Found {record['Type']} record with IP: {ip_address}")
                       
                        # Create PTR record in the PTR zone (in-addr.arpa)
                        response = create_ptr_record(route53_client, ptr_hosted_zone_id, ip_address, domain_name)
                        if response:
                            logger.info(f"PTR record created successfully for {record['Name']} (IP: {ip_address})")
                        else:
                            logger.error(f"Failed to create PTR record for {record['Name']} (IP: {ip_address})")
                    else:
                        logger.info(f"Skipping record of type {record['Type']} for {record['Name']}")
            except ClientError as e:
                logger.error(f"Error listing record sets in region {region}: {e}")
                continue
 
    return {
        'statusCode': 200,
        'body': json.dumps('PTR records creation process completed.')
    }
 
