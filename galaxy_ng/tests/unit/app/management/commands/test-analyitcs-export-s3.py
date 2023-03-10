from unittest.mock import patch, mock_open, ANY
from io import StringIO
from django.core.management import call_command, CommandError
from django.test import TestCase
import os

s3_details = {
    "aws_access_key_id": "blah",
    "aws_secret_access_key": "blah",
    "aws_region": "blah",
    "aws_bucket": "blah"
}


class TestAnalyticsExportS3Command(TestCase):
    def setUp(self):
        super().setUp()

    def test_command_output(self):
        call_command('analytics-export-s3')

    @patch("builtins.open", new_callable=mock_open, read_data="data")
    @patch('boto3.client')
    @patch.dict(os.environ, s3_details, clear=True) 
    def test_write_file_to_s3_success(self, getenv, boto3, mock_file):
        out = StringIO()

        assert os.getenv("aws_access_key_id") == "blah"
        assert os.getenv("aws_secret_access_key") == "blah"
        assert os.getenv("aws_region") == "blah"
        assert os.getenv("aws_bucket") == "blah"

        self.assertTrue(mock.called)
        mock_file.assert_called_with(ANY)
        self.assertIn("Completed successfully")

    @patch("builtins.open", new_callable=mock_open, read_data="data")
    @patch('boto3.client')
    @patch.dict(os.environ, s3_details, clear=True) 
    def test_write_file_to_s3_failure(self, mock_file):
        out = StringIO()
        call_command('delete-user', '--user', 'system:bar', stdout=out)
        self.assertIn("User not found", out.getvalue())
