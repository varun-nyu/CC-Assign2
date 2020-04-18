import boto3

client=boto3.client('rekognition')

response = client.create_stream_processor(
    Input={
        'KinesisVideoStream': {
            'Arn': 'arn:aws:kinesisvideo:us-east-1:146486855224:stream/Vid2/1587165228227'
        }
    },
    Output={
        'KinesisDataStream': {
            'Arn': 'arn:aws:kinesis:us-east-1:146486855224:stream/Vid2DS'
        }
    },
    Name='NewAss21',
    Settings={
        'FaceSearch': {
            'CollectionId': 'ass21'
        }
    },
    RoleArn='arn:aws:iam::146486855224:role/Assign2Role'
)

print(response)