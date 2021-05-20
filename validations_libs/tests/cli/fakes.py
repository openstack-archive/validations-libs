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
import sys

from unittest import TestCase

from validations_libs.cli import app
from validations_libs.cli import base
from validations_libs import utils


try:
    from unittest import mock
except ImportError:
    import mock


class BaseCommand(TestCase):

    def check_parser(self, cmd, args, verify_args):
        try:
            cmd_parser = cmd.get_parser('check_parser')
            parsed_args = cmd_parser.parse_args(args)
        except SystemExit:
            raise Exception("Argument parse failed")
        for av in verify_args:
            attr, value = av
            if attr:
                self.assertIn(attr, parsed_args)
                self.assertEqual(value, getattr(parsed_args, attr))
        return parsed_args

    def setUp(self):
        super(BaseCommand, self).setUp()
        self._set_args([])
        self.app = app.ValidationCliApp()

    def _set_args(self, args):
        sys.argv = sys.argv[:1]
        sys.argv.extend(args)
        return args


KEYVALUEACTION_VALUES = {
    'valid': 'foo=bar',
    'invalid_noeq': 'foo>bar',
    'invalid_multieq': 'foo===bar',
    'invalid_nokey': '=bar',
    'invalid_multikey': 'foo=bar,fizz=buzz'
}
