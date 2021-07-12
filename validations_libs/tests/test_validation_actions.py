#   Copyright 2020 Red Hat, Inc.
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

import json

from unittest import TestCase

from validations_libs.tests import fakes
from validations_libs.validation_actions import ValidationActions


class TestValidationActions(TestCase):

    def setUp(self):
        super(TestValidationActions, self).setUp()
        self.column_name = ('ID', 'Name', 'Groups', 'Categories', 'Products')

    @mock.patch('validations_libs.utils.parse_all_validations_on_disk',
                return_value=fakes.VALIDATIONS_LIST)
    def test_validation_list(self, mock_validation_dir):
        validations_list = ValidationActions('/tmp/foo')

        self.assertEqual(validations_list.list_validations(),
                         (self.column_name, [('my_val1',
                                              'My Validation One Name',
                                              ['prep', 'pre-deployment'],
                                              ['os', 'system', 'ram'],
                                              ['product1']),
                                             ('my_val2',
                                              'My Validation Two Name',
                                              ['prep', 'pre-introspection'],
                                              ['networking'],
                                              ['product1'])]))

    @mock.patch('validations_libs.utils.os.access', return_value=True)
    @mock.patch('validations_libs.utils.os.path.exists', return_value=True)
    @mock.patch('validations_libs.utils.get_validations_playbook',
                return_value=['/tmp/foo/fake.yaml'])
    def test_validation_skip_validation(self, mock_validation_play, mock_exists, mock_access):

        playbook = ['fake.yaml']
        inventory = 'tmp/inventory.yaml'
        skip_list = {'fake': {'hosts': 'ALL',
                              'reason': None,
                              'lp': None
                             }
                    }

        run = ValidationActions()
        run_return = run.run_validations(playbook, inventory,
                                         validations_dir='/tmp/foo',
                                         skip_list=skip_list,
                                         limit_hosts=None)
        self.assertEqual(run_return, [])

    @mock.patch('validations_libs.utils.current_time',
                return_value='time')
    @mock.patch('validations_libs.utils.uuid.uuid4',
                return_value='123')
    @mock.patch('validations_libs.utils.os.makedirs')
    @mock.patch('validations_libs.utils.os.access',
                return_value=True)
    @mock.patch('validations_libs.utils.os.path.exists',
                return_value=True)
    @mock.patch('validations_libs.utils.get_validations_playbook',
                return_value=['/tmp/foo/fake.yaml'])
    @mock.patch('validations_libs.ansible.Ansible.run')
    def test_validation_skip_on_specific_host(self, mock_ansible_run,
                                              mock_validation_play,
                                              mock_exists,
                                              mock_access,
                                              mock_makedirs,
                                              mock_uuid,
                                              mock_time):

        mock_ansible_run.return_value = ('fake.yaml', 0, 'successful')
        run_called_args = {
            'workdir': '/var/log/validations/artifacts/123_fake.yaml_time',
            'playbook': '/tmp/foo/fake.yaml',
            'base_dir': '/usr/share/ansible',
            'playbook_dir': '/tmp/foo',
            'parallel_run': True,
            'inventory': 'tmp/inventory.yaml',
            'output_callback': 'validation_stdout',
            'callback_whitelist': None,
            'quiet': True,
            'extra_vars': None,
            'limit_hosts': '!cloud1',
            'extra_env_variables': None,
            'ansible_cfg': None,
            'gathering_policy': 'explicit',
            'ansible_artifact_path': '/var/log/validations/artifacts/123_fake.yaml_time',
            'log_path': '/var/log/validations',
            'run_async': False,
            'python_interpreter': None,
            'ssh_user': None
        }

        playbook = ['fake.yaml']
        inventory = 'tmp/inventory.yaml'
        skip_list = {'fake': {'hosts': 'cloud1',
                              'reason': None,
                              'lp': None
                             }
                    }

        run = ValidationActions()
        run_return = run.run_validations(playbook, inventory,
                                         log_path='/var/log/validations',
                                         validations_dir='/tmp/foo',
                                         skip_list=skip_list,
                                         limit_hosts='!cloud1')

        mock_ansible_run.assert_called_with(**run_called_args)

    @mock.patch('validations_libs.utils.current_time',
                return_value='time')
    @mock.patch('validations_libs.utils.uuid.uuid4',
                return_value='123')
    @mock.patch('validations_libs.utils.os.makedirs')
    @mock.patch('validations_libs.utils.os.access',
                return_value=True)
    @mock.patch('validations_libs.utils.os.path.exists',
                return_value=True)
    @mock.patch('validations_libs.utils.get_validations_playbook',
                return_value=['/tmp/foo/fake.yaml'])
    @mock.patch('validations_libs.ansible.Ansible.run')
    def test_validation_skip_with_limit_host(self, mock_ansible_run,
                                             mock_validation_play,
                                             mock_exists,
                                             mock_access,
                                             mock_makedirs,
                                             mock_uuid,
                                             mock_time):

        mock_ansible_run.return_value = ('fake.yaml', 0, 'successful')
        run_called_args = {
            'workdir': '/var/log/validations/artifacts/123_fake.yaml_time',
            'playbook': '/tmp/foo/fake.yaml',
            'base_dir': '/usr/share/ansible',
            'playbook_dir': '/tmp/foo',
            'parallel_run': True,
            'inventory': 'tmp/inventory.yaml',
            'output_callback': 'validation_stdout',
            'callback_whitelist': None,
            'quiet': True,
            'extra_vars': None,
            'limit_hosts': '!cloud1,cloud,!cloud2',
            'extra_env_variables': None,
            'ansible_cfg': None,
            'gathering_policy': 'explicit',
            'ansible_artifact_path': '/var/log/validations/artifacts/123_fake.yaml_time',
            'log_path': '/var/log/validations',
            'run_async': False,
            'python_interpreter': None,
            'ssh_user': None
        }

        playbook = ['fake.yaml']
        inventory = 'tmp/inventory.yaml'
        skip_list = {'fake': {'hosts': 'cloud1',
                              'reason': None,
                              'lp': None
                             }
                    }

        run = ValidationActions()
        run_return = run.run_validations(playbook, inventory,
                                         log_path='/var/log/validations',
                                         validations_dir='/tmp/foo',
                                         skip_list=skip_list,
                                         limit_hosts='cloud,cloud1,!cloud2')

        mock_ansible_run.assert_called_with(**run_called_args)

    @mock.patch('validations_libs.utils.os.makedirs')
    @mock.patch('validations_libs.utils.os.access', return_value=True)
    @mock.patch('validations_libs.utils.os.path.exists', return_value=True)
    @mock.patch('validations_libs.validation_actions.ValidationLogs.get_results',
                side_effect=fakes.FAKE_SUCCESS_RUN)
    @mock.patch('validations_libs.utils.parse_all_validations_on_disk')
    @mock.patch('validations_libs.ansible.Ansible.run')
    def test_validation_run_success(self, mock_ansible_run,
                                    mock_validation_dir,
                                    mock_results, mock_exists, mock_access,
                                    mock_makedirs):

        mock_validation_dir.return_value = [{
            'description': 'My Validation One Description',
            'groups': ['prep', 'pre-deployment'],
            'id': 'foo',
            'name': 'My Validition One Name',
            'parameters': {}}]

        mock_ansible_run.return_value = ('foo.yaml', 0, 'successful')

        expected_run_return = fakes.FAKE_SUCCESS_RUN[0]

        playbook = ['fake.yaml']
        inventory = 'tmp/inventory.yaml'

        run = ValidationActions()
        run_return = run.run_validations(playbook, inventory,
                                         group=fakes.GROUPS_LIST,
                                         validations_dir='/tmp/foo')
        self.assertEqual(run_return, expected_run_return)

    @mock.patch('validations_libs.utils.get_validations_playbook')
    def test_validation_run_wrong_validation_name(self, mock_validation_play):
        mock_validation_play.return_value = []

        run = ValidationActions()
        self.assertRaises(RuntimeError, run.run_validations,
                          validation_name='fake.yaml',
                          validations_dir='/tmp/foo'
                          )

    @mock.patch('validations_libs.utils.os.makedirs')
    @mock.patch('validations_libs.utils.os.access', return_value=True)
    @mock.patch('validations_libs.utils.os.path.exists', return_value=True)
    @mock.patch('validations_libs.validation_logs.ValidationLogs.get_results')
    @mock.patch('validations_libs.utils.parse_all_validations_on_disk')
    @mock.patch('validations_libs.ansible.Ansible.run')
    def test_validation_run_failed(self, mock_ansible_run,
                                   mock_validation_dir, mock_results,
                                   mock_exists, mock_access,
                                   mock_makedirs):

        mock_validation_dir.return_value = [{
            'description': 'My Validation One Description',
            'groups': ['prep', 'pre-deployment'],
            'id': 'foo',
            'name': 'My Validition One Name',
            'parameters': {}}]

        mock_ansible_run.return_value = ('foo.yaml', 0, 'failed')

        mock_results.return_value = [{'Duration': '0:00:01.761',
                                      'Host_Group': 'overcloud',
                                      'Status': 'PASSED',
                                      'Status_by_Host': 'subnode-1,PASSED',
                                      'UUID': 'foo',
                                      'Unreachable_Hosts': '',
                                      'Validations': 'ntp'}]

        expected_run_return = [{'Duration': '0:00:01.761',
                                'Host_Group': 'overcloud',
                                'Status': 'PASSED',
                                'Status_by_Host': 'subnode-1,PASSED',
                                'UUID': 'foo',
                                'Unreachable_Hosts': '',
                                'Validations': 'ntp'}]

        playbook = ['fake.yaml']
        inventory = 'tmp/inventory.yaml'

        run = ValidationActions()
        run_return = run.run_validations(playbook, inventory,
                                         group=fakes.GROUPS_LIST,
                                         validations_dir='/tmp/foo')
        self.assertEqual(run_return, expected_run_return)

    @mock.patch('validations_libs.ansible.Ansible._playbook_check',
                side_effect=RuntimeError)
    @mock.patch('validations_libs.utils.os.makedirs')
    @mock.patch('validations_libs.utils.os.access', return_value=True)
    @mock.patch('validations_libs.utils.os.path.exists', return_value=True)
    @mock.patch('validations_libs.utils.parse_all_validations_on_disk')
    def test_spinner_exception_failure_condition(self, mock_validation_dir,
                                                 mock_exists, mock_access,
                                                 mock_makedirs,
                                                 mock_playbook_check):

        mock_validation_dir.return_value = [{
            'description': 'My Validation One Description',
            'groups': ['prep', 'pre-deployment'],
            'id': 'foo',
            'name': 'My Validition One Name',
            'parameters': {}}]
        playbook = ['fake.yaml']
        inventory = 'tmp/inventory.yaml'

        run = ValidationActions()

        self.assertRaises(RuntimeError, run.run_validations, playbook,
                          inventory, group=fakes.GROUPS_LIST,
                          validations_dir='/tmp/foo')

    @mock.patch('validations_libs.ansible.Ansible._playbook_check',
                side_effect=RuntimeError)
    @mock.patch('validations_libs.utils.os.makedirs')
    @mock.patch('validations_libs.utils.os.access', return_value=True)
    @mock.patch('validations_libs.utils.os.path.exists', return_value=True)
    @mock.patch('validations_libs.utils.parse_all_validations_on_disk')
    @mock.patch('sys.__stdin__.isatty', return_value=True)
    def test_spinner_forced_run(self, mock_stdin_isatty, mock_validation_dir,
                                mock_exists, mock_access, mock_makedirs,
                                mock_playbook_check):

        mock_validation_dir.return_value = [{
            'description': 'My Validation One Description',
            'groups': ['prep', 'pre-deployment'],
            'id': 'foo',
            'name': 'My Validition One Name',
            'parameters': {}}]
        playbook = ['fake.yaml']
        inventory = 'tmp/inventory.yaml'

        run = ValidationActions()

        self.assertRaises(RuntimeError, run.run_validations, playbook,
                          inventory, group=fakes.GROUPS_LIST,
                          validations_dir='/tmp/foo')

    @mock.patch('validations_libs.utils.get_validations_playbook',
                return_value=[])
    def test_validation_run_no_validation(self, mock_get_val):
        playbook = ['fake.yaml']
        inventory = 'tmp/inventory.yaml'

        run = ValidationActions()
        self.assertRaises(RuntimeError, run.run_validations, playbook,
                          inventory)

    @mock.patch('validations_libs.utils.parse_all_validations_on_disk',
                return_value=fakes.VALIDATIONS_LIST)
    @mock.patch('validations_libs.validation.Validation._get_content',
                return_value=fakes.FAKE_PLAYBOOK[0])
    @mock.patch('validations_libs.validation_logs.ValidationLogs.'
                'get_logfile_content_by_validation',
                return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST)
    @mock.patch('six.moves.builtins.open')
    @mock.patch('os.path.exists', return_value=True)
    def test_validation_show(self, mock_exists, mock_open,
                             mock_parse_validation, mock_data, mock_log):
        data = {'Name': 'Advanced Format 512e Support',
                'Description': 'foo', 'Groups': ['prep', 'pre-deployment'],
                'Categories': ['os', 'storage'],
                'Products': ['product1'],
                'ID': '512e',
                'Parameters': {}}
        data.update({'Last execution date': '2019-11-25 13:40:14',
                     'Number of execution': 'Total: 1, Passed: 0, Failed: 1'})
        validations_show = ValidationActions()
        out = validations_show.show_validations('512e')
        self.assertEqual(out, data)

    @mock.patch('os.path.exists', return_value=False)
    def test_validation_show_not_found(self, mock_exists):
        validations_show = ValidationActions()
        self.assertRaises(
            RuntimeError,
            validations_show.show_validations,
            '512e'
        )

    @mock.patch('validations_libs.utils.parse_all_validations_on_disk',
                return_value=fakes.VALIDATIONS_LIST)
    @mock.patch('yaml.safe_load', return_value=fakes.GROUP)
    @mock.patch('six.moves.builtins.open')
    def test_group_information(self, mock_open, mock_yaml, mock_data):
        v_actions = ValidationActions()
        col, values = v_actions.group_information('512e')
        self.assertEqual(col, ('Groups', 'Description',
                               'Number of Validations'))
        self.assertEqual(values, [('no-op', 'noop-foo', 2),
                                  ('post', 'post-foo', 2),
                                  ('pre', 'pre-foo', 2)])

    @mock.patch('six.moves.builtins.open')
    def test_show_validations_parameters_wrong_validations_type(self, mock_open):
        v_actions = ValidationActions()
        self.assertRaises(TypeError,
                          v_actions.show_validations_parameters,
                          validations='foo')

    @mock.patch('six.moves.builtins.open')
    def test_show_validations_parameters_wrong_groups_type(self, mock_open):
        v_actions = ValidationActions()
        self.assertRaises(TypeError,
                          v_actions.show_validations_parameters,
                          groups=('foo'))

    @mock.patch('six.moves.builtins.open')
    def test_show_validations_parameters_wrong_categories_type(self, mock_open):
        v_actions = ValidationActions()
        self.assertRaises(TypeError,
                          v_actions.show_validations_parameters,
                          categories={'foo': 'bar'})

    @mock.patch('six.moves.builtins.open')
    def test_show_validations_parameters_wrong_products_type(self, mock_open):
        v_actions = ValidationActions()
        self.assertRaises(TypeError,
                          v_actions.show_validations_parameters,
                          products={'foo': 'bar'})

    @mock.patch('validations_libs.utils.get_validations_playbook',
                return_value=['/foo/playbook/foo.yaml'])
    @mock.patch('validations_libs.utils.get_validations_parameters')
    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_show_validations_parameters(self, mock_open, mock_load,
                                         mock_get_param, mock_get_play):
        mock_get_param.return_value = {'foo':
                                       {'parameters': fakes.FAKE_METADATA}}
        v_actions = ValidationActions()
        result = v_actions.show_validations_parameters(validations=['foo'])
        self.assertEqual(result, mock_get_param.return_value)

    @mock.patch('six.moves.builtins.open')
    def test_show_validations_parameters_non_supported_format(self, mock_open):
        v_actions = ValidationActions()
        self.assertRaises(RuntimeError,
                          v_actions.show_validations_parameters,
                          validations=['foo'], output_format='bar')

    @mock.patch('validations_libs.validation_logs.ValidationLogs.'
                'get_logfile_by_validation',
                return_value=['/tmp/123_foo_2020-03-30T13:17:22.447857Z.json'])
    @mock.patch('json.load',
                return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_show_history_str(self, mock_open, mock_load, mock_get_log):
        v_actions = ValidationActions()
        col, values = v_actions.show_history('512e')
        self.assertEqual(col, ('UUID', 'Validations',
                               'Status', 'Execution at',
                               'Duration'))
        self.assertEqual(values, [('008886df-d297-1eaa-2a74-000000000008',
                                   '512e', 'PASSED',
                                   '2019-11-25T13:40:14.404623Z',
                                   '0:00:03.753')])

    @mock.patch('validations_libs.validation_logs.ValidationLogs.'
                'get_logfile_by_validation',
                return_value=['/tmp/123_foo_2020-03-30T13:17:22.447857Z.json'])
    @mock.patch('json.load',
                return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_show_history_list(self, mock_open, mock_load, mock_get_log):
        v_actions = ValidationActions()
        col, values = v_actions.show_history(['512e'])
        self.assertEqual(col, ('UUID', 'Validations',
                               'Status', 'Execution at',
                               'Duration'))
        self.assertEqual(values, [('008886df-d297-1eaa-2a74-000000000008',
                                   '512e', 'PASSED',
                                   '2019-11-25T13:40:14.404623Z',
                                   '0:00:03.753')])

    @mock.patch('validations_libs.validation_logs.ValidationLogs.'
                'get_all_logfiles',
                return_value=['/tmp/123_foo_2020-03-30T13:17:22.447857Z.json'])
    @mock.patch('json.load',
                return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_show_history_all(self, mock_open, mock_load, mock_get_log):
        v_actions = ValidationActions()
        col, values = v_actions.show_history()
        self.assertEqual(col, ('UUID', 'Validations',
                               'Status', 'Execution at',
                               'Duration'))
        self.assertEqual(values, [('008886df-d297-1eaa-2a74-000000000008',
                                   '512e', 'PASSED',
                                   '2019-11-25T13:40:14.404623Z',
                                   '0:00:03.753')])

    @mock.patch('os.stat')
    @mock.patch('validations_libs.validation_logs.ValidationLogs.'
                'get_all_logfiles',
                return_value=[
                    '/tmp/123_foo_2020-03-30T13:17:22.447857Z.json',
                    '/tmp/123_bar_2020-03-05T13:17:22.447857Z.json'])
    @mock.patch('json.load',
                return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_show_history_most_recent(self, mock_open, mock_load,
                                      mock_get_log, mock_stat):

        first_validation = mock.MagicMock()
        second_validation = mock.MagicMock()

        first_validation.st_mtime = 5
        second_validation.st_mtime = 7

        validations = {
            '/tmp/123_foo_2020-03-30T13:17:22.447857Z.json': first_validation,
            '/tmp/123_bar_2020-03-05T13:17:22.447857Z.json': second_validation
        }

        def _generator(x=None):
            if x:
                return validations[x]
            return first_validation

        mock_stat.side_effect = _generator

        v_actions = ValidationActions()
        col, values = v_actions.show_history(history_limit=1)

        self.assertEqual(col, ('UUID', 'Validations',
                               'Status', 'Execution at',
                               'Duration'))
        self.assertEqual(values, [('008886df-d297-1eaa-2a74-000000000008',
                                   '512e', 'PASSED',
                                   '2019-11-25T13:40:14.404623Z',
                                   '0:00:03.753')])

    @mock.patch('validations_libs.validation_logs.ValidationLogs.'
                'get_logfile_by_validation',
                return_value=['/tmp/123_foo_2020-03-30T13:17:22.447857Z.json'])
    @mock.patch('json.load',
                return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_get_status(self, mock_open, mock_load, mock_get_log):
        v_actions = ValidationActions()
        col, values = v_actions.get_status('foo')
        self.assertEqual(col, ['name', 'host', 'status', 'task_data'])
        self.assertEqual(values, [('Check if iscsi.service is enabled', 'foo',
                                  'FAILED', {})])

    def test_get_status_no_param(self):
        v_actions = ValidationActions()
        self.assertRaises(RuntimeError, v_actions.get_status)
