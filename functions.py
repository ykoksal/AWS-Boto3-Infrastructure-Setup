import boto3


def show_ec2_instances(region_name='eu-central-1'):
    ec2_client = boto3.client('ec2', region_name=region_name)
    resp = ec2_client.describe_instances()
    print(resp)


def create_vpc(ec2_client, name='VPC-boto3', CidrBlock='10.1.0.0/16'):
    get_vpc = ec2_client.describe_vpcs(
        Filters=[
            {
                'Name': 'cidr',
                'Values': [
                    CidrBlock,
                ]
            },
        ]
    )
    if get_vpc["Vpcs"]:
        vpc_id = get_vpc["Vpcs"][0]["VpcId"]
        print(f"There is already a VPC named {name} with id={vpc_id} this VPC's id is returned")
    else:
        vpc = ec2_client.create_vpc(CidrBlock=CidrBlock,
                                    TagSpecifications=[
                                        {
                                            'ResourceType': 'vpc',
                                            'Tags': [{'Key': 'Name', 'Value': name}]
                                        }]
                                    )
        vpc_id = vpc['Vpc']['VpcId']

    return vpc_id


def create_igw(ec2_client, vpc_id, name='IGW-boto3'):
    get_igw = ec2_client.describe_internet_gateways(
        Filters=[

            {
                'Name': 'tag:Name',
                'Values': [
                    name
                ]
            }
        ]
    )

    if get_igw["InternetGateways"]:
        igw_id = get_igw["InternetGateways"][0]["InternetGatewayId"]
        print(
            f"There is already an Internet Gateway named {name} with id={igw_id} this Internet Gateway's id is returned")
    else:
        igw = ec2_client.create_internet_gateway(
            TagSpecifications=[
                {
                    'ResourceType': 'internet-gateway',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': name
                        }
                    ]
                }
            ]
        )
        igw_id = igw["InternetGateway"]["InternetGatewayId"]
        ec2_client.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
        print(f"Created an Internet Gateway named {name} with id={igw_id} and attached to VPCId={vpc_id}")
    return igw_id


def create_subnet(ec2_client, vpc_id, availability_zone='eu-central-1', name='Subnet-boto3',
                  CidrBlock='10.1.0.0/24'):

    get_subnet = ec2_client.describe_subnets(
        Filters=[
            {
                'Name': 'tag:Name',
                'Values': [
                    name
                ]
            }
        ]
    )
    if get_subnet["Subnets"]:
        subnet_id = get_subnet["Subnets"][0]["SubnetId"]
        print(f"There is already a Subnet named {name} with id={subnet_id} this Subnet's id is returned")
    else:
        subnet = ec2_client.create_subnet(VpcId=vpc_id, CidrBlock=CidrBlock, AvailabilityZone=availability_zone,
                                          TagSpecifications=[
                                              {
                                                  'ResourceType': 'subnet',
                                                  'Tags': [
                                                      {
                                                          'Key': 'Name',
                                                          'Value': name
                                                      }
                                                  ]
                                              }

                                          ]
                                          )
        subnet_id = subnet['Subnet']['SubnetId']
        print(f"Created a Subnet named {name} with id={subnet_id}")
    return subnet_id


def create_route_table(ec2_client, vpc_id, subnet_id, destination_cidr_block='0.0.0.0/0', gateway_id="",
                       name='RouteTable-boto3'):
    get_route_table = ec2_client.describe_route_tables(
        Filters=[
            {
                'Name': 'tag:Name',
                'Values': [
                    name
                ]
            }
        ]
    )
    if get_route_table["RouteTables"]:
        route_table_id = get_route_table["RouteTables"][0]["RouteTableId"]
        print(f"There is already a Route Table named {name} with id={route_table_id} this Route Table's id is returned")
    else:
        route_table = ec2_client.create_route_table(
            VpcId=vpc_id,
            TagSpecifications=[
                {
                    'ResourceType': 'route-table',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': name

                        }
                    ]
                }
            ])
        route_table_id = route_table['RouteTable']['RouteTableId']
        ec2_client.create_route(
            DestinationCidrBlock=destination_cidr_block,
            GatewayId=gateway_id,
            RouteTableId=route_table_id
        )
        print(
            f"Created a Route Table named {name} with id={route_table_id}")
    return route_table_id


def associate_route_table(ec2_client, subnet_id, route_table_id):
    ec2_client.associate_route_table(
        SubnetId=subnet_id,
        RouteTableId=route_table_id
    )
    print(f"Associated Route Table having id={route_table_id} with SubnetId={subnet_id}")
    return True


def create_ec2_instance(ec2_client, subnet_id, sg_id, key_pair, name, ami_id='ami-09024b009ae9e7adf', bool_eip=True,
                        UserData=''):
    """

    :param ec2_client:
    :param subnet_id:
    :param sg_id:
    :param key_pair:
    :param name:
    :param ami_id:
    :param bool_eip:
    :param UserData:
    :return: ec2 instance id
    """
    get_ec2_instance = ec2_client.describe_instances(
        Filters=[
            {
                'Name': 'tag:Name',
                'Values': [
                    name
                ]
            }
        ]
    )

    if get_ec2_instance["Reservations"]:
        ec2_instance_id = get_ec2_instance["Reservations"][0]["InstanceId"]
        print(
            f"There is already an EC2 instance named {name} with id={ec2_instance_id}. This EC2 instance's id is returned")
    else:
        response = ec2_client.run_instances(
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
                'DeleteOnTermination': True,
                'Groups': [sg_id]
            }
            ]
        )
        ec2_instances = response.get('Instances')
        ec2_instance_id = ec2_instances[0]['InstanceId']
        # ec2_instance_ids = [instance.get('InstanceId') for instance in ec2_instances]
        print(
            f"Created an EC2 instance named {name} with id={ec2_instance_id}, SubnetId={subnet_id}, and SGroupId={sg_id}")
    return ec2_instance_id


def create_security_group(ec2_client, vpc_id, rules_list, name='SG-boto3', description=''):
    """
    Creates Security Group with given set of rules and assigns it to a EC2 instance.
    TODO: set a parameter for private EC2 instance so that it could only be connected through SSH from the Public EC2
        instance -- PublicEC2CidrIp=public_ec2_instance_ip + "/32"
    :param ec2_client:
    :param vpc_id:
    :param public_ec2_instance:
    :param rules_list: list of rules in integer format
    :param name:
    :param description:
    :return:
    """

    get_security_group = ec2_client.describe_security_groups(
        Filters=[
            {
                'Name': 'tag:Name',
                'Values': [
                    name
                ]
            }
        ]
    )

    if get_security_group["SecurityGroups"]:
        sg_id = get_security_group["SecurityGroups"][0]["GroupId"]
        print(f"There is already a Security Group named {name} with id={sg_id}.This Security Group's id is returned.")
    else:
        # Create the security group for Public Instance
        security_group = ec2_client.create_security_group(
            GroupName=name,
            Description=description,
            VpcId=vpc_id,
            TagSpecifications=[{
                'ResourceType': 'security-group',
                'Tags': [{'Key': 'Name', 'Value': name}]
            }]
        )

        for rule in rules_list:
            ec2_client.authorize_security_group_ingress(
                GroupId=security_group['GroupId'],
                IpProtocol='tcp',
                FromPort=rule,  # SSH port
                ToPort=rule,
                CidrIp='0.0.0.0/0'
            )

        # ec2_client.modify_instance_attribute(
        #     InstanceId=ec2_instance_id,
        #     Groups=[security_group['GroupId']]
        # )
        sg_id = security_group.get('GroupId')
        print(f"Created a Security Group named {name} with GroupId={sg_id}")
    return sg_id


def create_nat_gateway(ec2_client, public_subnet_id, name='natgw-boto3'):
    get_nat_gateway = ec2_client.describe_nat_gateways(
        Filters=[
            {
                'Name': 'tag:Name',
                'Values': [
                    name
                ]
            }
        ]
    )

    if get_nat_gateway["NatGateways"]:
        natgw_id = get_nat_gateway["NatGateways"][0]["NatGatewayId"]
        print(f"There is already a NAT Gateway named {name} with id={natgw_id}.This NAT Gateway's id is returned.")
    else:
        eip = ec2_client.allocate_address(Domain='vpc')
        nat_gateway = ec2_client.create_nat_gateway(SubnetId=public_subnet_id, AllocationId=eip['AllocationId'],
                                                    TagSpecifications=[
                                                        {
                                                            'ResourceType': 'natgateway',
                                                            'Tags': [{'Key': 'Name', 'Value': name}]

                                                        }
                                                    ]
                                                    )
        natgw_id = nat_gateway["NatGateway"]["NatGatewayId"]
        print(f"Created a NAT Gateway named {name} with Id={natgw_id} and associated with SubnetId={public_subnet_id}")
    return natgw_id


def check_nat_gateway_available(ec2_client, nat_gateway_id):
    nat_gateway = ec2_client.describe_nat_gateways(NatGatewayIds=[nat_gateway_id])
    status = nat_gateway['NatGateways'][0]['State']
    return status == 'available'