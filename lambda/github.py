from dataclasses import dataclass


@dataclass
class GitBodyForSlack:
    reviewer: str | None
    pr_owner: str | None
    comment: str | None
    comment_url: str | None

    # GitHub Webhooksから送信されたbodyから自クラスを生成する
    @staticmethod
    def from_event_body(body):
        pr_owner: str | None = GitBodyForSlack._select_pr_owner(body)
        reviewer: str | None = body.get("comment", {}).get("user", {}).get("login")
        comment: str | None = body.get("comment", {}).get("body", {})
        comment_url: str | None = body.get("comment", {}).get("html_url", {})

        return GitBodyForSlack(reviewer, pr_owner, comment, comment_url)

    # PR作者のGitHub IDを取得する
    @staticmethod
    def _select_pr_owner(body) -> str | None:
        if body.get("issue"):
            # PRにコメントしたとき
            return body.get("issue", {}).get("user", {}).get("login")
        else:
            # PRのコードに対してコメントしたとき
            return body.get("pull_request", {}).get("user", {}).get("login")
