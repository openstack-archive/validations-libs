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

from cliff.show import ShowOne

from validations_libs.validation_actions import ValidationActions
from validations_libs import constants
from validations_libs.cli.parseractions import CommaListAction


class Show(ShowOne):
    """Validation Show client implementation class"""

    def get_parser(self, parser):
        """Argument parser for validation show"""
        parser = super(Show, self).get_parser(parser)
        parser.add_argument('--validation-dir', dest='validation_dir',
                            default=constants.ANSIBLE_VALIDATION_DIR,
                            help=("Path where the validation playbooks "
                                  "is located."))
        parser.add_argument('validation_name',
                            metavar="<validation>",
                            type=str,
                            help="Show a specific validation.")
        return parser

    def take_action(self, parsed_args):
        """Take validation action"""
        # Get parameters:
        validation_dir = parsed_args.validation_dir
        validation_name = parsed_args.validation_name

        v_actions = ValidationActions(validation_path=validation_dir)
        data = v_actions.show_validations(validation_name)

        if data:
            return data.keys(), data.values()


class ShowGroup(ShowOne):
    """Validation Show group client implementation class"""

    def get_parser(self, parser):
        """Argument parser for validation show group"""
        parser = super(ShowGroup, self).get_parser(parser)
        parser.add_argument('--validation-dir', dest='validation_dir',
                            default=constants.ANSIBLE_VALIDATION_DIR,
                            help=("Path where the validation playbooks "
                                  "is located."))
        parser.add_argument('--group', '-g',
                            metavar='<group_name>',
                            dest="group",
                            help=("Show a specific group."))
        return parser

    def take_action(self, parsed_args):
        """Take validation action"""
        # Get parameters:
        validation_dir = parsed_args.validation_dir
        group = parsed_args.group

        v_actions = ValidationActions(validation_path=validation_dir)
        return v_actions.group_information(group)


class ShowParameter(ShowOne):
    """Display Validations Parameters"""

    def get_parser(self, parser):
        parser = super(ShowParameter, self).get_parser(parser)

        parser.add_argument('--validation-dir', dest='validation_dir',
                            default=constants.ANSIBLE_VALIDATION_DIR,
                            help=("Path where the validation playbooks "
                                  "is located."))

        ex_group = parser.add_mutually_exclusive_group(required=False)
        ex_group.add_argument(
            '--validation',
            metavar='<validation_id>[,<validation_id>,...]',
            dest='validation_name',
            action=CommaListAction,
            default=[],
            help=("List specific validations, "
                  "if more than one validation is required "
                  "separate the names with commas: "
                  "--validation check-ftype,512e | "
                  "--validation 512e")
        )

        ex_group.add_argument(
            '--group', '-g',
            metavar='<group_id>[,<group_id>,...]',
            action=CommaListAction,
            default=[],
            help=("List specific group validations, "
                  "if more than one group is required "
                  "separate the group names with commas: "
                  "pre-upgrade,prep | "
                  "openshift-on-openstack")
        )

        parser.add_argument(
            '--download',
            action='store',
            default=None,
            help=("Create a json or a yaml file "
                  "containing all the variables "
                  "available for the validations: "
                  "/tmp/myvars")
        )

        parser.add_argument(
            '--format-output',
            action='store',
            metavar='<format_output>',
            default='json',
            choices=['json', 'yaml'],
            help=("Print representation of the validation. "
                  "The choices of the output format is json,yaml. ")
        )

        return parser

    def take_action(self, parsed_args):
        v_actions = ValidationActions(parsed_args.validation_dir)
        params = v_actions.show_validations_parameters(
            parsed_args.validation_name,
            parsed_args.group,
            parsed_args.format_output,
            parsed_args.download)
        if parsed_args.download:
            print("The file {} has been created successfully".format(
                parsed_args.download))
        return params.keys(), params.values()
