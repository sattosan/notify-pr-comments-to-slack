import json
import unittest
from unittest.mock import patch

from src import slack


class TestExtractMentions(unittest.TestCase):
    def test_empty_text(self):
        text = ""
        expected_mentions = []
        self.assertEqual(slack.extract_mentions(text), expected_mentions)

    def test_no_mentions(self):
        text = "This is a sample text without any mentions."
        expected_mentions = []
        self.assertEqual(slack.extract_mentions(text), expected_mentions)

    def test_single_mention(self):
        text = "Hello @username How are you?"
        expected_mentions = ["@username"]
        self.assertEqual(slack.extract_mentions(text), expected_mentions)

    def test_multiple_mentions(self):
        text = "Hey @user1\n, have you met @user2\r\n @user1 @user2 let's grab lunch!"
        actual = slack.extract_mentions(text)
        self.assertTrue("@user1" in actual)
        self.assertTrue("@user2" in actual)

    def test_duplicate_mentions(self):
        text = "@user1 @user2 @user1 @user2"
        actual = slack.extract_mentions(text)
        self.assertTrue("@user1" in actual)
        self.assertTrue("@user2" in actual)


class TestConvertSlackMentions(unittest.TestCase):
    @patch.dict(
        "fixtures.mention_dic", {"@user1": "slack_user1", "@user2": "slack_user2"}
    )
    def test_convert_slack_mentions_with_mentions(self):
        github_mentions = ["@user1", "@user2"]
        pr_owner = "user3"
        reviewer = "user4"
        expected_output = ["slack_user1", "slack_user2"]

        result = slack.convert_slack_mentions(github_mentions, pr_owner, reviewer)

        self.assertEqual(result, expected_output)

    @patch.dict(
        "fixtures.mention_dic", {"@user1": "slack_user1", "@user2": "slack_user2"}
    )
    def test_convert_slack_mentions_without_mentions(self):
        github_mentions = []
        pr_owner = "user1"
        reviewer = "user2"
        expected_output = ["slack_user1"]

        result = slack.convert_slack_mentions(github_mentions, pr_owner, reviewer)

        self.assertEqual(result, expected_output)

    @patch.dict(
        "fixtures.mention_dic", {"@user1": "slack_user1", "@user2": "slack_user2"}
    )
    def test_convert_slack_mentions_ignore_github_actions(self):
        github_mentions = ["user1"]
        pr_owner = "user2"
        reviewer = "github-actions[bot]"
        expected_output = None

        result = slack.convert_slack_mentions(github_mentions, pr_owner, reviewer)

        self.assertEqual(result, expected_output)

    @patch.dict(
        "fixtures.mention_dic", {"@user1": "slack_user1", "@user2": "slack_user2"}
    )
    def test_convert_slack_mentions_self_mention(self):
        github_mentions = ["@user1"]
        pr_owner = "user1"
        reviewer = "user1"
        expected_output = ["slack_user1"]

        result = slack.convert_slack_mentions(github_mentions, pr_owner, reviewer)

        self.assertEqual(result, expected_output)

    @patch.dict(
        "fixtures.mention_dic", {"@user1": "slack_user1", "@user2": "slack_user2"}
    )
    def test_convert_slack_mentions_ignore_self_mention(self):
        github_mentions = []
        pr_owner = "user1"
        reviewer = "user1"
        expected_output = None

        result = slack.convert_slack_mentions(github_mentions, pr_owner, reviewer)

        self.assertEqual(result, expected_output)

    @patch.dict(
        "fixtures.mention_dic", {"@user1": "slack_user1", "@user2": "slack_user2"}
    )
    def test_convert_slack_mentions_no_mentions(self):
        github_mentions = []
        pr_owner = "user1"
        reviewer = "user2"
        expected_output = ["slack_user1"]

        result = slack.convert_slack_mentions(github_mentions, pr_owner, reviewer)

        self.assertEqual(result, expected_output)


class TestSelectSlackUserName(unittest.TestCase):
    def setUp(self):
        self.mocked_mention_dic = {
            "@user1": "slack_user1",
            "@user2": "slack_user2",
        }

    def test_valid_github_user_name(self):
        # 正常な入力のテストケース
        with patch.dict("fixtures.mention_dic", self.mocked_mention_dic):
            self.assertEqual(slack.select_slack_user_name("user1"), "slack_user1")

    def test_empty_github_user_name(self):
        # 空の入力のテストケース
        with patch.dict("fixtures.mention_dic", self.mocked_mention_dic):
            self.assertEqual(slack.select_slack_user_name(""), None)

    def test_none_github_user_name(self):
        # Noneの入力のテストケース
        with patch.dict("fixtures.mention_dic", self.mocked_mention_dic):
            self.assertEqual(slack.select_slack_user_name(None), None)

    def test_missing_mention_in_dic(self):
        # mention_dicに該当するユーザ名が存在しない場合のテストケース
        with patch.dict("fixtures.mention_dic", self.mocked_mention_dic):
            self.assertEqual(slack.select_slack_user_name("user3"), None)


class TestCreateMentionText(unittest.TestCase):
    def test_empty_slack_mentions(self):
        # 空の入力のテストケース
        slack_mentions = []
        expected_result = ""

        result = slack.create_mention_text(slack_mentions)
        self.assertEqual(result, expected_result)

    def test_single_slack_mention(self):
        # 1つのメンションがある場合のテストケース
        slack_mentions = ["hoge"]
        expected_result = "<@hoge>\n"

        result = slack.create_mention_text(slack_mentions)
        self.assertEqual(result, expected_result)

    def test_multiple_slack_mentions(self):
        # 複数のメンションがある場合のテストケース
        slack_mentions = ["hoge", "fuga", "piyo"]
        expected_result = "<@hoge> <@fuga> <@piyo>\n"

        result = slack.create_mention_text(slack_mentions)
        self.assertEqual(result, expected_result)


class TestCreateSendData(unittest.TestCase):
    def test_all_none(self):
        # 全ての引数がNoneの場合のテストケース
        mentions = None
        reviewer = None
        comment = None
        comment_url = None

        expected_result = json.dumps(
            {
                "channel": "#test",
                "text": "以下のコメントがありました\n```None```\nlink: None",
            }
        ).encode("utf-8")

        result = slack.create_send_data(mentions, reviewer, comment, comment_url)
        self.assertEqual(result, expected_result)

    def test_with_mentions_reviewer_comment_url(self):
        # 引数が全て与えられた場合のテストケース
        mentions = ["user1", "user2"]
        reviewer = "reviewer"
        comment = "This is a comment."
        comment_url = "http://example.com"

        expected_result = json.dumps(
            {
                "channel": "#test",
                "text": "<@user1> <@user2>\n*reviewer* さんから以下のコメントがありました\n```This is a comment.```\nlink: http://example.com",
            }
        ).encode("utf-8")

        result = slack.create_send_data(mentions, reviewer, comment, comment_url)
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
