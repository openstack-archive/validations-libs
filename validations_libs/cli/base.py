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

import os
import sys

from cliff import _argparse
from cliff.command import Command
from cliff.lister import Lister
from cliff.show import ShowOne

from validations_libs import constants
from validations_libs import utils

# Handle backward compatibility for Cliff 2.16.0 in stable/train:
if hasattr(_argparse, 'SmartHelpFormatter'):
    from cliff._argparse import SmartHelpFormatter
else:
    from cliff.command import _SmartHelpFormatter as SmartHelpFormatter


class Base:
    """Base class for CLI arguments management"""
    config = {}

    def set_argument_parser(self, vf_parser, args, section='default'):
        """ Set Arguments parser depending of the precedence ordering:
            * User CLI arguments
            * Configuration file
            * Default CLI values
        """
        # load parser
        parser = vf_parser.get_parser(vf_parser)
        # load cli args and skip binary and action
        cli_args = sys.argv[2:]
        cli_key = [arg.lstrip(parser.prefix_chars).replace('-', '_')
                   for arg in cli_args if arg.startswith('--')]

        self.config = utils.load_config(os.path.abspath(args.config))
        config_args = self.config.get(section, {})
        for key, value in args._get_kwargs():
            if key in cli_key:
                config_args.update({key: value})
            elif parser.get_default(key) != value:
                config_args.update({key: value})
            elif key not in config_args.keys():
                config_args.update({key: value})
        return vars(args).update(**config_args)


class BaseCommand(Command):
    """Base Command client implementation class"""

    def get_parser(self, prog_name):
        """Argument parser for base command"""
        self.base = Base()
        parser = _argparse.ArgumentParser(
            description=self.get_description(),
            epilog=self.get_epilog(),
            prog=prog_name,
            formatter_class=SmartHelpFormatter,
            conflict_handler='resolve',
        )
        for hook in self._hooks:
            hook.obj.get_parser(parser)

        parser.add_argument(
            '--config',
            dest='config',
            default=utils.find_config_file(),
            help=("Config file path for Validation.")
        )

        return parser


class BaseLister(Lister):
    """Base Lister client implementation class"""

    def get_parser(self, prog_name):
        """Argument parser for base lister"""
        parser = super(BaseLister, self).get_parser(prog_name)
        self.base = Base()
        vf_parser = _argparse.ArgumentParser(
            description=self.get_description(),
            epilog=self.get_epilog(),
            prog=prog_name,
            formatter_class=SmartHelpFormatter,
            conflict_handler='resolve',
        )

        for action in parser._actions:
            vf_parser._add_action(action)

        vf_parser.add_argument(
            '--config',
            dest='config',
            default=utils.find_config_file(),
            help=("Config file path for Validation.")
        )

        return vf_parser


class BaseShow(ShowOne):
    """Base Show client implementation class"""

    def get_parser(self, parser):
        """Argument parser for base show"""
        parser = super(BaseShow, self).get_parser(parser)
        self.base = Base()
        parser.add_argument(
            '--config',
            dest='config',
            default=utils.find_config_file(),
            help=("Config file path for Validation.")
        )

        return parser
