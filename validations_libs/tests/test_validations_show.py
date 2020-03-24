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
from validations_libs.validation_actions import ValidationActions


class TestValidatorShow(TestCase):

    def setUp(self):
        super(TestValidatorShow, self).setUp()

    @mock.patch('validations_libs.utils.parse_all_validations_on_disk',
                return_value=fakes.VALIDATIONS_LIST)
    @mock.patch('validations_libs.validation.Validation._get_content',
                return_value=fakes.FAKE_PLAYBOOK)
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
