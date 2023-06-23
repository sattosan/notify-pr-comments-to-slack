import ast
import json
import os
from urllib import request


def get_secret():
    headers = {"X-Aws-Parameters-Secrets-Token": os.environ["AWS_SESSION_TOKEN"]}

    secrets_extension_endpoint = (
        "http://localhost:2773/secretsmanager/get?secretId=notify-pr-comments"
    )
    req = request.Request(secrets_extension_endpoint, headers=headers)
    with request.urlopen(req) as res:
        body = json.loads(res.read())
        if "SecretString" in body:
            return ast.literal_eval(body["SecretString"])

    return None
