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
from validations_libs.cli.base import BaseLister
from validations_libs.cli.parseractions import CommaListAction
from validations_libs.cli import constants as cli_constants


class ValidationList(BaseLister):
    """List the Validations Catalog"""

    def get_parser(self, parser):
        """Argument parser for validation run"""
        parser = super(ValidationList, self).get_parser(parser)
        parser.add_argument('--group', '-g',
                            metavar='<group_id>[,<group_id>,...]',
                            action=CommaListAction,
                            default=[],
                            help=cli_constants.VAL_GROUP_DESC)
        parser.add_argument('--category',
                            metavar='<category_id>[,<category_id>,...]',
                            action=CommaListAction,
                            default=[],
                            help=cli_constants.VAL_CAT_DESC)
        parser.add_argument('--product',
                            metavar='<product_id>[,<product_id>,...]',
                            action=CommaListAction,
                            default=[],
                            help=cli_constants.VAL_PROD_DESC)
        parser.add_argument('--validation-dir', dest='validation_dir',
                            default=constants.ANSIBLE_VALIDATION_DIR,
                            help=cli_constants.PLAY_PATH_DESC)
        return parser

    def take_action(self, parsed_args):
        """Take validation action"""
        # Merge config and CLI args:
        self.base.set_argument_parser(self, parsed_args)

        group = parsed_args.group
        category = parsed_args.category
        product = parsed_args.product
        validation_dir = parsed_args.validation_dir
        group = parsed_args.group

        v_actions = ValidationActions(validation_path=validation_dir)
        return (v_actions.list_validations(groups=group,
                                           categories=category,
                                           products=product,
                                           validation_config=self.base.config))
