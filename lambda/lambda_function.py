import json

import fixtures
import settings
import urllib3
import validate

http = urllib3.PoolManager()
user_dic = fixtures.user_dic


# Slackに送信するメッセージを作成する
def create_send_data(user, mention, body, comment_url):
    formatted_mention = f"<@{mention}>\n" if mention else ""
    formatted_user = f"*{user}* さんから" if user else ""
    message = f"{formatted_mention}{formatted_user}以下のコメントがありました\n```{body}```\nlink: {comment_url}"
    data = {
        "channel": "#test",
        "text": message
    }
    return json.dumps(data).encode('utf-8')


# Slackにメッセージを送信
def post_slack(user: str, body: str, comment_url: str, webhooks_url: str):
    mention: str = search_mention(body)
    send_data = create_send_data(user, mention, body, comment_url)
    http.request('POST', webhooks_url, body=send_data)


# GitHubのユーザ名と対応するSlackのユーザ名を返す
def select_slack_user_name(github_user_name: str) -> str:
    return user_dic[github_user_name]


# GitHubのメンションを探し、見つかれば対応するSlackのユーザ名を返す
def search_mention(body: str) -> str | None:
    for github_user_name in user_dic:
        if f"@{github_user_name}" in body:
            return user_dic[github_user_name]
    return None


# エントリーポイント
def lambda_handler(event, _):
    secret = settings.get_secret()
    ok, body = validate.validate_request(event, secret)
    if not ok:
        # リクエストが無効だった場合
        return body

    SLACK_WEBHOOKS_URL = secret["SLACK_WEBHOOKS_URL"]
    comment = body["comment"]
    user_name = select_slack_user_name(comment["user"]["login"])
    post_slack(user_name, comment['body'], comment["html_url"], SLACK_WEBHOOKS_URL)

    return {
        'statusCode': 200,
        'body': '{"message": "send message to slack"}'
    }
