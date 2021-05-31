#   Copyright 2020 Red Hat, Inc.
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

from validations_libs.validation_logs import ValidationLogs
from validations_libs.tests import fakes


class TestValidationLogs(TestCase):

    def setUp(self):
        super(TestValidationLogs, self).setUp()

    @mock.patch('json.load', return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST)
    @mock.patch('six.moves.builtins.open')
    def test_validation_log_file(self, mock_open, mock_json):
        vlogs = ValidationLogs('/tmp/foo')
        content = vlogs._get_content('/tmp/foo/bar.json')
        self.assertEqual(content, fakes.VALIDATIONS_LOGS_CONTENTS_LIST)

    @mock.patch('six.moves.builtins.open')
    def test_log_not_found(self, mock_open):
        mock_open.side_effect = IOError()
        vlogs = ValidationLogs()
        self.assertRaises(
            IOError,
            vlogs._get_content,
            '/var/log/non-existing.json'
        )

    @mock.patch('glob.glob')
    @mock.patch('json.load')
    @mock.patch('six.moves.builtins.open')
    def test_get_logfile_by_validation(self, mock_open, mock_json, mock_glob):
        mock_glob.return_value = \
            ['/tmp/123_foo_2020-03-30T13:17:22.447857Z.json']
        vlogs = ValidationLogs('/tmp/foo')
        log = vlogs.get_logfile_by_validation('foo')
        self.assertEqual(log,
                         ['/tmp/123_foo_2020-03-30T13:17:22.447857Z.json'])

    @mock.patch('glob.glob')
    @mock.patch('json.load',
                return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_get_logfile_content_by_validation(self, mock_open, mock_json,
                                               mock_glob):
        mock_glob.return_value = \
            ['/tmp/123_foo_2020-03-30T13:17:22.447857Z.json']
        vlogs = ValidationLogs('/tmp/foo')
        content = vlogs.get_logfile_content_by_validation('foo')
        self.assertEqual(content, fakes.VALIDATIONS_LOGS_CONTENTS_LIST)

    @mock.patch('glob.glob')
    @mock.patch('json.load')
    @mock.patch('six.moves.builtins.open')
    def test_get_logfile_by_uuid(self, mock_open, mock_json, mock_glob):
        mock_glob.return_value = \
            ['/tmp/123_foo_2020-03-30T13:17:22.447857Z.json']
        vlogs = ValidationLogs('/tmp/foo')
        log = vlogs.get_logfile_by_uuid('123')
        self.assertEqual(log,
                         ['/tmp/123_foo_2020-03-30T13:17:22.447857Z.json'])

    @mock.patch('glob.glob')
    @mock.patch('json.load',
                return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_get_logfile_content_by_uuid(self, mock_open, mock_json,
                                         mock_glob):
        mock_glob.return_value = \
            ['/tmp/123_foo_2020-03-30T13:17:22.447857Z.json']
        vlogs = ValidationLogs('/tmp/foo')
        content = vlogs.get_logfile_content_by_uuid('123')
        self.assertEqual(content, fakes.VALIDATIONS_LOGS_CONTENTS_LIST)

    @mock.patch('glob.glob')
    @mock.patch('json.load')
    @mock.patch('six.moves.builtins.open')
    def test_get_logfile_by_uuid_validation_id(self, mock_open, mock_json,
                                               mock_glob):
        mock_glob.return_value = \
            ['/tmp/123_foo_2020-03-30T13:17:22.447857Z.json']
        vlogs = ValidationLogs('/tmp/foo')
        log = vlogs.get_logfile_by_uuid_validation_id('123', 'foo')
        self.assertEqual(log,
                         ['/tmp/123_foo_2020-03-30T13:17:22.447857Z.json'])

    @mock.patch('glob.glob')
    @mock.patch('json.load',
                return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_get_logfile_content_by_uuid_validation_id(self, mock_open,
                                                       mock_json,
                                                       mock_glob):
        mock_glob.return_value = \
            ['/tmp/123_foo_2020-03-30T13:17:22.447857Z.json']
        vlogs = ValidationLogs('/tmp/foo')
        content = vlogs.get_logfile_content_by_uuid_validation_id('123', 'foo')
        self.assertEqual(content, fakes.VALIDATIONS_LOGS_CONTENTS_LIST)

    @mock.patch('os.path.isfile')
    @mock.patch('os.listdir')
    @mock.patch('json.load',
                return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_get_all_logfiles(self, mock_open, mock_json,
                              mock_listdir, mock_isfile):
        mock_listdir.return_value = \
            ['/tmp/123_foo_2020-03-30T13:17:22.447857Z.json']
        mock_isfile.return_value = True
        vlogs = ValidationLogs('/tmp/foo')
        log = vlogs.get_all_logfiles()
        self.assertEqual(log,
                         ['/tmp/123_foo_2020-03-30T13:17:22.447857Z.json'])

    @mock.patch('os.path.isfile')
    @mock.patch('os.listdir')
    @mock.patch('json.load',
                return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_get_all_logfiles_yaml(self, mock_open, mock_json,
                                   mock_listdir, mock_isfile):
        mock_listdir.return_value = \
            ['/tmp/123_foo_2020-03-30T13:17:22.447857Z.json',
             '/tmp/123_foo_2020-03-30T13:17:22.447857Z.yaml']
        mock_isfile.return_value = True
        vlogs = ValidationLogs('/tmp/foo')
        log = vlogs.get_all_logfiles(extension='yaml')
        self.assertEqual(log,
                         ['/tmp/123_foo_2020-03-30T13:17:22.447857Z.yaml'])

    @mock.patch('os.path.isfile')
    @mock.patch('os.listdir')
    @mock.patch('json.load',
                return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_get_all_logfiles_bad_name(self, mock_open, mock_json,
                                       mock_listdir, mock_isfile):
        mock_listdir.return_value = \
            ['/tmp/123_foo_2020-03-30T13:17:22.447857Z.json',
             '/tmp/fooo_json.py']
        mock_isfile.return_value = True
        vlogs = ValidationLogs('/tmp/foo')
        log = vlogs.get_all_logfiles()
        self.assertEqual(log,
                         ['/tmp/123_foo_2020-03-30T13:17:22.447857Z.json'])

    @mock.patch('os.path.isfile')
    @mock.patch('os.listdir')
    @mock.patch('json.load',
                return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_get_all_logfiles_content(self, mock_open, mock_json,
                                      mock_listdir, mock_isfile):
        mock_listdir.return_value = \
            ['/tmp/123_foo_2020-03-30T13:17:22.447857Z.json']
        mock_isfile.return_value = True
        vlogs = ValidationLogs('/tmp/foo')
        content = vlogs.get_all_logfiles_content()
        self.assertEqual(content, fakes.VALIDATIONS_LOGS_CONTENTS_LIST)

    @mock.patch('json.load',
                return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_get_validations_stats(self, mock_open, mock_json):
        vlogs = ValidationLogs('/tmp/foo')
        content = vlogs.get_validations_stats(
            fakes.VALIDATIONS_LOGS_CONTENTS_LIST)
        self.assertEqual(content, fakes.VALIDATIONS_STATS)

    @mock.patch('validations_libs.validation_logs.ValidationLogs.'
                'get_logfile_by_uuid_validation_id')
    @mock.patch('json.load',
                return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_get_results(self, mock_open, mock_json, mock_get_validation):
        mock_get_validation.return_value = \
            ['/tmp/123_foo_2020-03-30T13:17:22.447857Z.json']
        vlogs = ValidationLogs('/tmp/foo')
        content = vlogs.get_results(uuid='123', validation_id='foo')
        self.assertEqual(content, [{
            'UUID': '123',
            'Validations': 'foo',
            'Status': 'PASSED',
            'Status_by_Host': 'undercloud,PASSED',
            'Host_Group': 'undercloud',
            'Unreachable_Hosts': '',
            'Duration': '0:00:03.753',
            'Validations': 'foo'}])

    def test_get_results_none(self):
        vlogs = ValidationLogs('/tmp/foo')
        self.assertRaises(RuntimeError, vlogs.get_results, uuid=None)

    @mock.patch('validations_libs.validation_logs.ValidationLogs.'
                'get_logfile_by_uuid_validation_id')
    @mock.patch('json.load',
                return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_get_results_list(self, mock_open, mock_json, mock_get_validation):
        mock_get_validation.return_value = \
            ['/tmp/123_foo_2020-03-30T13:17:22.447857Z.json']
        vlogs = ValidationLogs('/tmp/foo')
        content = vlogs.get_results(uuid=['123', '123'], validation_id='foo')
        self.assertEqual(content, [
            {
                'UUID': '123',
                'Validations': 'foo',
                'Status': 'PASSED',
                'Status_by_Host': 'undercloud,PASSED',
                'Host_Group': 'undercloud',
                'Unreachable_Hosts': '',
                'Duration': '0:00:03.753',
                'Validations': 'foo'},
            {
                'UUID': '123',
                'Validations': 'foo',
                'Status': 'PASSED',
                'Status_by_Host': 'undercloud,PASSED',
                'Host_Group': 'undercloud',
                'Unreachable_Hosts': '',
                'Duration': '0:00:03.753',
                'Validations': 'foo'}])
