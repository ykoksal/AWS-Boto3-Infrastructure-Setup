import time
from functions import *

#########  Show current EC2 instances in the eu-central-1 region #########
show_ec2_instances(region_name='eu-central-1')

######### Create Infrastructure #########

# Init
session = boto3.Session(region_name='eu-central-1')
ec2 = session.resource('ec2')
ec2_client = boto3.client(service_name='ec2', region_name='eu-central-1')

# Creating Resources
vpc_id = create_vpc(ec2_client=ec2_client, name='VPC-boto3-yigit', CidrBlock='10.23.0.0/16')
igw_id = create_igw(ec2_client=ec2_client, vpc_id=vpc_id, name='IGW-boto3-yigit')

public_subnet_id = create_subnet(
    ec2_client=ec2_client,
    vpc_id=vpc_id,
    availability_zone="eu-central-1a",
    name='Subnet-Public-boto3',
    CidrBlock='10.23.0.0/24')
private_subnet_id = create_subnet(
    ec2_client=ec2_client,
    vpc_id=vpc_id,
    availability_zone="eu-central-1b",
    name='Subnet-Private-boto3',
    CidrBlock='10.23.1.0/24')

natgw_id = create_nat_gateway(
    ec2_client=ec2_client,
    public_subnet_id=public_subnet_id,
    name='Natgw-boto3')

while not check_nat_gateway_available(ec2_client, nat_gateway_id=natgw_id):
    print("Waiting for NAT gateway to be activated...")
    time.sleep(30)

public_rt_id = create_route_table(
    ec2_client=ec2_client,
    vpc_id=vpc_id,
    subnet_id=public_subnet_id,
    destination_cidr_block='0.0.0.0/0',
    gateway_id=igw_id,
    name='PublicSubnetRT-boto3'
)
associate_route_table(
    ec2_client=ec2_client,
    subnet_id=public_subnet_id,
    route_table_id=public_rt_id
)

private_rt_id = create_route_table(
    ec2_client=ec2_client,
    vpc_id=vpc_id,
    subnet_id=private_subnet_id,
    destination_cidr_block='0.0.0.0/0',
    gateway_id=natgw_id,
    name='PrivateSubnetRT-boto3'
)
associate_route_table(
    ec2_client=ec2_client,
    subnet_id=private_subnet_id,
    route_table_id=private_rt_id
)

sg_public_id = create_security_group(
    ec2_client=ec2_client,
    vpc_id=vpc_id,
    rules_list=[80, 22],
    name='SG-PublicEC2-boto3',
    description='Security Group for Public EC2 Instance'
)

public_ec2_instance_id = create_ec2_instance(
    ec2_client=ec2_client,
    subnet_id=public_subnet_id,
    sg_id=sg_public_id,
    key_pair='demo-yigit-keypair',
    name='Public-EC2-boto3',
    ami_id='ami-09024b009ae9e7adf',
    bool_eip=True,
    UserData="""#!/bin/bash
                yum update -y
                yum install httpd -y
                systemctl start httpd
                systemctl enable httpd
             """
  )

sg_private_id = create_security_group(
    ec2_client=ec2_client,
    vpc_id=vpc_id,
    rules_list=[22],
    name='SG-PrivateEC2-boto3',
    description='Security Group for Private EC2 Instance'
)

private_ec2_instance_id = create_ec2_instance(
    ec2_client=ec2_client,
    subnet_id=private_subnet_id,
    sg_id=sg_private_id,
    key_pair='demo-yigit-keypair',
    name='Private-EC2-boto3',
    ami_id='ami-09024b009ae9e7adf',
    bool_eip=False,
    UserData="""#!/bin/bash
                yum update -y
                yum install unzip -y
             """
  )

#Get EC2 Instance IPs
public_ec2_instance_private_ip = \
    ec2_client.describe_instances(InstanceIds=[public_ec2_instance_id])['Reservations'][0]['Instances'][0][
        'PrivateIpAddress']

public_ec2_instance_public_ip = \
    ec2_client.describe_instances(InstanceIds=[public_ec2_instance_id])['Reservations'][0]['Instances'][0][
        'PublicIpAddress']

private_ec2_instance_private_ip = \
    ec2_client.describe_instances(InstanceIds=[private_ec2_instance_id])['Reservations'][0]['Instances'][0][
        'PrivateIpAddress']