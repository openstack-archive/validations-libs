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

from unittest import mock
from unittest import TestCase

from validations_libs.tests import fakes
from validations_libs.run import Run


class TestValidatorRun(TestCase):

    def setUp(self):
        super(TestValidatorRun, self).setUp()

    @mock.patch('validations_libs.utils.parse_all_validations_on_disk')
    @mock.patch('validations_libs.ansible.Ansible.run')
    @mock.patch('validations_libs.utils.create_artifacts_dir',
                return_value=('1234', '/tmp/'))
    def test_validation_run_success(self, mock_tmp, mock_ansible_run,
                                    mock_validation_dir):
        mock_validation_dir.return_value = [{
            'description': 'My Validation One Description',
            'groups': ['prep', 'pre-deployment'],
            'id': 'foo',
            'name': 'My Validition One Name',
            'parameters': {}}]
        mock_ansible_run.return_value = ('foo.yaml', 0, 'successful')

        expected_run_return = [
            {'validation': {'playbook': 'foo.yaml',
                            'rc_code': 0,
                            'status': 'successful',
                            'validation_id': '1234'}},
            {'validation': {'playbook': 'foo.yaml',
                            'rc_code': 0,
                            'status': 'successful',
                            'validation_id': '1234'}}]

        playbook = ['fake.yaml']
        inventory = 'tmp/inventory.yaml'

        run = Run()
        run_return = run.run_validations(playbook, inventory,
                                         group=fakes.GROUPS_LIST,
                                         validations_dir='/tmp/foo')
        self.assertEqual(run_return, expected_run_return)

    @mock.patch('validations_libs.utils.parse_all_validations_on_disk')
    @mock.patch('validations_libs.ansible.Ansible.run')
    @mock.patch('validations_libs.utils.create_artifacts_dir',
                return_value=('1234', '/tmp/'))
    def test_validation_run_failed(self, mock_tmp, mock_ansible_run,
                                   mock_validation_dir):
        mock_validation_dir.return_value = [{
            'description': 'My Validation One Description',
            'groups': ['prep', 'pre-deployment'],
            'id': 'foo',
            'name': 'My Validition One Name',
            'parameters': {}}]
        mock_ansible_run.return_value = ('foo.yaml', 0, 'failed')

        expected_run_return = [
            {'validation': {'playbook': 'foo.yaml',
                            'rc_code': 0,
                            'status': 'failed',
                            'validation_id': '1234'}},
            {'validation': {'playbook': 'foo.yaml',
                            'rc_code': 0,
                            'status': 'failed',
                            'validation_id': '1234'}}]

        playbook = ['fake.yaml']
        inventory = 'tmp/inventory.yaml'

        run = Run()
        run_return = run.run_validations(playbook, inventory,
                                         group=fakes.GROUPS_LIST,
                                         validations_dir='/tmp/foo')
        self.assertEqual(run_return, expected_run_return)

    def test_validation_run_no_validation(self):
        playbook = ['fake.yaml']
        inventory = 'tmp/inventory.yaml'

        run = Run()
        self.assertRaises(RuntimeError, run.run_validations, playbook,
                          inventory)
