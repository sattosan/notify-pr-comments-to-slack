import hashlib
import hmac
import json


def validate_request(event, secret):
    if secret is None:
        return False, {"statusCode": 400, "body": "Bad Request" }

    if 'headers' not in event or 'X-Hub-Signature' not in event['headers']:
        return False, {"statusCode": 400, "body": "Bad Request" }
    headers = event['headers']
    # HMAC値による簡易認証処理
    signature = headers['X-Hub-Signature']
    signedBody = "sha1=" + hmac.new(bytes(secret["GITHUB_WEBHOOKS_SECRET"], 'utf-8'), bytes(event['body'], 'utf-8'), hashlib.sha1).hexdigest()
    if (signature != signedBody):
        return False, {"statusCode": 401, "body": "Unauthorized"}

    # プルリクの情報を抽出
    body = json.loads(event['body'])
    if "action" not in body:
        # actionのキーがなければ終了
        return False, {
            'statusCode': 200,
            'body': '{"message": "action is not found in body"}'
        }

    if body["action"] != "created":
        # コメント作成以外(削除や更新イベント)は通知しない
        return False, {
            'statusCode': 200,
            'body': '{"message": "skip comment because action type isn\'t created"}'
        }

    if "comment" not in body:
        return False, {
            'statusCode': 200,
            'body': '{"message": "comment is not found in body"}'
        }

    return True, body
