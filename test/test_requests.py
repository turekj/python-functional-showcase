import unittest
from unittest.mock import patch, MagicMock

import requests

from rx_extensions.requests import rx_request


class TestRequests(unittest.TestCase):
    @patch('requests.request')
    def test_that_subscribing_invokes_request(self, request):
        """
        Test that subscribing to a request invokes requests library
        passing proper arguments.
        """
        r = rx_request('GET', 'URL', first_arg=2, second_arg=3)

        r.subscribe(on_next=lambda n: None)

        request.assert_called_once_with('GET', 'URL', first_arg=2,
                                        second_arg=3)

    @patch('requests.request')
    def test_that_next_value_is_returned_on_no_error(self, request):
        """
        Test that a value from request is returned when no error is
        raised.
        """
        result = None

        def on_next(value):
            nonlocal result
            result = value

        response = requests.Response()
        response.status_code = 200
        request.return_value = response
        r = rx_request('get', 'url')

        r.subscribe(on_next=on_next)

        self.assertEqual(response, result)

    @patch('requests.request')
    def test_that_completed_is_invoked_on_no_error(self, request):
        """
        Test that completed callback is invoked on no error.
        """
        completed = False

        def on_completed():
            nonlocal completed
            completed = True

        response = requests.Response()
        response.status_code = 200
        request.return_value = response
        r = rx_request('get', 'url')

        r.subscribe(on_completed=on_completed)

        self.assertTrue(completed)

    @patch('requests.request')
    def test_that_error_callback_is_not_invoked_on_no_error(self, request):
        """
        Test that error callback is not invoked on no error.
        """
        error = False

        def on_error(_):
            nonlocal error
            error = True

        response = requests.Response()
        response.status_code = 200
        request.return_value = response
        r = rx_request('get', 'url')

        r.subscribe(on_error=on_error)

        self.assertFalse(error)

    @patch('requests.request')
    def test_that_error_callback_is_invoked_on_error(self, request):
        """
        Test that error callback is invoked when error is raised.
        """
        error = None

        def on_error(e):
            nonlocal error
            error = e

        response = MagicMock()
        response.raise_for_status.side_effect = ValueError
        request.return_value = response
        r = rx_request('get', 'url')

        r.subscribe(on_error=on_error)

        self.assertIsInstance(error, ValueError)
