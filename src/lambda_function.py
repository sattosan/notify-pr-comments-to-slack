import settings
import slack
import validate
from git_body_for_slack import GitBodyForSlack


# エントリーポイント
def lambda_handler(event, _):
    secret = settings.get_secret()
    ok, body = validate.validate_request(event, secret)
    if not ok:
        # リクエストが無効だった場合
        return body

    body_for_slack: GitBodyForSlack = GitBodyForSlack.from_event_body(body)
    SLACK_WEBHOOKS_URL = secret["SLACK_WEBHOOKS_URL"]

    slack.post_slack(body_for_slack, SLACK_WEBHOOKS_URL)

    return {"statusCode": 200, "body": '{"message": "send message to slack"}'}
