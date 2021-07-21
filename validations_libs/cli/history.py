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

from validations_libs import constants
from validations_libs.validation_actions import ValidationActions
from validations_libs.validation_logs import ValidationLogs
from validations_libs.cli.base import BaseCommand
from validations_libs.cli.base import BaseLister


class ListHistory(BaseLister):
    """Display Validations execution history"""

    def get_parser(self, parser):
        parser = super(ListHistory, self).get_parser(parser)

        parser.add_argument('--validation',
                            metavar="<validation_id>",
                            type=str,
                            help='Display execution history for a validation')
        parser.add_argument('--limit',
                            dest='history_limit',
                            type=int,
                            default=15,
                            help=(
                                'Display <n> most recent '
                                'runs of the selected <validation>. '
                                '<n> must be > 0\n'
                                'The default display limit is set to 15.\n'))
        parser.add_argument('--validation-log-dir', dest='validation_log_dir',
                            default=constants.VALIDATIONS_LOG_BASEDIR,
                            help=("Path where the validation log files "
                                  "is located."))
        return parser

    def take_action(self, parsed_args):

        if parsed_args.history_limit < 1:
            raise ValueError(
                (
                    "Number <n> of the most recent runs must be > 0. "
                    "You have provided {}").format(
                        parsed_args.history_limit))
        self.app.LOG.info(
            (
                "Limiting output to the maximum of "
                "{} last validations.").format(
                parsed_args.history_limit))

        actions = ValidationActions()

        return actions.show_history(
            validation_ids=parsed_args.validation,
            log_path=parsed_args.validation_log_dir,
            history_limit=parsed_args.history_limit)


class GetHistory(BaseCommand):
    """Display details about a specific Validation execution"""

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

        self.app.LOG.debug(
            (
                "Obtaining information about the validation run {}\n"
                "From directory {}"
            ).format(
                parsed_args.uuid,
                parsed_args.validation_log_dir))

        vlogs = ValidationLogs(logs_path=parsed_args.validation_log_dir)

        try:
            log_files = vlogs.get_logfile_content_by_uuid(parsed_args.uuid)
        except IOError as io_error:
            raise RuntimeError(
                (
                    "Encountered a following IO error while attempting read a log "
                    "file linked to UUID: {} .\n"
                    "{}"
                ).format(
                    parsed_args.uuid,
                    io_error))

        if log_files:
            if parsed_args.full:
                for log_file in log_files:
                    print(json.dumps(log_file, indent=4, sort_keys=True))
            else:
                for log_file in log_files:
                    for validation_result in log_file.get('validation_output', []):
                        print(json.dumps(validation_result['task'],
                                         indent=4,
                                         sort_keys=True))
        else:
            raise RuntimeError(
                "Could not find the log file linked to this UUID: {}".format(
                parsed_args.uuid))
