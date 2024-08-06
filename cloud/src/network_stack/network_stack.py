from aws_cdk import Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from constructs import Construct

from utils.stack_util import add_tags_to_stack
from typing import Dict

class NetworkStack(Stack):
    vpc = None

    def __init__(self, scope: Construct, construct_id: str, config: Dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Apply common tags to stack resources.
        add_tags_to_stack(self, config)

        # VPC
        self.vpc = ec2.Vpc(
            self,
            id="vpc",
            nat_gateways=1,  # One NAT Gateway for the private subnets
            ip_addresses=ec2.IpAddresses.cidr(config["network"]["vpc"]["cidr"]),
            max_azs=3,  # Adjust this to the number of Availability Zones you want to use
            vpc_name="Vpc-"+config["stage"],
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public-subnet",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="private-subnet-with-egress",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="private-subnet-isolated",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24
                )
            ],
        )
        
        # Select the subnets for VPC endpoint interfaces
        subnet_vpc_endpoint_interface = self.vpc.select_subnets(
            subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
        ).subnets[0]

        subnet_selection_interface = ec2.SubnetSelection(
            subnets=[subnet_vpc_endpoint_interface]
        )
        
        # VPC Flow Logs
        log_group = logs.LogGroup(self, "flow-logs-group")
        flow_log_role = iam.Role(
            self,
            "FlowLogRole",
            role_name="FlowLogRole-"+config["stage"],
            assumed_by=iam.ServicePrincipal("vpc-flow-logs.amazonaws.com"),
        )
        ec2.FlowLog(
            self,
            "FlowLog",
            flow_log_name="FlowLog-"+config["stage"],
            resource_type=ec2.FlowLogResourceType.from_vpc(self.vpc),
            destination=ec2.FlowLogDestination.to_cloud_watch_logs(
                log_group, flow_log_role
            ),
        )

        # VPC Endpoints
        self.vpc.add_gateway_endpoint(
            "vpce-s3",
            service=ec2.GatewayVpcEndpointAwsService.S3,
            subnets=[ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)]
        )
        self.vpc.add_interface_endpoint(
            "vpce-ecr",
            service=ec2.InterfaceVpcEndpointAwsService.ECR,
            subnets=subnet_selection_interface,
        )
        self.vpc.add_interface_endpoint(
            "vpce-ecr-docker",
            service=ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER,
            subnets=subnet_selection_interface,
        )
        self.vpc.add_interface_endpoint(
            "vpce-cloudwatch-logs",
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS,
            subnets=subnet_selection_interface,
        )
        self.vpc.add_interface_endpoint(
            "vpce-cloudwatch",
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH,
            subnets=subnet_selection_interface,
        )
        self.vpc.add_interface_endpoint(
            "vpce-ecs",
            service=ec2.InterfaceVpcEndpointAwsService.ECS,
            subnets=subnet_selection_interface,
        )
        self.vpc.add_interface_endpoint(
            "vpce-ecs-agent",
            service=ec2.InterfaceVpcEndpointAwsService.ECS_AGENT,
            subnets=subnet_selection_interface,
        )
        self.vpc.add_interface_endpoint(
            "vpce-ecs-telemetry",
            service=ec2.InterfaceVpcEndpointAwsService.ECS_TELEMETRY,
            subnets=subnet_selection_interface,
        )
        self.vpc.add_interface_endpoint(
            "vpce-xray",
            service=ec2.InterfaceVpcEndpointAwsService.XRAY,
            subnets=subnet_selection_interface,
        )
        self.vpc.add_interface_endpoint(
            "vpce-ses",
            service=ec2.InterfaceVpcEndpointAwsService.SES,
            subnets=subnet_selection_interface,
        )
        self.vpc.add_interface_endpoint(
            "vpce-ssm",
            service=ec2.InterfaceVpcEndpointAwsService.SSM,
            subnets=subnet_selection_interface,
        )
        self.vpc.add_interface_endpoint(
            "vpce-ssm-messages",
            service=ec2.InterfaceVpcEndpointAwsService.SSM_MESSAGES,
            subnets=subnet_selection_interface,
        )
        self.vpc.add_interface_endpoint(
            "vpce-ec2-messages",
            service=ec2.InterfaceVpcEndpointAwsService.EC2_MESSAGES,
            subnets=subnet_selection_interface,
        )
        self.vpc.add_interface_endpoint(
            "vpce-ec2",
            service=ec2.InterfaceVpcEndpointAwsService.EC2,
            subnets=subnet_selection_interface,
        )
        self.vpc.add_gateway_endpoint(
            "DynamoDbEndpoint",
            service=ec2.GatewayVpcEndpointAwsService.DYNAMODB,
            subnets=[ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)]
        )
