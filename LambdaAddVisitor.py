import json
import boto3
import decimal

import time
from random import randint

def add_faces_to_collection(bucket,photo,collection_id):


    
    client=boto3.client('rekognition')

    response=client.index_faces(CollectionId=collection_id,
                                Image={'S3Object':{'Bucket':bucket,'Name':photo}},
                                ExternalImageId=photo,
                                MaxFaces=1,
                                QualityFilter="AUTO",
                                DetectionAttributes=['ALL'])

    print ('Results for ' + photo)  
    print('Faces indexed:')                     
    for faceRecord in response['FaceRecords']:
         return faceRecord['Face']['FaceId']
    return len(response['FaceRecords'])

def create_visitor(name,phone,s3Image):
    num = randint(100000, 999999)
    faceId = add_faces_to_collection('visitors-buck',s3Image,'assignment-2')
    print(faceId)
    visitors_photo = []

    s3 = boto3.resource('s3')
    copy_source = {
    'Bucket': 'visitors-buck',
    'Key': s3Image
    }
    s3.meta.client.copy(copy_source, 'assign2b',s3Image)
    print("Here - 2")
    client = boto3.client('s3')
    x = client.delete_object(Bucket='visitors-buck', Key=s3Image)
    print(x)
    print("Here - 3")
    photo={'objectKey':s3Image , 'bucket' : 'assign2b', 'createdTimestamp' : str(time.ctime(time.time()))}
    print("Here - 4")
    visitors_photo.append(photo)
    my_visitor_entry = {'faceId' : faceId , 'name' : name , 'phone' : phone , 'photo' : visitors_photo}
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('visitors')
    print("Here - 1")
    response = table.put_item(Item=my_visitor_entry, TableName='visitors')
    print("response ->")
    print(response)



def lambda_handler(event, context):
    # TODO implement
    # print(event)
    resp = {}
    create_visitor(event['queryStringParameters']['name'], event['queryStringParameters']['phone'], event['queryStringParameters']['s3_image']  )
    resp['status'] = 'added'
    return {
        'statusCode': 200,

        'headers': {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Methods": "*"
    },
        'body': json.dumps(resp)
    }
