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

from validations_libs.group import Group
from validations_libs.tests import fakes


class TestGroup(TestCase):

    def setUp(self):
        super(TestGroup, self).setUp()

    @mock.patch('yaml.safe_load', return_value=fakes.GROUP)
    @mock.patch('six.moves.builtins.open')
    def test_get_data(self, mock_open, mock_yaml):
        grp = Group('/tmp/foo')
        data = grp.get_data
        self.assertEqual(data, fakes.GROUP)

    @mock.patch('yaml.safe_load', return_value=fakes.GROUP)
    @mock.patch('six.moves.builtins.open')
    def test_get_formated_group(self, mock_open, mock_yaml):
        grp = Group('/tmp/foo')
        ret = [('no-op', 'noop-foo'), ('post', 'post-foo'), ('pre', 'pre-foo')]
        data = grp.get_formated_group
        self.assertEqual(data, ret)

    @mock.patch('yaml.safe_load', return_value=fakes.GROUP)
    @mock.patch('six.moves.builtins.open')
    def test_get_groups_keys_list(self, mock_open, mock_yaml):
        grp = Group('/tmp/foo')
        ret = ['no-op', 'post', 'pre']
        data = grp.get_groups_keys_list
        self.assertEqual(data, ret)

    @mock.patch('six.moves.builtins.open')
    def test_group_file_not_found(self, mock_open):
        mock_open.side_effect = IOError()
        self.assertRaises(
            IOError,
            Group,
            'non-existing.yaml'
        )
