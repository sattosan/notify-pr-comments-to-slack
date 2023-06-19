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

    SLACK_WEBHOOKS_URL = secret["SLACK_WEBHOOKS_URL"]
    comment = body["comment"]
    user_name: str | None = slack.select_slack_user_name(comment["user"]["login"])
    slack.post_slack(user_name, comment['body'], comment["html_url"], SLACK_WEBHOOKS_URL)

    return {
        'statusCode': 200,
        'body': '{"message": "send message to slack"}'
    }
