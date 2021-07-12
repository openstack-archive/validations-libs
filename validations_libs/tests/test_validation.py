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
        self.assertEqual(data, fakes.FAKE_PLAYBOOK[0])

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_get_metadata(self, mock_open, mock_yaml):
        val = Validation('/tmp/foo')
        data = val.get_metadata
        self.assertEqual(data, fakes.FAKE_METADATA)

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_WRONG_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_get_metadata_wrong_playbook(self, mock_open, mock_yaml):
        with self.assertRaises(NameError) as exc_mgr:
            Validation('/tmp/foo').get_metadata
        self.assertEqual('No metadata found in validation foo',
                         str(exc_mgr.exception))

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK2)
    @mock.patch('six.moves.builtins.open')
    def test_get_vars(self, mock_open, mock_yaml):
        val = Validation('/tmp/foo')
        data = val.get_vars
        self.assertEqual(data, fakes.FAKE_VARS)

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_get_vars_no_vars(self, mock_open, mock_yaml):
        val = Validation('/tmp/foo')
        data = val.get_vars
        self.assertEqual(data, {})

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_WRONG_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_get_vars_no_metadata(self, mock_open, mock_yaml):
        with self.assertRaises(NameError) as exc_mgr:
            Validation('/tmp/foo').get_vars
        self.assertEqual('No metadata found in validation foo',
                         str(exc_mgr.exception))

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_get_id(self, mock_open, mock_yaml):
        val = Validation('/tmp/foo')
        id = val.id
        get_id = val.get_id
        self.assertEqual(id, 'foo')
        self.assertEqual(get_id, 'foo')

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_groups(self, mock_open, mock_yaml):
        val = Validation('/tmp/foo')
        groups = val.groups
        self.assertEqual(groups, ['prep', 'pre-deployment'])

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_WRONG_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_groups_with_no_metadata(self, mock_open, mock_yaml):
        with self.assertRaises(NameError) as exc_mgr:
            Validation('/tmp/foo').groups
        self.assertEqual('No metadata found in validation foo',
                         str(exc_mgr.exception))

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK3)
    @mock.patch('six.moves.builtins.open')
    def test_groups_with_no_existing_groups(self, mock_open, mock_yaml):
        val = Validation('/tmp/foo')
        groups = val.groups
        self.assertEqual(groups, [])

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_categories(self, mock_open, mock_yaml):
        val = Validation('/tmp/foo')
        categories = val.categories
        self.assertEqual(categories, ['os', 'storage'])

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_WRONG_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_categories_with_no_metadata(self, mock_open, mock_yaml):
        with self.assertRaises(NameError) as exc_mgr:
            Validation('/tmp/foo').categories
        self.assertEqual('No metadata found in validation foo',
                         str(exc_mgr.exception))

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK3)
    @mock.patch('six.moves.builtins.open')
    def test_categories_with_no_existing_categories(self, mock_open, mock_yaml):
        val = Validation('/tmp/foo')
        categories = val.categories
        self.assertEqual(categories, [])

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_products(self, mock_open, mock_yaml):
        val = Validation('/tmp/foo')
        products = val.products
        self.assertEqual(products, ['product1'])

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_WRONG_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_products_with_no_metadata(self, mock_open, mock_yaml):
        with self.assertRaises(NameError) as exc_mgr:
            Validation('/tmp/foo').products
        self.assertEqual('No metadata found in validation foo',
                         str(exc_mgr.exception))

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK3)
    @mock.patch('six.moves.builtins.open')
    def test_products_with_no_existing_products(self, mock_open, mock_yaml):
        val = Validation('/tmp/foo')
        products = val.products
        self.assertEqual(products, [])

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_get_ordered_dict(self, mock_open, mock_yaml):
        val = Validation('/tmp/foo')
        data = val.get_ordered_dict
        self.assertEqual(data, fakes.FAKE_PLAYBOOK[0])

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_get_formated_data(self, mock_open, mock_yaml):
        val = Validation('/tmp/foo')
        data = val.get_formated_data
        self.assertEqual(data, fakes.FORMATED_DATA)

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_WRONG_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_get_formated_data_no_metadata(self, mock_open, mock_yaml):
        with self.assertRaises(NameError) as exc_mgr:
            Validation('/tmp/foo').get_formated_data
        self.assertEqual('No metadata found in validation foo',
                         str(exc_mgr.exception))

    @mock.patch('six.moves.builtins.open')
    def test_validation_not_found(self, mock_open):
        mock_open.side_effect = IOError()
        self.assertRaises(
            IOError,
            Validation,
            'non-existing.yaml'
        )
