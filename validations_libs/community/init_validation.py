#!/usr/bin/env python

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

import logging
import re
# @matbu backward compatibility for stable/train
try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path

from validations_libs import constants, utils

LOG = logging.getLogger(__name__)


class CommunityValidation:
    """Init Community Validation Role and Playbook Command Class

    Initialize a new community role using ansible-galaxy and create a playboook
    from a template.
    """

    def __init__(self, validation_name):
        """Construct Role and Playbook."""
        self._validation_name = validation_name

    def execute(self):
        """Execute the actions necessary to create a new community validation

        Check if the role name is compliant with Ansible specification
        Initializing the new role using ansible-galaxy
        Creating the validation playbook from a template on disk

        :rtype: ``NoneType``
        """
        if not self.is_role_name_compliant:
            raise RuntimeError(
                "Role Name are limited to contain only lowercase "
                "alphanumeric characters, plus '_', '-' and start with an "
                "alpha character."
            )

        cmd = ['ansible-galaxy', 'init', '-v',
               '--offline', self.role_name,
               '--init-path', self.role_basedir]

        result = utils.run_command_and_log(LOG, cmd)

        if result != 0:
            raise RuntimeError(
                (
                    "Ansible Galaxy failed to create the role "
                    "{}, returned {}."
                    .format(self.role_name, result)
                )
            )

        LOG.info("New role created successfully in {}"
                 .format(self.role_dir_path))

        try:
            self.create_playbook()
        except (PermissionError, OSError) as error:
            raise RuntimeError(
                (
                    "Exception {} encountered while trying to write "
                    "the community validation playbook file {}."
                    .format(error, self.playbook_path)
                )
            )

        LOG.info("New playbook created successfully in {}"
                 .format(self.playbook_path))

    def create_playbook(self, content=constants.COMMUNITY_PLAYBOOK_TEMPLATE):
        """Create the playbook for the new community validation"""
        playbook = content.format(self.role_name)
        with open(self.playbook_path, 'w') as playbook_file:
            playbook_file.write(playbook)

    def is_role_exists(self):
        """New role existence check

        This class method checks if the new role name is already existing
        in the official validations catalog and in the current community
        validations directory.

        First, it gets the list of the role names available in
        ``constants.ANSIBLE_ROLES_DIR``. If there is a match in at least one
        of the directories, it returns ``True``, otherwise ``False``.

        :rtype: ``Boolean``
        """
        non_community_roles = []
        if Path(constants.ANSIBLE_ROLES_DIR).exists():
            non_community_roles = [
                Path(x).name
                for x in Path(constants.ANSIBLE_ROLES_DIR).iterdir()
                if x.is_dir()
            ]

        return Path(self.role_dir_path).exists() or \
            self.role_name in non_community_roles

    def is_playbook_exists(self):
        """New playbook existence check

        This class method checks if the new playbook file is already existing
        in the official validations catalog and in the current community
        validations directory.

        First, it gets the list of the playbooks yaml file available in
        ``constants.ANSIBLE_VALIDATIONS_DIR``. If there is a match in at least
        one of the directories, it returns ``True``, otherwise ``False``.

        :rtype: ``Boolean``
        """
        non_community_playbooks = []
        if Path(constants.ANSIBLE_VALIDATION_DIR).exists():
            non_community_playbooks = [
                Path(x).name
                for x in Path(constants.ANSIBLE_VALIDATION_DIR).iterdir()
                if x.is_file()
            ]

        return Path(self.playbook_path).exists() or \
            self.playbook_name in non_community_playbooks

    def is_community_validations_enabled(self, base_config):
        """Checks if the community validations are enabled in the config file

        :param base_config: Contents of the configuration file
        :type base_config: ``Dict``

        :rtype: ``Boolean``
        """
        config = base_config
        default_conf = (config.get('default', {})
                        if isinstance(config, dict) else {})
        return default_conf.get('enable_community_validations', True)

    @property
    def role_name(self):
        """Returns the community validation role name

        :rtype: ``str``
        """
        if re.match(r'^[a-z][a-z0-9_-]+$', self._validation_name) and \
           '-' in self._validation_name:
            return self._validation_name.replace('-', '_')
        return self._validation_name

    @property
    def role_basedir(self):
        """Returns the absolute path of the community validations roles

        :rtype: ``pathlib.PosixPath``
        """
        return constants.COMMUNITY_ROLES_DIR

    @property
    def role_dir_path(self):
        """Returns the community validation role directory name

        :rtype: ``pathlib.PosixPath``
        """
        return Path.joinpath(self.role_basedir, self.role_name)

    @property
    def is_role_name_compliant(self):
        """Check if the role name is compliant with Ansible Rules

        Roles Name are limited to contain only lowercase
        alphanumeric characters, plus '_' and start with an
        alpha character.

        :rtype: ``Boolean``
        """
        if not re.match(r'^[a-z][a-z0-9_]+$', self.role_name):
            return False
        return True

    @property
    def playbook_name(self):
        """Return the new playbook name with the yaml extension

        :rtype: ``str``
        """
        return self._validation_name.replace('_', '-') + ".yaml"

    @property
    def playbook_basedir(self):
        """Returns the absolute path of the community playbooks directory

        :rtype: ``pathlib.PosixPath``
        """
        return constants.COMMUNITY_PLAYBOOKS_DIR

    @property
    def playbook_path(self):
        """Returns the absolute path of the new community playbook yaml file

        :rtype: ``pathlib.PosixPath``
        """
        return Path.joinpath(self.playbook_basedir, self.playbook_name)
