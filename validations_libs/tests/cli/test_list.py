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

from validations_libs.cli import lister
from validations_libs.tests import fakes
from validations_libs.tests.cli.fakes import BaseCommand


class TestList(BaseCommand):

    def setUp(self):
        super(TestList, self).setUp()
        self.cmd = lister.ValidationList(self.app, None)

    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'list_validations',
                return_value=fakes.VALIDATIONS_LIST)
    def test_list_validations(self, mock_list):
        arglist = ['--validation-dir', 'foo']
        verifylist = [('validation_dir', 'foo')]

        val_list = [
            {'description': 'My Validation One Description',
             'groups': ['prep', 'pre-deployment'],
             'categories': ['os', 'system', 'ram'],
             'products': ['product1'],
             'id': 'my_val1',
             'name': 'My Validation One Name',
             'parameters': {}
            }, {
             'description': 'My Validation Two Description',
             'groups': ['prep', 'pre-introspection'],
             'categories': ['networking'],
             'products': ['product1'],
             'id': 'my_val2',
             'name': 'My Validation Two Name',
             'parameters': {'min_value': 8}
            }]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.assertEqual(result, val_list)

    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'list_validations',
                return_value=[])
    def test_list_validations_empty(self, mock_list):
        arglist = ['--validation-dir', 'foo']
        verifylist = [('validation_dir', 'foo')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.assertEqual(result, [])

    @mock.patch('validations_libs.utils.parse_all_validations_on_disk',
                return_value=fakes.VALIDATIONS_LIST_GROUP)
    def test_list_validations_group(self, mock_list):
        arglist = ['--validation-dir', 'foo', '--group', 'prep']
        verifylist = [('validation_dir', 'foo'),
                      ('group', ['prep'])]

        val_list = fakes.VALIDATION_LIST_RESULT

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.assertEqual(result, val_list)

    @mock.patch('validations_libs.utils.parse_all_validations_on_disk',
                return_value=fakes.VALIDATIONS_LIST_GROUP)
    def test_list_validations_by_category(self, mock_list):
        arglist = ['--validation-dir', 'foo', '--category', 'networking']
        verifylist = [('validation_dir', 'foo'),
                      ('category', ['networking'])]

        val_list = fakes.VALIDATION_LIST_RESULT

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.assertEqual(result, val_list)

    @mock.patch('validations_libs.utils.parse_all_validations_on_disk',
                return_value=fakes.VALIDATIONS_LIST_GROUP)
    def test_list_validations_by_product(self, mock_list):
        arglist = ['--validation-dir', 'foo', '--product', 'product1']
        verifylist = [('validation_dir', 'foo'),
                      ('product', ['product1'])]

        val_list = fakes.VALIDATION_LIST_RESULT

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.assertEqual(result, val_list)
