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

import json
import sys

from cliff.lister import Lister

from validations_libs.validation_actions import ValidationActions
from validations_libs import constants
from validations_libs.cli.parseractions import CommaListAction


class ValidationList(Lister):
    """Validation List client implementation class"""

    def get_parser(self, parser):
        """Argument parser for validation run"""
        parser = super(ValidationList, self).get_parser(parser)
        parser.add_argument('--group', '-g',
                            metavar='<group>[,<group>,...]',
                            action=CommaListAction,
                            default=[],
                            help=("Run specific group validations, "
                                  "if more than one group is required "
                                  "separate the group names with commas: "
                                  "--group pre-upgrade,prep | "
                                  "--group openshift-on-openstack"))
        parser.add_argument('--validation-dir', dest='validation_dir',
                            default=constants.ANSIBLE_VALIDATION_DIR,
                            help=("Path where the validation playbooks "
                                  "is located."))
        return parser

    def take_action(self, parsed_args):
        """Take validation action"""
        # Get parameters:
        group = parsed_args.group
        validation_dir = parsed_args.validation_dir

        v_actions = ValidationActions(validation_path=validation_dir)
        return (v_actions.list_validations(group))
