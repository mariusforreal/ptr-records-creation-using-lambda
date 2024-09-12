# ptr-records-creation-using-lambda
Automating PTR Record Creation in Private Hosted Zones Using AWS Lambda

This repository provides a solution to automate the creation of PTR (Pointer) records for reverse DNS lookups in private hosted zones in AWS Route 53. The automation uses AWS Lambda functions to create PTR records based on existing DNS entries and reverse DNS lookup results.

Features

Automated PTR Record Creation: Automatically create PTR records for IP addresses in AWS Route 53 private hosted zones.
Reverse DNS Lookup: Perform reverse DNS lookups on IP addresses to verify the associated domain names.
Integration with AWS Route 53: Leverage boto3 to interact with Route 53 and manage DNS entries.
Multi-Region Support: Configure the Lambda to operate across multiple AWS regions.

Prerequisites:

Before deploying the Lambda functions, ensure the following prerequisites are met:

AWS Account: An active AWS account with sufficient permissions to create and manage Lambda functions, Route 53 hosted zones, and resource record sets.
Private Hosted Zone: A Route 53 private hosted zone configured for reverse DNS (e.g., 201.10.in-addr.arpa or in-addr.arpa)., In this case, I used in-addr.arpa
IAM Role: The Lambda function needs a role with the following permissions:
route53:ListHostedZones
route53:ListResourceRecordSets
route53:ChangeResourceRecordSets
Python 3.x: Ensure the Lambda runtime is configured to use Python 3.x, as the code is written in Python.
Setup

1. Clone the Repository
bash
Copy code
git clone https://github.com/your-username/aws-lambda-ptr-records.git
cd aws-lambda-ptr-records

3. AWS Lambda Code
The repository includes two main Lambda functions:

create_ptr_records.py: This function iterates through hosted zones, identifies DNS entries, and creates corresponding PTR records.
reverse_dns_lookup.py: This function performs reverse DNS lookups for given IP addresses to validate or fetch associated domain names.

3. Deploy the Lambda Functions
You can deploy the Lambda functions manually or via an AWS service such as AWS CloudFormation, AWS CLI, or AWS SAM. Below is a manual deployment example.

a. Package the Lambda function ( Optional ), you could create two seperate functions, one with create_ptr_records.py, and the other with reverse_dns_lookup.py

Compress the Python files and dependencies:
bash
Copy code
zip -r function.zip create_ptr_records.py reverse_dns_lookup.py

b. Create the Lambda function in AWS

Open the AWS Lambda console.
Choose Create function and select Author from scratch.
Provide a name (e.g., PTRRecordAutomation) and set the Runtime to Python 3.x.
Upload the function.zip file created earlier.
Assign the necessary IAM role with permissions mentioned above.

4. Configure Environment Variables
In the Lambda configuration, set the following environment variables for flexibility:

regions: A comma-separated list of AWS regions to target (e.g., us-east-1,us-west-2).
hosted_zone_id: The ID of the private hosted zone where PTR records will be created (e.g., ZXXXXXXXXXXXXX). (This is not needed since the lambda code is written to iterate through all hosted zones and create records)

5. Test the Lambda Function
Use the Test feature in the Lambda console to verify that the PTR records are being created correctly. You can pass a sample event as follows:

json
Copy code
{
  "ip_address": "192.168.1.10"
}

6. Monitor Logs
Check the function’s logs in CloudWatch to track the PTR creation process and reverse DNS lookups. The logs will provide insights into any errors or issues.

Example CloudWatch Log Output
plaintext
Copy code
INFO: Found A record with IP: 192.168.1.10
INFO: PTR record created for IP: 192.168.1.10 in hosted zone: ZXXXXXXXXXXXXX
INFO: PTR record creation successful.

Usage

Trigger the Lambda: Set up the Lambda function to trigger periodically (e.g., using CloudWatch Events or EventBridge). You can also trigger it manually if needed.
Automatic PTR Record Creation: The Lambda function will loop through the hosted zones and create PTR records for any new IP addresses found.
Reverse DNS Lookup: The reverse lookup function verifies the correct association between the domain name and the IP address.

Customization

Modify the TTL for PTR records in the create_ptr_record function.
Extend the Lambda to handle different types of records or additional DNS zones.
Security Considerations

Ensure that your Lambda execution role has the minimum necessary permissions.
Restrict access to your private hosted zones to authorized VPCs.
Enable logging and monitoring to audit changes to DNS records.
Troubleshooting

No PTR Record Created: Check if the hosted zone ID is correct and if the function has the necessary permissions to make changes in Route 53.
Lambda Timeout: If the Lambda function times out, consider increasing its timeout setting, especially for large numbers of DNS records.
License

Feel free to customize this README as needed for your specific setup!

Cheers
