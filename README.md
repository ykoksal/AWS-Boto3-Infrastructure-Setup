# AWS Infrastructure Setup with Boto3 SDK

This repository contains Python scripts for managing AWS resources using the Boto3 SDK. The scripts showcase how to interact with AWS EC2 instances, VPCs, Subnets, Internet Gateways, Route Tables, Security Groups, and NAT Gateways programmatically. The main objectives include listing EC2 instances, creating VPCs, subnets, route tables, security groups, and EC2 instances within a defined VPC infrastructure.

## Features

- **List EC2 Instances:** Retrieves and displays a list of all EC2 instances in the eu-central-1 region, providing insights into the existing infrastructure.
- **Create VPC:** Establishes a new VPC with custom CIDR blocks, demonstrating VPC setup and tagging.
- **Set Up Internet Gateway:** Attaches an internet gateway to the VPC, enabling communication between the VPC and the internet.
- **Provision Subnets:** Creates public and private subnets within the VPC, illustrating subnet management and tagging.
- **Configure Route Tables:** Sets up route tables for public and private subnets, including routes for internet access and internal networking.
- **Launch EC2 Instances:** Initiates EC2 instances in both public and private subnets, showcasing instance creation, configuration, and networking setup.
- **Manage Security Groups:** Demonstrates creating and configuring security groups for EC2 instances to control inbound and outbound traffic.
- **Deploy NAT Gateway:** Establishes a NAT Gateway in the public subnet, allowing private subnet instances to access the internet securely.

## Usage

To use these scripts, you need to have AWS CLI configured with appropriate permissions and Boto3 installed in your Python environment.

1. **Configuration**: Ensure AWS CLI is configured with access key, secret key, and default region (`eu-central-1` is used in the scripts).

2. **Dependencies**: Install Boto3 using pip:
   ```
   pip install boto3
   ```

3. **Execution**: Run the scripts individually or as a whole to set up the AWS infrastructure. The script sections are labeled as Part1 and Part2 for ease of testing and deployment.

## Important Notes

- Make sure your AWS account has the necessary permissions to create and manage the resources defined in the scripts.
- The scripts are set to run in the `eu-central-1` region. Adjust the region as per your requirement.
- Key pairs, AMI IDs, and security group configurations should be reviewed and adjusted according to your security and operational needs.
- Be mindful of the AWS costs associated with creating and using these resources.

## License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details.