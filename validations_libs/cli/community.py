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

import logging

from validations_libs import constants, utils
from validations_libs.cli.base import BaseCommand
from validations_libs.community.init_validation import \
    CommunityValidation as com_val

LOG = logging.getLogger(__name__)


class CommunityValidationInit(BaseCommand):
    """Initialize Community Validation Skeleton"""

    def get_parser(self, parser):
        """Argument parser for Community Validation Init"""
        parser = super(CommunityValidationInit, self).get_parser(parser)

        parser.add_argument(
            'validation_name',
            metavar="<validation_name>",
            type=str,
            help=(
                "The name of the Community Validation:\n"
                "Validation name is limited to contain only lowercase "
                "alphanumeric characters, plus '_' or '-' and starts "
                "with an alpha character. \n"
                "Ex: my-val, my_val2. \n"
                "This will generate an Ansible role and a playbook in "
                f"{constants.COMMUNITY_VALIDATIONS_BASEDIR}. "
                "Note that the structure of this directory will be created at "
                "the first use."
            )
        )

        if self.app:
            # Merge config and CLI args:
            return self.base.set_argument_parser(parser)
        return parser

    def take_action(self, parsed_args):
        """Take Community Validation Action"""

        co_validation = com_val(parsed_args.validation_name)

        if co_validation.is_community_validations_enabled(self.base.config):
            LOG.debug(
                (
                    "Checking the presence of the community validations "
                    f"{constants.COMMUNITY_VALIDATIONS_BASEDIR} directory..."
                )
            )

            utils.check_community_validations_dir()

            if co_validation.is_role_exists():
                raise RuntimeError(
                    (
                    f"An Ansible role called {co_validation.role_name} "
                    "already exist in: \n"
                    f" - {constants.COMMUNITY_ROLES_DIR}\n"
                    f" - {constants.ANSIBLE_ROLES_DIR}"
                    )
                )

            if co_validation.is_playbook_exists():
                raise RuntimeError(
                    (
                    f"An Ansible playbook called {co_validation.playbook_name} "
                    "already exist in: \n"
                    f" - {constants.COMMUNITY_PLAYBOOKS_DIR}\n"
                    f" - {constants.ANSIBLE_VALIDATION_DIR}"
                    )
                )

            co_validation.execute()
        else:
            raise RuntimeError(
                "The Community Validations are disabled:\n"
                "To enable them, set [DEFAULT].enable_community_validations "
                "to 'True' in the configuration file."
            )
