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

from validations_libs import utils
from validations_libs.tests import fakes
from validations_libs.validation_logs import ValidationLogs


class TestUtils(TestCase):

    def setUp(self):
        super(TestUtils, self).setUp()
        self.vlog = ValidationLogs()

    @mock.patch('validations_libs.validation.Validation._get_content',
                return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_get_validations_data(self, mock_open, mock_data):
        output = {'Name': 'Advanced Format 512e Support',
                  'Description': 'foo', 'Groups': ['prep', 'pre-deployment'],
                  'ID': '512e'}
        res = utils.get_validations_data('/foo/512e.yaml')
        self.assertEqual(res, output)

    def test_get_validations_stats(self):
        res = self.vlog.get_validations_stats(
            fakes.VALIDATIONS_LOGS_CONTENTS_LIST)
        self.assertEqual(res, fakes.VALIDATIONS_STATS)
