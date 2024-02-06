import time
import boto3
from functions import *

#########  Show current EC2 instances in the eu-central-1 region #########
show_ec2_instances(region_name='eu-central-1')

######### Create Infrastructure #########

# Init
session = boto3.Session(region_name='eu-central-1')
ec2 = session.resource('ec2')
ec2_client = boto3.client('ec2', region_name='eu-central-1')

# Creating Resources
vpc = create_vpc(ec2=ec2, name='VPC2-python', CidrBlock='10.23.0.0/16')
igw = create_igw(ec2, vpc, name='IGW-python')
public_subnet = create_subnet(vpc, name='Subnet2-Public-python', CidrBlock='10.23.0.0/24')
private_subnet = create_subnet(vpc, name='Subnet2-Public-python', CidrBlock='10.23.1.0/24')
natgw = create_NAT_gateway(ec2_client, public_subnet_id=public_subnet.id, name='natgw2-python')
natgw_id = natgw['NatGateway']['NatGatewayId']

while not check_nat_gateway_available(ec2_client, nat_gateway_id=natgw_id):
    print("Waiting for NAT gateway to be activated...")
    time.sleep(10)

public_rt = create_route_table(vpc, destination_cidr_block='0.0.0.0/0', gateway_id=igw.id,
                               name='Public-Subnet2-RT-python', subnet_id=public_subnet.id)
private_rt = create_route_table(vpc, destination_cidr_block='0.0.0.0/0', gateway_id=natgw_id,
                                name='Private-Subnet2-RT-python', subnet_id=private_subnet.id)
public_ec2_instance = create_ec2_instance(name='Public-Ec2-python2', key_pair='demo-yigit-keypair',
                                          subnet_id=public_subnet.id, bool_eip=True,
                                          UserData="""#!/bin/bash
                                                        yum update -y
                                                        yum install httpd -y
                                                        systemctl start httpd
                                                        systemctl enable httpd
                                                     """
                                          )
private_ec2_instance = create_ec2_instance(name='Private-Ec2-python2', key_pair='demo-yigit-keypair',
                                           subnet_id=private_subnet.id,
                                           bool_eip=False,
                                           UserData="""#!/bin/bash
                                                        yum update -y
                                                        yum install unzip -y
                                                     """
                                           )
sg_public = create_public_ec2_security_group(vpc=vpc, public_ec2_instance=public_ec2_instance,
                                             name='SG2-PublicEc2-python',
                                             description='Security Group for Public Instance')

public_ec2_instance_ip = \
    ec2_client.describe_instances(InstanceIds=[public_ec2_instance[0].id])['Reservations'][0]['Instances'][0][
        'PrivateIpAddress']
sg_private = create_private_ec2_security_group(ec2_client=ec2_client,
                                               vpc=vpc,
                                               private_ec2_instance=private_ec2_instance,
                                               name='SG2-PrivateEc2-python',
                                               description='Security Group for Private Instance',
                                               PublicEC2CidrIp=public_ec2_instance_ip + "/32")

private_ec2_instance_ip = \
    ec2_client.describe_instances(InstanceIds=[private_ec2_instance[0].id])['Reservations'][0]['Instances'][0][
        'PrivateIpAddress']
public_ec2_instance_public_ip = \
    ec2_client.describe_instances(InstanceIds=[public_ec2_instance[0].id])['Reservations'][0]['Instances'][0][
        'PublicIpAddress']
