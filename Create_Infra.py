#!/usr/bin/python
# - *- coding: utf- 8 - *- .
# AWS credentials from AWSCLI configuration
import boto3
# For exit
import sys
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
elb_cli = boto3.client('elbv2')
""" :type : pyboto3.elbv2 """
as_cli = boto3.client('autoscaling')
""" :type : pyboto3.autoscaling """
dryrun = False
region = 'eu-west-2'
vpc_id = 'vpc-85955dec'
igw_id = 'igw-e6ea2e8f'
# S3
bucket_name = 'jstmybucket'
# Route Tables
route_table_private_name = 'Private'
route_table_public_name = 'Public'

route_tables_name = [route_table_private_name, route_table_public_name]
# Tags
environement = 'Dev'
app = 'My Application'
# NACL
nacl_public_name = 'Public_Access'
nacl_private_name = 'Private_Access'

nacls_name = [nacl_public_name, nacl_private_name]
nacls_id = []

# Security groups
sg_web_name = 'Web_SG'
sg_db_name = 'DB_SG'

sgs_name = [sg_web_name, sg_db_name]
sgs_id = []

# Elastic load balancer
elb_name = 'My-Application-ELB'

# Auto scaling groups
launch_config_name = 'MyApp-WebServer-LC'
userdata_file = 'ec2-userdata.txt'
ami_id = 'ami-f1949e95'
key_name = 'MyApp'
asg_name = 'Web_ASG'

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
subnets_public_id = []
subnets_private_id = []

# ***********************
# *  CREATE FUNCTIONS   *
# ***********************
# Find SG by tag value
def list_sg_by_tag_value(tagkey, tagvalue):
    """
        When passed a tag key, tag value this will return a list of NACLs that were found.
        :param tagkey:str
        :param tagvalue:str
        :return: list
    """

    response = ec2_cli.describe_security_groups(Filters=[
        {'Name': 'tag:' + tagkey, 'Values': [tagvalue]}
    ])
    sg_id_list = []
    for result in response["SecurityGroups"]:
        sg_id_list.append(result['GroupId'])

    return sg_id_list
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
        print colored("A Route Table with the name '%s' already exists with Id %s!\n Script aborted" % (route_tables_name[i], test), 'red')
        # sys.exit()
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
            subnets_public_id.append((subnet.subnet_id))
            ec2_res.RouteTable(public_route_table_id).associate_with_subnet(
                DryRun=dryrun,
                SubnetId=subnet.subnet_id
            )
            print colored("\tThe '%s' Route table has been associated with %s subnet!" %
                          (route_table_public_name, subnets_name[i]), 'green')
        elif 'Private' in subnets_name[i]:
            subnets_private_id.append((subnet.subnet_id))
            ec2_res.RouteTable(private_route_table_id).associate_with_subnet(
                DryRun=dryrun,
                SubnetId=subnet.subnet_id
            )
            print colored("\tThe '%s' Route table has been associated with %s subnet!" %
                          (route_table_private_name, subnets_name[i]), 'green')
    else:
        print colored("The %s CIDR Block is used by the subnet with Id %s! Script aborted" % (subnets_cidr[i], test), 'red')
        # sys.exit()

    i += 1

# ***********************
# *    CREATE NACL      *
# ***********************

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
            # create inbound/outbound rule for ELB ephemeral ports
            nacl.create_entry(
                DryRun=dryrun,
                RuleNumber=30,
                Protocol='6',
                RuleAction='allow',
                Egress=False,  # egress = True correspond à une outbound rule
                CidrBlock='172.31.0.0/21',
                PortRange={
                    'From': 1024,
                    'To': 65535
                }
            )
            nacl.create_entry(
                DryRun=dryrun,
                RuleNumber=30,
                Protocol='6',
                RuleAction='allow',
                Egress=True,  # egress = True correspond à une outbound rule
                CidrBlock='172.31.0.0/21',
                PortRange={
                    'From': 1024,
                    'To': 65535
                }
            )
            print colored("\tInbound/outbound rules for ELB ephemeral ports has been created in '%s' Network ACL!" % (nacls_name[i]), 'green')
            # create inbound/outbound rule for linux ephemeral ports
            nacl.create_entry(
                DryRun=dryrun,
                RuleNumber=40,
                Protocol='6',
                RuleAction='allow',
                Egress=False,  # egress = True correspond à une outbound rule
                CidrBlock='0.0.0.0/0',
                PortRange={
                    'From': 32768,
                    'To': 61000
                }
            )
            nacl.create_entry(
                DryRun=dryrun,
                RuleNumber=40,
                Protocol='6',
                RuleAction='allow',
                Egress=True,  # egress = True correspond à une outbound rule
                CidrBlock='0.0.0.0/0',
                PortRange={
                    'From': 32768,
                    'To': 61000
                }
            )
            print colored("\tInbound/outbound rules for Linux ephemeral ports has been created in '%s' Network ACL!" % (nacls_name[i]), 'green')
            # Associate the Public NACL with public subnets
            # get all NACLs
            NACLS = ec2_cli.describe_network_acls()
            # get association IDs
            myAssociations = []
            for acl in NACLS['NetworkAcls']:
                if acl["VpcId"] == vpc_id and len(acl['Associations']) > 0:
                    myAssociations = acl['Associations']
                    break
            # replace associations to our ACL with
            for a in myAssociations:
                if a['SubnetId'] in subnets_public_id:
                    ec2_cli.replace_network_acl_association(
                        AssociationId=a['NetworkAclAssociationId'],
                        NetworkAclId=nacl.id
                    )
                    print colored("\t'%s' subnet has been associated with the '%s' Network ACL!" % (a['SubnetId'], nacl.id), 'green')
        elif 'Private' in nacls_name[i]:
            # create inbound/outbound rule for all ports
            nacl.create_entry(
                DryRun=dryrun,
                RuleNumber=10,
                Protocol='-1',
                RuleAction='allow',
                Egress=False,  # egress = True correspond à une outbound rule
                CidrBlock='0.0.0.0/0'
            )
            nacl.create_entry(
                DryRun=dryrun,
                RuleNumber=10,
                Protocol='-1',
                RuleAction='allow',
                Egress=True,  # egress = True correspond à une outbound rule
                CidrBlock='0.0.0.0/0'
            )
            print colored("\tInbound/outbound rules for all ports has been created in '%s' Network ACL!" % (nacls_name[i]), 'green')
            # Associate the Private NACL with private subnets
            # get all NACLs
            NACLS = ec2_cli.describe_network_acls()
            # get association IDs
            myAssociations = []
            for acl in NACLS['NetworkAcls']:
                if acl["VpcId"] == vpc_id and len(acl['Associations']) > 0:
                    myAssociations = acl['Associations']
                    break
            # replace associations to our ACL with
            for a in myAssociations:
                if a['SubnetId'] in subnets_private_id:
                    ec2_cli.replace_network_acl_association(
                        AssociationId=a['NetworkAclAssociationId'],
                        NetworkAclId=nacl.id
                    )
                    print colored("\t'%s' subnet has been associated with the '%s' Network ACL!" % (a['SubnetId'], nacl.id), 'green')
    else:
        print colored("A Network ACL with the name '%s' already exists with Id %s! Script aborted" % (nacls_name[i], test), 'red')
        # sys.exit()
    i += 1

# ***********************
# *      CREATE SG      *
# ***********************

i = 0
while i < len(sgs_name):
    # Create a Security group
    # Test if a security group with Tag Name already exists
    test = list_sg_by_tag_value("Name", sgs_name[i])
    # If there is no route table in test, we create teh route table
    if test == []:
        sg = ec2_res.create_security_group(
            DryRun=dryrun,
            GroupName=sgs_name[i],
            Description='Security group for My Application',
            VpcId=vpc_id
        )
        # Defining Name tag on new Route Table
        tags = sg.create_tags(
            DryRun=dryrun,
            Tags=[
                {
                    'Key': 'Name',
                    'Value': sgs_name[i]
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
        print colored("The '%s' Security Group has been created with id %s!" % (sgs_name[i], sg.group_id), 'green')
        # Adding rules to the SG
        if 'Web' in sgs_name[i]:
            sg_web_id = sg.group_id
            # authorize all traffic from this security group
            sg.authorize_ingress(
                DryRun=dryrun,
                GroupName=sgs_name[i],
                SourceSecurityGroupName=sgs_name[i]
            )
            # authorize HTTP traffic from anywhere
            sg.authorize_ingress(
                DryRun=dryrun,
                GroupName=sgs_name[i],
                IpProtocol='6',
                FromPort=80,
                ToPort=80,
                CidrIp='0.0.0.0/0'
            )
            # authorize SSH traffic from anywhere
            sg.authorize_ingress(
                DryRun=dryrun,
                GroupName=sgs_name[i],
                IpProtocol='6',
                FromPort=22,
                ToPort=22,
                CidrIp='0.0.0.0/0'
            )
            # authorize MySQL traffic from anywhere
            sg.authorize_ingress(
                DryRun=dryrun,
                GroupName=sgs_name[i],
                IpProtocol='6',
                FromPort=3306,
                ToPort=3306,
                CidrIp='172.31.0.0/21'
            )
            print colored("\tInbound/outbound rules for Web servers has been created in '%s' Security Group!" % sgs_name[i], 'green')
        elif 'DB' in sgs_name[i]:
            sg_db_id = sg.group_id
            # authorize MySQL traffic from anywhere
            sg.authorize_ingress(
                DryRun=dryrun,
                GroupName=sgs_name[i],
                IpProtocol='6',
                FromPort=3306,
                ToPort=3306,
                CidrIp='172.31.0.0/21'
            )
            # authorize SSH traffic from anywhere
            sg.authorize_ingress(
                DryRun=dryrun,
                GroupName=sgs_name[i],
                IpProtocol='6',
                FromPort=22,
                ToPort=22,
                CidrIp='0.0.0.0/0'
            )
            print colored("\tInbound/outbound rules for database servers has been created in '%s' Security Group!" % sgs_name[i], 'green')
        else:
            print colored("A Security Group with the name '%s' already exists with Id %s!\n Script aborted" % (sgs_name[i], test), 'red')
            # sys.exit()
    i += 1

# ***********************
# *     CREATE ELB      *
# ***********************
# create the ELB
elb = elb_cli.create_load_balancer(
    Name=elb_name,
    Subnets=[
        subnets_public_id[0],
        subnets_public_id[1]
    ],
    SecurityGroups=[sg_web_id],
    Scheme='internet-facing',
    Tags=[
        {
            'Key': 'Name',
            'Value': elb_name
        },
        {
            'Key': 'Env',
            'Value': environement
        },
        {
            'Key': 'App',
            'Value': app
        }
    ],
    IpAddressType='ipv4'
)
for lb in elb['LoadBalancers']:
    elb_arn = lb['LoadBalancerArn']

print colored("The '%s' Elastic Load Balancer has been created!" % elb_name, 'green')
# create the target group
tg_name = 'Web-Servers-TG'
target_group = elb_cli.create_target_group(
    Name=tg_name,
    Protocol='HTTP',
    Port=80,
    VpcId=vpc_id,
    HealthCheckProtocol='HTTP',
    HealthCheckPort='80',
    HealthCheckPath='/',
    Matcher={
        'HttpCode': '200'
    }
)

for tg in target_group['TargetGroups']:
    tg_arn = tg['TargetGroupArn']

tags = elb_cli.add_tags(
    ResourceArns=[tg_arn],
    Tags=[
        {
            'Key': 'Name',
            'Value': tg_name
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
print colored("\tThe 'Web-Servers-TG' Target Group has been created and attached to %s!" % elb_name, 'green')
# create the listener

listener = elb_cli.create_listener(
    LoadBalancerArn=elb_arn,
    Protocol='HTTP',
    Port=80,
    DefaultActions=[
        {
            'Type': 'forward',
            'TargetGroupArn': tg_arn
        },
    ]
)
print colored("\tAn HTTP Listener has been created and attached to %s!" % elb_name, 'green')

# ***********************
# *     CREATE ASG      *
# ***********************

# Create launch configuration

f = open(userdata_file, 'r')
user_data = f.read()
lc = as_cli.create_launch_configuration(
    LaunchConfigurationName=launch_config_name,
    ImageId=ami_id,
    KeyName=key_name,
    SecurityGroups=[sg_web_id],
    InstanceType='t2.micro',
    UserData=user_data,
    InstanceMonitoring={
        'Enabled': False
    },
    EbsOptimized=False,
    AssociatePublicIpAddress=False
)
print colored("The '%s' Launch Configuration has been created!" % launch_config_name, 'green')

# Create the auto scaling group
asg = as_cli.create_auto_scaling_group(
    AutoScalingGroupName=asg_name,
    LaunchConfigurationName=launch_config_name,
    MinSize=1,
    MaxSize=4,
    DesiredCapacity=2,
    DefaultCooldown=300,
    # AvailabilityZones=[subnet1_az, subnet2_az],
    TargetGroupARNs=[tg_arn],
    HealthCheckType='ELB',
    HealthCheckGracePeriod=300,
    TerminationPolicies=["Default"],
    NewInstancesProtectedFromScaleIn=False,
    VPCZoneIdentifier='%s, %s' % (subnets_public_id[0], subnets_public_id[1]),
    Tags=[
        {
            "ResourceType": "auto-scaling-group",
            "ResourceId": asg_name,
            "PropagateAtLaunch": True,
            "Value": app,
            "Key": 'App'
        },
        {
            "ResourceType": "auto-scaling-group",
            "ResourceId": asg_name,
            "PropagateAtLaunch": True,
            "Value": environement,
            "Key": 'Env'
        },
        {
            "ResourceType": "auto-scaling-group",
            "ResourceId": asg_name,
            "PropagateAtLaunch": True,
            "Value": 'MyApp-WebServer',
            "Key": 'Name'
        }
    ]
)
print colored("The '%s' Auto Scaling Group has been created and associated with '%s' Configuration Launch !" % (asg_name, launch_config_name), 'green')

# Create bucket

# s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': region})
