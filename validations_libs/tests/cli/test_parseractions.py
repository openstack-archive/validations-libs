#   Copyright 2021 Red Hat, Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#
try:
    from unittest import mock
except ImportError:
    import mock

from unittest import TestCase
from validations_libs.cli import parseractions

import argparse
from validations_libs.tests.cli.fakes import KEYVALUEACTION_VALUES


class TestParserActions(TestCase):

    def setUp(self):
        self.action = parseractions.KeyValueAction("", "fizz")
        self.mock_parser = mock.MagicMock()
        self.test_values = KEYVALUEACTION_VALUES

        self.mock_namespace = mock.MagicMock()
        self.mock_namespace.fizz = None

        super(TestParserActions, self).setUp()

    def test_keyvalueaction_valid(self):

        self.action(
            self.mock_parser,
            self.mock_namespace,
            self.test_values['valid'])

        self.assertIn('fizz', dir(self.mock_namespace))
        self.assertDictEqual({'foo': 'bar'}, self.mock_namespace.fizz)
        self.tearDown()

    def test_keyvalueaction_invalid_no_eq_sign(self):

        self.assertRaises(
            argparse.ArgumentTypeError,
            self.action,
            self.mock_parser,
            self.mock_namespace,
            self.test_values['invalid_noeq']
        )

        self.assertIn('fizz', dir(self.mock_namespace))
        self.assertDictEqual({}, self.mock_namespace.fizz)
        self.tearDown()

    def test_keyvalueaction_invalid_invalid_multieq(self):

        self.assertRaises(
            argparse.ArgumentTypeError,
            self.action,
            self.mock_parser,
            self.mock_namespace,
            self.test_values['invalid_multieq']
        )

        self.assertIn('fizz', dir(self.mock_namespace))
        self.assertDictEqual({}, self.mock_namespace.fizz)
        self.tearDown()

    def test_keyvalueaction_invalid_invalid_nokey(self):

        self.assertRaises(
            argparse.ArgumentTypeError,
            self.action,
            self.mock_parser,
            self.mock_namespace,
            self.test_values['invalid_nokey']
        )

        self.assertIn('fizz', dir(self.mock_namespace))
        self.assertDictEqual({}, self.mock_namespace.fizz)
        self.tearDown()

    def test_keyvalueaction_invalid_invalid_multikey(self):

        self.assertRaises(
            argparse.ArgumentTypeError,
            self.action,
            self.mock_parser,
            self.mock_namespace,
            self.test_values['invalid_multikey']
        )

        self.assertIn('fizz', dir(self.mock_namespace))
        self.assertDictEqual({}, self.mock_namespace.fizz)
        self.tearDown()
