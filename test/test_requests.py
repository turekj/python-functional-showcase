import unittest
from unittest.mock import patch, MagicMock

import requests
import rx

from rx_extensions.requests import rx_request, rx_json_request


class TestRxRequest(unittest.TestCase):
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


class TestRxJSONRequest(unittest.TestCase):
    @patch('rx_extensions.requests.rx_request')
    def test_that_json_request_should_pass_params_to_request(self, request):
        """
        Test that rx_json_request should pass all params to request.
        """
        r = rx_json_request('POST', 'http://google.com', p='v')

        r.subscribe(on_next=lambda _: None)

        request.assert_called_once_with('POST', 'http://google.com', p='v')

    @patch('rx_extensions.requests.rx_request')
    def test_that_method_should_return_json_on_success(self, request):
        """
        Test that rx_json_request should return parsed JSON if
        request was successful.
        """
        result = None

        def on_next(v):
            nonlocal result
            result = v

        value = MagicMock()
        value.json.return_value = {'json': 'dict'}
        observable = rx.Observable.from_([value])
        request.return_value = observable
        r = rx_json_request('GET', 'http://google.com')

        r.subscribe(on_next=on_next)

        self.assertEqual({'json': 'dict'}, result)

    @patch('rx_extensions.requests.rx_request')
    def test_that_method_should_not_call_on_error_if_success(self, request):
        """
        Test that rx_json_request should not call on_error callback
        if JSON parsing is successful.
        """
        error = False

        def on_error(_):
            nonlocal error
            error = True

        value = MagicMock()
        observable = rx.Observable.from_([value])
        request.return_value = observable
        r = rx_json_request('POST', 'http://google.com', p='v')

        r.subscribe(on_error=on_error)

        self.assertFalse(error)

    @patch('rx_extensions.requests.rx_request')
    def test_that_method_should_call_on_error_if_failure(self, request):
        """
        Test that rx_json_request should call on_error callback if
        JSON parsing fails.
        """
        error = None

        def on_error(e):
            nonlocal error
            error = e

        value = MagicMock()
        value.json.side_effect = ValueError
        observable = rx.Observable.from_([value])
        request.return_value = observable
        r = rx_json_request('POST', 'http://google.com', p='v')

        r.subscribe(on_error=on_error)

        self.assertIsInstance(error, ValueError)
