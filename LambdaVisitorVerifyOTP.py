import json
import boto3
import decimal

import time
def replace_decimals(obj):
    if isinstance(obj, list):
        for i in range(0,len(obj)):
            obj[i] = replace_decimals(obj[i])
        return obj
    elif isinstance(obj, dict):
        for k in obj.keys():
            obj[k] = replace_decimals(obj[k])
        return obj
    elif isinstance(obj, decimal.Decimal):
        return str(obj)
        # In my original code I'm converting to int or float, comment the line above if necessary.
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj

def verify_otp(otp):
    client = boto3.resource('dynamodb')
    table = client.Table('passcodes')
    response = table.get_item(Key={'otp': otp}, TableName='passcodes')
    response = replace_decimals(response)

    # my_passcodes_entry = {'faceId' : '12', 'otp': '6283', 'expiration' : str(int(time.time() + 300))}
    # table.put_item(Item=my_passcodes_entry, TableName='passcodes' )

    if 'Item' not in response:
        return False
    table.delete_item(Key={'otp': otp}, TableName='passcodes')
    return True



def lambda_handler(event, context):

    response = {}
    if verify_otp(event['queryStringParameters']['OTP']):
        response['status'] = 'verified'
    else:
        response['status'] = 'unverified'
    return {
        'statusCode': 200,
         'headers': {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Methods": "*"
    },
        'body': json.dumps(response)
    }
