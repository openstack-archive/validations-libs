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
import os
import sys

from cliff.command import Command
from cliff.lister import Lister

from validations_libs import constants
from validations_libs.validation_actions import ValidationActions
from validations_libs.validation_logs import ValidationLogs


class ListHistory(Lister):
    """Display Validations execution history"""

    def get_parser(self, parser):
        parser = super(ListHistory, self).get_parser(parser)

        parser.add_argument('--validation',
                            metavar="<validation>",
                            type=str,
                            help='Display execution history for a validation')
        parser.add_argument('--validation-log-dir', dest='validation_log_dir',
                            default=constants.VALIDATIONS_LOG_BASEDIR,
                            help=("Path where the validation log files "
                                  "is located."))
        return parser

    def take_action(self, parsed_args):
        actions = ValidationActions(parsed_args.validation_log_dir)
        return actions.show_history(parsed_args.validation)


class GetHistory(Command):
    """Display details about a Validation execution"""

    def get_parser(self, parser):
        parser = super(GetHistory, self).get_parser(parser)
        parser.add_argument('uuid',
                            metavar="<uuid>",
                            type=str,
                            help='Validation UUID Run')

        parser.add_argument('--full',
                            action='store_true',
                            help='Show Full Details for the run')

        parser.add_argument('--validation-log-dir', dest='validation_log_dir',
                            default=constants.VALIDATIONS_LOG_BASEDIR,
                            help=("Path where the validation log files "
                                  "is located."))
        return parser

    def take_action(self, parsed_args):
        vlogs = ValidationLogs(logs_path=parsed_args.validation_log_dir)
        data = vlogs.get_logfile_content_by_uuid(parsed_args.uuid)
        if data:
            if parsed_args.full:
                for d in data:
                    print(json.dumps(d, indent=4, sort_keys=True))
            else:
                for d in data:
                    for p in d.get('validation_output', []):
                        print(json.dumps(p['task'],
                                         indent=4,
                                         sort_keys=True))
        else:
            raise RuntimeError(
                "Could not find the log file linked to this UUID: %s" %
                parsed_args.uuid)
