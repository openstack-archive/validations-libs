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
                  'Parameters': {}}
        res = utils.get_validations_data('512e')
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
        mock_glob.return_value = \
            ['/foo/playbook/foo.yaml']
        result = utils.parse_all_validations_on_disk('/foo/playbook')
        self.assertEqual(result, [fakes.FAKE_METADATA])

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
        mock_glob.return_value = \
            ['/foo/playbook/foo.yaml']
        result = utils.parse_all_validations_on_disk('/foo/playbook',
                                                     ['prep'])
        self.assertEqual(result, [fakes.FAKE_METADATA])

    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    @mock.patch('glob.glob')
    def test_parse_all_validations_on_disk_by_category(self, mock_glob,
                                                       mock_open,
                                                       mock_load):
        mock_glob.return_value = \
            ['/foo/playbook/foo.yaml']
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
        mock_glob.return_value = \
            ['/foo/playbook/foo.yaml']
        result = utils.parse_all_validations_on_disk('/foo/playbook',
                                                     products=['product1'])
        self.assertEqual(result, [fakes.FAKE_METADATA])

    @mock.patch('os.path.isfile')
    @mock.patch('os.listdir')
    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_get_validations_playbook_by_id(self, mock_open, mock_load,
                                            mock_listdir, mock_isfile):
        mock_listdir.return_value = ['foo.yaml']
        mock_isfile.return_value = True
        result = utils.get_validations_playbook('/foo/playbook',
                                                validation_id=['foo'])
        self.assertEqual(result, ['/foo/playbook/foo.yaml'])

    @mock.patch('os.path.isfile')
    @mock.patch('os.listdir')
    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_get_validations_playbook_by_id_group(self, mock_open, mock_load,
                                                  mock_listdir, mock_isfile):
        mock_listdir.return_value = ['foo.yaml']
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
    @mock.patch('os.listdir')
    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_get_validations_playbook_by_category(self, mock_open, mock_load,
                                                  mock_listdir, mock_isfile):
        mock_listdir.return_value = ['foo.yaml']
        mock_isfile.return_value = True
        result = utils.get_validations_playbook('/foo/playbook',
                                                categories=['os', 'storage'])
        self.assertEqual(result, ['/foo/playbook/foo.yaml'])

    @mock.patch('os.path.isfile')
    @mock.patch('os.listdir')
    @mock.patch('yaml.safe_load', return_value=fakes.FAKE_PLAYBOOK)
    @mock.patch('six.moves.builtins.open')
    def test_get_validations_playbook_by_product(self, mock_open, mock_load,
                                                 mock_listdir, mock_isfile):
        mock_listdir.return_value = ['foo.yaml']
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
