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

import ansible_runner
import logging
import pkg_resources
import pwd
import os
import six
import sys
import tempfile
import threading
import yaml

from six.moves import configparser
from validations_libs import constants

LOG = logging.getLogger(__name__ + ".ansible")

# NOTE(cloudnull): This is setting the FileExistsError for py2 environments.
#                  When we no longer support py2 (centos7) this should be
#                  removed.
try:
    FileExistsError = FileExistsError
except NameError:
    FileExistsError = OSError

try:
    version = pkg_resources.get_distribution("ansible_runner").version
    backward_compat = (version < '1.4.4')
except pkg_resources.DistributionNotFound:
    backward_compat = False


class Ansible(object):

    def __init__(self, uuid=None):
        self.log = logging.getLogger(__name__ + ".Ansible")
        self.uuid = uuid

    def _playbook_check(self, play, playbook_dir=None):
        """Check if playbook exist"""
        if not os.path.exists(play):
            play = os.path.join(playbook_dir, play)
            if not os.path.exists(play):
                raise RuntimeError('No such playbook: {}'.format(play))
        self.log.debug('Ansible playbook {} found'.format(play))
        return play

    def _inventory(self, inventory, ansible_artifact_path):
        """Handle inventory for Ansible"""
        if inventory:
            if isinstance(inventory, six.string_types):
                # check is file path
                if os.path.exists(inventory):
                    return inventory
            elif isinstance(inventory, dict):
                inventory = yaml.safe_dump(
                    inventory,
                    default_flow_style=False
                )
            return ansible_runner.utils.dump_artifact(
                inventory,
                ansible_artifact_path,
                'hosts'
            )

    def _creates_ansible_fact_dir(self,
                                  temp_suffix='validagions-libs-ansible'):
        """Creates ansible fact dir"""
        ansible_fact_path = os.path.join(
            os.path.join(
                tempfile.gettempdir(),
                temp_suffix
            ),
            'fact_cache'
        )

        try:
            os.makedirs(ansible_fact_path)
            return ansible_fact_path
        except FileExistsError:
            self.log.debug(
                'Directory "{}" was not created because it'
                ' already exists.'.format(
                    ansible_fact_path
                )
            )

    def _get_extra_vars(self, extra_vars):
        """Manage extra_vars into a dict"""
        extravars = dict()
        if extra_vars:
            if isinstance(extra_vars, dict):
                extravars.update(extra_vars)
            elif os.path.exists(extra_vars) and os.path.isfile(extra_vars):
                with open(extra_vars) as f:
                    extravars.update(yaml.safe_load(f.read()))
        return extravars

    def _callback_whitelist(self, callback_whitelist, output_callback):
        """Set callback whitelist"""
        if callback_whitelist:
            callback_whitelist = ','.join([callback_whitelist,
                                          output_callback])
        else:
            callback_whitelist = output_callback
        return ','.join([callback_whitelist, 'profile_tasks'])

    def _ansible_env_var(self, output_callback, ssh_user, workdir, connection,
                         gathering_policy, module_path, key,
                         extra_env_variables, ansible_timeout,
                         callback_whitelist, base_dir):
        """Handle Ansible env var for Ansible config execution"""
        cwd = os.getcwd()
        env = os.environ.copy()
        env['ANSIBLE_SSH_ARGS'] = (
            '-o UserKnownHostsFile={} '
            '-o StrictHostKeyChecking=no '
            '-o ControlMaster=auto '
            '-o ControlPersist=30m '
            '-o ServerAliveInterval=64 '
            '-o ServerAliveCountMax=1024 '
            '-o Compression=no '
            '-o TCPKeepAlive=yes '
            '-o VerifyHostKeyDNS=no '
            '-o ForwardX11=no '
            '-o ForwardAgent=yes '
            '-o PreferredAuthentications=publickey '
            '-T'
        ).format(os.devnull)

        env['ANSIBLE_DISPLAY_FAILED_STDERR'] = True
        env['ANSIBLE_FORKS'] = 36
        env['ANSIBLE_TIMEOUT'] = ansible_timeout
        env['ANSIBLE_GATHER_TIMEOUT'] = 45
        env['ANSIBLE_SSH_RETRIES'] = 3
        env['ANSIBLE_PIPELINING'] = True
        env['ANSIBLE_REMOTE_USER'] = ssh_user
        env['ANSIBLE_STDOUT_CALLBACK'] = output_callback
        env['ANSIBLE_LIBRARY'] = os.path.expanduser(
            '~/.ansible/plugins/modules:'
            '{}:{}:'
            '/usr/share/ansible/plugins/modules:'
            '/usr/share/ceph-ansible/library:'
            '{}/library'.format(
                os.path.join(workdir, 'modules'),
                os.path.join(cwd, 'modules'),
                base_dir
            )
        )
        env['ANSIBLE_LOOKUP_PLUGINS'] = os.path.expanduser(
            '~/.ansible/plugins/lookup:'
            '{}:{}:'
            '/usr/share/ansible/plugins/lookup:'
            '/usr/share/ceph-ansible/plugins/lookup:'
            '{}/lookup_plugins'.format(
                os.path.join(workdir, 'lookup'),
                os.path.join(cwd, 'lookup'),
                base_dir
            )
        )
        env['ANSIBLE_CALLBACK_PLUGINS'] = os.path.expanduser(
            '~/.ansible/plugins/callback:'
            '{}:{}:'
            '/usr/share/ansible/plugins/callback:'
            '/usr/share/ceph-ansible/plugins/callback:'
            '{}/callback_plugins'.format(
                os.path.join(workdir, 'callback'),
                os.path.join(cwd, 'callback'),
                base_dir
            )
        )
        env['ANSIBLE_ACTION_PLUGINS'] = os.path.expanduser(
            '~/.ansible/plugins/action:'
            '{}:{}:'
            '/usr/share/ansible/plugins/action:'
            '/usr/share/ceph-ansible/plugins/actions:'
            '{}/action_plugins'.format(
                os.path.join(workdir, 'action'),
                os.path.join(cwd, 'action'),
                base_dir
            )
        )
        env['ANSIBLE_FILTER_PLUGINS'] = os.path.expanduser(
            '~/.ansible/plugins/filter:'
            '{}:{}:'
            '/usr/share/ansible/plugins/filter:'
            '/usr/share/ceph-ansible/plugins/filter:'
            '{}/filter_plugins'.format(
                os.path.join(workdir, 'filter'),
                os.path.join(cwd, 'filter'),
                base_dir
            )
        )
        env['ANSIBLE_ROLES_PATH'] = os.path.expanduser(
            '~/.ansible/roles:'
            '{}:{}:'
            '/usr/share/ansible/roles:'
            '/usr/share/ceph-ansible/roles:'
            '/etc/ansible/roles:'
            '{}/roles'.format(
                os.path.join(workdir, 'roles'),
                os.path.join(cwd, 'roles'),
                base_dir
            )
        )
        env['ANSIBLE_CALLBACK_WHITELIST'] = callback_whitelist
        env['ANSIBLE_RETRY_FILES_ENABLED'] = False
        env['ANSIBLE_HOST_KEY_CHECKING'] = False
        env['ANSIBLE_TRANSPORT'] = connection
        env['ANSIBLE_CACHE_PLUGIN_TIMEOUT'] = 7200

        if self.uuid:
            env['ANSIBLE_UUID'] = self.uuid

        if connection == 'local':
            env['ANSIBLE_PYTHON_INTERPRETER'] = sys.executable

        if gathering_policy in ('smart', 'explicit', 'implicit'):
            env['ANSIBLE_GATHERING'] = gathering_policy

        if module_path:
            env['ANSIBLE_LIBRARY'] = ':'.join(
                [env['ANSIBLE_LIBRARY'], module_path]
            )

        try:
            user_pwd = pwd.getpwuid(int(os.getenv('SUDO_UID', os.getuid())))
        except TypeError:
            home = os.path.expanduser('~')
        else:
            home = user_pwd.pw_dir

        env['ANSIBLE_LOG_PATH'] = os.path.join(home, 'ansible.log')

        if key:
            env['ANSIBLE_PRIVATE_KEY_FILE'] = key

        if extra_env_variables:
            if not isinstance(extra_env_variables, dict):
                msg = "extra_env_variables must be a dict"
                self.log.error(msg)
                raise SystemError(msg)
            else:
                env.update(extra_env_variables)

        return env

    def _encode_envvars(self, env):
        """Encode a hash of values.

        :param env: A hash of key=value items.
        :type env: `dict`.
        """
        for key, value in env.items():
            env[key] = six.text_type(value)
        else:
            return env

    def run(self, playbook, inventory, workdir, playbook_dir=None,
            connection='smart', output_callback='yaml',
            base_dir=constants.DEFAULT_VALIDATIONS_BASEDIR,
            ssh_user='root', key=None, module_path=None,
            limit_hosts=None, tags=None, skip_tags=None,
            verbosity=0, quiet=False, extra_vars=None,
            gathering_policy='smart',
            extra_env_variables=None, parallel_run=False,
            callback_whitelist=None, ansible_cfg=None,
            ansible_timeout=30, ansible_artifact_path=None, run_async=False):

        if not playbook_dir:
            playbook_dir = workdir

        playbook = self._playbook_check(playbook, playbook_dir)
        self.log.info(
            'Running Ansible playbook: {},'
            ' Working directory: {},'
            ' Playbook directory: {}'.format(
                playbook,
                workdir,
                playbook_dir
            )
        )

        # ansible_fact_path = self._creates_ansible_fact_dir()
        extravars = self._get_extra_vars(extra_vars)
        callback_whitelist = self._callback_whitelist(callback_whitelist,
                                                      output_callback)

        # Set ansible environment variables
        env = self._ansible_env_var(output_callback, ssh_user, workdir,
                                    connection, gathering_policy, module_path,
                                    key, extra_env_variables, ansible_timeout,
                                    callback_whitelist, base_dir)
        if not ansible_artifact_path:
            ansible_artifact_path = constants.VALIDATION_ANSIBLE_ARTIFACT_PATH
        if 'ANSIBLE_CONFIG' not in env and not ansible_cfg:
            ansible_cfg = os.path.join(ansible_artifact_path, 'ansible.cfg')
            config = configparser.ConfigParser()
            config.add_section('defaults')
            config.set('defaults', 'internal_poll_interval', '0.05')
            with open(ansible_cfg, 'w') as f:
                config.write(f)
            env['ANSIBLE_CONFIG'] = ansible_cfg
        elif 'ANSIBLE_CONFIG' not in env and ansible_cfg:
            env['ANSIBLE_CONFIG'] = ansible_cfg

        envvars = self._encode_envvars(env=env)
        r_opts = {
            'private_data_dir': workdir,
            'inventory': self._inventory(inventory, ansible_artifact_path),
            'playbook': playbook,
            'verbosity': verbosity,
            'quiet': quiet,
            'extravars': extravars,
            'artifact_dir': workdir,
            'rotate_artifacts': 256,
            'ident': ''
            }

        if not backward_compat:
            r_opts.update({
                'envvars': envvars,
                'project_dir': playbook_dir,
                'fact_cache': ansible_artifact_path,
                'fact_cache_type': 'jsonfile'
                })
        else:
            parallel_run = False

        if skip_tags:
            r_opts['skip_tags'] = skip_tags

        if tags:
            r_opts['tags'] = tags

        if limit_hosts:
            r_opts['limit'] = limit_hosts

        if parallel_run:
            r_opts['directory_isolation_base_path'] = ansible_artifact_path
        runner_config = ansible_runner.runner_config.RunnerConfig(**r_opts)
        runner_config.prepare()
        runner_config.env['ANSIBLE_STDOUT_CALLBACK'] = \
            envvars['ANSIBLE_STDOUT_CALLBACK']
        if backward_compat:
            runner_config.env.update(envvars)

        runner = ansible_runner.Runner(config=runner_config)
        if run_async:
            thr = threading.Thread(target=runner.run)
            thr.start()
            return playbook, runner.rc, runner.status
        status, rc = runner.run()
        return playbook, rc, status
