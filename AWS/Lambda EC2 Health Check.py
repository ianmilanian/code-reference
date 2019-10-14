import boto3

from datetime import datetime
from datetime import timedelta

def lambda_handler(event, context):
    kwargs = {'region_name': 'region'}
    cloud_watch = boto3.client('cloudwatch', **kwargs)
    for instance in boto3.client('ec2', **kwargs).describe_instances(Filters=[{}]).get('Reservations', []):
        id = instance['Instances'][0]['InstanceId']
        ip = instance['Instances'][0]['PrivateIpAddress']
        for metric in ['CPUUtilization', 'NetworkIn', 'NetworkOut', 'DiskReadOps', 'DiskReadBytes', 'DiskWriteOps', 'DiskWriteBytes']:
            metric_stats   = [d['Average'] for d in cloud_watch.get_metric_statistics(
                Namespace  = 'AWS/EC2',
                MetricName = metric,
                Dimensions = [{'Name':'InstanceId', 'Value':id}],
                StartTime  = datetime.now() - timedelta(minutes=60),
                EndTime    = datetime.now(),
                Period     = 300,
                Statistics = ['Average'])['Datapoints']]
            avg = int(sum(metric_stats) / len(metric_stats)) if metric_stats else None
            print(id, ip, metric, avg)
    return { 'statusCode': 200 }
