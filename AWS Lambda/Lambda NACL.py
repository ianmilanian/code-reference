import os
import json
import boto3

from base64 import b64decode
from datetime import datetime

ENCRYPTED = os.environ['network_acl_id']
DECRYPTED = boto3.client('kms', endpoint_url=os.environ['kms_endpoint']).decrypt(CiphertextBlob=b64decode(ENCRYPTED))['Plaintext']

def json_serialize(obj):
    if isinstance(obj, (datetime)):
        return obj.isoformat()

def lambda_handler(event, context):
    nacl = boto3.resource('ec2', endpoint_url=os.environ['ec2_endpoint']).NetworkAcl(DECRYPTED.decode("utf-8"))
    lock = any(entry.get('RuleNumber', None) == 1 for entry in nacl.entries) # lock exists?
    
    responses = []
	if lock:
		responses.append(nacl.delete_entry(Egress=False, RuleNumber=1))
		responses.append(nacl.delete_entry(Egress=True,  RuleNumber=1))
    else:
		responses.append(nacl.create_entry(CidrBlock='123.456.7.8/32', Egress=False, Protocol='-1', RuleAction='deny', RuleNumber=1))
		responses.append(nacl.create_entry(CidrBlock='123.456.7.8/32', Egress=True,  Protocol='-1', RuleAction='deny', RuleNumber=1))
    return json.loads(json.dumps(responses, default=json_serialize))
