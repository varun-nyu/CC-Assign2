import boto3

client = boto3.client('rekognition')

response = client.create_collection(
    CollectionId='ass21'
)

print(response)