import settings
import slack
import validate


# エントリーポイント
def lambda_handler(event, _):
    secret = settings.get_secret()
    ok, body = validate.validate_request(event, secret)
    if not ok:
        # リクエストが無効だった場合
        return body

    pr_owner: str = body["pull_request"]["user"]["login"]
    reviewer: str = body["comment"]["user"]["login"]
    comment: str = body["comment"]["body"]
    comment_url: str = body["comment"]["html_url"]
    SLACK_WEBHOOKS_URL = secret["SLACK_WEBHOOKS_URL"]

    slack.post_slack(reviewer, pr_owner, comment, comment_url, SLACK_WEBHOOKS_URL)

    return {"statusCode": 200, "body": '{"message": "send message to slack"}'}
