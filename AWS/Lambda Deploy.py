import sys
import tempfile

with tempfile.TemporaryDirectory() as build:        
    src  = "source.py" # local directory
    name = "treecloud-lambda"
    temp = r"{}\temp".format(build)
    dest = r"{}\deploy.zip".format(build)
    pip  = r"{}\Scripts\pip".format(build)
    aws  = r"{}\Scripts\aws".format(sys.exec_prefix)
    env  = r"{}\Scripts\virtualenv".format(sys.exec_prefix)
    
    # Create virtualenv and install modules.
    !@echo off
    !$env $build
    !$pip install boto3

    # Copy site-packages and move source.
    !mkdir $temp
    !move $src $temp
    !xcopy /q /e $build\Lib\site-packages $temp

    # Delete extra packages.
    !for /d %x in ($temp\boto*) do rd /s /q "%x"
    !for /d %x in ($temp\wheel*) do rd /s /q "%x"
    !for /d %x in ($temp\setuptools*) do rd /s /q "%x"
    !for /d %x in ($temp\easy-install*) do rd /s /q "%x"

    # Create deployment file.
    !7z a $dest $temp\.\*
    
    # Delete lambda function.
    !$aws lambda delete-function \
        --function-name $name
    
    # Create lambda function.
    !$aws lambda create-function \
        --function-name $name \
        --region us-east-1 \
        --zip-file fileb://$dest \
        --role arn:aws:iam::525363247818:role/treecloud-lambda-full \
        --handler source.lambda_handler \
        --runtime python3.6 \
        --timeout 10 \
        --memory-size 128
    
    # Invoke lambda function.
    !$aws lambda invoke \
        --function-name $name \
        output.txt

'''
import boto3

def lambda_handler(event, context):
    s3 = boto3.Session(region_name='us-east-1').resource('s3')
    for bucket in s3.buckets.all():
        print(bucket)
    return 'Hello from Lambda 2.0'
'''
