import ast
import json
import os
from urllib import request


def get_secret():
    aws_session_token = os.environ.get("AWS_SESSION_TOKEN", "")
    if not aws_session_token:
        return None

    headers = {"X-Aws-Parameters-Secrets-Token": aws_session_token}

    secrets_extension_endpoint = (
        "http://localhost:2773/secretsmanager/get?secretId=notify-pr-comments"
    )
    req = request.Request(secrets_extension_endpoint, headers=headers)
    with request.urlopen(req) as res:
        body = json.loads(res.read())
        if "SecretString" in body:
            return ast.literal_eval(body["SecretString"])

    return None
