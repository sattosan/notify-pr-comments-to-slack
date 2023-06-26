import json
import unittest
from io import BytesIO
from unittest.mock import patch

from src import settings


class TestGetSecret(unittest.TestCase):
    @patch('urllib.request.urlopen')
    def test_get_secret_with_secret_string(self, mock_urlopen):
        secret_string = '{"username": "admin", "password": "123456"}'
        expected_result = {"username": "admin", "password": "123456"}
        mock_urlopen.return_value = BytesIO(json.dumps({"SecretString": secret_string}).encode())

        with patch.dict("os.environ", {"AWS_SESSION_TOKEN": "test_token"}):
            result = settings.get_secret()

        self.assertEqual(result, expected_result)

    @patch('urllib.request.urlopen')
    def test_get_secret_without_secret_string(self, mock_urlopen):
        mock_urlopen.return_value = BytesIO(json.dumps({}).encode())

        with patch.dict("os.environ", {}):
            result = settings.get_secret()

        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
