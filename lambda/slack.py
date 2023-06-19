import json
import re

import fixtures
import urllib3

http = urllib3.PoolManager()
mention_dic = fixtures.mention_dic


# テキストからメンションを抽出する
def extract_mentions(text: str) -> list[str]:
    # @から空白または\r\nまたは行末までの部分をマッチさせるパターン
    pattern = r'@.*?(?=\s|\r\n|$)'
    mentions = re.findall(pattern, text, re.DOTALL)
    # 重複したメンションを削除して返す
    return list(set(mentions))


# GitHubのメンションを探し、見つかれば対応するSlackのユーザ名を返す
def convert_slack_mentions(github_mentions: list[str]) -> list[str]:
    slack_mentions: list[str] = []
    for mention in github_mentions:
        if mention in mention_dic:
            slack_mentions.append(mention_dic[mention])

    return slack_mentions


# GitHubのユーザ名と対応するSlackのユーザ名を返す
def select_slack_user_name(github_user_name: str) -> str | None:
    return mention_dic[github_user_name]


# Slackのメンションテキストを作成する
def create_mention_text(slack_mentions: list[str]) -> str:
    # メンションがなければ空文字を返す
    if not slack_mentions:
        return ""

    # 例）"@hoge @fuga\n"
    return " ".join([f"<@{m}>" for m in slack_mentions]) + "\n"


# Slackに送信するメッセージを作成する
def create_send_data(user: str | None, mentions: list[str], comment_text: str, comment_url: str):
    formatted_mentions = create_mention_text(mentions)
    formatted_user = f"*{user}* さんから" if user else ""
    message = f"{formatted_mentions}{formatted_user}以下のコメントがありました\n```{comment_text}```\nlink: {comment_url}"
    data = {
        "channel": "#test",
        "text": message
    }
    return json.dumps(data).encode('utf-8')


# Slackにメッセージを送信
def post_slack(user: str | None, comment_text: str, comment_url: str, webhooks_url: str):
    github_mentions: list[str] = extract_mentions(comment_text)
    slack_mentions: list[str] = convert_slack_mentions(github_mentions)
    send_data: dict = create_send_data(user, slack_mentions, comment_text, comment_url)
    http.request('POST', webhooks_url, body=send_data)
