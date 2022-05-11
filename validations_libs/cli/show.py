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

from validations_libs.validation_actions import ValidationActions
from validations_libs import constants
from validations_libs.cli.parseractions import CommaListAction
from validations_libs.cli.base import BaseShow, BaseLister
from validations_libs.cli import constants as cli_constants


class Show(BaseShow):
    """Show detailed informations about a Validation"""

    def get_parser(self, parser):
        """Argument parser for validation show"""
        parser = super(Show, self).get_parser(parser)
        parser.add_argument('--validation-dir', dest='validation_dir',
                            default=constants.ANSIBLE_VALIDATION_DIR,
                            help=cli_constants.PLAY_PATH_DESC)
        parser.add_argument('validation_name',
                            metavar="<validation>",
                            type=str,
                            help="Show a specific validation.")
        return parser

    def take_action(self, parsed_args):
        """Take validation action"""
        # Merge config and CLI args:
        self.base.set_argument_parser(self, parsed_args)
        # Get parameters:
        validation_dir = parsed_args.validation_dir
        validation_name = parsed_args.validation_name

        v_actions = ValidationActions(validation_path=validation_dir)
        data = v_actions.show_validations(
                validation_name, validation_config=self.base.config)

        if data:
            return data.keys(), data.values()


class ShowGroup(BaseLister):
    """Show detailed informations about Validation Groups"""

    def get_parser(self, parser):
        """Argument parser for validation show group"""
        parser = super(ShowGroup, self).get_parser(parser)

        parser.add_argument('--validation-dir', dest='validation_dir',
                            default=constants.ANSIBLE_VALIDATION_DIR,
                            help=cli_constants.PLAY_PATH_DESC)
        return parser

    def take_action(self, parsed_args):
        """Take validation action"""
        # Merge config and CLI args:
        self.base.set_argument_parser(self, parsed_args)

        v_actions = ValidationActions(parsed_args.validation_dir)

        return v_actions.group_information(
                validation_config=self.base.config)


class ShowParameter(BaseShow):
    """Show Validation(s) parameter(s)

    Display Validation(s) Parameter(s) which could be overriden during an
    execution. It could be filtered by **validation_id**, **group(s)**,
    **category(ies)** or by **products**.
    """

    def get_parser(self, parser):
        parser = super(ShowParameter, self).get_parser(parser)

        parser.add_argument('--validation-dir', dest='validation_dir',
                            default=constants.ANSIBLE_VALIDATION_DIR,
                            help=cli_constants.PLAY_PATH_DESC)

        ex_group = parser.add_mutually_exclusive_group(required=False)
        ex_group.add_argument(
            '--validation',
            metavar='<validation_id>[,<validation_id>,...]',
            dest='validation_name',
            action=CommaListAction,
            default=[],
            help=("List specific validations, "
                  "if more than one validation is required "
                  "separate the names with commas."))

        ex_group.add_argument(
            '--group', '-g',
            metavar='<group_id>[,<group_id>,...]',
            action=CommaListAction,
            default=[],
            help=cli_constants.VAL_GROUP_DESC)

        ex_group.add_argument(
            '--category',
            metavar='<category_id>[,<category_id>,...]',
            action=CommaListAction,
            default=[],
            help=cli_constants.VAL_CAT_DESC)

        ex_group.add_argument(
            '--product',
            metavar='<product_id>[,<product_id>,...]',
            action=CommaListAction,
            default=[],
            help=cli_constants.VAL_PROD_DESC)

        parser.add_argument(
            '--download',
            action='store',
            default=None,
            help=("Create a json or a yaml file "
                  "containing all the variables "
                  "available for the validations: "
                  "/tmp/myvars"))

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
        # Merge config and CLI args:
        self.base.set_argument_parser(self, parsed_args)

        validation_dir = parsed_args.validation_dir
        v_actions = ValidationActions(validation_dir)
        params = v_actions.show_validations_parameters(
            validations=parsed_args.validation_name,
            groups=parsed_args.group,
            categories=parsed_args.category,
            products=parsed_args.product,
            output_format=parsed_args.format_output,
            download_file=parsed_args.download,
            validation_config=self.base.config)

        if parsed_args.download:
            self.app.LOG.info(
                "The file {} has been created successfully".format(
                parsed_args.download))
        return params.keys(), params.values()
