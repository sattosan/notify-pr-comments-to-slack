import json
import re

import urllib3

from fixtures import mention_dic
from git_body_for_slack import GitBodyForSlack

http = urllib3.PoolManager()


# テキストからメンションを抽出する
def extract_mentions(text: str | None) -> list[str]:
    if not text:
        return []

    # @から空白または改行までの部分をマッチさせるパターン
    mention_pattern = re.compile(r"@.*?(?=\s|$)")
    mentions: list[str] = mention_pattern.findall(text)
    # 重複したメンションを削除して返す
    return list(set(mentions))


# GitHubのメンションを探し、見つかれば対応するSlackのユーザ名を返す
def convert_slack_mentions(
    github_mentions: list[str], pr_owner: str | None, reviewer: str | None
) -> list[str]:
    print(
        f"github_mentions: {github_mentions}, pr_owner: {pr_owner}, reviewer: {reviewer}"
    )
    # BOTのコメントは無視する
    if reviewer in ["github-actions[bot]", "sonarcloud[bot]"]:
        return None

    slack_mentions: list[str] = []
    for mention in github_mentions:
        if mention in mention_dic:
            slack_mentions.append(mention_dic[mention])

    if slack_mentions:
        return slack_mentions

    """
    # TODO バグがありそうなのでコメントアウト
    # 自分宛てのコメントは無視する
    if pr_owner == reviewer:
        return None
    """

    # コメントにメンションがなければ変わりにPR作者にメンションする
    pr_owner_slack_user_name = select_slack_user_name(pr_owner)
    return [pr_owner_slack_user_name] if pr_owner_slack_user_name else None


# GitHubのユーザ名と対応するSlackのユーザ名を返す
def select_slack_user_name(github_user_name: str | None) -> str | None:
    if not github_user_name:
        return None

    github_mention = f"@{github_user_name}"
    return mention_dic[github_mention] if github_mention in mention_dic else None


# Slackのメンションテキストを作成する
def create_mention_text(slack_mentions: list[str]) -> str:
    # メンションがなければ空文字を返す
    if not slack_mentions:
        return ""

    # 例）"@hoge @fuga\n"
    return " ".join([f"<@{m}>" for m in slack_mentions]) + "\n"


# Slackに送信するメッセージを作成する
def create_send_data(
    mentions: list[str],
    reviewer: str | None,
    comment: str | None,
    comment_url: str | None,
):
    formatted_mentions = create_mention_text(mentions)
    formatted_reviewer = f"*{reviewer}* さんから" if reviewer else ""
    message = f"{formatted_mentions}{formatted_reviewer}以下のコメントがありました\n```{comment}```\nlink: {comment_url}"
    data = {"channel": "#test", "text": message}
    return json.dumps(data).encode("utf-8")


# Slackにメッセージを送信
def post_slack(body: GitBodyForSlack, webhooks_url: str) -> None:
    github_mentions: list[str] = extract_mentions(body.comment)
    slack_mentions: list[str] = convert_slack_mentions(
        github_mentions, body.pr_owner, body.reviewer
    )

    # Slackのメンションが見つからなければ通知しない
    if not slack_mentions:
        return None

    send_data: dict = create_send_data(
        slack_mentions, body.reviewer, body.comment, body.comment_url
    )

    http.request("POST", webhooks_url, body=send_data)
