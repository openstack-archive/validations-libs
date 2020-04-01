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

from validations_libs.validation import Validation
from validations_libs.tests import fakes


class TestValidation(TestCase):

    def setUp(self):
        super(TestValidation, self).setUp()

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_get_data(self, mock_open, mock_yaml):
        val = Validation('/tmp/foo')
        data = val.get_data
        self.assertEquals(data, fakes.FAKE_PLAYBOOK[0])

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_get_metadata(self, mock_open, mock_yaml):
        val = Validation('/tmp/foo')
        data = val.get_metadata
        self.assertEquals(data, fakes.FAKE_METADATA)

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_get_id(self, mock_open, mock_yaml):
        val = Validation('/tmp/foo')
        id = val.id
        get_id = val.get_id
        self.assertEquals(id, 'foo')
        self.assertEquals(get_id, 'foo')

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_groups(self, mock_open, mock_yaml):
        val = Validation('/tmp/foo')
        groups = val.groups
        self.assertEquals(groups, ['prep', 'pre-deployment'])

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_get_ordered_dict(self, mock_open, mock_yaml):
        val = Validation('/tmp/foo')
        data = val.get_ordered_dict
        self.assertEquals(data, fakes.FAKE_PLAYBOOK[0])

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_get_formated_data(self, mock_open, mock_yaml):
        val = Validation('/tmp/foo')
        data = val.get_formated_data
        self.assertEquals(data, fakes.FORMATED_DATA)

    @mock.patch('six.moves.builtins.open')
    def test_validation_not_found(self, mock_open):
        mock_open.side_effect = IOError()
        self.assertRaises(
            IOError,
            Validation,
            'non-existing.yaml'
        )
