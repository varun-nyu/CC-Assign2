import boto3
import os

client = boto3.client('rekognition')
print("Setting up collection")

collectionId = input("Enter a collection id:")
# response = client.create_collection(
#     CollectionId=collectionId
# )

print("collection-id-response")
# print(response)

vidstream = input("Enter a vidstream arn:")
datastream = input("Enter a datastream arn:")
streamprocessorname = input("Enter a stream processor name arn:")
response = client.create_stream_processor(
    Input={
        'KinesisVideoStream': {
            'Arn': vidstream
        }
    },
    Output={
        'KinesisDataStream': {
            'Arn': datastream
        }
    },
    Name=streamprocessorname,
    Settings={
        'FaceSearch': {
            'CollectionId': collectionId
        }
    },
    RoleArn='arn:aws:iam::146486855224:role/Assign2Role'
)

os.system("aws rekognition list-collections")
os.system("aws rekognition list-stream-processors")

response = client.start_stream_processor(
    Name=streamprocessorname
)


connectionName = input("Enter a connection name:")
os.system("aws kinesis register-stream-consumer --consumer-name "+connectionName+" --stream-arn " + datastream)
