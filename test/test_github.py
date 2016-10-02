import unittest
from unittest.mock import patch

from service.github import GithubService


class TestGithub(unittest.TestCase):
    def setUp(self):
        self.sut = GithubService()

    @patch('service.github.rx_get_json')
    def test_user_details(self, rx_get_json):
        """
        Test that rx_user_details issues correct request.
        """
        rx_get_json.return_value = {'login': 'octocat'}

        result = self.sut.rx_user_details('octocat')

        self.assertEqual({'login': 'octocat'}, result)
        rx_get_json.assert_called_once_with(
            'https://api.github.com/users/octocat')

    @patch('service.github.rx_get_json')
    def test_starred_repositories(self, rx_get_json):
        """
        Test that rx_user_details issues correct request.
        """
        rx_get_json.return_value = [{'id': 123}]

        result = self.sut.rx_starred_repositories('octocat')

        self.assertEqual([{'id': 123}], result)
        rx_get_json.assert_called_once_with(
            'https://api.github.com/users/octocat/starred')
