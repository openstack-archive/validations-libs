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
from unittest import TestCase
import yaml
import sys
import importlib
from validations_libs.cli import common

try:
    from unittest import mock
except ImportError:
    import mock


class TestCommon(TestCase):

    def setUp(self):
        return super().setUp()

    def test_read_cli_data_file_with_example_file(self):
        example_data = {'check-cpu': {'hosts': 'undercloud',
                                      'lp': 'https://lp.fake.net',
                                      'reason': 'Unstable validation'},
                        'check-ram': {'hosts': 'all',
                                      'lp': 'https://lp.fake.net',
                                      'reason': 'Wrong ram value'}}
        data = common.read_cli_data_file('skiplist-example.yaml')
        self.assertEqual(data, example_data)

    @mock.patch('six.moves.builtins.open', side_effect=IOError)
    def test_read_cli_data_file_ioerror(self, mock_open):
        self.assertRaises(RuntimeError, common.read_cli_data_file, 'foo')

    @mock.patch('yaml.safe_load', side_effect=yaml.YAMLError)
    def test_read_cli_data_file_yaml_error(self, mock_yaml):
        self.assertRaises(RuntimeError, common.read_cli_data_file, 'foo')

    @mock.patch('cliff._argparse', spec={})
    def test_argparse_conditional_false(self, mock_argparse):
        """Test if the imporst are properly resolved based
        on presence of the `SmartHelpFormatter` in the namespace
        of the cliff._argparse.
        If the attribute isn't in the namespace, and it shouldn't be
        because the object is mocked to behave as a dictionary,
        the next statement after conditional will trigger `ImportError`.
        Because relevant class in the cliff module is mocked with side effect.
        """
        sys.modules[
            'cliff.command.SmartHelpFormatter'] = mock.MagicMock(
                side_effect=ImportError)

        self.assertRaises(
            ImportError,
            importlib.reload,
            common)
