import boto3

client=boto3.client('rekognition')

response = client.start_stream_processor(
    Name='Assign2SP'
)