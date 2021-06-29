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


from cliff import _argparse
from cliff.command import Command
from cliff.lister import Lister

# Handle backward compatibility for Cliff 2.16.0 in stable/train:
if hasattr(_argparse, 'SmartHelpFormatter'):
    from cliff._argparse import SmartHelpFormatter
else:
    from cliff.command import _SmartHelpFormatter as SmartHelpFormatter


class BaseCommand(Command):
    """Base Command client implementation class"""

    def get_parser(self, prog_name):
        """Argument parser for base command"""
        parser = _argparse.ArgumentParser(
            description=self.get_description(),
            epilog=self.get_epilog(),
            prog=prog_name,
            formatter_class=SmartHelpFormatter,
            conflict_handler='resolve',
        )
        for hook in self._hooks:
            hook.obj.get_parser(parser)
        return parser


class BaseLister(Lister):
    """Base Lister client implementation class"""

    def get_parser(self, prog_name):
        """Argument parser for base lister"""
        parser = super(BaseLister, self).get_parser(prog_name)
        vf_parser = _argparse.ArgumentParser(
            description=self.get_description(),
            epilog=self.get_epilog(),
            prog=prog_name,
            formatter_class=SmartHelpFormatter,
            conflict_handler='resolve',
        )

        for action in parser._actions:
            vf_parser._add_action(action)

        return vf_parser
