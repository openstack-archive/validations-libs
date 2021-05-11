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
    BACKWARD_COMPAT = (version < '1.4.0')
except pkg_resources.DistributionNotFound:
    BACKWARD_COMPAT = False


class Ansible(object):
    """An Object for encapsulating an Ansible execution"""

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
                    return os.path.abspath(inventory)
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
                                  temp_suffix='validations-libs-ansible'):
        """Creates ansible fact dir"""
        ansible_fact_path = os.path.join(
                tempfile.gettempdir(),
                temp_suffix,
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

    def _callbacks(self, callback_whitelist, output_callback, envvars={},
                   env={}):
        """Set callbacks"""
        # if output_callback is exported in env, then use it
        if isinstance(envvars, dict):
            env.update(envvars)
        output_callback = env.get('ANSIBLE_STDOUT_CALLBACK', output_callback)
        callback_whitelist = ','.join(filter(None, [callback_whitelist,
                                                    output_callback,
                                                    'validation_json',
                                                    'profile_tasks']))
        return callback_whitelist, output_callback

    def _ansible_env_var(self, output_callback, ssh_user, workdir, connection,
                         gathering_policy, module_path, key,
                         extra_env_variables, ansible_timeout,
                         callback_whitelist, base_dir, python_interpreter,
                         env={}):
        """Handle Ansible env var for Ansible config execution"""
        cwd = os.getcwd()
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
        if ssh_user:
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

        if python_interpreter:
            env['ANSIBLE_PYTHON_INTERPRETER'] = python_interpreter
        elif connection == 'local':
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
            connection='smart', output_callback=None,
            base_dir=constants.DEFAULT_VALIDATIONS_BASEDIR,
            ssh_user=None, key=None, module_path=None,
            limit_hosts=None, tags=None, skip_tags=None,
            verbosity=0, quiet=False, extra_vars=None,
            gathering_policy='smart',
            extra_env_variables=None, parallel_run=False,
            callback_whitelist=None, ansible_cfg=None,
            ansible_timeout=30, ansible_artifact_path=None,
            log_path=None, run_async=False, python_interpreter=None):
        """Execute one or multiple Ansible playbooks

        :param playbook: The Absolute path of the Ansible playbook
        :type playbook: ``string``
        :param inventory: Either proper inventory file or a
                          comma-separated list
        :type inventory: ``string``
        :param workdir: The absolute path of the Ansible-runner
                        artifacts directory
        :type workdir: ``string``
        :param playbook_dir: The absolute path of the Validations playbooks
                             directory
        :type playbook_dir: ``string``
        :param connection: Connection type (local, smart, etc).
                        (efaults to 'smart')
        :type connection: String
        :param output_callback: Callback for output format. Defaults to
                                'yaml'.
        :type output_callback: ``string``
        :param base_dir: The absolute path of the default validations base
                         directory
        :type base_dir: ``string``
        :param ssh_user: User for the ssh connection (Defaults to 'root')
        :type ssh_user: ``string``
        :param key: Private key to use for the ssh connection.
        :type key: ``string``
        :param module_path: Location of the ansible module and library.
        :type module_path: ``string``
        :param limit_hosts: Limit the execution to the hosts.
        :type limit_hosts: ``string``
        :param tags: Run specific tags.
        :type tags: ``string``
        :param skip_tags: Skip specific tags.
        :type skip_tags: ``string``
        :param verbosity: Verbosity level for Ansible execution.
        :type verbosity: ``integer``
        :param quiet: Disable all output (Defaults to False)
        :type quiet: ``boolean``
        :param extra_vars: Set additional variables as a Dict or the absolute
                        path of a JSON or YAML file type.
        :type extra_vars: Either a Dict or the absolute path of JSON or YAML
        :param gathering_policy: This setting controls the default policy of
                        fact gathering ('smart', 'implicit', 'explicit').
                        (Defaults to 'smart')
        :type gathering_facts: ``string``
        :param extra_env_vars: Set additional ansible variables using an
                                extravar dictionary.
        :type extra_env_vars: ``dict``
        :param parallel_run: Isolate playbook execution when playbooks are
                             to be executed with multi-processing.
        :type parallel_run: ``boolean``
        :param callback_whitelist: Comma separated list of callback plugins.
                                Custom output_callback is also whitelisted.
                                (Defaults to ``None``)
        :type callback_whitelist: ``list`` or ``string``
        :param ansible_cfg: Path to an ansible configuration file. One will be
                         generated in the artifact path if this option is None.
        :type ansible_cfg: ``string``
        :param ansible_timeout: Timeout for ansible connections.
                                (Defaults to ``30 minutes``)
        :type ansible_timeout: ``integer``
        :param ansible_artifact_path: The Ansible artifact path
        :type ansible_artifact_path: ``string``
        :param log_path: The absolute path of the validations logs directory
        :type log_path: ``string``
        :param run_async: Enable the Ansible asynchronous mode
                          (Defaults to 'False')
        :type run_async: ``boolean``
        :param python_interpreter: Path to the Python interpreter to be
                                   used for module execution on remote targets,
                                   or an automatic discovery mode (``auto``,
                                   ``auto_silent`` or the default one
                                   ``auto_legacy``)
        :type python_interpreter: ``string``

        :return: A ``tuple`` containing the the absolute path of the executed
                 playbook, the return code and the status of the run
        :rtype: ``tuple``
        """
        if not playbook_dir:
            playbook_dir = workdir

        if not ansible_artifact_path:
            if log_path:
                ansible_artifact_path = "{}/artifacts/".format(log_path)
            else:
                ansible_artifact_path = \
                    constants.VALIDATION_ANSIBLE_ARTIFACT_PATH

        playbook = self._playbook_check(playbook, playbook_dir)
        self.log.debug(
            'Running Ansible playbook: {},'
            ' Working directory: {},'
            ' Playbook directory: {}'.format(
                playbook,
                workdir,
                playbook_dir
            )
        )

        # Get env variables:
        env = {}
        env = os.environ.copy()
        extravars = self._get_extra_vars(extra_vars)

        if isinstance(callback_whitelist, list):
            callback_whitelist = ','.join(callback_whitelist)
        callback_whitelist, output_callback = self._callbacks(
            callback_whitelist,
            output_callback,
            extra_env_variables,
            env)
        # Set ansible environment variables
        env.update(self._ansible_env_var(output_callback, ssh_user, workdir,
                                         connection, gathering_policy,
                                         module_path, key, extra_env_variables,
                                         ansible_timeout, callback_whitelist,
                                         base_dir, python_interpreter))

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

        if log_path:
            env['VALIDATIONS_LOG_DIR'] = log_path

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

        if not BACKWARD_COMPAT:
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
        if BACKWARD_COMPAT:
            runner_config.env.update(envvars)

        runner = ansible_runner.Runner(config=runner_config)
        if run_async:
            thr = threading.Thread(target=runner.run)
            thr.start()
            return playbook, runner.rc, runner.status
        status, rc = runner.run()
        return playbook, rc, status
