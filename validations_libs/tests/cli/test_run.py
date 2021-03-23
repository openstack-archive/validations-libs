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

from validations_libs.cli import run
from validations_libs.tests import fakes
from validations_libs.tests.cli.fakes import BaseCommand


class TestRun(BaseCommand):

    def setUp(self):
        super(TestRun, self).setUp()
        self.cmd = run.Run(self.app, None)

    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'run_validations',
                return_value=None)
    def test_run_command_return_none(self, mock_run):
        arglist = ['--validation', 'foo']
        verifylist = [('validation_name', ['foo'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.assertEqual(result, None)

    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'run_validations',
                return_value=fakes.FAKE_SUCCESS_RUN)
    def test_run_command_success(self, mock_run):
        arglist = ['--validation', 'foo']
        verifylist = [('validation_name', ['foo'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

    def test_run_command_exclusive_group(self):
        arglist = ['--validation', 'foo', '--group', 'bar']
        verifylist = [('validation_name', ['foo'], 'group', 'bar')]

        self.assertRaises(Exception, self.check_parser, self.cmd,
                          arglist, verifylist)

    @mock.patch('validations_libs.cli.common.print_dict')
    @mock.patch('getpass.getuser',
                return_value='doe')
    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'run_validations',
                return_value=fakes.FAKE_SUCCESS_RUN)
    def test_run_command_extra_vars(self, mock_run, mock_user, mock_print):
        run_called_args = {
            'inventory': 'localhost',
            'limit_hosts': None,
            'group': [],
            'extra_vars': {'key': 'value'},
            'validations_dir': '/usr/share/ansible/validation-playbooks',
            'base_dir': '/usr/share/ansible/',
            'validation_name': ['foo'],
            'extra_env_vars': None,
            'quiet': True,
            'ssh_user': 'doe'}

        arglist = ['--validation', 'foo',
                   '--extra-vars', 'key=value']
        verifylist = [('validation_name', ['foo']),
                      ('extra_vars', {'key': 'value'})]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        mock_run.assert_called_with(**run_called_args)

    @mock.patch('validations_libs.cli.common.print_dict')
    @mock.patch('getpass.getuser',
                return_value='doe')
    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'run_validations',
                return_value=fakes.FAKE_SUCCESS_RUN)
    def test_run_command_extra_vars_twice(self, mock_run, mock_user,
                                          mock_print):
        run_called_args = {
            'inventory': 'localhost',
            'limit_hosts': None,
            'group': [],
            'extra_vars': {'key': 'value2'},
            'validations_dir': '/usr/share/ansible/validation-playbooks',
            'base_dir': '/usr/share/ansible/',
            'validation_name': ['foo'],
            'extra_env_vars': None,
            'quiet': True,
            'ssh_user': 'doe'}

        arglist = ['--validation', 'foo',
                   '--extra-vars', 'key=value1',
                   '--extra-vars', 'key=value2']
        verifylist = [('validation_name', ['foo']),
                      ('extra_vars', {'key': 'value2'})]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        mock_run.assert_called_with(**run_called_args)

    def test_run_command_exclusive_vars(self):
        arglist = ['--validation', 'foo',
                   '--extra-vars', 'key=value1',
                   '--extra-vars-file', '/foo/vars.yaml']
        verifylist = [('validation_name', ['foo']),
                      ('extra_vars', {'key': 'value2'})]

        self.assertRaises(Exception, self.check_parser, self.cmd,
                          arglist, verifylist)

    @mock.patch('yaml.safe_load', return_value={'key': 'value'})
    @mock.patch('six.moves.builtins.open')
    @mock.patch('getpass.getuser',
                return_value='doe')
    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'run_validations',
                return_value=fakes.FAKE_SUCCESS_RUN)
    def test_run_command_extra_vars_file(self, mock_run, mock_user, mock_open,
                                         mock_yaml):
        run_called_args = {
            'inventory': 'localhost',
            'limit_hosts': None,
            'group': [],
            'extra_vars': {'key': 'value'},
            'validations_dir': '/usr/share/ansible/validation-playbooks',
            'base_dir': '/usr/share/ansible/',
            'validation_name': ['foo'],
            'extra_env_vars': None,
            'quiet': True,
            'ssh_user': 'doe'}

        arglist = ['--validation', 'foo',
                   '--extra-vars-file', '/foo/vars.yaml']
        verifylist = [('validation_name', ['foo']),
                      ('extra_vars_file', '/foo/vars.yaml')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        mock_run.assert_called_with(**run_called_args)

    @mock.patch('getpass.getuser',
                return_value='doe')
    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'run_validations',
                return_value=fakes.FAKE_SUCCESS_RUN)
    def test_run_command_extra_env_vars(self, mock_run, mock_user):
        run_called_args = {
            'inventory': 'localhost',
            'limit_hosts': None,
            'group': [],
            'extra_vars': None,
            'validations_dir': '/usr/share/ansible/validation-playbooks',
            'base_dir': '/usr/share/ansible/',
            'validation_name': ['foo'],
            'extra_env_vars': {'key': 'value'},
            'quiet': True,
            'ssh_user': 'doe'}

        arglist = ['--validation', 'foo',
                   '--extra-env-vars', 'key=value']
        verifylist = [('validation_name', ['foo']),
                      ('extra_env_vars', {'key': 'value'})]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        mock_run.assert_called_with(**run_called_args)

    @mock.patch('getpass.getuser',
                return_value='doe')
    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'run_validations',
                return_value=fakes.FAKE_SUCCESS_RUN)
    def test_run_command_extra_env_vars_twice(self, mock_run, mock_user):
        run_called_args = {
            'inventory': 'localhost',
            'limit_hosts': None,
            'group': [],
            'extra_vars': None,
            'validations_dir': '/usr/share/ansible/validation-playbooks',
            'base_dir': '/usr/share/ansible/',
            'validation_name': ['foo'],
            'extra_env_vars': {'key': 'value2'},
            'quiet': True,
            'ssh_user': 'doe'}

        arglist = ['--validation', 'foo',
                   '--extra-env-vars', 'key=value1',
                   '--extra-env-vars', 'key=value2']
        verifylist = [('validation_name', ['foo']),
                      ('extra_env_vars', {'key': 'value2'})]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        mock_run.assert_called_with(**run_called_args)

    @mock.patch('getpass.getuser',
                return_value='doe')
    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'run_validations',
                return_value=fakes.FAKE_SUCCESS_RUN)
    def test_run_command_extra_env_vars_and_extra_vars(self, mock_run,
                                                       mock_user):
        run_called_args = {
            'inventory': 'localhost',
            'limit_hosts': None,
            'group': [],
            'extra_vars': {'key': 'value'},
            'validations_dir': '/usr/share/ansible/validation-playbooks',
            'base_dir': '/usr/share/ansible/',
            'validation_name': ['foo'],
            'extra_env_vars': {'key2': 'value2'},
            'quiet': True,
            'ssh_user': 'doe'}

        arglist = ['--validation', 'foo',
                   '--extra-vars', 'key=value',
                   '--extra-env-vars', 'key2=value2']
        verifylist = [('validation_name', ['foo']),
                      ('extra_vars', {'key': 'value'}),
                      ('extra_env_vars', {'key2': 'value2'})]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        mock_run.assert_called_with(**run_called_args)

    def test_run_command_exclusive_wrong_extra_vars(self):
        arglist = ['--validation', 'foo',
                   '--extra-vars', 'key=value1,key=value2']
        verifylist = [('validation_name', ['foo']),
                      ('extra_vars', {'key': 'value2'})]

        self.assertRaises(Exception, self.check_parser, self.cmd,
                          arglist, verifylist)

    @mock.patch('getpass.getuser',
                return_value='doe')
    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'run_validations',
                return_value=fakes.FAKE_FAILED_RUN)
    def test_run_command_failed_validation(self, mock_run, mock_user):
        run_called_args = {
            'inventory': 'localhost',
            'limit_hosts': None,
            'group': [],
            'extra_vars': {'key': 'value'},
            'validations_dir': '/usr/share/ansible/validation-playbooks',
            'base_dir': '/usr/share/ansible/',
            'validation_name': ['foo'],
            'extra_env_vars': {'key2': 'value2'},
            'quiet': True,
            'ssh_user': 'doe'}

        arglist = ['--validation', 'foo']
        verifylist = [('validation_name', ['foo'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(RuntimeError, self.cmd.take_action, parsed_args)
