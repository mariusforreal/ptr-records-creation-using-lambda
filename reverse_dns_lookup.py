import socket
import json
import logging
 
# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
 
def lambda_handler(event, context):
    """Lambda function handler to perform reverse DNS lookup"""
    # Extract IP address from event or environment variables
    ip_address = event.get('ip_address') or '8.8.8.8'  # default to Google's public DNS for testing
   
    try:
        # Perform reverse DNS lookup
        host, aliaslist, ipaddrlist = socket.gethostbyaddr(ip_address)
       
        # Log and return the results
        logger.info(f"IP Address: {ip_address} resolves to Host: {host}")
        logger.info(f"Aliases: {aliaslist}")
        logger.info(f"IP Address List: {ipaddrlist}")
       
        return {
            'statusCode': 200,
            'body': json.dumps({
                'ip_address': ip_address,
                'host': host,
                'aliases': aliaslist,
                'ip_addresses': ipaddrlist
            })
        }
   
    except socket.herror as e:
        logger.error(f"Reverse DNS lookup failed for IP {ip_address}: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': f"Reverse DNS lookup failed for IP {ip_address}",
                'message': str(e)
            })
        }
