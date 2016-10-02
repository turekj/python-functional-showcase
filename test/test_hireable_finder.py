import unittest
from unittest.mock import MagicMock, call

import rx

from logic.hireable import HireableFinder


class TestHireableFinder(unittest.TestCase):
    def setUp(self):
        self.users = {
            'manisero': {
                'id': 123, 'login': 'manisero', 'hireable': None
            },
            'octocat': {
                'id': 567, 'login': 'octocat', 'hireable': True,
            },
            'ninja_coder': {
                'id': 1337, 'login': 'ninja_coder', 'hireable': True,
            },
            'lame_guy': {
                'id': 0, 'login': 'lame_guy', 'hireable': False
            },
            'turekj': {
                'id': 666, 'login': 'turekj', 'hireable': True
            },
        }
        self.repositories = [
            {'id': 1, 'name': 'lame_guy/not-worth-a-penny-software'},
            {'id': 2, 'name': 'overpaid-experts/hello-world-printer'},
            {'id': 3, 'name': 'anonymous/facebook-scanner'},
        ]
        self.contributors = {
            'lame_guy/not-worth-a-penny-software': [
                {'id': 0, 'login': 'lame_guy'},
                {'id': 666, 'login': 'turekj'}
            ],
            'overpaid-experts/hello-world-printer': [
                {'id': 567, 'login': 'octocat'},
                {'id': 123, 'login': 'manisero'},
                {'id': 1337, 'login': 'ninja_coder'}
            ],
            'anonymous/facebook-scanner': [
                {'id': 0, 'login': 'lame_guy'},
                {'id': 1337, 'login': 'ninja_coder'}
            ]
        }

        def get_user(user):
            return rx.Observable.from_([self.users[user]])

        def get_repositories(_):
            return rx.Observable.from_([self.repositories])

        def get_contributors(repo):
            return rx.Observable.from_([self.contributors[repo]])

        self.github_service = MagicMock()
        self.github_service.rx_user_details.side_effect = get_user
        self.github_service.rx_starred_repositories.side_effect = \
            get_repositories
        self.github_service.rx_contributors.side_effect = get_contributors

        self.sut = HireableFinder(self.github_service)

    def test_find_hireable_method(self):
        """
        Test that find_hireable method returns correct results.
        """
        result = None

        def on_next(r):
            nonlocal result
            result = r

        self.sut.rx_find_hireable('turekj').subscribe(on_next=on_next)

        self.assertEqual(['ninja_coder', 'octocat'], result)
        self.github_service.rx_starred_repositories.assert_called_once_with(
            'turekj')
        self.github_service.rx_user_details.assert_has_calls([
            call('lame_guy'), call('octocat'), call('manisero'),
            call('ninja_coder')
        ], any_order=True)
        self.github_service.rx_contributors.assert_has_calls([
            call('lame_guy/not-worth-a-penny-software'),
            call('overpaid-experts/hello-world-printer'),
            call('anonymous/facebook-scanner'),
        ], any_order=True)
