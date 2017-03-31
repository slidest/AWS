#!/usr/bin/python
# AWS credentials from AWSCLI configuration
import boto3


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
subnets = []


# ***********************
# *  CREATE FUNCTIONS   *
# ***********************
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

# Create a Route Table without  IGW and with tags
# Test if a route table with Tag Name = route_table_private_name
test = list_routetable_by_tag_value("Name", route_table_private_name)
# If there is no route table in test, we create teh route table
if test is []:
    route_table_private = ec2_res.create_route_table(
          DryRun=dryrun,
          VpcId=vpc_id
          )

    # Defining Name tag on new Route Table
    route_table_private_tags = route_table_private.create_tags(
        DryRun=dryrun,
        Tags=[
            {
                'Key': 'Name',
                'Value': route_table_private_name
            },
            {
                'Key': 'Env',
                'Value': environement
            },
            {
                'Key': 'App',
                'Value': app
            },
        ]
    )
    print "The %s Route Table has been created with id %s!" % (route_table_private_name, route_table_private)
else:
    print "The %s Route Table already exists with Id %s!" % (route_table_private_name, test)
# Create a Route Table with IGW and with tags
# Test if a route table with Tag Name = route_table_public_name
test = list_routetable_by_tag_value("Name", route_table_public_name)
# If there is no route table in test, we create teh route table
if test is []:
    route_table_public = ec2_res.create_route_table(
          DryRun=dryrun,
          VpcId=vpc_id
          )

    # Defining Name tag on new Route Table
    tags = route_table_public.create_tags(
        DryRun=dryrun,
        Tags=[
            {
                'Key': 'Name',
                'Value': route_table_public_name
            },
            {
                'Key': 'Env',
                'Value': environement
            },
            {
                'Key': 'App',
                'Value': app
            },
        ]
    )

    # Adding a route to the IGW to the new Route Table
    route = route_table_public.create_route(
        DryRun=dryrun,
        DestinationCidrBlock='0.0.0.0/0',
        GatewayId=igw_id
    )
    print "The %s Route Table has been created with ID %s!" % (route_table_public_name, route_table_public)
else:
    print "The %s Route Table already exists with Id %s!" % (route_table_public_name, test)

# ***********************
# *   CREATE SUBNETS    *
# ***********************
i = 0
while i < len(subnets_name):
    # Create Subnet1 and with tags
    # Test if a Subnet with CidrBlock  = subnets_cidr[i]
    test = list_subnet_by_attribute_value('cidr', subnets_cidr[i])
    # If there is no S-subnet in test, we create the subnet
    if test is []:
        subnet = ec2_res.create_subnet(
            DryRun=dryrun,
            VpcId=vpc_id,
            CidrBlock=subnets_cidr[i],
            AvailabilityZone=subnets_az[i]
        )
        # Defining Name tag on new Route Table
        subnets.append(subnet)
        tags = subnet.create_tags(
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
                },
            ],
            DryRun=dryrun
        )
        print "The %s Subnet has been created : %s!" % (subnets_name[i], subnets)
    else:
        print "The %s CIDR Block is used by the subnet with Id %s!" % (subnets_cidr[i], test)

    i += 1

# Create bucket

# s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': region})
