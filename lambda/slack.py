import json
import re

import fixtures
import urllib3

http = urllib3.PoolManager()
mention_dic = fixtures.mention_dic


# テキストからメンションを抽出する
def extract_mentions(text: str) -> list[str]:
    # @から空白または改行までの部分をマッチさせるパターン
    mention_pattern = re.compile(r"@.*?(?=\s|$)")
    mentions: list[str] = mention_pattern.findall(text)
    # 重複したメンションを削除して返す
    return list(set(mentions))


# GitHubのメンションを探し、見つかれば対応するSlackのユーザ名を返す
def convert_slack_mentions(github_mentions: list[str], pr_owner: str) -> list[str]:
    slack_mentions: list[str] = []
    for mention in github_mentions:
        if mention in mention_dic:
            slack_mentions.append(mention_dic[mention])

    # コメントにメンションがなければ変わりにPR作者にメンションする
    return slack_mentions if slack_mentions else [select_slack_user_name(pr_owner)]


# GitHubのユーザ名と対応するSlackのユーザ名を返す
def select_slack_user_name(github_user_name: str) -> str | None:
    github_mention = f"@{github_user_name}"
    if github_mention in mention_dic:
        return mention_dic[github_mention]

    return None


# Slackのメンションテキストを作成する
def create_mention_text(slack_mentions: list[str]) -> str:
    # メンションがなければ空文字を返す
    if not slack_mentions:
        return ""

    # 例）"@hoge @fuga\n"
    return " ".join([f"<@{m}>" for m in slack_mentions]) + "\n"


# Slackに送信するメッセージを作成する
def create_send_data(
    mentions: list[str], reviewer: str, comment_text: str, comment_url: str
):
    formatted_mentions = create_mention_text(mentions)
    formatted_reviewer = f"*{reviewer}* さんから" if reviewer else ""
    message = f"{formatted_mentions}{formatted_reviewer}以下のコメントがありました\n```{comment_text}```\nlink: {comment_url}"
    data = {"channel": "#test", "text": message}
    return json.dumps(data).encode("utf-8")


# Slackにメッセージを送信
def post_slack(
    reviewer: str, pr_owner: str, comment_text: str, comment_url: str, webhooks_url: str
) -> None:
    github_mentions: list[str] = extract_mentions(comment_text)
    slack_mentions: list[str] = convert_slack_mentions(github_mentions, pr_owner)
    send_data: dict = create_send_data(
        slack_mentions, reviewer, comment_text, comment_url
    )

    http.request("POST", webhooks_url, body=send_data)
