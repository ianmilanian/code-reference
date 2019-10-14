import os
import json
import boto3

from datetime import datetime
from datetime import timedelta

def lambda_handler(event, context):
    def json_serialize(obj):
        if isinstance(obj, (datetime)):
            return obj.isoformat()
    def is_stale(snapshot, retention):
        return datetime.now() - snapshot['StartTime'].replace(tzinfo=None) > timedelta(days=retention)
    
    responses = []
    retention = int(os.environ['retention'])
    is_backup = {'Name': 'tag:Snapshot', 'Values': ['Yes']}
    is_volume = {'Name': 'status',       'Values': ['in-use']}
    tag_specs = [{'ResourceType': 'snapshot', 'Tags': [{'Key':'Snapshot', 'Value':'Yes'}]}]
    
    kwargs = {'endpoint_url': os.environ['ec2_endpoint'], 'region_name': 'region'}
    client = boto3.client('ec2', **kwargs)
    for volume in client.describe_volumes(Filters=[is_volume, is_backup]).get('Volumes', []):
        responses.append(client.create_snapshot(
            Description       = 'snapshot-123',
            VolumeId          = volume['VolumeId'],
            TagSpecifications = tag_specs))
        is_snapshot = {'Name': 'volume-id', 'Values': [volume['VolumeId']]}
        for snapshot in client.describe_snapshots(Filters=[is_snapshot, is_backup]).get('Snapshots', []):
            if is_stale(snapshot, retention):
                responses.append(boto3.resource('ec2', **kwargs).Snapshot(snapshot['SnapshotId']).delete())
    return json.loads(json.dumps(responses, default=json_serialize))
