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


class TestAnsible(TestCase):

    def setUp(self):
        super(TestAnsible, self).setUp()
        self.unlink_patch = mock.patch('os.unlink')
        self.addCleanup(self.unlink_patch.stop)
        self.unlink_patch.start()
        self.run = Ansible()

    @mock.patch('os.path.exists', return_value=False)
    @mock.patch('ansible_runner.utils.dump_artifact', autospec=True,
                return_value="/foo/inventory.yaml")
    def test_check_no_playbook(self, mock_dump_artifact, mock_exists):
        self.assertRaises(
            RuntimeError,
            self.run.run,
            'non-existing.yaml',
            'localhost,',
            '/tmp'
        )
        mock_exists.assert_called_with('/tmp/non-existing.yaml')

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
        self.assertEquals((_playbook, _rc, _status),
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
        self.assertEquals((_playbook, _rc, _status),
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
        self.assertEquals((_playbook, _rc, _status),
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
        self.assertEquals((_playbook, _rc, _status),
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
        self.assertEquals((_playbook, _rc, _status),
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

        mock_config.assert_called_with(**opt)
