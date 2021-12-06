# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
test_http_json
----------------------------------

Tests for `http_json` callback plugin.

"""
import re
from oslotest import base
try:
    from unittest import mock
except ImportError:
    import mock
from ansible.plugins.callback import CallbackBase

from validations_libs.callback_plugins import vf_http_json

from validations_libs.tests.callback_plugins import fakes


def is_iso_time(time_string):
    """
    Checks if string represents valid time in ISO format,
    with the default delimiter.
    Regex is somewhat convoluted, but general enough to last
    at least until the 9999 AD.

    Returns:
        True if string matches the pattern.
        False otherwise.
    """
    match = re.match(
        r'\d{4}-[01][0-9]-[0-3][0-9]T[0-3][0-9](:[0-5][0-9]){2}\.\d+Z',
        time_string)

    if match:
        return True
    else:
        return False


class TestHttpJson(base.BaseTestCase):

    def setUp(self):
        super(TestHttpJson, self).setUp()
        self.callback = vf_http_json.CallbackModule()

    def test_callback_instantiation(self):
        """
        Verifying that the CallbackModule is instantiated properly.
        Test checks presence of CallbackBase in the inheritance chain,
        in order to ensure that folowing tests are performed with
        the correct assumptions.
        """

        self.assertEqual(type(self.callback).__mro__[2], CallbackBase)

        """
        Every ansible callback needs to define variable with name and version.
        """
        self.assertIn('CALLBACK_NAME', dir(self.callback))
        self.assertIn('CALLBACK_VERSION', dir(self.callback))
        self.assertIn('CALLBACK_TYPE', dir(self.callback))

        self.assertEqual(self.callback.CALLBACK_NAME, 'http_json')

        self.assertIsInstance(self.callback.CALLBACK_VERSION, float)

        self.assertEqual(self.callback.CALLBACK_TYPE, 'aggregate')

        """
        Additionally, the 'http_json' callback performs several
        other operations during instantiation.
        """

        self.assertEqual(self.callback.env, {})
        self.assertIsNone(self.callback.t0)
        """
        Callback time sanity check only verifies general format
        of the stored time to be  iso format `YYYY-MM-DD HH:MM:SS.mmmmmm`
        with 'T' as a separator.
        For example: '2020-07-03T13:28:21.224103Z'
        """
        self.assertTrue(is_iso_time(self.callback.current_time))

    @mock.patch('validations_libs.callback_plugins.vf_http_json.request.urlopen', autospec=True)
    @mock.patch('validations_libs.callback_plugins.vf_http_json.json.dumps', autospec=True)
    @mock.patch('validations_libs.callback_plugins.vf_http_json.request.Request', autospec=True)
    def test_http_post(self, mock_request, mock_json, mock_url_open):

        vf_http_json.http_post(fakes.HTTP_POST_DATA)
        mock_request.assert_called_once()
        mock_json.assert_called_once_with(fakes.HTTP_POST_DATA)
        mock_url_open.assert_called_once()
