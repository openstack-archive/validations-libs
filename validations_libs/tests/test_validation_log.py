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

from validations_libs.validation_logs import ValidationLog
from validations_libs.tests import fakes


class TestValidationLog(TestCase):

    def setUp(self):
        super(TestValidationLog, self).setUp()

    @mock.patch('json.load')
    @mock.patch('six.moves.builtins.open')
    def test_validation_log_file(self, mock_open, mock_json):
        val = ValidationLog(
            logfile='/tmp/123_foo_2020-03-30T13:17:22.447857Z.json')
        self.assertEqual(val.uuid, '123')
        self.assertEqual(val.validation_id, 'foo')
        self.assertEqual(val.datetime, '2020-03-30T13:17:22.447857Z')

    @mock.patch('json.load')
    @mock.patch('six.moves.builtins.open')
    def test_validation_uuid_wo_validation_id(self, mock_open, mock_json):
        with self.assertRaises(Exception) as exc_mgr:
            ValidationLog(uuid='123')
        self.assertEqual('When not using logfile argument, the uuid and '
                         'validation_id have to be set',
                         str(exc_mgr.exception))

    @mock.patch('json.load')
    @mock.patch('six.moves.builtins.open')
    def test_validation_validation_id_wo_uuid(self, mock_open, mock_json):
        with self.assertRaises(Exception) as exc_mgr:
            ValidationLog(validation_id='foo')
        self.assertEqual('When not using logfile argument, the uuid and '
                         'validation_id have to be set',
                         str(exc_mgr.exception))

    @mock.patch('json.load')
    @mock.patch('six.moves.builtins.open')
    def test_validation_underscore_validation_id(self, mock_open, mock_json):
        val = ValidationLog(
            logfile='/tmp/123_foo_bar_2020-03-30T13:17:22.447857Z.json')
        self.assertEqual(val.uuid, '123')
        self.assertEqual(val.validation_id, 'foo_bar')
        self.assertEqual(val.datetime, '2020-03-30T13:17:22.447857Z')

    @mock.patch('json.load')
    @mock.patch('six.moves.builtins.open')
    def test_validation_wrong_log_file(self, mock_open, mock_json):
        msg = ('Wrong log file format, it should be formed '
               'such as {uuid}_{validation-id}_{timestamp}')
        with mock.patch('logging.Logger.warning') as mock_log:
            ValidationLog(
                logfile='/tmp/foo_2020-03-30T13:17:22.447857Z.json')
            mock_log.assert_called_with(msg)

    @mock.patch('glob.glob')
    @mock.patch('json.load',
                return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_get_log_path(self, mock_open, mock_yaml, mock_glob):
        mock_glob.return_value = \
            ['/tmp/123_foo_2020-03-30T13:17:22.447857Z.json']
        val = ValidationLog(uuid='123', validation_id='foo', log_path='/tmp')
        path = val.get_log_path()
        self.assertEqual(path,
                         '/tmp/123_foo_2020-03-30T13:17:22.447857Z.json')

    @mock.patch('glob.glob')
    @mock.patch('json.load')
    @mock.patch('six.moves.builtins.open')
    def test_get_logfile_infos(self, mock_open, mock_json, mock_glob):
        mock_glob.return_value = \
            ['/tmp/123_foo_2020-03-30T13:17:22.447857Z.json']
        val = ValidationLog(uuid='123', validation_id='foo', log_path='/tmp')
        log_info = val.get_logfile_infos
        self.assertEqual(log_info,
                         ['123', 'foo', '2020-03-30T13:17:22.447857Z'])

    @mock.patch('glob.glob')
    @mock.patch('json.load')
    @mock.patch('six.moves.builtins.open')
    def test_get_logfile_datetime(self, mock_open, mock_json, mock_glob):
        mock_glob.return_value = \
            ['/tmp/123_foo_2020-03-30T13:17:22.447857Z.json']
        val = ValidationLog(uuid='123', validation_id='foo', log_path='/tmp')
        datetime = val.get_logfile_datetime
        self.assertEqual(datetime, '2020-03-30T13:17:22.447857Z')

    @mock.patch('json.load', return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST)
    @mock.patch('six.moves.builtins.open')
    def test_get_logfile_content(self, mock_open, mock_json):
        val = ValidationLog(
            logfile='/tmp/123_foo_2020-03-30T13:17:22.447857Z.json')
        content = val.get_logfile_content
        self.assertEqual(content, fakes.VALIDATIONS_LOGS_CONTENTS_LIST)

    @mock.patch('json.load',
                return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_get_uuid(self, mock_open, mock_json):
        val = ValidationLog(
            logfile='/tmp/123_foo_2020-03-30T13:17:22.447857Z.json')
        uuid = val.get_uuid
        self.assertEqual(uuid, '123')
        self.assertEqual(val.uuid, '123')

    @mock.patch('json.load',
                return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_get_validation_id(self, mock_open, mock_json):
        val = ValidationLog(
            logfile='/tmp/123_foo_2020-03-30T13:17:22.447857Z.json')
        validation_id = val.get_validation_id
        self.assertEqual(validation_id, 'foo')
        self.assertEqual(val.validation_id, 'foo')

    @mock.patch('json.load',
                return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_get_status(self, mock_open, mock_json):
        val = ValidationLog(
            logfile='/tmp/123_foo_2020-03-30T13:17:22.447857Z.json')
        status = val.get_status
        self.assertEqual(status, 'PASSED')

    @mock.patch('json.load',
                return_value=fakes.FAILED_VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_get_status_failed(self, mock_open, mock_json):
        val = ValidationLog(
            logfile='/tmp/123_foo_2020-03-30T13:17:22.447857Z.json')
        status = val.get_status
        self.assertEqual(status, 'FAILED')

    @mock.patch('json.load',
                return_value=fakes.BAD_VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_get_status_unreachable(self, mock_open, mock_json):
        val = ValidationLog(
            logfile='/tmp/123_foo_2020-03-30T13:17:22.447857Z.json')
        status = val.get_status
        self.assertEqual(status, 'FAILED')

    @mock.patch('json.load',
                return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_get_host_group(self, mock_open, mock_json):
        val = ValidationLog(
            logfile='/tmp/123_foo_2020-03-30T13:17:22.447857Z.json')
        host_group = val.get_host_group
        self.assertEqual(host_group, 'undercloud')

    @mock.patch('json.load',
                return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_get_hosts_status(self, mock_open, mock_json):
        val = ValidationLog(
            logfile='/tmp/123_foo_2020-03-30T13:17:22.447857Z.json')
        host_group = val.get_hosts_status
        self.assertEqual(host_group, 'undercloud,PASSED')

    @mock.patch('json.load',
                return_value=fakes.FAILED_VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_get_hosts_status_failed(self, mock_open, mock_json):
        val = ValidationLog(
            logfile='/tmp/123_foo_2020-03-30T13:17:22.447857Z.json')
        host_group = val.get_hosts_status
        self.assertEqual(host_group, 'undercloud,FAILED')

    @mock.patch('json.load',
                return_value=fakes.BAD_VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_get_hosts_status_unreachable(self, mock_open, mock_json):
        val = ValidationLog(
            logfile='/tmp/123_foo_2020-03-30T13:17:22.447857Z.json')
        host_group = val.get_hosts_status
        self.assertEqual(host_group, 'undercloud,UNREACHABLE')

    @mock.patch('json.load',
                return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_get_unreachable_hosts(self, mock_open, mock_json):
        val = ValidationLog(
            logfile='/tmp/123_foo_2020-03-30T13:17:22.447857Z.json')
        unreachable = val.get_unreachable_hosts
        self.assertEqual(unreachable, '')

    @mock.patch('json.load',
                return_value=fakes.BAD_VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_get_unreachable_hosts_bad_data(self, mock_open, mock_json):
        val = ValidationLog(
            logfile='/tmp/123_foo_2020-03-30T13:17:22.447857Z.json')
        unreachable = val.get_unreachable_hosts
        self.assertEqual(unreachable, 'undercloud')

    @mock.patch('json.load',
                return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_get_duration(self, mock_open, mock_json):
        val = ValidationLog(
            logfile='/tmp/123_foo_2020-03-30T13:17:22.447857Z.json')
        duration = val.get_duration
        self.assertEqual(duration, '0:00:03.753')

    @mock.patch('json.load',
                return_value=fakes.BAD_VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_get_duration_bad_data(self, mock_open, mock_json):
        val = ValidationLog(
            logfile='/tmp/123_foo_2020-03-30T13:17:22.447857Z.json')
        duration = val.get_duration
        self.assertEqual(duration, '')

    @mock.patch('json.load',
                return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_get_start_time(self, mock_open, mock_json):
        val = ValidationLog(
            logfile='/tmp/123_foo_2020-03-30T13:17:22.447857Z.json')
        start_time = val.get_start_time
        self.assertEqual(start_time, '2019-11-25T13:40:14.404623Z')

    @mock.patch('json.load',
                return_value=fakes.BAD_VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_get_start_time_bad_data(self, mock_open, mock_json):
        val = ValidationLog(
            logfile='/tmp/123_foo_2020-03-30T13:17:22.447857Z.json')
        start_time = val.get_start_time
        self.assertEqual(start_time, '')

    @mock.patch('six.moves.builtins.open')
    def test_log_not_found(self, mock_open):
        mock_open.side_effect = IOError()
        self.assertRaises(
            IOError,
            ValidationLog,
            logfile='/tmp/fakelogs/non-existing.yaml'
        )

    def test_log_not_abs_path(self):
        self.assertRaises(
            ValueError,
            ValidationLog,
            logfile='fake.yaml'
        )

    @mock.patch('json.load')
    @mock.patch('six.moves.builtins.open')
    def test_log_bad_json(self, mock_open, mock_json):
        mock_json.side_effect = ValueError()
        self.assertRaises(
            ValueError,
            ValidationLog,
            logfile='bad.json'
        )

    @mock.patch('json.load',
                return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_is_valid_format(self, mock_open, mock_json):
        val = ValidationLog(
            logfile='/tmp/123_foo_2020-03-30T13:17:22.447857Z.json')
        self.assertTrue(val.is_valid_format())

    @mock.patch('json.load',
                return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_get_plays(self, mock_open, mock_json):
        val = ValidationLog(
            logfile='/tmp/123_foo_2020-03-30T13:17:22.447857Z.json')
        plays = val.get_plays
        self.assertEqual(
            plays,
            [fakes.VALIDATIONS_LOGS_CONTENTS_LIST[0]['plays'][0]['play']])

    @mock.patch('json.load',
                return_value=fakes.VALIDATIONS_LOGS_CONTENTS_LIST[0])
    @mock.patch('six.moves.builtins.open')
    def test_get_tasks_data(self, mock_open, mock_json):
        val = ValidationLog(
            logfile='/tmp/123_foo_2020-03-30T13:17:22.447857Z.json')
        tasks_data = val.get_tasks_data
        self.assertEqual(
            tasks_data,
            [
                fakes.VALIDATIONS_LOGS_CONTENTS_LIST[0]
                ['validation_output'][0]['task']])
