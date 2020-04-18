import boto3

client = boto3.client('kinesis')
response = client.get_records(
    ShardIterator='string',
    Limit=123
)