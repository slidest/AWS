#!/usr/bin/python
# - *- coding: utf- 8 - *- .
# AWS credentials from AWSCLI configuration
import boto3
# For colored print
from termcolor import colored




# Credential from session
# from boto3.session import Session
# session = Session(aws_access_key_id='xxxx',aws_secret_access_key='yyyy')
# s3 = session.resource('s3')


# ***********************
# *  DEFINE VARIABLES   *
# ***********************

# Variables for AWS resources
# Variable for calling AWS API. value : boto3 if coming from AWSCLI or session if coming from session
credential = boto3
s3_res = credential.resource('s3')
s3_cli = boto3.client('s3')
""" :type : pyboto3.s3 """
ec2_res = credential.resource('ec2')
ec2_cli = credential.client('ec2')
""" :type : pyboto3.ec2 """


dryrun = False
region = 'eu-west-2'
vpc_id = 'vpc-85955dec'
igw_id = 'igw-e6ea2e8f'
# S3
bucket_name = 'jstmybucket'
route_table_private_name = 'Private'
route_table_public_name = 'Public'

route_tables_name = [route_table_private_name, route_table_public_name]
# Tags
environement = 'Dev'
app = 'WebSite'
# NACL
nacl_public_name = 'Public_Access'
nacl_private_name = 'Private_Access'

nacls_name = [nacl_public_name, nacl_private_name]
nacls_id = []
# Subnets
subnet1_cidr = "172.31.1.0/24"
subnet2_cidr = "172.31.2.0/24"
subnet3_cidr = "172.31.3.0/24"
subnet4_cidr = "172.31.4.0/24"
subnet1_name = "Public_" + subnet1_cidr
subnet2_name = "Public_" + subnet2_cidr
subnet3_name = "Private_" + subnet3_cidr
subnet4_name = "Private_" + subnet4_cidr
subnet1_az = region + "a"
subnet2_az = region + "b"
subnet3_az = region + "a"
subnet4_az = region + "b"

subnets_name = [subnet1_name, subnet2_name, subnet3_name, subnet4_name]
subnets_cidr = [subnet1_cidr, subnet2_cidr, subnet3_cidr, subnet4_cidr]
subnets_az = [subnet1_az, subnet2_az, subnet3_az, subnet4_az]
subnets_id = []


# ***********************
# *  CREATE FUNCTIONS   *
# ***********************
# Find NACL by tag value
def list_nacl_by_tag_value(tagkey, tagvalue):
    """
        When passed a tag key, tag value this will return a list of NACLs that were found.
        :param tagkey:str
        :param tagvalue:str
        :return: list
    """

    response = ec2_cli.describe_network_acls(Filters=[
        {'Name': 'tag:' + tagkey, 'Values': [tagvalue]}
    ])
    nacl_id_list = []
    for result in response["NetworkAcls"]:
        nacl_id_list.append(result['NetworkAclId'])

    return nacl_id_list
# Find Route tables by tag value
def list_routetable_by_tag_value(tagkey, tagvalue):
    """
        When passed a tag key, tag value this will return a list of RouteTableIds that were found.
        :param tagkey:str
        :param tagvalue:str
        :return: list
    """

    response = ec2_cli.describe_route_tables(Filters=[
        {'Name': 'tag:' + tagkey, 'Values': [tagvalue]}
    ])
    route_tables_id_list = []
    for result in response["RouteTables"]:
        route_tables_id_list.append(result['RouteTableId'])

    return route_tables_id_list

# Find Subnets by attribute value
def list_subnet_by_attribute_value(attribute, value):
    """
        When passed a attribute key, attribute value this will return a list of SubnetIds that were found.
        :param attribute:str
        :param value:str
        :return: list
    """
    response = ec2_cli.describe_subnets(Filters=[
        {'Name': attribute, 'Values': [value]}
    ])
    subnets_id_list = []
    for result in response["Subnets"]:
        subnets_id_list.append(result['SubnetId'])

    return subnets_id_list

# ****************************************************************************************
# *                                     EXECUTION                                        *
# ****************************************************************************************

# ***********************
# * CREATE ROUTE TABLES *
# ***********************

i = 0
while i < len(route_tables_name):
    # Create a Route Table
    # Test if a route table with Tag Name already exists
    test = list_routetable_by_tag_value("Name", route_tables_name[i])
    # If there is no route table in test, we create teh route table
    if test == []:
        route_table = ec2_res.create_route_table(
              DryRun=dryrun,
              VpcId=vpc_id
              )
        # Defining Name tag on new Route Table
        route_table_tags = route_table.create_tags(
            DryRun=dryrun,
            Tags=[
                {
                    'Key': 'Name',
                    'Value': route_tables_name[i]
                },
                {
                    'Key': 'Env',
                    'Value': environement
                },
                {
                    'Key': 'App',
                    'Value': app
                }
            ]
        )
        if 'Public' in route_tables_name[i]:
            public_route_table_id = route_table.route_table_id
        elif 'Private' in route_tables_name[i]:
            private_route_table_id = route_table.route_table_id
        print colored("The %s Route Table has been created with id %s!" % (route_tables_name[i], route_table.route_table_id), 'green')
        # print "The %s Route Table has been created with id %s!" % (route_tables_name[i], route_table.route_table_id)
        # Adding a route to the IGW for the Public route table
        if 'Public' in route_tables_name[i]:
            public_route_table_id = route_table.route_table_id
            route = route_table.create_route(
                DryRun=dryrun,
                DestinationCidrBlock='0.0.0.0/0',
                GatewayId=igw_id
            )
            print colored('\tThe route for \'%s\' IGW has been added to the \'%s\' route table!' % (igw_id, route_tables_name[i]), 'green')
        elif 'Private' in route_tables_name[i]:
            private_route_table_id = route_table.route_table_id
    else:
        print colored("A Route Table with the name '%s' already exists with Id %s!" % (route_tables_name[i], test), 'yellow')
    i += 1

# ***********************
# *   CREATE SUBNETS    *
# ***********************
i = 0
while i < len(subnets_name):
    # Create Subnet1 and with tags
    # Test if a Subnet with CidrBlock  = subnets_cidr[i]
    test = list_subnet_by_attribute_value('cidr', subnets_cidr[i])
    # If there is no S-subnet in test, we create the subnet
    if test == []:
        subnet = ec2_res.create_subnet(
            DryRun=dryrun,
            VpcId=vpc_id,
            CidrBlock=subnets_cidr[i],
            AvailabilityZone=subnets_az[i]
        )
        subnets_id.append(subnet.subnet_id)
        # Defining Name tag on new Route Table
        tags = subnet.create_tags(
            DryRun=dryrun,
            Tags=[
                {
                    'Key': 'Name',
                    'Value': subnets_name[i]
                },
                {
                    'Key': 'Env',
                    'Value': environement
                },
                {
                    'Key': 'App',
                    'Value': app
                }
            ]
        )
        print colored("The '%s' Subnet has been created with ID %s!" % (subnets_name[i], subnet.subnet_id), 'green')
        # configure the route table for the subnets
        if 'Public' in subnets_name[i]:
            ec2_res.RouteTable(public_route_table_id).associate_with_subnet(
                DryRun=dryrun,
                SubnetId=subnet.subnet_id
            )
            print colored("\tThe '%s' Route table has been associated with %s subnet!" %
                          (route_table_public_name, subnets_name[i]), 'green')
        elif 'Private' in subnets_name[i]:
            ec2_res.RouteTable(private_route_table_id).associate_with_subnet(
                DryRun=dryrun,
                SubnetId=subnet.subnet_id
            )
            print colored("\tThe '%s' Route table has been associated with %s subnet!" %
                          (route_table_private_name, subnets_name[i]), 'green')
    else:
        print colored("The %s CIDR Block is used by the subnet with Id %s!" % (subnets_cidr[i], test), 'yellow')

    i += 1

# ***********************
# *    CREATE NACL      *
# ***********************
# faire le test sur le nom de la nacl comme pour les autres objets
i = 0
while i < len(nacls_name):
    # Create nacl and with tags
    # Test if a nacl with tag name = nacls_name[i]
    test = list_nacl_by_tag_value("Name", nacls_name[i])
    # If there is no S-subnet in test, we create the subnet
    if test == []:
        nacl = ec2_res.create_network_acl(
            DryRun=dryrun,
            VpcId=vpc_id
        )
        nacls_id.append(nacl.network_acl_id)
        # Defining Name tag on new Route Table
        tags = nacl.create_tags(
            DryRun=dryrun,
            Tags=[
                {
                    'Key': 'Name',
                    'Value': nacls_name[i]
                },
                {
                    'Key': 'Env',
                    'Value': environement
                },
                {
                    'Key': 'App',
                    'Value': app
                }
            ]
        )
        print colored("The '%s' network ACL has been created with ID %s!" % (nacls_name[i], nacl.network_acl_id), 'green')
        # configure rules for nacls
        if 'Public' in nacls_name[i]:
            # create inbound/outbound rule for HTTP
            nacl.create_entry(
                DryRun=dryrun,
                RuleNumber=10,
                Protocol='6',
                RuleAction='allow',
                Egress=False,  # egress = True correspond à une outbound rule
                CidrBlock='0.0.0.0/0',
                PortRange={
                    'From': 80,
                    'To': 80
                }
            )
            nacl.create_entry(
                DryRun=dryrun,
                RuleNumber=10,
                Protocol='6',
                RuleAction='allow',
                Egress=True,  # egress = True correspond à une outbound rule
                CidrBlock='0.0.0.0/0',
                PortRange={
                    'From': 80,
                    'To': 80
                }
            )
            print colored("\tInbound/outbound rules for HTTP has been created in '%s' Network ACL!" % (nacls_name[i]), 'green')
            # create inbound/outbound rule for SSH
            nacl.create_entry(
                DryRun=dryrun,
                RuleNumber=20,
                Protocol='6',
                RuleAction='allow',
                Egress=False,  # egress = True correspond à une outbound rule
                CidrBlock='0.0.0.0/0',
                PortRange={
                    'From': 22,
                    'To': 22
                }
            )
            nacl.create_entry(
                DryRun=dryrun,
                RuleNumber=20,
                Protocol='6',
                RuleAction='allow',
                Egress=True,  # egress = True correspond à une outbound rule
                CidrBlock='0.0.0.0/0',
                PortRange={
                    'From': 22,
                    'To': 22
                }
            )
            print colored("\tInbound/outbound rules for SSH has been created in '%s' Network ACL!" % (nacls_name[i]), 'green')
        elif 'Private' in nacls_name[i]:
            pass
            
    else:
        print colored("A Network ACL with the name '%s' already exists with Id %s!" % (nacls_name[i], test), 'yellow')

    i += 1


# Create bucket

# s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': region})
