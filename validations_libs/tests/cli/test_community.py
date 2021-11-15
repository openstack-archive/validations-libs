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

from validations_libs.cli import community
from validations_libs.cli import base
from validations_libs.community.init_validation import \
    CommunityValidation as cv
from validations_libs.tests import fakes
from validations_libs.tests.cli.fakes import BaseCommand


class TestCommunityValidationInit(BaseCommand):

    def setUp(self):
        super(TestCommunityValidationInit, self).setUp()
        self.cmd = community.CommunityValidationInit(self.app, None)
        self.base = base.Base()

    @mock.patch(
        'validations_libs.community.init_validation.CommunityValidation.execute')
    @mock.patch(
        'validations_libs.community.init_validation.CommunityValidation.is_playbook_exists',
        return_value=False)
    @mock.patch(
        'validations_libs.community.init_validation.CommunityValidation.is_role_exists',
        return_value=False)
    @mock.patch('validations_libs.utils.check_community_validations_dir')
    def test_validation_init(self,
                             mock_comval_dir,
                             mock_role_exists,
                             mock_play_exists,
                             mock_execute):
        args = self._set_args(['my_new_community_val'])
        verifylist = [('validation_name', 'my_new_community_val')]

        parsed_args = self.check_parser(self.cmd, args, verifylist)
        self.cmd.take_action(parsed_args)

    @mock.patch(
        'validations_libs.community.init_validation.CommunityValidation.is_community_validations_enabled',
        return_value=False)
    def test_validation_init_with_com_val_disabled(self, mock_config):
        args = self._set_args(['my_new_community_val'])
        verifylist = [('validation_name', 'my_new_community_val')]

        parsed_args = self.check_parser(self.cmd, args, verifylist)
        self.assertRaises(RuntimeError, self.cmd.take_action,
                          parsed_args)

    @mock.patch(
        'validations_libs.community.init_validation.CommunityValidation.is_role_exists',
        return_value=True)
    @mock.patch(
        'validations_libs.community.init_validation.CommunityValidation.is_playbook_exists',
        return_value=False)
    @mock.patch('validations_libs.utils.check_community_validations_dir')
    def test_validation_init_with_role_existing(self,
                                                mock_comval_dir,
                                                mock_playbook_exists,
                                                mock_role_exists):
        args = self._set_args(['my_new_community_val'])
        verifylist = [('validation_name', 'my_new_community_val')]

        parsed_args = self.check_parser(self.cmd, args, verifylist)
        self.assertRaises(RuntimeError, self.cmd.take_action,
                          parsed_args)

    @mock.patch(
        'validations_libs.community.init_validation.CommunityValidation.is_role_exists',
        return_value=False)
    @mock.patch(
        'validations_libs.community.init_validation.CommunityValidation.is_playbook_exists',
        return_value=True)
    @mock.patch('validations_libs.utils.check_community_validations_dir')
    def test_validation_init_with_playbook_existing(self,
                                                    mock_comval_dir,
                                                    mock_playbook_exists,
                                                    mock_role_exists):
        args = self._set_args(['my_new_community_val'])
        verifylist = [('validation_name', 'my_new_community_val')]

        parsed_args = self.check_parser(self.cmd, args, verifylist)
        self.assertRaises(RuntimeError, self.cmd.take_action,
                          parsed_args)
