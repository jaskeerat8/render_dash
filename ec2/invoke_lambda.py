# Importing Libraries
import os
import json
import boto3

def aws():
    # Setting up Boto3 Client
    region_name = "ap-southeast-2"
    secret_name = "dashboard"
    session = boto3.session.Session(region_name=region_name, aws_access_key_id=os.environ.get("aws_access_key_id"),
                                    aws_secret_access_key=os.environ.get("aws_secret_access_key"))
    sm_client = session.client(service_name="secretsmanager")
    lambda_client = session.client("lambda")

    # Reading Data from Secrets Manager
    try:
        get_secret_value_response = sm_client.get_secret_value(SecretId=secret_name)
        value = json.loads(get_secret_value_response["SecretString"])
    except Exception as e:
        value = e
    return lambda_client, value

def get_info(payload):
    lambda_client, value = aws()
    response = lambda_client.invoke(FunctionName=value["lambda_get_userinfo"], InvocationType="RequestResponse", Payload=json.dumps(payload))
    response_payload = json.loads(response["Payload"].read().decode("utf-8"))
    return response_payload["body"]

def generate_report(payload):
    lambda_client, value = aws()
    response = lambda_client.invoke(FunctionName=value["lambda_generate_report"], InvocationType="RequestResponse", Payload=json.dumps(payload))
    response_payload = json.loads(response["Payload"].read().decode("utf-8"))
    return response_payload["body"], response_payload["url"]

if __name__ == "__main__":
    print("Invoked Lambda")
