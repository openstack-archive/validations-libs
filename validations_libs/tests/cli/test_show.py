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

from validations_libs.cli import show
from validations_libs.tests import fakes
from validations_libs.tests.cli.fakes import BaseCommand


class TestShow(BaseCommand):

    def setUp(self):
        super(TestShow, self).setUp()
        self.cmd = show.Show(self.app, None)

    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'show_validations')
    def test_show_validations(self, mock_show):
        arglist = ['foo']
        verifylist = [('validation_name', 'foo')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)


class TestShowGroup(BaseCommand):

    def setUp(self):
        super(TestShowGroup, self).setUp()
        self.cmd = show.ShowGroup(self.app, None)

    @mock.patch('validations_libs.cli.show.ValidationActions', autospec=True)
    @mock.patch('yaml.safe_load', return_value=fakes.GROUP)
    @mock.patch('six.moves.builtins.open')
    def test_show_validations_group_info(self, mock_open, mock_yaml, mock_actions):
        arglist = []

        mock_info = mock.MagicMock()
        mock_info.group_information = mock.MagicMock(return_value='foo')
        mock_actions.return_value = mock_info

        parsed_args = self.check_parser(self.cmd, arglist, [])

        group_info = self.cmd.take_action(parsed_args)

        mock_actions.assert_called_once_with(
            validation_path=fakes.FAKE_VALIDATIONS_PATH)

        mock_info.group_information.assert_called_once()

        self.assertEqual('foo', group_info)


class TestShowParameter(BaseCommand):

    def setUp(self):
        super(TestShowParameter, self).setUp()
        self.cmd = show.ShowParameter(self.app, None)

    @mock.patch('six.moves.builtins.open')
    def test_show_validations_parameters_by_group(self, mock_open):
        arglist = ['--group', 'prep']
        verifylist = [('group', ['prep'])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

    def test_show_parameter_exclusive_group(self):
        arglist = ['--validation', 'foo', '--group', 'bar']
        verifylist = [('validation_name', ['foo'], 'group', ['bar'])]

        self.assertRaises(Exception, self.check_parser, self.cmd,
                          arglist, verifylist)

    @mock.patch('six.moves.builtins.open')
    def test_show_validations_parameters_by_validations(self, mock_open):
        arglist = ['--group', 'prep']
        verifylist = [('group', ['prep'])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'show_validations_parameters')
    def test_show_validations_parameters_by_categories(self, mock_show):
        arglist = ['--category', 'os']
        verifylist = [('category', ['os'])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'show_validations_parameters')
    def test_show_validations_parameters_by_products(self, mock_show):
        arglist = ['--product', 'product1']
        verifylist = [('product', ['product1'])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
