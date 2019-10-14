import os
import time
import json
import boto3

from base64 import b64encode
from base64 import b64decode

def decrypt(key):
    return boto3.client('kms').decrypt(CiphertextBlob=b64decode(os.environ[key]))['Plaintext'].decode()

def run_command(job):
    commands = [
        '$env:AWS_DEFAULT_REGION=(Get-SSMParameterValue -Names region_name -WithDecryption $True).Parameters[0].Value',
        '$env:AWS_ACCESS_KEY_ID=(Get-SSMParameterValue -Names access_key -WithDecryption $True).Parameters[0].Value',
        '$env:AWS_SECRET_ACCESS_KEY=(Get-SSMParameterValue -Names secret_key -WithDecryption $True).Parameters[0].Value']
    
    proc = job['processor']
    path = f'{decrypt("local_bin")}/{proc}'
    data = b64encode(json.dumps(job).encode()).decode()
    commands.append(f'Start-Process -FilePath "{path}/{proc}.exe" -workingdirectory "{path}" -RedirectStandardOutput {path}/debug.log -ArgumentList "{data}"')
    
    return boto3.client('ssm').send_command(
        InstanceIds  = [job['instance_id']],
        DocumentName = 'AWS-RunPowerShellScript',
        Parameters   = {'commands': commands})

def lambda_handler(event, context):
    for message in boto3.resource('sqs').Queue(decrypt(sqs_url)).receive_messages([]):
        run_command(json.loads(message.body))
        message.delete()
    return {'statusCode': 200 }
