REM /opt/python/package
mkdir libs && python -m pip install --target=libs boto3 requests
7z.exe a -tzip "lambda_function.zip" lambda_function.py .\libs\*
