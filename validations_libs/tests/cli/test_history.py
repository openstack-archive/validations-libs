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

from validations_libs.cli import history
from validations_libs.tests import fakes
from validations_libs.tests.cli.fakes import BaseCommand


class TestListHistory(BaseCommand):

    def setUp(self):
        super(TestListHistory, self).setUp()
        self.cmd = history.ListHistory(self.app, None)

    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'show_history',
                autospec=True)
    def test_list_history(self, mock_history):
        arglist = ['--validation-log-dir', '/foo/log/dir']
        verifylist = [('validation_log_dir', '/foo/log/dir')]

        self._set_args(arglist)
        col = ('UUID', 'Validations', 'Status', 'Execution at', 'Duration')
        values = [('008886df-d297-1eaa-2a74-000000000008',
                   '512e', 'PASSED',
                   '2019-11-25T13:40:14.404623Z',
                   '0:00:03.753')]
        mock_history.return_value = (col, values)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.assertEqual(result, (col, values))

    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'show_history')
    @mock.patch('validations_libs.utils.load_config',
                return_value=fakes.DEFAULT_CONFIG)
    def test_list_history_limit_with_config(self, mock_config, mock_history):
        arglist = ['--validation-log-dir', '/foo/log/dir']
        verifylist = [('validation_log_dir', '/foo/log/dir')]
        self._set_args(arglist)

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertEqual(parsed_args.history_limit, 15)

    @mock.patch('validations_libs.validation_actions.ValidationActions.'
                'show_history')
    @mock.patch('validations_libs.utils.load_config',
                return_value=fakes.WRONG_HISTORY_CONFIG)
    def test_list_history_limit_with_wrong_config(self, mock_config,
                                                  mock_history):
        arglist = ['--validation-log-dir', '/foo/log/dir']
        verifylist = [('validation_log_dir', '/foo/log/dir')]
        self._set_args(arglist)

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(ValueError, self.cmd.take_action, parsed_args)
        self.assertEqual(parsed_args.history_limit, 0)


class TestGetHistory(BaseCommand):

    def setUp(self):
        super(TestGetHistory, self).setUp()
        self.cmd = history.GetHistory(self.app, None)

    @mock.patch('validations_libs.validation_logs.ValidationLogs.'
                'get_logfile_content_by_uuid',
                return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST,
                autospec=True)
    def test_get_history(self, mock_logs):
        arglist = ['123']
        verifylist = [('uuid', '123')]
        self._set_args(arglist)

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

    @mock.patch('validations_libs.validation_logs.ValidationLogs.'
                'get_logfile_content_by_uuid',
                return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST,
                autospec=True)
    def test_get_history_from_log_dir(self, mock_logs):
        arglist = ['123', '--validation-log-dir', '/foo/log/dir']
        verifylist = [('uuid', '123'), ('validation_log_dir', '/foo/log/dir')]

        self._set_args(arglist)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

    @mock.patch('validations_libs.validation_logs.ValidationLogs.'
                'get_logfile_content_by_uuid',
                return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST,
                autospec=True)
    def test_get_history_full_arg(self, mock_logs):
        arglist = ['123', '--full']
        verifylist = [('uuid', '123'), ('full', True)]

        self._set_args(arglist)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
