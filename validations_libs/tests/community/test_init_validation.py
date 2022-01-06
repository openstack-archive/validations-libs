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

# @matbu backward compatibility for stable/train
try:
    from pathlib import PosixPath
    PATHLIB = 'pathlib'
except ImportError:
    from pathlib2 import PosixPath
    PATHLIB = 'pathlib2'

from unittest import TestCase

from validations_libs import constants
from validations_libs.community.init_validation import \
    CommunityValidation as cv
from validations_libs.tests import fakes


class TestCommunityValidation(TestCase):

    def setUp(self):
        super(TestCommunityValidation, self).setUp()

    def test_role_name_underscored(self):
        validation_name = "my_new_validation"
        co_val = cv(validation_name)
        role_name = co_val.role_name
        self.assertEqual(role_name, validation_name)

    def test_role_name_with_underscores_and_dashes(self):
        validation_name = "my_new-validation"
        co_val = cv(validation_name)
        self.assertEqual(co_val.role_name, "my_new_validation")

    def test_role_name_with_dashes_only(self):
        validation_name = "my-new-validation"
        co_val = cv(validation_name)
        self.assertEqual(co_val.role_name,
                         "my_new_validation")

    def test_role_name_compliant(self):
        validation_name = "my_new_validation"
        co_val = cv(validation_name)
        self.assertTrue(co_val.is_role_name_compliant)

    def test_role_name_not_compliant(self):
        validation_name = "123_my_new-validation"
        co_val = cv(validation_name)
        self.assertFalse(co_val.is_role_name_compliant)

    def test_role_basedir(self):
        validation_name = "my_new-validation"
        co_val = cv(validation_name)
        self.assertEqual(co_val.role_basedir,
                         constants.COMMUNITY_ROLES_DIR)

    def test_playbook_name_with_underscores(self):
        validation_name = "my_new_validation"
        co_val = cv(validation_name)
        self.assertEqual(co_val.playbook_name,
                         "my-new-validation.yaml")

    def test_playbook_name_with_underscores_and_dashes(self):
        validation_name = "my_new-validation"
        co_val = cv(validation_name)
        self.assertEqual(co_val.playbook_name,
                         "my-new-validation.yaml")

    def test_playbook_basedir(self):
        validation_name = "my_new-validation"
        co_val = cv(validation_name)
        self.assertEqual(co_val.playbook_basedir,
                         constants.COMMUNITY_PLAYBOOKS_DIR)

    @mock.patch('{}.Path.iterdir'.format(PATHLIB),
                return_value=fakes.FAKE_ROLES_ITERDIR2)
    @mock.patch('{}.Path.is_dir'.format(PATHLIB))
    @mock.patch('{}.Path.exists'.format(PATHLIB), side_effect=[False, True])
    def test_role_already_exists_in_comval(self,
                                           mock_play_path_exists,
                                           mock_path_is_dir,
                                           mock_path_iterdir):
        validation_name = "my-val"
        co_val = cv(validation_name)
        self.assertTrue(co_val.is_role_exists())

    @mock.patch('{}.Path.iterdir'.format(PATHLIB),
                return_value=fakes.FAKE_ROLES_ITERDIR1)
    @mock.patch('{}.Path.is_dir'.format(PATHLIB))
    @mock.patch('{}.Path.exists'.format(PATHLIB), side_effect=[True, False])
    def test_role_already_exists_in_non_comval(self,
                                               mock_play_path_exists,
                                               mock_path_is_dir,
                                               mock_path_iterdir):
        validation_name = "my-val"
        co_val = cv(validation_name)
        self.assertTrue(co_val.is_role_exists())

    @mock.patch('{}.Path.iterdir'.format(PATHLIB),
                return_value=fakes.FAKE_ROLES_ITERDIR2)
    @mock.patch('{}.Path.is_dir'.format(PATHLIB))
    @mock.patch('{}.Path.exists'.format(PATHLIB), side_effect=[True, False])
    def test_role_not_exists(self,
                             mock_path_exists,
                             mock_path_is_dir,
                             mock_path_iterdir):
        validation_name = "my-val"
        co_val = cv(validation_name)
        self.assertFalse(co_val.is_role_exists())

    @mock.patch('{}.Path.iterdir'.format(PATHLIB),
                return_value=fakes.FAKE_PLAYBOOKS_ITERDIR1)
    @mock.patch('{}.Path.is_file'.format(PATHLIB))
    @mock.patch('{}.Path.exists'.format(PATHLIB), side_effect=[True, False])
    def test_playbook_already_exists_in_non_comval(self,
                                                   mock_path_exists,
                                                   mock_path_is_file,
                                                   mock_path_iterdir):
        validation_name = "my_val"
        co_val = cv(validation_name)
        self.assertTrue(co_val.is_playbook_exists())

    @mock.patch('{}.Path.iterdir'.format(PATHLIB),
                return_value=fakes.FAKE_PLAYBOOKS_ITERDIR2)
    @mock.patch('{}.Path.is_file'.format(PATHLIB))
    @mock.patch('{}.Path.exists'.format(PATHLIB), side_effect=[False, True])
    def test_playbook_already_exists_in_comval(self,
                                               mock_path_exists,
                                               mock_path_is_file,
                                               mock_path_iterdir):
        validation_name = "my_val"
        co_val = cv(validation_name)
        self.assertTrue(co_val.is_playbook_exists())

    @mock.patch('{}.Path.iterdir'.format(PATHLIB),
                return_value=fakes.FAKE_PLAYBOOKS_ITERDIR2)
    @mock.patch('{}.Path.is_file'.format(PATHLIB))
    @mock.patch('{}.Path.exists'.format(PATHLIB), side_effect=[True, False])
    def test_playbook_not_exists(self,
                                 mock_path_exists,
                                 mock_path_is_file,
                                 mock_path_iterdir):
        validation_name = "my_val"
        co_val = cv(validation_name)
        self.assertFalse(co_val.is_playbook_exists())

    def test_execute_with_role_name_not_compliant(self):
        validation_name = "3_my-val"
        co_val = cv(validation_name)
        self.assertRaises(RuntimeError, co_val.execute)

    @mock.patch('validations_libs.community.init_validation.CommunityValidation.create_playbook')
    @mock.patch('validations_libs.utils.run_command_and_log',
                return_value=0)
    @mock.patch('validations_libs.community.init_validation.CommunityValidation.role_basedir',
                return_value=PosixPath("/foo/bar/roles"))
    @mock.patch('validations_libs.community.init_validation.LOG',
                autospec=True)
    def test_exec_new_role_with_galaxy(self,
                                       mock_log,
                                       mock_role_basedir,
                                       mock_run,
                                       mock_create_playbook):
        validation_name = "my_val"
        cmd = ['ansible-galaxy', 'init', '-v',
               '--offline', validation_name,
               '--init-path', mock_role_basedir]
        co_val = cv(validation_name)
        co_val.execute()
        mock_run.assert_called_once_with(mock_log, cmd)

    @mock.patch('validations_libs.community.init_validation.CommunityValidation.create_playbook')
    @mock.patch('validations_libs.utils.run_command_and_log',
                return_value=1)
    @mock.patch('validations_libs.community.init_validation.CommunityValidation.role_basedir',
                return_value=PosixPath("/foo/bar/roles"))
    @mock.patch('validations_libs.community.init_validation.LOG',
                autospec=True)
    def test_exec_new_role_with_galaxy_and_error(self,
                                                 mock_log,
                                                 mock_role_basedir,
                                                 mock_run,
                                                 mock_create_playbook):
        validation_name = "my_val"
        cmd = ['ansible-galaxy', 'init', '-v',
               '--offline', validation_name,
               '--init-path', mock_role_basedir]
        co_val = cv(validation_name)
        self.assertRaises(RuntimeError, co_val.execute)

    @mock.patch(
        'validations_libs.community.init_validation.CommunityValidation.create_playbook',
        side_effect=PermissionError)
    @mock.patch('validations_libs.utils.run_command_and_log',
                return_value=0)
    @mock.patch('validations_libs.community.init_validation.CommunityValidation.role_basedir',
                return_value=PosixPath("/foo/bar/roles"))
    @mock.patch('validations_libs.community.init_validation.LOG',
                autospec=True)
    def test_validation_init_create_playbook_with_issue(self,
                                                        mock_log,
                                                        mock_role_basedir,
                                                        mock_run,
                                                        mock_create_playbook):
        validation_name = "foo_bar"
        cmd = ['ansible-galaxy', 'init', '-v',
               '--offline', validation_name,
               '--init-path', mock_role_basedir]
        co_val = cv(validation_name)
        self.assertRaises(RuntimeError, co_val.execute)

    @mock.patch('builtins.open')
    @mock.patch('validations_libs.community.init_validation.CommunityValidation.playbook_path',
                return_value='/foo/bar/playbooks/my-val.yaml')
    @mock.patch('validations_libs.utils.run_command_and_log',
                return_value=0)
    @mock.patch('validations_libs.community.init_validation.CommunityValidation.role_basedir',
                return_value=PosixPath("/foo/bar/roles"))
    @mock.patch('validations_libs.community.init_validation.LOG',
                autospec=True)
    def test_validation_init_create_playbook(self,
                                             mock_log,
                                             mock_role_basedir,
                                             mock_run,
                                             mock_playbook_path,
                                             mock_open):
        validation_name = "my_val"
        co_val = cv(validation_name)
        co_val.execute()

        self.assertIn(
            mock.call(mock_playbook_path, 'w'),
            mock_open.mock_calls
        )
        self.assertIn(
            mock.call().__enter__().write(
                fakes.FAKE_PLAYBOOK_TEMPLATE
            ),
            mock_open.mock_calls
        )
