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

from ansible_runner import Runner
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

    def test_get_extra_vars_dict(self):
        extra_vars = {
            'foo': 'bar'
        }

        self.assertEqual(extra_vars, self.run._get_extra_vars(extra_vars))

    @mock.patch('yaml.safe_load', return_value={'fizz': 'buzz'})
    @mock.patch('six.moves.builtins.open', spec=open)
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

    @mock.patch('six.moves.builtins.open')
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

    @mock.patch('six.moves.builtins.open')
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

    @mock.patch('six.moves.builtins.open')
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
    @mock.patch('six.moves.builtins.open')
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
    @mock.patch('six.moves.builtins.open')
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

    @mock.patch('six.moves.builtins.open')
    @mock.patch('os.path.exists', return_value=True)
    @mock.patch('os.makedirs')
    @mock.patch.object(Runner, 'run',
                       return_value=fakes.fake_ansible_runner_run_return(rc=0))
    @mock.patch('ansible_runner.utils.dump_artifact', autospec=True,
                return_value="/foo/inventory.yaml")
    @mock.patch('ansible_runner.runner_config.RunnerConfig')
    @mock.patch('validations_libs.ansible.Ansible._ansible_env_var',
                return_value={'ANSIBLE_STDOUT_CALLBACK': 'fake.py'})
    @mock.patch('os.environ.copy', return_value={})
    @mock.patch('os.path.abspath', return_value='/tmp/foo/localhost')
    def test_run_specific_log_path(self, moch_path, mock_env, mock_env_var,
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
                    'ANSIBLE_STDOUT_CALLBACK': 'fake.py',
                    'ANSIBLE_CONFIG': '/tmp/foo/artifacts/ansible.cfg',
                    'VALIDATIONS_LOG_DIR': '/tmp/foo'},
                'project_dir': '/tmp',
                'fact_cache': '/tmp/foo/artifacts/',
                'fact_cache_type': 'jsonfile'
                })

        mock_config.assert_called_once_with(**opt)
