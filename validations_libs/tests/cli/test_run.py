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
import copy
try:
    from unittest import mock
except ImportError:
    import mock

from validations_libs.cli import run
from validations_libs.exceptions import ValidationRunException
from validations_libs.tests import fakes
from validations_libs.tests.cli.fakes import BaseCommand


class TestRun(BaseCommand):

    def setUp(self):
        super(TestRun, self).setUp()
        self.cmd = run.Run(self.app, None)

    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'run_validations',
                return_value=None,
                autospec=True)
    def test_run_command_return_none(self, mock_run):
        args = self._set_args(['--validation', 'foo'])
        verifylist = [('validation_name', ['foo'])]

        parsed_args = self.check_parser(self.cmd, args, verifylist)
        self.assertRaises(ValidationRunException, self.cmd.take_action, parsed_args)

    @mock.patch('validations_libs.cli.common.open')
    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'run_validations',
                return_value=copy.deepcopy(fakes.FAKE_SUCCESS_RUN),
                autospec=True)
    def test_run_command_success(self, mock_run, mock_open):
        args = self._set_args(['--validation', 'foo'])
        verifylist = [('validation_name', ['foo'])]

        parsed_args = self.check_parser(self.cmd, args, verifylist)
        self.cmd.take_action(parsed_args)

    def test_run_command_exclusive_group(self):
        arglist = ['--validation', 'foo', '--group', 'bar']
        self._set_args(arglist)
        verifylist = [('validation_name', ['foo'], 'group', 'bar')]

        self.assertRaises(Exception, self.check_parser, self.cmd,
                          arglist, verifylist)

    @mock.patch('validations_libs.constants.VALIDATIONS_LOG_BASEDIR')
    @mock.patch('validations_libs.cli.common.print_dict')
    @mock.patch('getpass.getuser',
                return_value='doe')
    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'run_validations',
                return_value=copy.deepcopy(fakes.FAKE_SUCCESS_RUN),
                autospec=True)
    @mock.patch('validations_libs.utils.load_config', return_value={})
    def test_run_command_extra_vars(self, mock_config,
                                    mock_run, mock_user,
                                    mock_print, mock_log_dir):
        run_called_args = {
            'inventory': 'localhost',
            'limit_hosts': None,
            'group': [],
            'category': [],
            'product': [],
            'extra_vars': {'key': 'value'},
            'validations_dir': '/usr/share/ansible/validation-playbooks',
            'base_dir': '/usr/share/ansible',
            'validation_name': ['foo'],
            'extra_env_vars': None,
            'python_interpreter': sys.executable,
            'quiet': True,
            'ssh_user': 'doe',
            'validation_config': {},
            'skip_list': None
            }

        arglist = ['--validation', 'foo',
                   '--extra-vars', 'key=value']
        verifylist = [('validation_name', ['foo']),
                      ('extra_vars', {'key': 'value'})]
        self._set_args(arglist)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        call_args = mock_run.mock_calls[0][2]

        self.assertDictEqual(call_args, run_called_args)

    @mock.patch('validations_libs.constants.VALIDATIONS_LOG_BASEDIR')
    @mock.patch('validations_libs.cli.common.print_dict')
    @mock.patch('getpass.getuser',
                return_value='doe')
    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'run_validations',
                return_value=copy.deepcopy(fakes.FAKE_SUCCESS_RUN),
                autospec=True)
    @mock.patch('validations_libs.utils.load_config', return_value={})
    def test_run_command_extra_vars_twice(self, mock_config, mock_run,
                                          mock_user, mock_print,
                                          mock_log_dir):
        run_called_args = {
            'inventory': 'localhost',
            'limit_hosts': None,
            'group': [],
            'category': [],
            'product': [],
            'extra_vars': {'key': 'value2'},
            'validations_dir': '/usr/share/ansible/validation-playbooks',
            'base_dir': '/usr/share/ansible',
            'validation_name': ['foo'],
            'extra_env_vars': None,
            'python_interpreter': sys.executable,
            'quiet': True,
            'ssh_user': 'doe',
            'validation_config': {},
            'skip_list': None
            }

        arglist = ['--validation', 'foo',
                   '--extra-vars', 'key=value1',
                   '--extra-vars', 'key=value2']
        verifylist = [('validation_name', ['foo']),
                      ('extra_vars', {'key': 'value2'})]
        self._set_args(arglist)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        call_args = mock_run.mock_calls[0][2]

        self.assertDictEqual(call_args, run_called_args)

    def test_run_command_exclusive_vars(self):
        arglist = ['--validation', 'foo',
                   '--extra-vars', 'key=value1',
                   '--extra-vars-file', '/foo/vars.yaml']
        verifylist = [('validation_name', ['foo']),
                      ('extra_vars', {'key': 'value2'})]

        self.assertRaises(Exception, self.check_parser, self.cmd,
                          arglist, verifylist)

    @mock.patch('validations_libs.constants.VALIDATIONS_LOG_BASEDIR')
    @mock.patch('yaml.safe_load', return_value={'key': 'value'})
    @mock.patch('builtins.open')
    @mock.patch('getpass.getuser',
                return_value='doe')
    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'run_validations',
                return_value=copy.deepcopy(fakes.FAKE_SUCCESS_RUN),
                autospec=True)
    @mock.patch('validations_libs.utils.load_config', return_value={})
    def test_run_command_extra_vars_file(self, mock_config, mock_run,
                                         mock_user, mock_open,
                                         mock_yaml, mock_log_dir):

        run_called_args = {
            'inventory': 'localhost',
            'limit_hosts': None,
            'group': [],
            'category': [],
            'product': [],
            'extra_vars': {'key': 'value'},
            'validations_dir': '/usr/share/ansible/validation-playbooks',
            'base_dir': '/usr/share/ansible',
            'validation_name': ['foo'],
            'extra_env_vars': None,
            'python_interpreter': sys.executable,
            'quiet': True,
            'ssh_user': 'doe',
            'validation_config': {},
            'skip_list': None
            }

        arglist = ['--validation', 'foo',
                   '--extra-vars-file', '/foo/vars.yaml']
        verifylist = [('validation_name', ['foo']),
                      ('extra_vars_file', '/foo/vars.yaml')]
        self._set_args(arglist)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        call_args = mock_run.mock_calls[0][2]

        self.assertDictEqual(call_args, run_called_args)

    @mock.patch('validations_libs.constants.VALIDATIONS_LOG_BASEDIR')
    @mock.patch('getpass.getuser',
                return_value='doe')
    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'run_validations',
                return_value=copy.deepcopy(fakes.FAKE_SUCCESS_RUN),
                autospec=True)
    @mock.patch('validations_libs.utils.load_config', return_value={})
    def test_run_command_extra_env_vars(self, mock_config, mock_run,
                                        mock_user, mock_log_dir):
        run_called_args = {
            'inventory': 'localhost',
            'limit_hosts': None,
            'group': [],
            'category': [],
            'product': [],
            'extra_vars': None,
            'validations_dir': '/usr/share/ansible/validation-playbooks',
            'base_dir': '/usr/share/ansible',
            'validation_name': ['foo'],
            'extra_env_vars': {'key': 'value'},
            'python_interpreter': sys.executable,
            'quiet': True,
            'ssh_user': 'doe',
            'validation_config': {},
            'skip_list': None
            }

        arglist = ['--validation', 'foo',
                   '--extra-env-vars', 'key=value']
        verifylist = [('validation_name', ['foo']),
                      ('extra_env_vars', {'key': 'value'})]
        self._set_args(arglist)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        call_args = mock_run.mock_calls[0][2]

        self.assertDictEqual(call_args, run_called_args)

    @mock.patch('validations_libs.constants.VALIDATIONS_LOG_BASEDIR')
    @mock.patch('getpass.getuser',
                return_value='doe')
    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'run_validations',
                return_value=copy.deepcopy(fakes.FAKE_SUCCESS_RUN),
                autospec=True)
    @mock.patch('validations_libs.utils.load_config', return_value={})
    def test_run_command_extra_env_vars_with_custom_callback(self,
                                                             mock_config,
                                                             mock_run,
                                                             mock_user,
                                                             mock_log_dir):
        run_called_args = {
            'inventory': 'localhost',
            'limit_hosts': None,
            'quiet': False,
            'group': [],
            'category': [],
            'product': [],
            'extra_vars': None,
            'validations_dir': '/usr/share/ansible/validation-playbooks',
            'base_dir': '/usr/share/ansible',
            'validation_name': ['foo'],
            'extra_env_vars': {'ANSIBLE_STDOUT_CALLBACK': 'default'},
            'python_interpreter': sys.executable,
            'quiet': False,
            'ssh_user': 'doe',
            'validation_config': {},
            'skip_list': None
            }

        arglist = ['--validation', 'foo',
                   '--extra-env-vars', 'ANSIBLE_STDOUT_CALLBACK=default']
        verifylist = [('validation_name', ['foo']),
                      ('extra_env_vars', {'ANSIBLE_STDOUT_CALLBACK': 'default'})]
        self._set_args(arglist)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        call_args = mock_run.mock_calls[0][2]

        self.assertDictEqual(call_args, run_called_args)

    @mock.patch('validations_libs.constants.VALIDATIONS_LOG_BASEDIR')
    @mock.patch('getpass.getuser',
                return_value='doe')
    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'run_validations',
                return_value=copy.deepcopy(fakes.FAKE_SUCCESS_RUN),
                autospec=True)
    @mock.patch('validations_libs.utils.load_config', return_value={})
    def test_run_command_extra_env_vars_twice(self, mock_config,
                                              mock_run, mock_user,
                                              mock_log_dir):
        run_called_args = {
            'inventory': 'localhost',
            'limit_hosts': None,
            'group': [],
            'category': [],
            'product': [],
            'extra_vars': None,
            'validations_dir': '/usr/share/ansible/validation-playbooks',
            'base_dir': '/usr/share/ansible',
            'validation_name': ['foo'],
            'extra_env_vars': {'key': 'value2'},
            'python_interpreter': sys.executable,
            'quiet': True,
            'ssh_user': 'doe',
            'validation_config': {},
            'skip_list': None
            }

        arglist = ['--validation', 'foo',
                   '--extra-env-vars', 'key=value1',
                   '--extra-env-vars', 'key=value2']
        verifylist = [('validation_name', ['foo']),
                      ('extra_env_vars', {'key': 'value2'})]
        self._set_args(arglist)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        call_args = mock_run.mock_calls[0][2]

        self.assertDictEqual(call_args, run_called_args)

    @mock.patch('validations_libs.constants.VALIDATIONS_LOG_BASEDIR')
    @mock.patch('getpass.getuser',
                return_value='doe')
    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'run_validations',
                return_value=copy.deepcopy(fakes.FAKE_SUCCESS_RUN),
                autospec=True)
    @mock.patch('validations_libs.utils.load_config', return_value={})
    def test_run_command_extra_env_vars_and_extra_vars(self,
                                                       mock_config,
                                                       mock_run,
                                                       mock_user,
                                                       mock_log_dir):
        run_called_args = {
            'inventory': 'localhost',
            'limit_hosts': None,
            'group': [],
            'category': [],
            'product': [],
            'extra_vars': {'key': 'value'},
            'validations_dir': '/usr/share/ansible/validation-playbooks',
            'base_dir': '/usr/share/ansible',
            'validation_name': ['foo'],
            'extra_env_vars': {'key2': 'value2'},
            'python_interpreter': sys.executable,
            'quiet': True,
            'ssh_user': 'doe',
            'validation_config': {},
            'skip_list': None
            }

        arglist = ['--validation', 'foo',
                   '--extra-vars', 'key=value',
                   '--extra-env-vars', 'key2=value2']
        verifylist = [('validation_name', ['foo']),
                      ('extra_vars', {'key': 'value'}),
                      ('extra_env_vars', {'key2': 'value2'})]
        self._set_args(arglist)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        call_args = mock_run.mock_calls[0][2]

        self.assertDictEqual(call_args, run_called_args)

    @mock.patch('validations_libs.utils.find_config_file',
                return_value="/etc/validations_foo.cfg")
    @mock.patch('validations_libs.constants.VALIDATIONS_LOG_BASEDIR')
    @mock.patch('getpass.getuser',
                return_value='doe')
    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'run_validations',
                return_value=copy.deepcopy(fakes.FAKE_FAILED_RUN),
                autospec=True)
    @mock.patch('validations_libs.utils.load_config', return_value={})
    def test_run_command_failed_validation(self, mock_config, mock_run, mock_user,
                                           mock_log_dir, mock_config_file):
        run_called_args = {
            'inventory': 'localhost',
            'limit_hosts': None,
            'group': [],
            'category': [],
            'product': [],
            'extra_vars': {'key': 'value'},
            'validations_dir': '/usr/share/ansible/validation-playbooks',
            'base_dir': '/usr/share/ansible',
            'validation_name': ['foo'],
            'extra_env_vars': {'key2': 'value2'},
            'python_interpreter': sys.executable,
            'quiet': True,
            'ssh_user': 'doe',
            'validation_config': {},
            'skip_list': None
            }

        arglist = [
            '--validation', 'foo',
            '--extra-vars', 'key=value',
            '--extra-env-vars', 'key2=value2']
        verifylist = [
            ('validation_name', ['foo']),
            ('extra_vars', {'key': 'value'}),
            ('extra_env_vars', {'key2': 'value2'})]

        self._set_args(arglist)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(ValidationRunException, self.cmd.take_action, parsed_args)
        call_args = mock_run.mock_calls[0][2]

        self.assertDictEqual(call_args, run_called_args)

    @mock.patch('validations_libs.constants.VALIDATIONS_LOG_BASEDIR')
    @mock.patch('getpass.getuser',
                return_value='doe')
    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'run_validations',
                return_value=[],
                autospec=True)
    def test_run_command_no_validation(self, mock_run, mock_user, mock_log_dir):
        run_called_args = {
            'inventory': 'localhost',
            'limit_hosts': None,
            'group': [],
            'category': [],
            'product': [],
            'extra_vars': {'key': 'value'},
            'validations_dir': '/usr/share/ansible/validation-playbooks',
            'base_dir': '/usr/share/ansible',
            'validation_name': ['foo'],
            'extra_env_vars': {'key2': 'value2'},
            'python_interpreter': sys.executable,
            'quiet': True,
            'ssh_user': 'doe',
            'validation_config': {},
            'skip_list': None,
            'log_path': mock_log_dir}

        arglist = [
            '--validation', 'foo',
            '--extra-vars', 'key=value',
            '--extra-env-vars', 'key2=value2']
        verifylist = [
            ('validation_name', ['foo']),
            ('extra_vars', {'key': 'value'}),
            ('extra_env_vars', {'key2': 'value2'})]

        self._set_args(arglist)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(ValidationRunException, self.cmd.take_action, parsed_args)

    @mock.patch('validations_libs.constants.VALIDATIONS_LOG_BASEDIR')
    @mock.patch('getpass.getuser',
                return_value='doe')
    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'run_validations',
                return_value=fakes.FAKE_SUCCESS_RUN)
    def test_run_with_wrong_config(self, mock_run,
                                   mock_user, mock_log_dir):
        arglist = ['--validation', 'foo', '--config', 'wrong.cfg']
        verifylist = [('validation_name', ['foo']),
                      ('config', 'wrong.cfg')]

        run_called_args = {
            'inventory': 'localhost',
            'limit_hosts': None,
            'group': [],
            'category': [],
            'product': [],
            'extra_vars': None,
            'validations_dir': '/usr/share/ansible/validation-playbooks',
            'base_dir': '/usr/share/ansible',
            'validation_name': ['foo'],
            'extra_env_vars': None,
            'python_interpreter': sys.executable,
            'quiet': True,
            'ssh_user': 'doe',
            'validation_config': {},
            'skip_list': None
            }

        self._set_args(arglist)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        mock_run.assert_called_with(**run_called_args)

    @mock.patch('validations_libs.constants.VALIDATIONS_LOG_BASEDIR')
    @mock.patch('getpass.getuser',
                return_value='doe')
    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'run_validations',
                return_value=fakes.FAKE_SUCCESS_RUN)
    @mock.patch('os.path.exists', return_value=True)
    def test_run_with_config(self, mock_exists,
                             mock_run, mock_user,
                             mock_log_dir):
        arglist = ['--validation', 'foo', '--config', 'config.cfg']
        verifylist = [('validation_name', ['foo']),
                      ('config', 'config.cfg')]

        run_called_args = {
            'inventory': 'localhost',
            'limit_hosts': None,
            'group': [],
            'category': [],
            'product': [],
            'extra_vars': None,
            'validations_dir': '/usr/share/ansible/validation-playbooks',
            'base_dir': '/usr/share/ansible',
            'validation_name': ['foo'],
            'extra_env_vars': None,
            'python_interpreter': sys.executable,
            'quiet': True,
            'ssh_user': 'doe',
            'validation_config': {},
            'skip_list': None
            }

        self._set_args(arglist)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        mock_run.assert_called_with(**run_called_args)

    @mock.patch('validations_libs.constants.VALIDATIONS_LOG_BASEDIR')
    @mock.patch('yaml.safe_load', return_value={'key': 'value'})
    @mock.patch('builtins.open')
    @mock.patch('getpass.getuser',
                return_value='doe')
    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'run_validations',
                return_value=copy.deepcopy(fakes.FAKE_SUCCESS_RUN))
    @mock.patch('validations_libs.utils.load_config', return_value={})
    def test_run_command_with_skip_list(self, mock_config, mock_run,
                                        mock_user, mock_open,
                                        mock_yaml, mock_log_dir):

        run_called_args = {
            'inventory': 'localhost',
            'limit_hosts': None,
            'group': [],
            'category': [],
            'product': [],
            'extra_vars': None,
            'validations_dir': '/usr/share/ansible/validation-playbooks',
            'base_dir': '/usr/share/ansible',
            'validation_name': ['foo'],
            'extra_env_vars': None,
            'python_interpreter': sys.executable,
            'quiet': True,
            'ssh_user': 'doe',
            'validation_config': {},
            'skip_list': {'key': 'value'}
            }

        arglist = ['--validation', 'foo',
                   '--skiplist', '/foo/skip.yaml']
        verifylist = [('validation_name', ['foo']),
                      ('skip_list', '/foo/skip.yaml')]
        self._set_args(arglist)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        mock_run.assert_called_with(**run_called_args)

    @mock.patch('validations_libs.constants.VALIDATIONS_LOG_BASEDIR')
    @mock.patch('yaml.safe_load', return_value=[{'key': 'value'}])
    @mock.patch('builtins.open')
    @mock.patch('getpass.getuser',
                return_value='doe')
    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'run_validations',
                return_value=copy.deepcopy(fakes.FAKE_SUCCESS_RUN))
    @mock.patch('validations_libs.utils.load_config', return_value={})
    def test_run_command_with_skip_list_bad_format(self, mock_config, mock_run,
                                                   mock_user, mock_open,
                                                   mock_yaml, mock_log_dir):

        arglist = ['--validation', 'foo',
                   '--skiplist', '/foo/skip.yaml']
        verifylist = [('validation_name', ['foo']),
                      ('skip_list', '/foo/skip.yaml')]
        self._set_args(arglist)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(ValidationRunException, self.cmd.take_action, parsed_args)
