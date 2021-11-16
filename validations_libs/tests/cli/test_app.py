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

try:
    from unittest import mock
except ImportError:
    import mock
from unittest import TestCase

from validations_libs.cli import app
from validations_libs.cli import lister
from validations_libs.cli import history


class TestArgApp(TestCase):

    def setUp(self):
        super(TestArgApp, self).setUp()
        self._set_args([])
        self.app = app.ValidationCliApp()

    def _set_args(self, args):
        sys.argv = sys.argv[:1]
        sys.argv.extend(args)
        return args

    def test_validation_dir_config_cli(self):
        args = ['--validation-dir', 'foo']
        self._set_args(args)
        cmd = lister.ValidationList(self.app, None)
        parser = cmd.get_parser('fake')
        parsed_args = parser.parse_args(args)
        self.assertEqual('foo', parsed_args.validation_dir)

    @mock.patch('validations_libs.utils.find_config_file',
                return_value='validation.cfg')
    def test_validation_dir_config_no_cli(self, mock_config):
        args = []
        self._set_args(args)
        cmd = lister.ValidationList(self.app, None)
        parser = cmd.get_parser('fake')
        parsed_args = parser.parse_args(args)
        self.assertEqual('/usr/share/ansible/validation-playbooks',
                         parsed_args.validation_dir)

    @mock.patch('validations_libs.constants.ANSIBLE_VALIDATION_DIR', 'bar')
    @mock.patch('validations_libs.utils.find_config_file',
                return_value='/etc/validation.cfg')
    def test_validation_dir_config_no_cli_no_config(self, mock_config):
        args = []
        self._set_args(args)
        cmd = lister.ValidationList(self.app, None)
        parser = cmd.get_parser('fake')
        parsed_args = parser.parse_args(args)
        self.assertEqual('bar', parsed_args.validation_dir)

    @mock.patch('validations_libs.constants.ANSIBLE_VALIDATION_DIR',
                '/usr/share/ansible/validation-playbooks')
    @mock.patch('validations_libs.utils.find_config_file',
                return_value='validation.cfg')
    def test_validation_dir_config_no_cli_same_consts(self, mock_config):
        args = []
        self._set_args(args)
        cmd = lister.ValidationList(self.app, None)
        parser = cmd.get_parser('fake')
        parsed_args = parser.parse_args(args)
        self.assertEqual('/usr/share/ansible/validation-playbooks',
                         parsed_args.validation_dir)

    def test_get_history_cli_arg(self):
        args = ['123', '--validation-log-dir', '/foo/log/dir']
        self._set_args(args)
        cmd = history.GetHistory(self.app, None)
        parser = cmd.get_parser('fake')
        parsed_args = parser.parse_args(args)
        self.assertEqual('/foo/log/dir',
                         parsed_args.validation_log_dir)

    @mock.patch('validations_libs.utils.find_config_file',
                return_value='validation.cfg')
    def test_get_history_cli_arg_and_config_file(self, mock_config):
        args = ['123', '--validation-log-dir', '/foo/log/dir']
        self._set_args(args)
        cmd = history.GetHistory(self.app, None)
        parser = cmd.get_parser('fake')
        parsed_args = parser.parse_args(args)
        self.assertEqual('/foo/log/dir',
                         parsed_args.validation_log_dir)

    @mock.patch('validations_libs.constants.VALIDATIONS_LOG_BASEDIR',
                '/home/foo/validations')
    @mock.patch('validations_libs.utils.find_config_file',
                return_value='validation.cfg')
    def test_get_history_no_cli_arg_and_config_file(self, mock_config):
        args = ['123']
        self._set_args(args)
        cmd = history.GetHistory(self.app, None)
        parser = cmd.get_parser('fake')
        parsed_args = parser.parse_args(args)
        self.assertEqual('/home/foo/validations',
                         parsed_args.validation_log_dir)
