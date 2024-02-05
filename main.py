import boto3
import time

def show_ec2_instances():
    ec2_client = boto3.client('ec2', region_name='eu-central-1')
    resp = ec2_client.describe_instances()
    print(resp)


def create_vpc(ec2, name='VPC-python-yigit', CidrBlock='10.1.0.0/16'):
    vpc = ec2.create_vpc(CidrBlock=CidrBlock,
                         TagSpecifications=[
                             {
                                 'ResourceType': 'vpc',
                                 'Tags': [{'Key': 'Name', 'Value': name}]
                             }]
                         )
    vpc.wait_until_available()
    # Tagging after the creation of the vpc if necessary
    # vpc.create_tags(Tags=[{'Key': 'Name', 'Value': 'VPC-python-yigit'}])
    return vpc


# InternetGateway
def create_igw(vpc, name='IGW-python-yigit'):
    igw = ec2.create_internet_gateway(TagSpecifications=[{'ResourceType': 'internet-gateway',
                                                          'Tags': [{'Key': 'Name', 'Value': name}]
                                                          }
                                                         ]
                                      )
    vpc.attach_internet_gateway(InternetGatewayId=igw.id)
    return igw


def create_subnet(vpc, name='Subnet-Public-python-yigit', CidrBlock='10.1.0.0/24'):
    subnet = vpc.create_subnet(CidrBlock=CidrBlock)
    subnet.create_tags(Tags=[{'Key': 'Name', 'Value': name}])
    return subnet


def create_route_table(vpc, destination_cidr_block='0.0.0.0/0', gateway_id="", name='RouteTable-python-yigit',
                       subnet_id=""):
    route_table = vpc.create_route_table()
    route_table.create_tags(Tags=[{'Key': 'Name', 'Value': name}])
    route_table.create_route(
        DestinationCidrBlock=destination_cidr_block,
        GatewayId=gateway_id
    )
    route_table.associate_with_subnet(SubnetId=subnet_id)
    return route_table


def create_ec2_instance(subnet_id, name='', ami_id='ami-09024b009ae9e7adf', bool_eip=True, UserData=''):
    ec2_instance = ec2.create_instances(
        ImageId=ami_id,
        InstanceType='t2.micro',
        MaxCount=1,
        MinCount=1,
        KeyName='demo-yigit-keypair',
        UserData=UserData,
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [{'Key': 'Name', 'Value': name}]
            }],
        NetworkInterfaces=[{
            'SubnetId': subnet_id,
            'DeviceIndex': 0,
            'AssociatePublicIpAddress': bool_eip,
            'DeleteOnTermination': True
        }
        ]
    )
    # ec2_client.create_tags(Resources=[ec2_instance[0].id], Tags=[{'Key': 'Name', 'Value': 'PublicEC2-python-yigit'}])
    # public_ec2_info = ec2_client.describe_instances(InstanceIds=ec2_instance[0].id)

    # Assigning Elastic Ip for Public Ec2 Instance
    # if bool_eip:
    #     resp_allocate = ec2_client.allocate_address()
    #     elastic_ip = resp_allocate['PublicIp']
    #     ec2_client.associate_address(
    #         InstanceId=ec2_instance[0].id,
    #         PublicIp=elastic_ip
    #     )
    return ec2_instance


def create_public_ec2_security_group(vpc, public_ec2_instance, name='SG-PublicEc2-python-yigit', description=''):
    # Create the security group for Public Instance
    sg_public = ec2_client.create_security_group(
        GroupName=name,
        Description=description,
        VpcId=vpc.id,
        TagSpecifications=[{
            'ResourceType': 'security-group',
            'Tags': [{'Key': 'Name', 'Value': name}]
        }]
    )

    ec2_client.authorize_security_group_ingress(
        GroupId=sg_public['GroupId'],
        IpProtocol='tcp',
        FromPort=22,  # SSH port
        ToPort=22,
        CidrIp='0.0.0.0/0'
    )

    ec2_client.authorize_security_group_ingress(
        GroupId=sg_public['GroupId'],
        IpProtocol='tcp',
        FromPort=80,
        ToPort=80,
        CidrIp='0.0.0.0/0'
    )

    ec2_client.modify_instance_attribute(
        InstanceId=public_ec2_instance[0].id,
        Groups=[sg_public['GroupId']]
    )
    return sg_public


def create_private_ec2_security_group(vpc, private_ec2_instance, name='SG-PrivateEc2-python-yigit', PublicEC2CidrIp='', description=''):
    sg_private = ec2_client.create_security_group(
        GroupName=name,
        Description=description,
        VpcId=vpc.id,
        TagSpecifications=[{
                'ResourceType': 'security-group',
                'Tags': [{'Key': 'Name', 'Value': name}]
            }]
    )

    ec2_client.authorize_security_group_ingress(
        GroupId=sg_private['GroupId'],
        IpProtocol='tcp',
        FromPort=22,
        ToPort=22,
        CidrIp=PublicEC2CidrIp
    )
    # response = ec2_client.revoke_security_group_ingress(
    #     GroupId=sg_private['GroupId'],
    #     IpProtocol='tcp',
    #     FromPort=22,
    #     ToPort=22,
    #     CidrIp='0.0.0.0/0'
    # )

    # Assign SG to the instance
    ec2_client.modify_instance_attribute(
        InstanceId=private_ec2_instance[0].id,
        Groups=[sg_private['GroupId']]
    )
    return sg_private


def create_NAT_gateway(ec2_client, public_subnet_id, name='natgw-python-yigit'):
    eip = ec2_client.allocate_address(Domain='vpc')
    nat_gateway = ec2_client.create_nat_gateway(SubnetId=public_subnet_id, AllocationId=eip['AllocationId'],
                                                TagSpecifications=[{'ResourceType': 'natgateway',
                                                                    'Tags': [{'Key': 'Name', 'Value': name}]
                                                                    }
                                                                   ])
    return nat_gateway

def check_nat_gateway_available(ec2_client, nat_gateway_id):
    nat_gateway = ec2_client.describe_nat_gateways(NatGatewayIds=[nat_gateway_id])
    status = nat_gateway['NatGateways'][0]['State']
    return status == 'available'


################### Run ########################
# Part1
show_ec2_instances()

# Part2
# Init
session = boto3.Session(region_name='eu-central-1')
ec2 = session.resource('ec2')
ec2_client = boto3.client('ec2', region_name='eu-central-1')

# Creating Resources
vpc = create_vpc(ec2, name='VPC2-python-yigit', CidrBlock='10.23.0.0/16')
igw = create_igw(vpc)
public_subnet = create_subnet(vpc, name='Subnet2-Public-python-yigit', CidrBlock='10.23.0.0/24')
private_subnet = create_subnet(vpc, name='Subnet2-Public-python-yigit', CidrBlock='10.23.1.0/24')
natgw = create_NAT_gateway(ec2_client, public_subnet_id=public_subnet.id, name='natgw2-python-yigit')
natgw_id = natgw['NatGateway']['NatGatewayId']

while not check_nat_gateway_available(ec2_client,nat_gateway_id=natgw_id):
    print("Waiting for NAT gateway to be activated...")
    time.sleep(10)

public_rt = create_route_table(vpc, destination_cidr_block='0.0.0.0/0', gateway_id=igw.id,
                               name='Public-Subnet2-RT-python-yigit', subnet_id=public_subnet.id)
private_rt = create_route_table(vpc, destination_cidr_block='0.0.0.0/0', gateway_id=natgw_id,
                                name='Private-Subnet2-RT-python-yigit', subnet_id=private_subnet.id)
public_ec2_instance = create_ec2_instance(name='Public-Ec2-python2-yigit', subnet_id=public_subnet.id, bool_eip=True,
                                          UserData="""#!/bin/bash
                                                        yum update -y
                                                        yum install httpd -y
                                                        systemctl start httpd
                                                        systemctl enable httpd
                                                     """
                                          )
private_ec2_instance = create_ec2_instance(name='Private-Ec2-python2-yigit', subnet_id=private_subnet.id,
                                           bool_eip=False,
                                           UserData="""#!/bin/bash
                                                        yum update -y
                                                        yum install unzip -y
                                                     """
                                           )
sg_public = create_public_ec2_security_group(vpc=vpc, public_ec2_instance=public_ec2_instance,
                                             name='SG2-PublicEc2-python-yigit', description='Security Group for Public Instance')

public_ec2_instance_ip = ec2_client.describe_instances(InstanceIds=[public_ec2_instance[0].id])['Reservations'][0]['Instances'][0]['PrivateIpAddress']
sg_private = create_private_ec2_security_group(vpc=vpc, private_ec2_instance=private_ec2_instance,
                                               name='SG2-PrivateEc2-python-yigit', description='Security Group for Private Instance',
                                               PublicEC2CidrIp=public_ec2_instance_ip+"/32")


private_ec2_instance_ip = ec2_client.describe_instances(InstanceIds=[private_ec2_instance[0].id])['Reservations'][0]['Instances'][0]['PrivateIpAddress']
public_ec2_instance_public_ip = ec2_client.describe_instances(InstanceIds=[public_ec2_instance[0].id])['Reservations'][0]['Instances'][0]['PublicIpAddress']



#Config
public_ec2_id = public_ec2_instance[0].id
private_ec2_id = private_ec2_instance[0].id
public_instance = ec2.Instance(public_ec2_id)
private_instance = ec2.Instance(private_ec2_id)

#Start Instances
resp_start_public_instance = public_instance.start()
resp_start_private_instance = private_instance.start()
public_start_code = resp_start_public_instance['ResponseMetadata']['HTTPStatusCode']
private_start_code = resp_start_private_instance['ResponseMetadata']['HTTPStatusCode']
print(f'Start HTTP Responses\nPrivate Instance: {private_start_code}, Public Instance: {public_start_code})')

#Stop Instances
resp_stop_public_instance = public_instance.stop()
resp_stop_private_instance = private_instance.stop()
public_stop_code = resp_stop_public_instance['ResponseMetadata']['HTTPStatusCode']
private_stop_code = resp_stop_private_instance['ResponseMetadata']['HTTPStatusCode']
print(f'Stop HTTP Responses\nPrivate Instance: {private_stop_code},\nPublic Instance: {public_stop_code})')

#Terminate Instances
resp_terminate_public_instance = public_instance.terminate()
resp_terminate_private_instance = private_instance.terminate()
public_terminate_code = resp_terminate_public_instance['ResponseMetadata']['HTTPStatusCode']
private_terminate_code = resp_terminate_private_instance['ResponseMetadata']['HTTPStatusCode']
print(f'terminate HTTP Responses\nPrivate Instance: {private_terminate_code},\nPublic Instance: {public_terminate_code})')


