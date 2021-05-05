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

import getpass
import sys

from validations_libs import constants
from validations_libs.validation_actions import ValidationActions
from validations_libs.cli import common
from validations_libs.cli.base import BaseCommand
from validations_libs.cli.parseractions import CommaListAction, KeyValueAction


class Run(BaseCommand):
    """Validation Run client implementation class"""

    def get_parser(self, parser):
        """Argument parser for validation run"""
        parser = super(Run, self).get_parser(parser)
        parser.add_argument(
            '--limit', action='store', required=False, help=(
                "A string that identifies a single node or comma-separated "
                "list of nodes to be upgraded in parallel in this upgrade "
                " run invocation. For example: --limit \"compute-0,"
                "compute-1,compute-5\"."))

        parser.add_argument(
            '--ssh-user',
            dest='ssh_user',
            default=getpass.getuser(),
            help=("SSH user name for the Ansible ssh connection."))

        parser.add_argument('--validation-dir', dest='validation_dir',
                            default=constants.ANSIBLE_VALIDATION_DIR,
                            help=("Path where the validation playbooks "
                                  "is located."))

        parser.add_argument('--ansible-base-dir', dest='ansible_base_dir',
                            default=constants.DEFAULT_VALIDATIONS_BASEDIR,
                            help=("Path where the ansible roles, library "
                                  "and plugins are located."))

        parser.add_argument(
            '--validation-log-dir',
            dest='validation_log_dir',
            default=constants.VALIDATIONS_LOG_BASEDIR,
            help=(
                "Path where the log files and artifacts will be located. "))

        parser.add_argument('--inventory', '-i', type=str,
                            default="localhost",
                            help="Path of the Ansible inventory.")

        parser.add_argument('--output-log', dest='output_log',
                            default=None,
                            help=("Path where the run result will be stored."))

        parser.add_argument('--junitxml', dest='junitxml',
                            default=None,
                            help=("Path where the run result in JUnitXML "
                                  "format will be stored."))

        parser.add_argument(
            '--python-interpreter',
            metavar="--python-interpreter <PYTHON_INTERPRETER_PATH>",
            action="store",
            default="{}".format(
                sys.executable if sys.executable else "/usr/bin/python"
            ),
            help=("Python interpreter for Ansible execution. "))

        parser.add_argument(
            '--extra-env-vars',
            action=KeyValueAction,
            default=None,
            metavar="key1=<val1> [--extra-vars key3=<val3>]",
            help=(
                " Add extra environment variables you may need "
                "to provide to your Ansible execution "
                "as KEY=VALUE pairs. Note that if you pass the same "
                "KEY multiple times, the last given VALUE for that same KEY "
                "will override the other(s)"))

        extra_vars_group = parser.add_mutually_exclusive_group(required=False)
        extra_vars_group.add_argument(
            '--extra-vars',
            default=None,
            metavar="key1=<val1> [--extra-vars key3=<val3>]",
            action=KeyValueAction,
            help=(
                "Add Ansible extra variables to the validation(s) execution "
                "as KEY=VALUE pair(s). Note that if you pass the same "
                "KEY multiple times, the last given VALUE for that same KEY "
                "will override the other(s)"))

        extra_vars_group.add_argument(
            '--extra-vars-file',
            action='store',
            default=None,
            help=(
                "Add a JSON/YAML file containing extra variable "
                "to a validation: "
                "--extra-vars-file /home/stack/vars.[json|yaml]."))

        ex_group = parser.add_mutually_exclusive_group(required=True)
        ex_group.add_argument(
            '--validation',
            metavar='<validation_id>[,<validation_id>,...]',
            dest="validation_name",
            action=CommaListAction,
            default=[],
            help=("Run specific validations, "
                  "if more than one validation is required "
                  "separate the names with commas: "
                  "--validation check-ftype,512e | "
                  "--validation 512e"))

        ex_group.add_argument(
            '--group', '-g',
            metavar='<group>[,<group>,...]',
            action=CommaListAction,
            default=[],
            help=("Run specific group validations, "
                  "if more than one group is required "
                  "separate the group names with commas: "
                  "--group pre-upgrade,prep | "
                  "--group openshift-on-openstack"))

        return parser

    def take_action(self, parsed_args):
        """Take validation action"""
        v_actions = ValidationActions(
            validation_path=parsed_args.validation_dir)

        # Ansible execution should be quiet while using the validations_json
        # default callback and be verbose while passing ANSIBLE_SDTOUT_CALLBACK
        # environment variable to Ansible through the --extra-env-vars argument
        quiet_mode = True
        extra_env_vars = parsed_args.extra_env_vars
        if extra_env_vars:
            if "ANSIBLE_STDOUT_CALLBACK" in extra_env_vars.keys():
                quiet_mode = False

        extra_vars = parsed_args.extra_vars
        if parsed_args.extra_vars_file:
            self.app.LOG.debug(
                "Loading extra vars file {}".format(
                    parsed_args.extra_vars_file))

            extra_vars = common.read_extra_vars_file(parsed_args.extra_vars_file)

        try:
            results = v_actions.run_validations(
                inventory=parsed_args.inventory,
                limit_hosts=parsed_args.limit,
                group=parsed_args.group,
                extra_vars=extra_vars,
                validations_dir=parsed_args.validation_dir,
                base_dir=parsed_args.ansible_base_dir,
                validation_name=parsed_args.validation_name,
                extra_env_vars=extra_env_vars,
                python_interpreter=parsed_args.python_interpreter,
                quiet=quiet_mode,
                ssh_user=parsed_args.ssh_user,
                log_path=parsed_args.validation_log_dir
            )
        except RuntimeError as e:
            raise RuntimeError(e)

        if results:
            failed_rc = any([r for r in results if r['Status'] == 'FAILED'])
            if parsed_args.output_log:
                common.write_output(parsed_args.output_log, results)
            if parsed_args.junitxml:
                common.write_junitxml(parsed_args.junitxml, results)
            common.print_dict(results)
            if failed_rc:
                raise RuntimeError("One or more validations have failed.")
        else:
            msg = ("No validation has been run, please check "
                   "log in the Ansible working directory.")
            raise RuntimeError(msg)
