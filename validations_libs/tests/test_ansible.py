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

import pkg_resources
try:
    from unittest import mock
except ImportError:
    import mock
from unittest import TestCase
import os

from ansible_runner import Runner
from validations_libs import constants
from validations_libs.ansible import Ansible
from validations_libs.tests import fakes


try:
    version = pkg_resources.get_distribution("ansible_runner").version
    backward_compat = (version < '1.4.0')
except pkg_resources.DistributionNotFound:
    backward_compat = False

# NOTE(cloudnull): This is setting the FileExistsError for py2 environments.
#                  When we no longer support py2 (centos7) this should be
#                  removed.
try:
    FileExistsError = FileExistsError
except NameError:
    FileExistsError = OSError


class TestAnsible(TestCase):

    def setUp(self):
        """
        Initiates objects needed for testing. Most importantly the Ansible.
        Also replaces Ansible.log with a MagicMock to check against.
        """
        super(TestAnsible, self).setUp()
        self.unlink_patch = mock.patch('os.unlink')
        self.addCleanup(self.unlink_patch.stop)
        self.unlink_patch.start()
        self.run = Ansible()
        self.run.log = mock.MagicMock()

    @mock.patch('logging.getLogger')
    def test_ansible_init(self, mock_logger):
        """
        Test of Ansible init.
        Verifies that uuid atribute is properly set and that
        the logger has appropriate name assigned.
        """
        fake_uuid = 'foo'

        ansible = Ansible(fake_uuid)

        mock_logger.assert_called_once_with(
            'validations_libs.ansible.Ansible')

        self.assertEqual(fake_uuid, ansible.uuid)

    @mock.patch('os.path.exists', return_value=False)
    @mock.patch('ansible_runner.utils.dump_artifact', autospec=True,
                return_value="/foo/inventory.yaml")
    def test_check_no_playbook(self, mock_dump_artifact, mock_exists):
        """
        Checks if providing nonexistent playbook raises RuntimeError.
        Checks if os.path.exists is called both with name of the play file
        and with the path consisting of playbook and directory.
        Insists on order of the calls.
        Allows additional calls both before and after the required sequence.
        """
        self.assertRaises(
            RuntimeError,
            self.run.run,
            'non-existing.yaml',
            'localhost,',
            '/tmp'
        )

        exists_calls = [
            mock.call('non-existing.yaml'),
            mock.call('/tmp/non-existing.yaml')
        ]

        mock_exists.assert_has_calls(exists_calls)

    @mock.patch('os.path.abspath', return_value='/absolute/path/foo')
    @mock.patch('os.path.exists', return_value=True)
    def test_inventory_string_inventory(self, mock_exists, mock_abspath):
        """
        This test verifies that Ansible._inventory method properly handles
        valid inventory file paths.
        """
        inventory = 'foo'
        artifact_dir = 'bar'

        self.assertEqual(
            '/absolute/path/foo',
            self.run._inventory(inventory, artifact_dir))

        mock_exists.assert_called_once_with(inventory)
        mock_abspath.assert_called_once_with(inventory)

    @mock.patch('ansible_runner.utils.dump_artifact')
    def test_inventory_wrong_inventory_path(self, mock_dump_artifact):
        """
        Test verifies that Ansible._inventory method calls dump_artifact,
        if supplied by path to a nonexistent inventory file.
        """
        inventory = 'foo'
        artifact_dir = 'bar'

        self.run._inventory(inventory, artifact_dir)

        mock_dump_artifact.assert_called_once_with(
            inventory,
            artifact_dir,
            'hosts')

    @mock.patch('ansible_runner.utils.dump_artifact')
    @mock.patch('yaml.safe_dump', return_value='foobar')
    def test_inventory_dict_inventory(self, mock_yaml_dump,
                                      mock_dump_artifact):
        """
        Test verifies that Ansible._inventory method properly handles
        inventories provided as dict.
        """
        inventory = {
            'foo': 'bar'
        }
        artifact_dir = 'fizz'

        self.run._inventory(inventory, artifact_dir)

        mock_yaml_dump.assert_called_once_with(
            inventory,
            default_flow_style=False)

        mock_dump_artifact.assert_called_once_with(
            'foobar',
            artifact_dir,
            'hosts')

    @mock.patch('os.makedirs')
    @mock.patch('tempfile.gettempdir', return_value='/tmp')
    def test_creates_ansible_fact_dir_success(self, mock_get_temp_dir,
                                              mock_mkdirs):
        full_tmp_path = '/tmp/foo/fact_cache'

        self.assertEqual(
            full_tmp_path,
            self.run._creates_ansible_fact_dir('foo'))

        mock_mkdirs.assert_called_once_with(full_tmp_path)

    @mock.patch('os.makedirs', side_effect=FileExistsError())
    @mock.patch('tempfile.gettempdir', return_value='/tmp')
    def test_creates_ansible_fact_dir_exception(self, mock_get_temp_dir,
                                                mock_mkdirs):
        self.run._creates_ansible_fact_dir('foo')
        self.run.log.debug.assert_called_once_with(
            'Directory "{}" was not created because it'
            ' already exists.'.format(
                '/tmp/foo/fact_cache'
            ))

    def test_ansible_env_var_with_community_validations(self):
        # AP No config file (use the default True)
        env = self.run._ansible_env_var(
                output_callback="", ssh_user="", workdir="", connection="",
                gathering_policy="", module_path="", key="",
                extra_env_variables="", ansible_timeout="",
                callback_whitelist="", base_dir="", python_interpreter="",
                env={}, validation_cfg_file=None)

        assert("{}:".format(constants.COMMUNITY_LIBRARY_DIR) in env["ANSIBLE_LIBRARY"])
        assert("{}:".format(constants.COMMUNITY_ROLES_DIR) in env["ANSIBLE_ROLES_PATH"])
        assert("{}:".format(constants.COMMUNITY_LOOKUP_DIR) in env["ANSIBLE_LOOKUP_PLUGINS"])

        # AP config file with no settting (use the default True)
        env = self.run._ansible_env_var(
                output_callback="", ssh_user="", workdir="", connection="",
                gathering_policy="", module_path="", key="",
                extra_env_variables="", ansible_timeout="",
                callback_whitelist="", base_dir="", python_interpreter="",
                env={}, validation_cfg_file={"default": {}})

        assert("{}:".format(constants.COMMUNITY_LIBRARY_DIR) in env["ANSIBLE_LIBRARY"])
        assert("{}:".format(constants.COMMUNITY_ROLES_DIR) in env["ANSIBLE_ROLES_PATH"])
        assert("{}:".format(constants.COMMUNITY_LOOKUP_DIR) in env["ANSIBLE_LOOKUP_PLUGINS"])

        # AP config file with settting True
        env = self.run._ansible_env_var(
                output_callback="", ssh_user="", workdir="", connection="",
                gathering_policy="", module_path="", key="",
                extra_env_variables="", ansible_timeout="",
                callback_whitelist="", base_dir="", python_interpreter="",
                env={}, validation_cfg_file={"default": {"enable_community_validations": True}})

        assert("{}:".format(constants.COMMUNITY_LIBRARY_DIR) in env["ANSIBLE_LIBRARY"])
        assert("{}:".format(constants.COMMUNITY_ROLES_DIR) in env["ANSIBLE_ROLES_PATH"])
        assert("{}:".format(constants.COMMUNITY_LOOKUP_DIR) in env["ANSIBLE_LOOKUP_PLUGINS"])

    def test_ansible_env_var_without_community_validations(self):
        # AP config file with settting False
        env = self.run._ansible_env_var(
                output_callback="", ssh_user="", workdir="", connection="",
                gathering_policy="", module_path="", key="",
                extra_env_variables="", ansible_timeout="",
                callback_whitelist="", base_dir="", python_interpreter="",
                env={}, validation_cfg_file={"default": {"enable_community_validations": False}})

        assert("{}:".format(constants.COMMUNITY_LIBRARY_DIR) not in env["ANSIBLE_LIBRARY"])
        assert("{}:".format(constants.COMMUNITY_ROLES_DIR) not in env["ANSIBLE_ROLES_PATH"])
        assert("{}:".format(constants.COMMUNITY_LOOKUP_DIR) not in env["ANSIBLE_LOOKUP_PLUGINS"])

    def test_get_extra_vars_dict(self):
        extra_vars = {
            'foo': 'bar'
        }

        self.assertEqual(extra_vars, self.run._get_extra_vars(extra_vars))

    @mock.patch('yaml.safe_load', return_value={'fizz': 'buzz'})
    @mock.patch('builtins.open', spec=open)
    @mock.patch('os.path.exists', return_value=True)
    @mock.patch('os.path.isfile', return_value=True)
    def test_get_extra_vars_path(self, mock_isfile,
                                 mock_exists,
                                 mock_open,
                                 mock_yaml_load):

        self.assertEqual(
            {'fizz': 'buzz'},
            self.run._get_extra_vars('/foo/bar'))

        mock_open.assert_called_once_with('/foo/bar')

    @mock.patch('builtins.open')
    @mock.patch('os.path.exists', return_value=True)
    @mock.patch('os.makedirs')
    @mock.patch.object(
        Runner,
        'run',
        return_value=fakes.fake_ansible_runner_run_return(rc=1,
                                                          status='failed')
    )
    @mock.patch('ansible_runner.utils.dump_artifact', autospec=True,
                return_value="/foo/inventory.yaml")
    @mock.patch('ansible_runner.runner_config.RunnerConfig')
    def test_ansible_runner_error(self, mock_config, mock_dump_artifact,
                                  mock_run, mock_mkdirs, mock_exists,
                                  mock_open):

        _playbook, _rc, _status = self.run.run('existing.yaml',
                                               'localhost,',
                                               '/tmp')
        self.assertEqual((_playbook, _rc, _status),
                         ('existing.yaml', 1, 'failed'))

    @mock.patch('builtins.open')
    @mock.patch('os.path.exists', return_value=True)
    @mock.patch('os.makedirs')
    @mock.patch.object(Runner, 'run',
                       return_value=fakes.fake_ansible_runner_run_return(rc=0))
    @mock.patch('ansible_runner.utils.dump_artifact', autospec=True,
                return_value="/foo/inventory.yaml")
    @mock.patch('ansible_runner.runner_config.RunnerConfig')
    def test_run_success_default(self, mock_config, mock_dump_artifact,
                                 mock_run, mock_mkdirs, mock_exists,
                                 mock_open):
        _playbook, _rc, _status = self.run.run(
            playbook='existing.yaml',
            inventory='localhost,',
            workdir='/tmp'
        )
        self.assertEqual((_playbook, _rc, _status),
                         ('existing.yaml', 0, 'successful'))

    @mock.patch('builtins.open')
    @mock.patch('os.path.exists', return_value=True)
    @mock.patch('os.makedirs')
    @mock.patch.object(Runner, 'run',
                       return_value=fakes.fake_ansible_runner_run_return(rc=0))
    @mock.patch('ansible_runner.utils.dump_artifact', autospec=True,
                return_value="/foo/inventory.yaml")
    @mock.patch('ansible_runner.runner_config.RunnerConfig')
    def test_run_success_gathering_policy(self, mock_config,
                                          mock_dump_artifact, mock_run,
                                          mock_mkdirs, mock_exists,
                                          mock_open):
        _playbook, _rc, _status = self.run.run(
            playbook='existing.yaml',
            inventory='localhost,',
            workdir='/tmp',
            connection='local',
            gathering_policy='smart'
        )
        self.assertEqual((_playbook, _rc, _status),
                         ('existing.yaml', 0, 'successful'))

    @mock.patch('os.path.exists', return_value=True)
    @mock.patch('os.makedirs')
    @mock.patch.object(Runner, 'run',
                       return_value=fakes.fake_ansible_runner_run_return(rc=0))
    @mock.patch('ansible_runner.utils.dump_artifact', autospec=True,
                return_value="/foo/inventory.yaml")
    @mock.patch('builtins.open')
    @mock.patch('ansible_runner.runner_config.RunnerConfig')
    def test_run_success_local(self, mock_config, mock_open,
                               mock_dump_artifact, mock_run,
                               mock_mkdirs, mock_exists
                               ):
        _playbook, _rc, _status = self.run.run(
            playbook='existing.yaml',
            inventory='localhost,',
            workdir='/tmp',
            connection='local'
        )
        self.assertEqual((_playbook, _rc, _status),
                         ('existing.yaml', 0, 'successful'))

    @mock.patch('os.path.exists', return_value=True)
    @mock.patch('os.makedirs')
    @mock.patch.object(Runner, 'run',
                       return_value=fakes.fake_ansible_runner_run_return(rc=0))
    @mock.patch('ansible_runner.utils.dump_artifact', autospec=True,
                return_value="/foo/inventory.yaml")
    @mock.patch('builtins.open')
    @mock.patch('ansible_runner.runner_config.RunnerConfig')
    def test_run_success_run_async(self, mock_config, mock_open,
                                   mock_dump_artifact, mock_run,
                                   mock_mkdirs, mock_exists
                                   ):
        _playbook, _rc, _status = self.run.run(
            playbook='existing.yaml',
            inventory='localhost,',
            workdir='/tmp',
            connection='local',
            run_async=True
        )
        self.assertEqual((_playbook, _rc, _status),
                         ('existing.yaml', None, 'unstarted'))

    @mock.patch('builtins.open')
    @mock.patch('os.path.exists', return_value=True)
    @mock.patch('os.makedirs')
    @mock.patch.object(Runner, 'run',
                       return_value=fakes.fake_ansible_runner_run_return(rc=0))
    @mock.patch('ansible_runner.utils.dump_artifact', autospec=True,
                return_value="/foo/inventory.yaml")
    @mock.patch('ansible_runner.runner_config.RunnerConfig')
    @mock.patch('validations_libs.ansible.Ansible._ansible_env_var',
                return_value={'ANSIBLE_STDOUT_CALLBACK': 'fake'})
    @mock.patch('os.environ.copy', return_value={})
    @mock.patch('os.path.abspath', return_value='/tmp/foo/localhost')
    def test_run_specific_log_path(self, mock_path, mock_env, mock_env_var,
                                   mock_config, mock_dump_artifact, mock_run,
                                   mock_mkdirs, mock_exists, mock_open):
        _playbook, _rc, _status = self.run.run(
            playbook='existing.yaml',
            inventory='localhost,',
            workdir='/tmp',
            log_path='/tmp/foo'
        )

        opt = {
            'artifact_dir': '/tmp',
            'extravars': {},
            'ident': '',
            'inventory': '/tmp/foo/localhost',
            'playbook': 'existing.yaml',
            'private_data_dir': '/tmp',
            'quiet': False,
            'rotate_artifacts': 256,
            'verbosity': 0}

        if not backward_compat:
            opt.update({
                'envvars': {
                    'ANSIBLE_STDOUT_CALLBACK': 'fake',
                    'ANSIBLE_CONFIG': '/tmp/foo/artifacts/ansible.cfg',
                    'VALIDATIONS_LOG_DIR': '/tmp/foo'},
                'project_dir': '/tmp',
                'fact_cache': '/tmp/foo/artifacts/',
                'fact_cache_type': 'jsonfile'
                })

        mock_config.assert_called_once_with(**opt)

    @mock.patch('os.path.exists', return_value=True)
    @mock.patch('os.makedirs')
    @mock.patch.object(Runner, 'run',
                       return_value=fakes.fake_ansible_runner_run_return(rc=0))
    @mock.patch('ansible_runner.utils.dump_artifact', autospec=True,
                return_value="/foo/inventory.yaml")
    @mock.patch('builtins.open')
    @mock.patch('ansible_runner.runner_config.RunnerConfig')
    def test_run_success_with_config(self, mock_config, mock_open,
                                     mock_dump_artifact, mock_run,
                                     mock_mkdirs, mock_exists
                                     ):
        fake_config = {'default': fakes.DEFAULT_CONFIG,
                       'ansible_environment':
                       fakes.ANSIBLE_ENVIRONNMENT_CONFIG,
                       'ansible_runner': fakes.ANSIBLE_RUNNER_CONFIG
                       }
        _playbook, _rc, _status = self.run.run(
            playbook='existing.yaml',
            inventory='localhost,',
            workdir='/tmp',
            connection='local',
            ansible_artifact_path='/tmp',
            validation_cfg_file=fake_config
        )
        self.assertEqual((_playbook, _rc, _status),
                         ('existing.yaml', 0, 'successful'))
        mock_open.assert_called_with('/tmp/validation.cfg', 'w')

    @mock.patch('os.path.exists', return_value=True)
    @mock.patch('os.makedirs')
    @mock.patch.object(Runner, 'run',
                       return_value=fakes.fake_ansible_runner_run_return(rc=0))
    @mock.patch('ansible_runner.utils.dump_artifact', autospec=True,
                return_value="/foo/inventory.yaml")
    @mock.patch('builtins.open')
    @mock.patch('ansible_runner.runner_config.RunnerConfig')
    def test_run_success_with_empty_config(self, mock_config, mock_open,
                                           mock_dump_artifact, mock_run,
                                           mock_mkdirs, mock_exists
                                           ):
        fake_config = {}
        _playbook, _rc, _status = self.run.run(
            playbook='existing.yaml',
            inventory='localhost,',
            workdir='/tmp',
            connection='local',
            ansible_cfg_file='/foo.cfg',
            ansible_artifact_path='/tmp',
            validation_cfg_file=fake_config
        )
        self.assertEqual((_playbook, _rc, _status),
                         ('existing.yaml', 0, 'successful'))
        mock_open.assert_not_called()

    @mock.patch('os.path.exists', return_value=True)
    @mock.patch('os.makedirs')
    @mock.patch.object(Runner, 'run',
                       return_value=fakes.fake_ansible_runner_run_return(rc=0))
    @mock.patch('ansible_runner.utils.dump_artifact', autospec=True,
                return_value="/foo/inventory.yaml")
    @mock.patch('builtins.open')
    @mock.patch('ansible_runner.runner_config.RunnerConfig')
    def test_run_success_with_ansible_config(self, mock_config, mock_open,
                                             mock_dump_artifact, mock_run,
                                             mock_mkdirs, mock_exists
                                             ):
        fake_config = {}
        _playbook, _rc, _status = self.run.run(
            playbook='existing.yaml',
            inventory='localhost,',
            workdir='/tmp',
            connection='local',
            ansible_artifact_path='/tmp',
            validation_cfg_file=fake_config
        )
        self.assertEqual((_playbook, _rc, _status),
                         ('existing.yaml', 0, 'successful'))
        mock_open.assert_called_with('/tmp/ansible.cfg', 'w')

    @mock.patch('builtins.open')
    @mock.patch('os.path.exists', return_value=True)
    @mock.patch.object(
        Runner,
        'run',
        return_value=fakes.fake_ansible_runner_run_return(rc=0))
    @mock.patch(
        'ansible_runner.utils.dump_artifact',
        autospec=True,
        return_value="/foo/inventory.yaml")
    @mock.patch('ansible_runner.runner_config.RunnerConfig')
    @mock.patch(
        'validations_libs.ansible.Ansible._ansible_env_var',
        return_value={'ANSIBLE_STDOUT_CALLBACK': 'fake'})
    @mock.patch('os.path.abspath', return_value='/tmp/foo/localhost')
    @mock.patch('os.environ.copy', return_value={})
    def test_run_no_log_path(self, mock_env, mock_path,
                             mock_env_var, mock_config,
                             mock_dump_artifact, mock_run,
                             mock_exists, mock_open):
        """
        Tests if leaving default (None) log_path appropriately sets
        'ANSIBLE_CONFIG' and 'fact_cache' envvars,
        using constants.constants.VALIDATION_ANSIBLE_ARTIFACT_PATH.
        Bulk of the mocks are only for purposes of convenience.

        Assertions:
            Presence of key: value pairs.
        """
        _playbook, _rc, _status = self.run.run(
            playbook='existing.yaml',
            inventory='localhost,',
            workdir='/tmp')

        opt = {
            'artifact_dir': '/tmp',
            'extravars': {},
            'ident': '',
            'inventory': '/tmp/foo/localhost',
            'playbook': 'existing.yaml',
            'private_data_dir': '/tmp',
            'quiet': False,
            'rotate_artifacts': 256,
            'verbosity': 0}

        if not backward_compat:
            opt.update({
                'envvars': {
                    'ANSIBLE_STDOUT_CALLBACK': 'fake',
                    'ANSIBLE_CONFIG': os.path.join(
                        constants.VALIDATION_ANSIBLE_ARTIFACT_PATH,
                        'ansible.cfg')},
                'project_dir': '/tmp',
                'fact_cache': constants.VALIDATION_ANSIBLE_ARTIFACT_PATH,
                'fact_cache_type': 'jsonfile'})

        mock_config.assert_called_once_with(**opt)

    @mock.patch('builtins.open')
    @mock.patch('os.path.exists', return_value=True)
    @mock.patch.object(
        Runner,
        'run',
        return_value=fakes.fake_ansible_runner_run_return(rc=0))
    @mock.patch(
        'ansible_runner.utils.dump_artifact',
        autospec=True,
        return_value="/foo/inventory.yaml")
    @mock.patch('ansible_runner.runner_config.RunnerConfig')
    @mock.patch(
        'validations_libs.ansible.Ansible._ansible_env_var',
        return_value={'ANSIBLE_STDOUT_CALLBACK': 'fake'})
    @mock.patch('os.path.abspath', return_value='/tmp/foo/localhost')
    @mock.patch('os.environ.copy', return_value={})
    def test_run_tags(self, mock_env, mock_path,
                      mock_env_var, mock_config,
                      mock_dump_artifact, mock_run,
                      mock_exists, mock_open):
        """
        Tests if specifying tags appropriately sets
        'tags' envvar, passed as dict entry to RunnerConfig.
        Bulk of the mocks are only for purposes of convenience.

        Assertions:
            Presence of key: value pairs.
        """
        tags = ','.join(['master', 'train', 'fake'])

        _playbook, _rc, _status = self.run.run(
            playbook='existing.yaml',
            inventory='localhost,',
            workdir='/tmp',
            log_path='/tmp/foo',
            tags=tags)

        opt = {
        'artifact_dir': '/tmp',
        'extravars': {},
        'ident': '',
        'inventory': '/tmp/foo/localhost',
        'playbook': 'existing.yaml',
        'private_data_dir': '/tmp',
        'quiet': False,
        'rotate_artifacts': 256,
        'verbosity': 0,
        'tags': tags}

        if not backward_compat:
            opt.update({
                'envvars': {
                    'ANSIBLE_STDOUT_CALLBACK': 'fake',
                    'ANSIBLE_CONFIG': '/tmp/foo/artifacts/ansible.cfg',
                    'VALIDATIONS_LOG_DIR': '/tmp/foo'},
                'project_dir': '/tmp',
                'fact_cache': '/tmp/foo/artifacts/',
                'fact_cache_type': 'jsonfile'})

        mock_config.assert_called_once_with(**opt)

    @mock.patch('builtins.open')
    @mock.patch('os.path.exists', return_value=True)
    @mock.patch.object(
        Runner,
        'run',
        return_value=fakes.fake_ansible_runner_run_return(rc=0))
    @mock.patch('ansible_runner.runner_config.RunnerConfig')
    @mock.patch(
        'validations_libs.ansible.Ansible._encode_envvars',
        return_value={
            'ANSIBLE_STDOUT_CALLBACK': 'fake',
            'ANSIBLE_CALLBACK_WHITELIST': 'fake,validation_json,profile_tasks',
            'ANSIBLE_CONFIG': os.path.join(
                constants.VALIDATION_ANSIBLE_ARTIFACT_PATH,
                'ansible.cfg')})
    @mock.patch(
        'os.environ.copy',
        return_value={'ANSIBLE_STDOUT_CALLBACK': 'fake'})
    @mock.patch('os.path.abspath', return_value='/tmp/foo/localhost')
    def test_run_ansible_playbook_dir(self, mock_path, mock_env,
                                      mock_encode_envvars,
                                      mock_config, mock_run,
                                      mock_exists, mock_open):
        """
        Tests if leaving default (None) log_path and setting playbook_dir
        appropriately sets 'project_dir' value in r_opts dict.
        Bulk of the mocks are only for purposes of convenience.

        Assertions:
            Presence of key: value pairs.
        """
        _playbook, _rc, _status = self.run.run(
            playbook='existing.yaml',
            inventory='localhost,',
            workdir='/tmp',
            playbook_dir='/tmp/fake_playbooks')

        opt = {
            'artifact_dir': '/tmp',
            'extravars': {},
            'ident': '',
            'inventory': '/tmp/foo/localhost',
            'playbook': 'existing.yaml',
            'private_data_dir': '/tmp',
            'quiet': False,
            'rotate_artifacts': 256,
            'verbosity': 0}

        if not backward_compat:
            opt.update({
                'envvars': {
                    'ANSIBLE_STDOUT_CALLBACK': 'fake',
                    'ANSIBLE_CONFIG': os.path.join(
                        constants.VALIDATION_ANSIBLE_ARTIFACT_PATH,
                        'ansible.cfg'),
                    'ANSIBLE_CALLBACK_WHITELIST': 'fake,validation_json,profile_tasks'
                    },
                'project_dir': '/tmp/fake_playbooks',
                'fact_cache': constants.VALIDATION_ANSIBLE_ARTIFACT_PATH,
                'fact_cache_type': 'jsonfile'})

        mock_config.assert_called_once_with(**opt)

    @mock.patch('builtins.open')
    @mock.patch('os.path.exists', return_value=True)
    @mock.patch.object(
        Runner,
        'run',
        return_value=fakes.fake_ansible_runner_run_return(rc=0))
    @mock.patch('ansible_runner.runner_config.RunnerConfig')
    @mock.patch(
        'validations_libs.ansible.Ansible._ansible_env_var',
        return_value={
            'ANSIBLE_STDOUT_CALLBACK': 'fake',
            'ANSIBLE_CALLBACK_WHITELIST': 'log_plays,mail,fake,validation_json,profile_tasks'
            })
    @mock.patch('os.environ.copy', return_value={})
    def test_run_callback_whitelist_extend(self, mock_env,
                                           mock_env_var, mock_config,
                                           mock_run, mock_exists,
                                           mock_open):
        """Tests if Ansible._callbacks method appropriately constructs callback_whitelist,
        when provided explicit whitelist and output_callback.
        Bulk of the mocks are only for purposes of convenience.

        Assertions:
            Presence of key: value pairs.
        """
        _playbook, _rc, _status = self.run.run(
            ssh_user='root',
            playbook='existing.yaml',
            inventory='localhost,',
            workdir='/tmp',
            log_path='/tmp/foo',
            output_callback='fake',
            callback_whitelist='log_plays,mail')

        args = {
            'output_callback': 'fake',
            'ssh_user': 'root',
            'workdir': '/tmp',
            'connection': 'smart',
            'gathering_policy': 'smart',
            'module_path': None,
            'key': None,
            'extra_env_variables': None,
            'ansible_timeout': 30,
            'callback_whitelist': 'log_plays,mail,fake,profile_tasks,vf_validation_json',
            'base_dir': '/usr/share/ansible',
            'python_interpreter': None}

        #Specific form of Ansible.env_var neccessiates convoluted arg unpacking.
        mock_env_var.assert_called_once_with(*args.values(), validation_cfg_file=None)

    @mock.patch('builtins.open')
    @mock.patch('os.path.exists', return_value=True)
    @mock.patch.object(
        Runner,
        'run',
        return_value=fakes.fake_ansible_runner_run_return(rc=0))
    @mock.patch('ansible_runner.runner_config.RunnerConfig')
    @mock.patch(
        'validations_libs.ansible.Ansible._ansible_env_var',
        return_value={
            'ANSIBLE_STDOUT_CALLBACK': 'fake',
            'ANSIBLE_CALLBACK_WHITELIST': 'fake,validation_json,profile_tasks'
            })
    @mock.patch('os.environ.copy', return_value={})
    def test_run_callback_whitelist_none(self, mock_env,
                                         mock_env_var, mock_config,
                                         mock_run, mock_exists,
                                         mock_open):
        """Tests if Ansible._callbacks method appropriately constructs callback_whitelist,
        when provided default (None) whitelist and specific output_callback.
        Bulk of the mocks are only for purposes of convenience.

        Assertions:
            Presence of key: value pairs.
        """
        _playbook, _rc, _status = self.run.run(
            ssh_user='root',
            playbook='existing.yaml',
            inventory='localhost,',
            workdir='/tmp',
            log_path='/tmp/foo',
            output_callback='fake')

        args = {
            'output_callback': 'fake',
            'ssh_user': 'root',
            'workdir': '/tmp',
            'connection': 'smart',
            'gathering_policy': 'smart',
            'module_path': None,
            'key': None,
            'extra_env_variables': None,
            'ansible_timeout': 30,
            'callback_whitelist': 'fake,profile_tasks,vf_validation_json',
            'base_dir': '/usr/share/ansible',
            'python_interpreter': None}

        #Specific form of Ansible.env_var neccessiates convoluted arg unpacking.
        mock_env_var.assert_called_once_with(*args.values(), validation_cfg_file=None)

    @mock.patch('builtins.open')
    @mock.patch('os.path.exists', return_value=True)
    @mock.patch.object(
        Runner,
        'run',
        return_value=fakes.fake_ansible_runner_run_return(rc=0))
    @mock.patch('ansible_runner.runner_config.RunnerConfig')
    @mock.patch(
        'validations_libs.ansible.Ansible._ansible_env_var',
        return_value={
            'ANSIBLE_STDOUT_CALLBACK': 'different_fake',
            'ANSIBLE_CALLBACK_WHITELIST': 'different_fake,validation_json,profile_tasks'
            })
    @mock.patch(
        'os.environ.copy',
        return_value={'ANSIBLE_STDOUT_CALLBACK': 'different_fake'})
    def test_run_callback_precedence(self, mock_env,
                                     mock_env_var, mock_config,
                                     mock_run, mock_exists, mock_open):
        """Tests if Ansible._callbacks method reaches for output_callback
        if and only if env dict doesn't contain 'ANSIBLE_STDOUT_CALLBACK' key.
        Bulk of the mocks are only for purposes of convenience.

        Assertions:
            Presence of key: value pairs.
        """
        _playbook, _rc, _status = self.run.run(
            ssh_user='root',
            playbook='existing.yaml',
            inventory='localhost,',
            workdir='/tmp',
            log_path='/tmp/foo',
            output_callback='fake')

        args = {
            'output_callback': 'different_fake',
            'ssh_user': 'root',
            'workdir': '/tmp',
            'connection': 'smart',
            'gathering_policy': 'smart',
            'module_path': None,
            'key': None,
            'extra_env_variables': None,
            'ansible_timeout': 30,
            'callback_whitelist': 'different_fake,profile_tasks,vf_validation_json',
            'base_dir': '/usr/share/ansible',
            'python_interpreter': None}

        #Specific form of Ansible.env_var neccessiates convoluted arg unpacking.
        mock_env_var.assert_called_once_with(*args.values(), validation_cfg_file=None)

    @mock.patch('builtins.open')
    @mock.patch('os.path.exists', return_value=True)
    @mock.patch.object(
        Runner,
        'run',
        return_value=fakes.fake_ansible_runner_run_return(rc=0))
    @mock.patch('ansible_runner.runner_config.RunnerConfig')
    @mock.patch(
        'validations_libs.ansible.Ansible._ansible_env_var',
        return_value={
            'ANSIBLE_STDOUT_CALLBACK': 'fake',
            'ANSIBLE_CALLBACK_WHITELIST': 'fake,validation_json,profile_tasks'
            })
    @mock.patch(
        'os.environ.copy',
        return_value={'ANSIBLE_STDOUT_CALLBACK': 'fake'})
    def test_run_ansible_artifact_path_set(self, mock_env,
                                           mock_env_var, mock_config,
                                           mock_run, mock_exists, mock_open):
        """Tests if specified 'ansible_artifact_path' is passed in a valid
        and unchanged form to RunnerConfig as value of 'fact_cache' param.
        Additional assertion on number of calls is placed,
        to ensure that RunnerConfig is called only once.
        Otherwise followup assertions could fail.

        Assertions:
            Validity of specified path in filesystem:
                os.lstat raises FileNotFoundError only if specified path is valid,
                but does not exist in current filesystem.

            Passing of specified value (ansible_artifact_path) to RunnerConfig.
        """
        _playbook, _rc, _status = self.run.run(
            playbook='existing.yaml',
            inventory='localhost,',
            workdir='/tmp',
            log_path='/tmp/foo',
            output_callback='fake',
            ansible_artifact_path='/tmp/artifact/path')

        mock_config.assert_called_once()

        """Is the path even valid in our filesystem? Index 1 stands for kwargs in py<=36.
        os.lstat raises FileNotFoundError only if specified path is valid,
        but does not exist in current filesystem.
        """
        self.assertRaises(FileNotFoundError, os.lstat, mock_config.call_args[1]['fact_cache'])

        self.assertTrue('/tmp/artifact/path' in mock_config.call_args[1]['fact_cache'])

    @mock.patch('builtins.open')
    @mock.patch('os.path.exists', return_value=True)
    @mock.patch.object(
        Runner,
        'run',
        return_value=fakes.fake_ansible_runner_run_return(rc=0))
    @mock.patch('ansible_runner.runner_config.RunnerConfig')
    @mock.patch(
        'validations_libs.ansible.Ansible._ansible_env_var',
        return_value={
            'ANSIBLE_STDOUT_CALLBACK': 'fake',
            'ANSIBLE_CALLBACK_WHITELIST': 'fake,validation_json,profile_tasks'
            })
    @mock.patch(
        'os.environ.copy',
        return_value={'ANSIBLE_STDOUT_CALLBACK': 'fake'})
    def test_run_ansible_artifact_path_from_log_path(self, mock_env,
                                                     mock_env_var, mock_config,
                                                     mock_run, mock_exists, mock_open):
        """Tests if specified 'log_path' is passed in a valid
        and unchanged form to RunnerConfig as value of 'fact_cache' param,
        in absence of specified 'ansible_artifact_path'.
        Additional assertion on number of calls is placed,
        to ensure that RunnerConfig is called only once.
        Otherwise followup assertions could fail.

        Assertions:
            Validity of specified path in filesystem.:
                os.lstat raises FileNotFoundError only if specified path is valid,
                but does not exist in current filesystem.

            Passing of specified value (log_path) to RunnerConfig.
        """
        _playbook, _rc, _status = self.run.run(
            playbook='existing.yaml',
            inventory='localhost,',
            workdir='/tmp',
            log_path='/tmp/foo',
            output_callback='fake')

        mock_config.assert_called_once()
        """Is the path even valid in our filesystem? Index 1 stands for kwargs in py<=36.
        os.lstat raises FileNotFoundError only if specified path is valid,
        but does not exist in current filesystem.
        """
        self.assertRaises(FileNotFoundError, os.lstat, mock_config.call_args[1]['fact_cache'])

        self.assertTrue('/tmp/foo' in mock_config.call_args[1]['fact_cache'])

    @mock.patch.object(
        constants,
        'VALIDATION_ANSIBLE_ARTIFACT_PATH',
        new='foo/bar')
    @mock.patch('builtins.open')
    @mock.patch('os.path.exists', return_value=True)
    @mock.patch.object(
        Runner,
        'run',
        return_value=fakes.fake_ansible_runner_run_return(rc=0))
    @mock.patch('ansible_runner.runner_config.RunnerConfig')
    @mock.patch(
        'validations_libs.ansible.Ansible._ansible_env_var',
        return_value={
            'ANSIBLE_STDOUT_CALLBACK': 'fake',
            'ANSIBLE_CALLBACK_WHITELIST': 'fake,validation_json,profile_tasks',
            })
    @mock.patch(
        'os.environ.copy',
        return_value={'ANSIBLE_STDOUT_CALLBACK': 'fake'})
    def test_run_ansible_artifact_path_from_constants(self, mock_env,
                                                      mock_env_var, mock_config,
                                                      mock_run, mock_exists,
                                                      mock_open):
        """Tests if 'constants.constants.VALIDATION_ANSIBLE_ARTIFACT_PATH' passed in a valid
        and unchanged form to RunnerConfig as value of 'fact_cache' param,
        in absence of specified 'ansible_artifact_path' or 'log_path'.
        Additional assertion on number of calls is placed,
        to ensure that RunnerConfig is called only once.
        Otherwise followup assertions could fail.

        Assertions:
            Validity of specified path in filesystem.:
                os.lstat raises FileNotFoundError only if specified path is valid,
                but does not exist in current filesystem.

            Passing of specified value (log_path) to RunnerConfig.
        """
        _playbook, _rc, _status = self.run.run(
            playbook='existing.yaml',
            inventory='localhost,',
            workdir='/tmp')

        mock_config.assert_called_once()
        """Is the path even valid in our filesystem? Index 1 stands for kwargs in py<=36.
        os.lstat raises FileNotFoundError only if specified path is valid,
        but does not exist in current filesystem.
        """
        self.assertRaises(FileNotFoundError, os.lstat, mock_config.call_args[1]['fact_cache'])

        self.assertTrue(constants.VALIDATION_ANSIBLE_ARTIFACT_PATH in mock_config.call_args[1]['fact_cache'])

    @mock.patch('builtins.open')
    @mock.patch('os.path.exists', return_value=True)
    @mock.patch.object(
        Runner,
        'run',
        return_value=fakes.fake_ansible_runner_run_return(rc=0))
    @mock.patch('ansible_runner.runner_config.RunnerConfig')
    @mock.patch(
        'validations_libs.ansible.Ansible._encode_envvars',
        return_value={
            'ANSIBLE_STDOUT_CALLBACK': 'fake',
            'ANSIBLE_CALLBACK_WHITELIST': 'fake,validation_json,profile_tasks',
            'ANSIBLE_CONFIG': os.path.join(
                constants.VALIDATION_ANSIBLE_ARTIFACT_PATH,
                'ansible.cfg')})
    @mock.patch(
        'os.environ.copy',
        return_value={'ANSIBLE_STDOUT_CALLBACK': 'fake'})
    def test_run_ansible_envvars(self, mock_env,
                                 mock_encode_envvars,
                                 mock_config, mock_run,
                                 mock_exists, mock_open):
        """Tests if Ansible._ansible_env_var method,
        and following conditionals, correctly assemble the env dict.

        Assertions:
            Dictinary passed to Ansible._encode_envvars contains key: value
            pairs representing proper superset of key: value pairs required.
        """
        _playbook, _rc, _status = self.run.run(
            playbook='existing.yaml',
            inventory='localhost,',
            workdir='/tmp')

        env = {
            'ANSIBLE_STDOUT_CALLBACK': 'fake',
            'ANSIBLE_DISPLAY_FAILED_STDERR': True,
            'ANSIBLE_FORKS': 36,
            'ANSIBLE_TIMEOUT': 30,
            'ANSIBLE_GATHER_TIMEOUT': 45,
            'ANSIBLE_SSH_RETRIES': 3,
            'ANSIBLE_PIPELINING': True,
            'ANSIBLE_CALLBACK_WHITELIST': 'fake,profile_tasks,vf_validation_json',
            'ANSIBLE_RETRY_FILES_ENABLED': False,
            'ANSIBLE_HOST_KEY_CHECKING': False,
            'ANSIBLE_TRANSPORT': 'smart',
            'ANSIBLE_CACHE_PLUGIN_TIMEOUT': 7200,
            'ANSIBLE_GATHERING': 'smart',
            'ANSIBLE_CONFIG': os.path.join(
                constants.VALIDATION_ANSIBLE_ARTIFACT_PATH,
                'ansible.cfg')}

        #Test will work properly only if the method was called once.
        mock_encode_envvars.assert_called_once()

        """True if, and only if, every item (key:value pair) in the env dict
        is also present in the kwargs dict. Index 1 stands for kwargs in py<=36
        This test does not rely on order of items.
        """
        self.assertGreaterEqual(
            mock_encode_envvars.call_args[1]['env'].items(),
            env.items())

    @mock.patch('builtins.open')
    @mock.patch('os.path.exists', return_value=True)
    @mock.patch.object(
        Runner,
        'run',
        return_value=fakes.fake_ansible_runner_run_return(rc=0))
    @mock.patch('ansible_runner.runner_config.RunnerConfig')
    @mock.patch(
        'validations_libs.ansible.Ansible._encode_envvars',
        return_value={
            'ANSIBLE_STDOUT_CALLBACK': 'fake',
            'ANSIBLE_CALLBACK_WHITELIST': 'fake,validation_json,profile_tasks',
            'ANSIBLE_CONFIG': '/tmp/foo/artifacts/ansible.cfg'})
    @mock.patch(
        'os.environ.copy',
        return_value={'ANSIBLE_STDOUT_CALLBACK': 'fake'})
    def test_run_ansible_envvars_logdir(self, mock_env,
                                        mock_encode_envvars,
                                        mock_config, mock_run,
                                        mock_exists, mock_open):
        """Tests if Ansible._ansible_env_var method,
        and following conditionals, correctly assemble the env dict.
        While using the specified `log_path` value in appropriate places.

        Assertions:
            Dictinary passed to Ansible._encode_envvars contains key: value
            pairs representing proper superset of key: value pairs required.
        """
        _playbook, _rc, _status = self.run.run(
            playbook='existing.yaml',
            inventory='localhost,',
            workdir='/tmp',
            log_path='/tmp/foo')

        env = {
            'ANSIBLE_STDOUT_CALLBACK': 'fake',
            'ANSIBLE_DISPLAY_FAILED_STDERR': True,
            'ANSIBLE_FORKS': 36,
            'ANSIBLE_TIMEOUT': 30,
            'ANSIBLE_GATHER_TIMEOUT': 45,
            'ANSIBLE_SSH_RETRIES': 3,
            'ANSIBLE_PIPELINING': True,
            'ANSIBLE_CALLBACK_WHITELIST': 'fake,profile_tasks,vf_validation_json',
            'ANSIBLE_RETRY_FILES_ENABLED': False,
            'ANSIBLE_HOST_KEY_CHECKING': False,
            'ANSIBLE_TRANSPORT': 'smart',
            'ANSIBLE_CACHE_PLUGIN_TIMEOUT': 7200,
            'ANSIBLE_GATHERING': 'smart',
            'ANSIBLE_CONFIG': '/tmp/foo/artifacts/ansible.cfg',
            'VALIDATIONS_LOG_DIR': '/tmp/foo'}

        #Test will work properly only if the method was called once.
        mock_encode_envvars.assert_called_once()

        """True if, and only if, every item (key:value pair) in the env dict
        is also present in the kwargs dict. Index 1 stands for kwargs in py<=36
        This test does not rely on order of items.
        """
        self.assertGreaterEqual(
            mock_encode_envvars.call_args[1]['env'].items(),
            env.items())
