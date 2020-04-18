import json
import boto3

S3_LINK = "https://assign2b.s3.amazonaws.com/"
def get_visitors():
	s3_client = boto3.client('s3')
	d = s3_client.list_objects(Bucket='visitors-buck')
	result = []
	for k in d["Contents"]:
		temp = {}
		link = S3_LINK + k["Key"]
		temp["s3_image"] = k["Key"]
		temp["link"] = link
		result.append(temp)
	return result



def lambda_handler(event, context):
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps(get_visitors(), indent=4, sort_keys=True, default=str)
    }
