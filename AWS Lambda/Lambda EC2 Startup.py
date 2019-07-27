import os
import boto3

def lambda_handler(event, context):
    def get_id(instance):
        return instance['Instances'][0]['InstanceId']
    
    monitored = {'Name': 'tag:Startup', 'Values': ['Yes']}
    kwargs    = {'endpoint_url': os.environ['ec2_endpoint'], 'region_name': 'region'}
    client    = boto3.client('ec2', **kwargs)
    instances = client.describe_instances(Filters=[monitored]).get('Reservations', [])
    return client.start_instances(InstanceIds=[get_id(instance) for instance in instances])
