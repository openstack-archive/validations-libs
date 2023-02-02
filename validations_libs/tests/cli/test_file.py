#   Copyright 2023 Red Hat, Inc.
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
from validations_libs import constants
try:
    from unittest import mock
except ImportError:
    import mock

from validations_libs.cli import file
from validations_libs.exceptions import ValidationRunException
from validations_libs.tests import fakes
from validations_libs.tests.cli.fakes import BaseCommand


class TestRun(BaseCommand):

    maxDiff = None

    def setUp(self):
        super(TestRun, self).setUp()
        self.cmd = file.File(self.app, None)

    @mock.patch('yaml.safe_load', return_value=fakes.PARSED_YAML_FILE)
    @mock.patch('validations_libs.utils.load_config', return_value={})
    @mock.patch('builtins.open')
    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'run_validations',
                return_value=copy.deepcopy(fakes.FAKE_SUCCESS_RUN),
                autospec=True)
    def test_file_command_success(self, mock_run, mock_open, mock_config, mock_load):
        expected_args = {
            'validation_name': ['check-rhsm-version'],
            'group': ['prep', 'pre-deployment'],
            'category': [],
            'product': [],
            'exclude_validation': ['fips-enabled'],
            'exclude_group': None,
            'exclude_category': None,
            'exclude_product': None,
            'validation_config': {},
            'limit_hosts': 'undercloud-0,undercloud-1',
            'ssh_user': 'stack',
            'inventory': 'tmp/inventory.yaml',
            'base_dir': '/usr/share/ansible',
            'python_interpreter': '/usr/bin/python',
            'skip_list': {},
            'extra_vars': {'key1': 'val1'},
            'extra_env_vars': {'key1': 'val1', 'key2': 'val2'}}

        args = self._set_args(['foo'])
        verifylist = [('path_to_file', 'foo')]
        parsed_args = self.check_parser(self.cmd, args, verifylist)
        self.cmd.take_action(parsed_args)
        mock_run.assert_called_with(mock.ANY, **expected_args)

    @mock.patch('yaml.safe_load', return_value=fakes.PARSED_YAML_FILE)
    @mock.patch('validations_libs.utils.load_config', return_value={})
    @mock.patch('builtins.open')
    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'run_validations',
                return_value=copy.deepcopy(fakes.FAKE_SUCCESS_RUN),
                autospec=True)
    def test_file_command_success_full(self, mock_run, mock_open, mock_config, mock_load):
        expected_args = {
            'validation_name': ['check-rhsm-version'],
            'group': ['prep', 'pre-deployment'],
            'category': [],
            'product': [],
            'exclude_validation': ['fips-enabled'],
            'exclude_group': None,
            'exclude_category': None,
            'exclude_product': None,
            'validation_config': {},
            'limit_hosts': 'undercloud-0,undercloud-1',
            'ssh_user': 'stack',
            'inventory': 'tmp/inventory.yaml',
            'base_dir': '/usr/share/ansible',
            'python_interpreter': '/usr/bin/python',
            'skip_list': {},
            'extra_vars': {'key1': 'val1'},
            'extra_env_vars': {'key1': 'val1', 'key2': 'val2'}}

        args = self._set_args(['foo',
                               '--junitxml', 'bar'])
        verifylist = [('path_to_file', 'foo'),
                      ('junitxml', 'bar')]

        parsed_args = self.check_parser(self.cmd, args, verifylist)
        self.cmd.take_action(parsed_args)
        mock_run.assert_called_with(mock.ANY, **expected_args)

    @mock.patch('yaml.safe_load', return_value=fakes.PARSED_YAML_FILE)
    @mock.patch('validations_libs.utils.load_config', return_value={})
    @mock.patch('builtins.open')
    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'run_validations',
                return_value=copy.deepcopy(fakes.FAKE_SUCCESS_RUN),
                autospec=True)
    @mock.patch('validations_libs.utils.parse_all_validations_on_disk')
    def test_validations_on_disk_exists(self, mock_validation_dir,
                                        mock_run, mock_open, mock_config, mock_load):
        args = self._set_args(['foo'])
        verifylist = [('path_to_file', 'foo')]

        mock_validation_dir.return_value = [{'id': 'foo',
                                             'description': 'foo',
                                             'groups': ['prep', 'pre-deployment'],
                                             'categories': ['os', 'storage'],
                                             'products': ['product1'],
                                             'name': 'Advanced Format 512e Support',
                                             'path': '/tmp'}]

        parsed_args = self.check_parser(self.cmd, args, verifylist)
        self.cmd.take_action(parsed_args)

    @mock.patch('builtins.open')
    def test_run_validation_cmd_parser_error(self, mock_open):
        args = self._set_args(['something', 'foo'])
        verifylist = [('path_to_file', 'foo')]

        self.assertRaises(Exception, self.check_parser, self.cmd, args, verifylist)

    @mock.patch('yaml.safe_load', return_value=fakes.PARSED_YAML_FILE)
    @mock.patch('validations_libs.utils.load_config', return_value={})
    @mock.patch('builtins.open')
    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'run_validations',
                return_value=copy.deepcopy(fakes.FAKE_FAILED_RUN),
                autospec=True)
    def test_validation_failed_run(self, mock_run, mock_open, mock_config, mock_load):
        args = self._set_args(['foo'])
        verifylist = [('path_to_file', 'foo')]
        parsed_args = self.check_parser(self.cmd, args, verifylist)
        self.assertRaises(ValidationRunException, self.cmd.take_action, parsed_args)

    @mock.patch('yaml.safe_load', return_value=fakes.PARSED_YAML_FILE)
    @mock.patch('validations_libs.utils.load_config', return_value={})
    @mock.patch('builtins.open')
    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'run_validations',
                return_value=copy.deepcopy(fakes.FAKE_FAILED_RUN),
                autospec=True)
    def test_validation_failed_run_junixml(self, mock_run, mock_open, mock_config, mock_load):
        args = self._set_args(['foo',
                               '--junitxml', 'bar'])
        verifylist = [('path_to_file', 'foo'),
                      ('junitxml', 'bar')]
        parsed_args = self.check_parser(self.cmd, args, verifylist)
        self.assertRaises(ValidationRunException, self.cmd.take_action, parsed_args)

    @mock.patch('yaml.safe_load', return_value=fakes.PARSED_YAML_FILE_EXTRA_VARS)
    @mock.patch('validations_libs.utils.load_config', return_value={})
    @mock.patch('builtins.open')
    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'run_validations',
                return_value=copy.deepcopy(fakes.FAKE_SUCCESS_RUN),
                autospec=True)
    def test_extra_vars(self, mock_run, mock_open, mock_config, mock_load):
        args = self._set_args(['foo'])
        verifylist = [('path_to_file', 'foo')]
        expected_args = {
            'validation_name': ['check-rhsm-version'],
            'group': ['prep', 'pre-deployment'],
            'category': [],
            'product': [],
            'exclude_validation': ['fips-enabled'],
            'exclude_group': None,
            'exclude_category': None,
            'exclude_product': None,
            'validation_config': {},
            'limit_hosts': 'undercloud-0,undercloud-1',
            'ssh_user': 'stack',
            'inventory': 'tmp/inventory.yaml',
            'base_dir': '/usr/share/ansible',
            'python_interpreter': '/usr/bin/python',
            'skip_list': {},
            'extra_vars': {'key1': 'val1'},
            'extra_env_vars': {'key1': 'val1', 'key2': 'val2'}}

        parsed_args = self.check_parser(self.cmd, args, verifylist)
        self.cmd.take_action(parsed_args)
        mock_run.assert_called_with(mock.ANY, **expected_args)

    @mock.patch('yaml.safe_load', return_value=fakes.PARSED_YAML_FILE_WRONG_FORMAT)
    @mock.patch('builtins.open')
    def test_file_command_wrong_file_format(self, mock_open, mock_load):
        args = self._set_args(['foo'])
        verifylist = [('path_to_file', 'foo')]
        parsed_args = self.check_parser(self.cmd, args, verifylist)
        self.assertRaises(ValidationRunException, self.cmd.take_action, parsed_args)

    @mock.patch('yaml.safe_load')
    @mock.patch('builtins.open')
    def test_file_command_wrong_file_not_found(self, mock_open, mock_load):
        args = self._set_args(['foo'])
        verifylist = [('path_to_file', 'foo')]
        parsed_args = self.check_parser(self.cmd, args, verifylist)
        self.assertRaises(ValidationRunException, self.cmd.take_action, parsed_args)

    @mock.patch('yaml.safe_load', return_value=fakes.PARSED_YAML_FILE_WRONG_CONFIG)
    @mock.patch('builtins.open')
    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'run_validations',
                return_value=copy.deepcopy(fakes.FAKE_SUCCESS_RUN),
                autospec=True)
    def test_file_command_wrong_config(self, mock_run, mock_open, mock_load):
        args = self._set_args(['foo'])
        verifylist = [('path_to_file', 'foo')]
        expected_args = {
            'validation_name': ['check-rhsm-version'],
            'group': ['prep', 'pre-deployment'],
            'category': [],
            'product': [],
            'exclude_validation': ['fips-enabled'],
            'exclude_group': None,
            'exclude_category': None,
            'exclude_product': None,
            'validation_config': {},
            'limit_hosts': 'undercloud-0,undercloud-1',
            'ssh_user': 'stack',
            'inventory': 'tmp/inventory.yaml',
            'base_dir': '/usr/share/ansible',
            'python_interpreter': '/usr/bin/python',
            'skip_list': {},
            'extra_vars': {'key1': 'val1'},
            'extra_env_vars': {'key1': 'val1', 'key2': 'val2'}}

        parsed_args = self.check_parser(self.cmd, args, verifylist)
        self.cmd.take_action(parsed_args)
        mock_run.assert_called_with(mock.ANY, **expected_args)

    @mock.patch('yaml.safe_load', return_value=fakes.PARSED_YAML_FILE_NO_VALIDATION)
    @mock.patch('builtins.open')
    def test_file_command_no_validation(self, mock_open, mock_load):
        args = self._set_args(['foo'])
        verifylist = [('path_to_file', 'foo')]
        parsed_args = self.check_parser(self.cmd, args, verifylist)
        self.assertRaises(ValidationRunException, self.cmd.take_action, parsed_args)
