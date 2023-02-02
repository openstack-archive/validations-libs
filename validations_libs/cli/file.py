#!/usr/bin/env python

#   Copyright 2023 Red Hat, Inc.
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

import getpass
import os
from validations_libs import utils
from validations_libs.cli import common
from validations_libs.cli.base import BaseCommand
from validations_libs.validation_actions import ValidationActions
from validations_libs.exceptions import ValidationRunException
from validations_libs import constants


class File(BaseCommand):
    """Include and exclude validations by name(s), group(s), category(ies) or by product(s)
    and run them from File"""

    def get_parser(self, parser):
        """Argument parser for validation file"""
        parser = super(File, self).get_parser(parser)

        parser.add_argument(
            dest='path_to_file',
            default=None,
            help=("The path where the YAML file is stored.\n"))

        parser.add_argument(
            '--junitxml',
            dest='junitxml',
            default=None,
            help=("Path where the run result in JUnitXML format will be stored.\n"))
        return parser

    def take_action(self, parsed_args):
        """Take action"""
        # Merge config and CLI args:
        self.base.set_argument_parser(self, parsed_args)

        # Verify if the YAML file is valid
        if parsed_args.path_to_file:
            try:
                yaml_file = common.read_cli_data_file(parsed_args.path_to_file)
                if not isinstance(yaml_file, dict):
                    raise ValidationRunException("Wrong format of the File.")
            except FileNotFoundError as e:
                raise FileNotFoundError(e)
        # Load the config file, if it is specified in the YAML file
        if 'config' in yaml_file and len('config') in yaml_file != 0:
            try:
                self.base.config = utils.load_config(os.path.abspath(yaml_file['config']))
            except FileNotFoundError as e:
                raise FileNotFoundError(e)
        else:
            self.base.config = {}
        v_actions = ValidationActions(yaml_file.get('validation-dir', constants.ANSIBLE_VALIDATION_DIR),
                                      log_path=yaml_file.get('validation-log-dir',
                                                             constants.VALIDATIONS_LOG_BASEDIR))
        # Check for the presence of the extra-vars and extra-vars-file so they can
        # be properly processed without overriding each other.
        if 'extra-vars-file' in yaml_file and 'extra-vars' in yaml_file:
            parsed_extra_vars_file = common.read_cli_data_file(yaml_file['extra-vars-file'])
            parsed_extra_vars = yaml_file['extra-vars']
            parsed_extra_vars.update(parsed_extra_vars_file)
            self.app.LOG.debug('Note that if you pass the same '
                               'KEY multiple times, the last given VALUE for that same KEY '
                               'will override the other(s).')
        elif 'extra-vars-file' in yaml_file:
            parsed_extra_vars = common.read_cli_data_file(yaml_file['extra-vars-file'])
        elif 'extra-vars' in yaml_file:
            parsed_extra_vars = yaml_file['extra-vars']
        else:
            parsed_extra_vars = None
        if 'limit' in yaml_file:
            hosts = yaml_file.get('limit')
            hosts_converted = ",".join(hosts)
        else:
            hosts_converted = None
        if 'inventory' in yaml_file:
            inventory_path = os.path.expanduser(yaml_file.get('inventory', 'localhost'))
        else:
            inventory_path = 'localhost'

        try:
            results = v_actions.run_validations(
                validation_name=yaml_file.get('include_validation', []),
                group=yaml_file.get('include_group', []),
                category=yaml_file.get('include_category', []),
                product=yaml_file.get('include_product', []),
                exclude_validation=yaml_file.get('exclude_validation'),
                exclude_group=yaml_file.get('exclude_group'),
                exclude_category=yaml_file.get('exclude_category'),
                exclude_product=yaml_file.get('exclude_product'),
                validation_config=self.base.config,
                limit_hosts=hosts_converted,
                ssh_user=yaml_file.get('ssh-user', getpass.getuser()),
                inventory=inventory_path,
                base_dir=yaml_file.get('ansible-base-dir', '/usr/share/ansible'),
                python_interpreter=yaml_file.get('python-interpreter', '/usr/bin/python3'),
                skip_list={},
                extra_vars=parsed_extra_vars,
                extra_env_vars=yaml_file.get('extra-env-vars'))
        except (RuntimeError, ValidationRunException) as e:
            raise ValidationRunException(e)

        if results:
            failed_rc = any([r for r in results if r['Status'] == 'FAILED'])
            if yaml_file.get('output-log'):
                common.write_output(yaml_file.get('output-log'), results)
            if parsed_args.junitxml:
                common.write_junitxml(parsed_args.junitxml, results)
            common.print_dict(results)
            if failed_rc:
                raise ValidationRunException("One or more validations have failed.")
        else:
            msg = ("No validation has been run, please check "
                   "log in the Ansible working directory.")
            raise ValidationRunException(msg)
