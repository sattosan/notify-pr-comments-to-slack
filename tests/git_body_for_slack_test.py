import unittest

from src.git_body_for_slack import GitBodyForSlack


class TestGitBodyForSlack(unittest.TestCase):
    def test_from_event_body(self):
        body = {
            "issue": {"user": {"login": "pr_owner"}},
            "comment": {
                "user": {"login": "reviewer"},
                "body": "comment body",
                "html_url": "comment url",
            },
            "repository": {"name": "repository name"},
        }
        expected_result = GitBodyForSlack(
            reviewer="reviewer",
            pr_owner="pr_owner",
            comment="comment body",
            comment_url="comment url",
            repository="repository name",
        )

        result = GitBodyForSlack.from_event_body(body)

        self.assertEqual(result, expected_result)

    def test_select_pr_owner_with_issue(self):
        body = {"issue": {"user": {"login": "pr_owner"}}}
        expected_result = "pr_owner"

        result = GitBodyForSlack._select_pr_owner(body)

        self.assertEqual(result, expected_result)

    def test_select_pr_owner_with_pull_request(self):
        body = {"pull_request": {"user": {"login": "pr_owner"}}}
        expected_result = "pr_owner"

        result = GitBodyForSlack._select_pr_owner(body)

        self.assertEqual(result, expected_result)

    def test_select_pr_owner_with_unknown_body(self):
        body = {}
        expected_result = None

        result = GitBodyForSlack._select_pr_owner(body)

        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
