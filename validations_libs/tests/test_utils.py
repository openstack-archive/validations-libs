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

import logging
import os
import subprocess

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

from validations_libs import utils, constants
from validations_libs.tests import fakes


class TestUtils(TestCase):

    def setUp(self):
        super(TestUtils, self).setUp()

    @mock.patch('validations_libs.validation.Validation._get_content',
                return_value=fakes.FAKE_PLAYBOOK[0])
    @mock.patch('six.moves.builtins.open')
    @mock.patch('os.path.exists', return_value=True)
    def test_get_validations_data(self, mock_exists, mock_open, mock_data):
        output = {'Name': 'Advanced Format 512e Support',
                  'Description': 'foo', 'Groups': ['prep', 'pre-deployment'],
                  'Categories': ['os', 'storage'],
                  'Products': ['product1'],
                  'ID': '512e',
                  'Parameters': {},
                  'Path': '/tmp'}
        res = utils.get_validations_data('512e')
        self.assertEqual(res, output)

    @mock.patch('validations_libs.validation.Validation._get_content',
                return_value=fakes.FAKE_PLAYBOOK[0])
    @mock.patch('six.moves.builtins.open')
    @mock.patch('os.path.exists', side_effect=(False, True))
    def test_get_community_validations_data(self, mock_exists, mock_open, mock_data):
        """
            The main difference between this test and test_get_validations_data
            is that this one tries to load first the validations_commons validation
            then it fails as os.path.exists returns false and then looks for it in the
            community validations.
        """
        output = {'Name': 'Advanced Format 512e Support',
                  'Description': 'foo', 'Groups': ['prep', 'pre-deployment'],
                  'Categories': ['os', 'storage'],
                  'Products': ['product1'],
                  'ID': '512e',
                  'Parameters': {},
                  'Path': '/tmp'}
        res = utils.get_validations_data('512e')
        self.assertEqual(res, output)

    @mock.patch('validations_libs.validation.Validation._get_content',
                return_value=fakes.FAKE_PLAYBOOK[0])
    @mock.patch('six.moves.builtins.open')
    @mock.patch('os.path.exists', side_effect=(False, True))
    def test_get_community_disabled_validations_data(self, mock_exists, mock_open, mock_data):
        """
            This test is similar to test_get_community_validations_data in the sense that it
            doesn't find the validations_commons one and should look for community validations
            but the setting is disabled by the config so it shouldn't find any validations
        """
        output = {}
        res = utils.get_validations_data(
                '512e',
                validation_config={'default': {"enable_community_validations": False}})
        self.assertEqual(res, output)

    @mock.patch('os.path.exists', return_value=True)
    def test_get_validations_data_wrong_type(self, mock_exists):
        validation = ['val1']
        self.assertRaises(TypeError,
                          utils.get_validations_data,
                          validation)

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    @mock.patch('glob.glob')
    def test_parse_all_validations_on_disk(self, mock_glob, mock_open,
                                           mock_load):
        mock_glob.side_effect = \
            (['/foo/playbook/foo.yaml'], [])
        result = utils.parse_all_validations_on_disk('/foo/playbook')
        self.assertEqual(result, [fakes.FAKE_METADATA])

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    @mock.patch('glob.glob')
    def test_parse_community_validations_on_disk(
                self, mock_glob, mock_open, mock_load):
        mock_glob.side_effect = \
            ([], ['/foo/playbook/foo.yaml'])
        result = utils.parse_all_validations_on_disk('/foo/playbook')
        self.assertEqual(result, [fakes.FAKE_METADATA])

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    @mock.patch('glob.glob')
    def test_parse_all_community_disabled_validations_on_disk(
                self, mock_glob, mock_open, mock_load):
        mock_glob.side_effect = \
            ([], ['/foo/playbook/foo.yaml'])
        result = utils.parse_all_validations_on_disk(
                '/foo/playbook',
                validation_config={'default': {"enable_community_validations": False}})
        self.assertEqual(result, [])

    def test_parse_all_validations_on_disk_wrong_path_type(self):
        self.assertRaises(TypeError,
                          utils.parse_all_validations_on_disk,
                          path=['/foo/playbook'])

    def test_parse_all_validations_on_disk_wrong_groups_type(self):
        self.assertRaises(TypeError,
                          utils.parse_all_validations_on_disk,
                          path='/foo/playbook',
                          groups='foo1,foo2')

    def test_parse_all_validations_on_disk_wrong_categories_type(self):
        self.assertRaises(TypeError,
                          utils.parse_all_validations_on_disk,
                          path='/foo/playbook',
                          categories='foo1,foo2')

    def test_parse_all_validations_on_disk_wrong_products_type(self):
        self.assertRaises(TypeError,
                          utils.parse_all_validations_on_disk,
                          path='/foo/playbook',
                          products='foo1,foo2')

    def test_get_validations_playbook_wrong_validation_id_type(self):
        self.assertRaises(TypeError,
                          utils.get_validations_playbook,
                          path='/foo/playbook',
                          validation_id='foo1,foo2')

    def test_get_validations_playbook_wrong_groups_type(self):
        self.assertRaises(TypeError,
                          utils.get_validations_playbook,
                          path='/foo/playbook',
                          groups='foo1,foo2')

    def test_get_validations_playbook_wrong_categories_type(self):
        self.assertRaises(TypeError,
                          utils.get_validations_playbook,
                          path='/foo/playbook',
                          categories='foo1,foo2')

    def test_get_validations_playbook_wrong_products_type(self):
        self.assertRaises(TypeError,
                          utils.get_validations_playbook,
                          path='/foo/playbook',
                          products='foo1,foo2')

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    @mock.patch('glob.glob')
    def test_parse_all_validations_on_disk_by_group(self, mock_glob,
                                                    mock_open,
                                                    mock_load):
        mock_glob.side_effect = \
            (['/foo/playbook/foo.yaml'], [])
        result = utils.parse_all_validations_on_disk('/foo/playbook',
                                                     ['prep'])
        self.assertEqual(result, [fakes.FAKE_METADATA])

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    @mock.patch('glob.glob')
    def test_parse_all_validations_on_disk_by_category(self, mock_glob,
                                                       mock_open,
                                                       mock_load):
        mock_glob.side_effect = \
            (['/foo/playbook/foo.yaml'], [])
        result = utils.parse_all_validations_on_disk('/foo/playbook',
                                                     categories=['os'])
        self.assertEqual(result, [fakes.FAKE_METADATA])

    def test_get_validations_playbook_wrong_path_type(self):
        self.assertRaises(TypeError,
                          utils.get_validations_playbook,
                          path=['/foo/playbook'])

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    @mock.patch('glob.glob')
    def test_parse_all_validations_on_disk_by_product(self, mock_glob,
                                                      mock_open,
                                                      mock_load):
        mock_glob.side_effect = (['/foo/playbook/foo.yaml'], [])
        result = utils.parse_all_validations_on_disk('/foo/playbook',
                                                     products=['product1'])
        self.assertEqual(result, [fakes.FAKE_METADATA])

    @mock.patch('os.path.isfile')
    @mock.patch('glob.glob')
    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_get_validations_playbook_by_id(self, mock_open, mock_load,
                                            mock_glob, mock_isfile):
        mock_glob.side_effect = (['/foo/playbook/foo.yaml'], [])
        mock_isfile.return_value = True
        result = utils.get_validations_playbook('/foo/playbook',
                                                validation_id=['foo'])
        self.assertEqual(result, ['/foo/playbook/foo.yaml'])

    @mock.patch('os.path.isfile')
    @mock.patch('glob.glob')
    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_get_community_playbook_by_id(self, mock_open, mock_load,
                                          mock_glob, mock_isfile):
        mock_glob.side_effect = (
                [],
                ['/home/foo/community-validations/playbooks/foo.yaml'])
        mock_isfile.return_value = True
        # AP this needs a bit of an explanation. We look at the explicity at
        #  the /foo/playbook directory but the community validation path is
        #  implicit and we find there the id that we are looking for.
        result = utils.get_validations_playbook('/foo/playbook',
                                                validation_id=['foo'])
        self.assertEqual(result, ['/home/foo/community-validations/playbooks/foo.yaml'])

    @mock.patch('os.path.isfile')
    @mock.patch('glob.glob')
    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_get_community_disabled_playbook_by_id(
                self, mock_open, mock_load, mock_glob, mock_isfile):
        mock_glob.side_effect = (
                [],
                ['/home/foo/community-validations/playbooks/foo.yaml'])
        mock_isfile.return_value = True
        # The validations_commons validation is not found and community_vals is disabled
        #  So no validation should be found.
        result = utils.get_validations_playbook(
                '/foo/playbook',
                validation_id=['foo'],
                validation_config={'default': {"enable_community_validations": False}})
        self.assertEqual(result, [])

    @mock.patch('os.path.isfile')
    @mock.patch('glob.glob')
    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_get_community_playbook_by_id_not_found(
                self, mock_open, mock_load, mock_glob, mock_isfile):
        mock_glob.side_effect = (
                [],
                ['/home/foo/community-validations/playbooks/foo.yaml/'])
        # the is file fails
        mock_isfile.return_value = False
        result = utils.get_validations_playbook('/foo/playbook',
                                                validation_id=['foo'])
        self.assertEqual(result, [])

    @mock.patch('os.path.isfile')
    @mock.patch('glob.glob')
    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_get_validations_playbook_by_id_group(self, mock_open, mock_load,
                                                  mock_glob, mock_isfile):
        mock_glob.side_effect = (['/foo/playbook/foo.yaml'], [])
        mock_isfile.return_value = True
        result = utils.get_validations_playbook('/foo/playbook', ['foo'], ['prep'])
        self.assertEqual(result, ['/foo/playbook/foo.yaml',
                                  '/foo/playbook/foo.yaml'])

    @mock.patch('os.path.isfile')
    @mock.patch('os.listdir')
    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_get_validations_playbook_group_not_exist(self, mock_open,
                                                      mock_load,
                                                      mock_listdir,
                                                      mock_isfile):
        mock_listdir.return_value = ['foo.yaml']
        mock_isfile.return_value = True
        result = utils.get_validations_playbook('/foo/playbook',
                                                groups=['no_group'])
        self.assertEqual(result, [])

    @mock.patch('os.path.isfile')
    @mock.patch('glob.glob')
    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_get_validations_playbook_by_category(self, mock_open, mock_load,
                                                  mock_glob, mock_isfile):
        mock_glob.side_effect = (['/foo/playbook/foo.yaml'], [])
        mock_isfile.return_value = True
        result = utils.get_validations_playbook('/foo/playbook',
                                                categories=['os', 'storage'])
        self.assertEqual(result, ['/foo/playbook/foo.yaml'])

    @mock.patch('os.path.isfile')
    @mock.patch('glob.glob')
    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_get_validations_playbook_by_product(self, mock_open, mock_load,
                                                 mock_glob, mock_isfile):
        mock_glob.side_effect = (['/foo/playbook/foo.yaml'], [])
        mock_isfile.return_value = True
        result = utils.get_validations_playbook('/foo/playbook',
                                                products=['product1'])
        self.assertEqual(result, ['/foo/playbook/foo.yaml'])

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_get_validation_parameters(self, mock_open, mock_load):

        result = utils.get_validation_parameters('/foo/playbook/foo.yaml')
        self.assertEqual(result, {})

    @mock.patch('yaml.safe_load', return_value=fakes.GROUP)
    @mock.patch('six.moves.builtins.open')
    def test_read_validation_groups_file(self, mock_open, mock_load):

        result = utils.read_validation_groups_file('/foo/groups.yaml')
        self.assertEqual(result, {'no-op': [{'description': 'noop-foo'}],
                                  'post': [{'description': 'post-foo'}],
                                  'pre': [{'description': 'pre-foo'}]})

    @mock.patch('yaml.safe_load', return_value=fakes.GROUP)
    @mock.patch('six.moves.builtins.open')
    def test_get_validation_group_name_list(self, mock_open, mock_load):

        result = utils.get_validation_group_name_list('/foo/groups.yaml')
        self.assertEqual(result, ['no-op', 'post', 'pre'])

    @mock.patch('validations_libs.utils.parse_all_validations_on_disk',
                return_value=[fakes.FAKE_METADATA])
    @mock.patch('yaml.safe_load', return_value=fakes.GROUP)
    @mock.patch('six.moves.builtins.open')
    def test_get_validations_details(self, mock_open, mock_load, mock_parse):

        result = utils.get_validations_details('foo')
        self.assertEqual(result, fakes.FAKE_METADATA)

    @mock.patch('six.moves.builtins.open')
    def test_get_validations_details_wrong_type(self, mock_open):
        validation = ['foo']
        self.assertRaises(TypeError,
                          utils.get_validations_details,
                          validation=validation)

    def test_get_validations_parameters_wrong_validations_data_type(self):
        self.assertRaises(TypeError,
                          utils.get_validations_parameters,
                          validations_data='/foo/playbook1.yaml')

    def test_get_validations_parameters_wrong_validation_name_type(self):
        self.assertRaises(TypeError,
                          utils.get_validations_parameters,
                          validations_data=['/foo/playbook1.yaml',
                                            '/foo/playbook2.yaml'],
                          validation_name='playbook1,playbook2')

    def test_get_validations_parameters_wrong_groups_type(self):
        self.assertRaises(TypeError,
                          utils.get_validations_parameters,
                          validations_data=['/foo/playbook1.yaml',
                                            '/foo/playbook2.yaml'],
                          groups='group1,group2')

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK2)
    @mock.patch('six.moves.builtins.open')
    def test_get_validations_parameters_no_group(self, mock_open, mock_load):

        result = utils.get_validations_parameters(['/foo/playbook/foo.yaml'],
                                                  ['foo'])
        output = {'foo': {'parameters': {'foo': 'bar'}}}
        self.assertEqual(result, output)

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK2)
    @mock.patch('six.moves.builtins.open')
    def test_get_validations_parameters_no_val(self, mock_open, mock_load):

        result = utils.get_validations_parameters(['/foo/playbook/foo.yaml'],
                                                  [], ['prep'])
        output = {'foo': {'parameters': {'foo': 'bar'}}}
        self.assertEqual(result, output)

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_get_validations_parameters_nothing(self, mock_open, mock_load):

        result = utils.get_validations_parameters(['/foo/playbook/foo.yaml'],
                                                  [], [])
        self.assertEqual(result, {})

    @mock.patch('validations_libs.utils.LOG', autospec=True)
    @mock.patch('validations_libs.utils.os.makedirs')
    @mock.patch(
        'validations_libs.utils.os.access',
        side_effect=[False, True])
    @mock.patch('validations_libs.utils.os.path.exists', return_value=True)
    def test_create_log_dir_access_issue(self, mock_exists,
                                         mock_access, mock_mkdirs,
                                         mock_log):
        log_path = utils.create_log_dir("/foo/bar")
        self.assertEqual(log_path, constants.VALIDATIONS_LOG_BASEDIR)

    @mock.patch('validations_libs.utils.LOG', autospec=True)
    @mock.patch(
        'validations_libs.utils.os.makedirs',
        side_effect=PermissionError)
    @mock.patch(
        'validations_libs.utils.os.access',
        autospec=True,
        return_value=True)
    @mock.patch(
        'validations_libs.utils.os.path.exists',
        autospec=True,
        side_effect=fakes._accept_default_log_path)
    def test_create_log_dir_existence_issue(self, mock_exists,
                                            mock_access, mock_mkdirs,
                                            mock_log):
        """Tests behavior after encountering non-existence
        of the the selected log folder, failed attempt to create it
        (raising PermissionError), and finally resorting to a fallback.
        """
        log_path = utils.create_log_dir("/foo/bar")
        self.assertEqual(log_path, constants.VALIDATIONS_LOG_BASEDIR)

    @mock.patch('validations_libs.utils.LOG', autospec=True)
    @mock.patch('validations_libs.utils.os.makedirs')
    @mock.patch('validations_libs.utils.os.access', return_value=True)
    @mock.patch('validations_libs.utils.os.path.exists', return_value=True)
    def test_create_log_dir_success(self, mock_exists,
                                    mock_access, mock_mkdirs,
                                    mock_log):
        """Test successful log dir retrieval on the first try.
        """
        log_path = utils.create_log_dir("/foo/bar")
        self.assertEqual(log_path, "/foo/bar")

    @mock.patch('validations_libs.utils.LOG', autospec=True)
    @mock.patch(
        'validations_libs.utils.os.makedirs',
        side_effect=PermissionError)
    @mock.patch('validations_libs.utils.os.access', return_value=False)
    @mock.patch('validations_libs.utils.os.path.exists', return_value=False)
    def test_create_log_dir_runtime_err(self, mock_exists,
                                        mock_access, mock_mkdirs,
                                        mock_log):
        """Test if failure of the fallback raises 'RuntimeError'
        """
        self.assertRaises(RuntimeError, utils.create_log_dir, "/foo/bar")

    @mock.patch('validations_libs.utils.LOG', autospec=True)
    @mock.patch(
        'validations_libs.utils.os.makedirs',
        side_effect=PermissionError)
    @mock.patch('validations_libs.utils.os.access', return_value=False)
    @mock.patch(
        'validations_libs.utils.os.path.exists',
        side_effect=fakes._accept_default_log_path)
    def test_create_log_dir_default_perms_runtime_err(
                                        self, mock_exists,
                                        mock_access, mock_mkdirs,
                                        mock_log):
        """Test if the inaccessible fallback raises 'RuntimeError'
        """
        self.assertRaises(RuntimeError, utils.create_log_dir, "/foo/bar")

    @mock.patch('validations_libs.utils.LOG', autospec=True)
    @mock.patch('validations_libs.utils.os.makedirs')
    @mock.patch('validations_libs.utils.os.access', return_value=False)
    @mock.patch('validations_libs.utils.os.path.exists', return_value=False)
    def test_create_log_dir_mkdirs(self, mock_exists,
                                   mock_access, mock_mkdirs,
                                   mock_log):
        """Test successful creation of the directory if the first access fails.
        """

        log_path = utils.create_log_dir("/foo/bar")
        self.assertEqual(log_path, "/foo/bar")

    @mock.patch(
        'validations_libs.utils.os.makedirs',
        side_effect=PermissionError)
    def test_create_artifacts_dir_runtime_err(self, mock_mkdirs):
        """Test if failure to create artifacts dir raises 'RuntimeError'.
        """
        self.assertRaises(RuntimeError, utils.create_artifacts_dir, "/foo/bar")

    def test_eval_types_str(self):
        self.assertIsInstance(utils._eval_types('/usr'), str)

    def test_eval_types_bool(self):
        self.assertIsInstance(utils._eval_types('True'), bool)

    def test_eval_types_int(self):
        self.assertIsInstance(utils._eval_types('15'), int)

    def test_eval_types_dict(self):
        self.assertIsInstance(utils._eval_types('{}'), dict)

    @mock.patch('os.path.exists', return_value=True)
    @mock.patch('configparser.ConfigParser.sections',
                return_value=['default'])
    def test_load_config(self, mock_config, mock_exists):
        results = utils.load_config('foo.cfg')
        self.assertEqual(results, {})

    def test_default_load_config(self):
        results = utils.load_config('validation.cfg')
        self.assertEqual(results['default'], fakes.DEFAULT_CONFIG)

    def test_ansible_runner_load_config(self):
        results = utils.load_config('validation.cfg')
        self.assertEqual(results['ansible_runner'],
                         fakes.ANSIBLE_RUNNER_CONFIG)

    def test_ansible_environment_config_load_config(self):
        results = utils.load_config('validation.cfg')
        self.assertEqual(
            results['ansible_environment']['ANSIBLE_CALLBACK_WHITELIST'],
            fakes.ANSIBLE_ENVIRONNMENT_CONFIG['ANSIBLE_CALLBACK_WHITELIST'])
        self.assertEqual(
            results['ansible_environment']['ANSIBLE_STDOUT_CALLBACK'],
            fakes.ANSIBLE_ENVIRONNMENT_CONFIG['ANSIBLE_STDOUT_CALLBACK'])

    @mock.patch('validations_libs.utils.LOG', autospec=True)
    @mock.patch('{}.Path.exists'.format(PATHLIB),
                return_value=False)
    @mock.patch('{}.Path.is_dir'.format(PATHLIB),
                return_value=False)
    @mock.patch('{}.Path.iterdir'.format(PATHLIB),
                return_value=iter([]))
    @mock.patch('{}.Path.mkdir'.format(PATHLIB))
    def test_check_creation_community_validations_dir(self, mock_mkdir,
                                                      mock_iterdir,
                                                      mock_isdir,
                                                      mock_exists,
                                                      mock_log):
        basedir = PosixPath('/foo/bar/community-validations')
        subdir = fakes.COVAL_SUBDIR
        result = utils.check_community_validations_dir(basedir, subdir)
        self.assertEqual(result,
                         [PosixPath('/foo/bar/community-validations'),
                          PosixPath("/foo/bar/community-validations/roles"),
                          PosixPath("/foo/bar/community-validations/playbooks"),
                          PosixPath("/foo/bar/community-validations/library"),
                          PosixPath("/foo/bar/community-validations/lookup_plugins")]
                         )

    @mock.patch('validations_libs.utils.LOG', autospec=True)
    @mock.patch('{}.Path.is_dir'.format(PATHLIB), return_value=True)
    @mock.patch('{}.Path.exists'.format(PATHLIB), return_value=True)
    @mock.patch('{}.Path.iterdir'.format(PATHLIB),
                return_value=fakes.FAKE_COVAL_MISSING_SUBDIR_ITERDIR1)
    @mock.patch('{}.Path.mkdir'.format(PATHLIB))
    def test_check_community_validations_dir_with_missing_subdir(self,
                                                                 mock_mkdir,
                                                                 mock_iterdir,
                                                                 mock_exists,
                                                                 mock_isdir,
                                                                 mock_log):
        basedir = PosixPath('/foo/bar/community-validations')
        subdir = fakes.COVAL_SUBDIR
        result = utils.check_community_validations_dir(basedir, subdir)
        self.assertEqual(result,
                         [PosixPath('/foo/bar/community-validations/library'),
                          PosixPath('/foo/bar/community-validations/lookup_plugins')])


class TestRunCommandAndLog(TestCase):
    def setUp(self):
        self.mock_logger = mock.Mock(spec=logging.Logger)

        self.mock_process = mock.Mock()
        self.mock_process.stdout.readline.side_effect = ['foo\n', 'bar\n']
        self.mock_process.wait.side_effect = [0]
        self.mock_process.returncode = 0

        mock_sub = mock.patch('subprocess.Popen',
                              return_value=self.mock_process)
        self.mock_popen = mock_sub.start()
        self.addCleanup(mock_sub.stop)

        self.cmd = ['exit', '0']
        self.e_cmd = ['exit', '1']
        self.log_calls = [mock.call('foo'),
                          mock.call('bar')]

    def test_success_default(self):
        retcode = utils.run_command_and_log(self.mock_logger, self.cmd)
        self.mock_popen.assert_called_once_with(self.cmd,
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.STDOUT,
                                                shell=False,
                                                cwd=None, env=None)
        self.assertEqual(retcode, 0)
        self.mock_logger.debug.assert_has_calls(self.log_calls,
                                                any_order=False)

    @mock.patch('subprocess.Popen')
    def test_error_subprocess(self, mock_popen):
        mock_process = mock.Mock()
        mock_process.stdout.readline.side_effect = ['Error\n']
        mock_process.wait.side_effect = [1]
        mock_process.returncode = 1

        mock_popen.return_value = mock_process

        retcode = utils.run_command_and_log(self.mock_logger, self.e_cmd)
        mock_popen.assert_called_once_with(self.e_cmd, stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT,
                                           shell=False, cwd=None,
                                           env=None)

        self.assertEqual(retcode, 1)
        self.mock_logger.debug.assert_called_once_with('Error')

    def test_success_env(self):
        test_env = os.environ.copy()
        retcode = utils.run_command_and_log(self.mock_logger, self.cmd,
                                            env=test_env)
        self.mock_popen.assert_called_once_with(self.cmd,
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.STDOUT,
                                                shell=False,
                                                cwd=None, env=test_env)
        self.assertEqual(retcode, 0)
        self.mock_logger.debug.assert_has_calls(self.log_calls,
                                                any_order=False)

    def test_success_cwd(self):
        test_cwd = '/usr/local/bin'
        retcode = utils.run_command_and_log(self.mock_logger, self.cmd,
                                            cwd=test_cwd)
        self.mock_popen.assert_called_once_with(self.cmd,
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.STDOUT,
                                                shell=False,
                                                cwd=test_cwd, env=None)
        self.assertEqual(retcode, 0)
        self.mock_logger.debug.assert_has_calls(self.log_calls,
                                                any_order=False)

    def test_success_no_retcode(self):
        run = utils.run_command_and_log(self.mock_logger, self.cmd,
                                        retcode_only=False)
        self.mock_popen.assert_called_once_with(self.cmd,
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.STDOUT,
                                                shell=False,
                                                cwd=None, env=None)
        self.assertEqual(run, self.mock_process)
        self.mock_logger.debug.assert_not_called()
