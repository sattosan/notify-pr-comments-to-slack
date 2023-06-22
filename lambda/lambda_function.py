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

    pr_owner: str = body.get("pull_request", {}).get("user", {}).get("login")
    reviewer: str = body.get("comment", {}).get("user", {}).get("login")
    comment: str = body.get("comment", {}).get("body", {})
    comment_url: str = body.get("comment", {}).get("html_url", {})
    SLACK_WEBHOOKS_URL = secret["SLACK_WEBHOOKS_URL"]

    slack.post_slack(reviewer, pr_owner, comment, comment_url, SLACK_WEBHOOKS_URL)

    return {"statusCode": 200, "body": '{"message": "send message to slack"}'}
