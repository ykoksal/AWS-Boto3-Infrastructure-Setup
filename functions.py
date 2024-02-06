import boto3

def show_ec2_instances(region_name='eu-central-1'):
    ec2_client = boto3.client('ec2', region_name=region_name)
    resp = ec2_client.describe_instances()
    print(resp)


def create_vpc(ec2, name='VPC-python', CidrBlock='10.1.0.0/16'):

    vpc = ec2.create_vpc(CidrBlock=CidrBlock,
                         TagSpecifications=[
                             {
                                 'ResourceType': 'vpc',
                                 'Tags': [{'Key': 'Name', 'Value': name}]
                             }]
                         )
    vpc.wait_until_available()
    return vpc


def create_igw(ec2, vpc, name='IGW-python'):
    igw = ec2.create_internet_gateway(TagSpecifications=[{'ResourceType': 'internet-gateway',
                                                          'Tags': [{'Key': 'Name', 'Value': name}]
                                                          }
                                                         ]
                                      )
    vpc.attach_internet_gateway(InternetGatewayId=igw.id)
    return igw


def create_subnet(vpc, name='Subnet-Public-python', CidrBlock='10.1.0.0/24'):
    subnet = vpc.create_subnet(CidrBlock=CidrBlock)
    subnet.create_tags(Tags=[{'Key': 'Name', 'Value': name}])
    return subnet


def create_route_table(vpc, destination_cidr_block='0.0.0.0/0', gateway_id="", name='RouteTable-python',
                       subnet_id=""):
    route_table = vpc.create_route_table()
    route_table.create_tags(Tags=[{'Key': 'Name', 'Value': name}])
    route_table.create_route(
        DestinationCidrBlock=destination_cidr_block,
        GatewayId=gateway_id
    )
    route_table.associate_with_subnet(SubnetId=subnet_id)
    return route_table


def create_ec2_instance(ec2, subnet_id, key_pair, name='', ami_id='ami-09024b009ae9e7adf', bool_eip=True, UserData=''):
    ec2_instance = ec2.create_instances(
        ImageId=ami_id,
        InstanceType='t2.micro',
        MaxCount=1,
        MinCount=1,
        KeyName=key_pair,
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

    return ec2_instance


def create_public_ec2_security_group(ec2_client, vpc, public_ec2_instance, name='SG-PublicEc2-python', description=''):
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


def create_private_ec2_security_group(ec2_client, vpc, private_ec2_instance, name='SG-PrivateEc2-python', PublicEC2CidrIp='', description=''):
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


    # Assign SG to the instance
    ec2_client.modify_instance_attribute(
        InstanceId=private_ec2_instance[0].id,
        Groups=[sg_private['GroupId']]
    )
    return sg_private


def create_NAT_gateway(ec2_client, public_subnet_id, name='natgw-python'):
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


def resource_checker(ec2_client, type, id):
    type_list = {"natgw": ec2_client.describe_nat_gateways(NatGatewayIds=[id])}

    natgw = ec2_client.describe_nat_gateways(NatGatewayIds=[id])
    status = nat_gateway['NatGateways'][0]['State']
    return status == 'available'


def check_vpc(ec2_client, ec2, name='VPC-python', CidrBlock='10.1.0.0/16'):
    response = ec2_client.describe_vpcs(
        Filters=[
            {
                'Name': 'cidr',
                'Values': [
                    CidrBlock,
                ]
            },
        ]
    )
    if response["Vpcs"]:
        return True
    else:
        return False