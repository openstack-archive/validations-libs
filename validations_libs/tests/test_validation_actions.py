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
from unittest import TestCase

from validations_libs.tests import fakes
from validations_libs.validation_actions import ValidationActions


class TestValidationActions(TestCase):

    def setUp(self):
        super(TestValidationActions, self).setUp()
        self.column_name = ('ID', 'Name', 'Groups')

    @mock.patch('validations_libs.utils.parse_all_validations_on_disk',
                return_value=fakes.VALIDATIONS_LIST)
    def test_validation_list(self, mock_validation_dir):
        validations_list = ValidationActions(fakes.GROUPS_LIST, '/tmp/foo')

        self.assertEqual(validations_list.list_validations(),
                         (self.column_name, [('my_val1',
                                              'My Validation One Name',
                                              ['prep', 'pre-deployment']),
                                             ('my_val2',
                                              'My Validation Two Name',
                                             ['prep', 'pre-introspection'])]))

    @mock.patch('validations_libs.validation_logs.ValidationLogs.get_results')
    @mock.patch('validations_libs.utils.parse_all_validations_on_disk')
    @mock.patch('validations_libs.ansible.Ansible.run')
    @mock.patch('validations_libs.utils.create_artifacts_dir',
                return_value=('1234', '/tmp/'))
    def test_validation_run_success(self, mock_tmp, mock_ansible_run,
                                    mock_validation_dir, mock_results):
        mock_validation_dir.return_value = [{
            'description': 'My Validation One Description',
            'groups': ['prep', 'pre-deployment'],
            'id': 'foo',
            'name': 'My Validition One Name',
            'parameters': {}}]
        mock_ansible_run.return_value = ('foo.yaml', 0, 'successful')

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

    @mock.patch('validations_libs.utils.get_validations_playbook')
    def test_validation_run_wrong_validation_name(self, mock_validation_play):
        mock_validation_play.return_value = []

        run = ValidationActions()
        self.assertRaises(RuntimeError, run.run_validations,
                          validation_name='fake.yaml',
                          validations_dir='/tmp/foo'
                          )

    @mock.patch('validations_libs.validation_logs.ValidationLogs.get_results')
    @mock.patch('validations_libs.utils.parse_all_validations_on_disk')
    @mock.patch('validations_libs.ansible.Ansible.run')
    @mock.patch('validations_libs.utils.create_artifacts_dir',
                return_value=('1234', '/tmp/'))
    def test_validation_run_failed(self, mock_tmp, mock_ansible_run,
                                   mock_validation_dir, mock_results):
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

    def test_validation_run_no_validation(self):
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
                'get_all_logfiles_content',
                return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST)
    @mock.patch('six.moves.builtins.open')
    @mock.patch('os.path.exists', return_value=True)
    def test_validation_show(self, mock_exists, mock_open,
                             mock_parse_validation, mock_data, mock_log):
        data = {'Name': 'Advanced Format 512e Support',
                'Description': 'foo', 'Groups': ['prep', 'pre-deployment'],
                'ID': '512e'}
        data.update({'Last execution date': '2019-11-25 13:40:14',
                     'Number of execution': 'Total: 1, Passed: 1, Failed: 0'})
        validations_show = ValidationActions()
        out = validations_show.show_validations('512e')
        self.assertEqual(out, data)

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
        result = v_actions.show_validations_parameters('foo')
        self.assertEqual(result, {'foo': {'parameters': fakes.FAKE_METADATA}})

    @mock.patch('validations_libs.validation_logs.ValidationLogs.'
                'get_logfile_by_validation',
                return_value=['/tmp/123_foo_2020-03-30T13:17:22.447857Z.json'])
    @mock.patch('json.load',
                return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_show_history(self, mock_open, mock_load, mock_get_log):
        v_actions = ValidationActions()
        col, values = v_actions.show_history('foo')
        self.assertEqual(col, ('UUID', 'Validations',
                               'Status', 'Execution at',
                               'Duration'))
        self.assertEqual(values, [('123', 'foo', 'PASSED',
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
        self.assertEqual(values, [('123', 'foo', 'PASSED',
                                   '2019-11-25T13:40:14.404623Z',
                                   '0:00:03.753')])
