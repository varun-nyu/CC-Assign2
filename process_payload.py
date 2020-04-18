import base64, time, json, sys,decimal
import time

from random import randint
from pip._internal import main
main(['install', 'boto3', '--target', '/tmp/'])
sys.path.insert(0,'/tmp/')
import boto3
import cv2


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

def save_shot(streamARN, fragmentNumber,faceId):
    print("In SavedShot")
    s3_client = boto3.client('s3')
    rekClient=boto3.client('rekognition')
    
    kvs = boto3.client("kinesisvideo")
    
    endpoint = kvs.get_data_endpoint(
        APIName="GET_MEDIA",
        StreamARN=streamARN
    )['DataEndpoint']
    # print("Kinesis Data endpoint: ",endpoint)

    kvam = boto3.client("kinesis-video-media", endpoint_url=endpoint)

    kvs_stream = kvam.get_media( StreamARN=streamARN, StartSelector={ 'StartSelectorType': 'FRAGMENT_NUMBER', 'AfterFragmentNumber': fragmentNumber})

    
    collectionId="assign2"
    # print("KVS Stream: ",kvs_stream)
    with open('/tmp/stream.mkv', 'wb') as f:
        streamBody = kvs_stream['Payload'].read(1024*512)
        f.write(streamBody)
        cap = cv2.VideoCapture('/tmp/stream.mkv')
        ret, frame = cap.read() 
        cv2.imwrite('/tmp/frame.jpg', frame)
        fileName= 'SavedShot'+'-'+fragmentNumber+ '-T-'+ str(time.time())+'.jpg'
        print ('before upload')
        s3_client.upload_file(
            '/tmp/frame.jpg',
            'saved-shots', 
            fileName
        )
        cap.release()
        print('Image uploaded')

    return

def store_image(streamARN, fragmentNumber,faceId):
    print("In Store Image")
    s3_client = boto3.client('s3')
    rekClient=boto3.client('rekognition')
    
    kvs = boto3.client("kinesisvideo")
    
    endpoint = kvs.get_data_endpoint(
        APIName="GET_MEDIA",
        StreamARN=streamARN
    )['DataEndpoint']
    print("Kinesis Data endpoint: ",endpoint)

    kvam = boto3.client("kinesis-video-media", endpoint_url=endpoint)

    kvs_stream = kvam.get_media( StreamARN=streamARN, StartSelector={ 'StartSelectorType': 'FRAGMENT_NUMBER', 'AfterFragmentNumber': fragmentNumber})

    
    collectionId="assign2"
    print("KVS Stream: ",kvs_stream)
    
    with open('/tmp/stream.mkv', 'wb') as f:

        streamBody = kvs_stream['Payload'].read(1024*512)
        f.write(streamBody)
      
        s3_client.upload_file(
            '/tmp/stream.mkv',
            'smart-door-vo', 
            'mkvfile.mkv'
        )
       
        cap = cv2.VideoCapture('/tmp/stream.mkv')
       
        
        ret, frame = cap.read() 
        cv2.imwrite('/tmp/frame.jpg', frame)
        
        
        
        fileName= 'FaceId'+'-'+fragmentNumber+'.jpg'
        print ('before upload')
        s3_client.upload_file(
            '/tmp/frame.jpg',
            'smart-door-vo', 
            fileName
        )
        cap.release()
        print('Image uploaded')
        return fileName, "face"
    return

def tackle_new_visitor(data):
    print("New Visitor")
    streamARN = data['StreamArn']
    fragmentNumber = data['FragmentNumber']
    fileName,faceId=store_image(streamARN,fragmentNumber, None)
    return

def generate_otp(phone):
    print("Generate OTP")
    otp = randint(100000, 999999)
    
    item = {}
    item['otp'] = str(otp)
    item['faceid'] = 'static'
    item['expiration'] = str(int(time.time() + 300))

    client = boto3.resource('dynamodb')
    table = client.Table('passcodes')
    response = table.get_item(Key={'phone': phone}, TableName='passcodes')
    if 'Item' not in response:
        table.put_item(Item=item)
        sns = boto3.client('sns')
        message = "Your otp is : " + str(otp)
        x = sns.publish(PhoneNumber = phone, Message=message )

def authorize(faceId):
    print("Authorize")
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('visitors')
    response = table.get_item(Key={'faceId': faceId}, TableName='visitors')
    response = replace_decimals(response)
    phone = response['Item']['phoneNumber']
    generate_otp(phone)

    print("Phone:" + phone)



def process_face_search_response(payload):
    print("Process Face Search")
    if(0!=len(payload)):
        if(0!=len(payload[0]['MatchedFaces'])):
            faceId = payload[0]['MatchedFaces'][0]['Face']['FaceId']
            print("Found Face Id :" + faceId)
            authorize(faceId)
    return



def lambda_handler(event, context):
    # TODO implement
    for record in event['Records']:
        
        payload = json.loads(base64.b64decode(record['kinesis']['data']))
        save_shot(payload['InputInformation']['KinesisVideo']['StreamArn'],payload['InputInformation']['KinesisVideo']['FragmentNumber'],None)
        print(payload)
        if 0 != len(payload['FaceSearchResponse'][0]['MatchedFaces']):
          process_face_search_response(payload['FaceSearchResponse'])
        else:
            tackle_new_visitor(payload['InputInformation']['KinesisVideo'])
    print("End Lambda")

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }