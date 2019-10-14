import boto3

from PIL import Image
from io import BytesIO

def lambda_handler(event, context):
    bucket_event  = event['Records'][0]['s3']
    bucket_name   = bucket_event['bucket']['name']
    bucket_key    = bucket_event['object']['key']
    bucket_object = boto3.resource('s3').Object(bucket_name, bucket_key)
    bucket_media  = bucket_object.get()['Body'].read()
    
    extension = bucket_key.split('.')[-1].lower()
    extension = 'JPEG' if extension in ['jpg', 'jpeg'] else 'PNG' if extension in ['png'] else None
    if extension:
        # https://pythonspot.com/netflix-like-thumbnails-with-python/
        img = Image.open(BytesIO(bucket_media))
        img = img.resize((128,128), Image.ANTIALIAS)
        key = f'thumbs/{bucket_key.split("/")[-1]}'
        with BytesIO() as buffer:
            img.save(buffer, extension)
            buffer.seek(0)
            boto3.resource('s3').Bucket(bucket_name).put_object(Body=buffer, Key=key)
    return {'statusCode': 200}
