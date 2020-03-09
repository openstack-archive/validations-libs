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
from validations_libs.list import List


class TestValidatorList(TestCase):

    def setUp(self):
        super(TestValidatorList, self).setUp()
        self.column_name = ('ID', 'Name', 'Groups')

    @mock.patch('validations_libs.utils.parse_all_validations_on_disk',
                return_value=fakes.VALIDATIONS_LIST)
    def test_validation_list(self, mock_validation_dir):
        validations_list = List(fakes.GROUPS_LIST, '/tmp/foo')

        self.assertEqual(validations_list.list_validations(),
                         (self.column_name, [('my_val1',
                                              'My Validition One Name',
                                              ['prep', 'pre-deployment']),
                                             ('my_val2',
                                              'My Validition Two Name',
                                             ['prep', 'pre-introspection'])]))
