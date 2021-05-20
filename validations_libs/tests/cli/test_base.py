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

try:
    from unittest import mock
except ImportError:
    import mock
from unittest import TestCase

from validations_libs.cli import lister
from validations_libs.cli import base
from validations_libs.tests import fakes
from validations_libs.tests.cli.fakes import BaseCommand

import argparse


class TestArgParse(argparse.ArgumentParser):

    config = 'foo'

    def __init__(self):
        super(TestArgParse, self).__init__()


class TestBase(BaseCommand):

    def setUp(self):
        super(TestBase, self).setUp()
        self.cmd = lister.ValidationList(self.app, None)
        self.base = base.Base()

    @mock.patch('argparse.ArgumentParser.parse_known_args',
                return_value=(TestArgParse(), ['foo-bar']))
    @mock.patch('os.path.abspath', return_value='/foo')
    @mock.patch('validations_libs.utils.load_config',
                return_value=fakes.DEFAULT_CONFIG)
    def test_config_args(self, mock_config, mock_path, mock_argv):
        cmd_parser = self.cmd.get_parser('check_parser')

        self.assertEqual(['foo_bar'], self.base._format_arg(cmd_parser))

    @mock.patch('os.path.abspath', return_value='/foo')
    @mock.patch('validations_libs.utils.load_config',
                return_value=fakes.DEFAULT_CONFIG)
    def test_argument_parser_cli_choice(self, mock_load, mock_path):
        arglist = ['--validation-dir', 'foo', '--config', 'validation.cfg']
        verifylist = [('validation_dir', 'foo')]
        self._set_args(arglist)
        cmd_parser = self.cmd.get_parser('check_parser')
        parser = self.base.set_argument_parser(cmd_parser)

        self.assertEqual(fakes.DEFAULT_CONFIG, self.base.config)
        self.assertEqual(parser.get_default('validation_dir'), 'foo')

    @mock.patch('os.path.abspath', return_value='/foo')
    @mock.patch('validations_libs.utils.load_config',
                return_value=fakes.DEFAULT_CONFIG)
    def test_argument_parser_config_choice(self, mock_load, mock_path):
        arglist = []
        verifylist = []
        self._set_args(arglist)
        cmd_parser = self.cmd.get_parser('check_parser')
        parser = self.base.set_argument_parser(cmd_parser)

        self.assertEqual(fakes.DEFAULT_CONFIG, self.base.config)
        self.assertEqual(parser.get_default('validation_dir'),
                         '/usr/share/ansible/validation-playbooks')

    @mock.patch('os.path.abspath', return_value='/foo')
    @mock.patch('validations_libs.utils.load_config',
                return_value={})
    def test_argument_parser_constant_choice(self, mock_load, mock_path):
        arglist = []
        verifylist = []
        self._set_args(arglist)
        cmd_parser = self.cmd.get_parser('check_parser')
        parser = self.base.set_argument_parser(cmd_parser)

        self.assertEqual({}, self.base.config)
        self.assertEqual(parser.get_default('validation_dir'),
                         '/usr/share/ansible/validation-playbooks')
