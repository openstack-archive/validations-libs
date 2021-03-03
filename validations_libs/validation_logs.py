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
import json
import glob
import logging
import os
import time
from os.path import join

from validations_libs import constants

LOG = logging.getLogger(__name__ + ".validation_logs")


class ValidationLog(object):
    """An object for encapsulating a Validation Log file"""

    def __init__(self, uuid=None, validation_id=None, logfile=None,
                 log_path=constants.VALIDATIONS_LOG_BASEDIR,
                 extension='json'):
        """Wrap the Validation Log file

        :param uuid: The uuid of the validation execution
        :type uuid: ``string``
        :param validation_id: The ID of the validation
        :type validation_id: ``string``
        :param logfile: The absolute path of the log file
        :type logfile: ``string`
        :param log_path: The absolute path of the logs directory
        :type log_path: ``string``
        :param extension: The file extension (Default to 'json')
        :type extension: ``string``
        """
        # Set properties
        self.uuid = uuid
        self.validation_id = validation_id
        self.abs_log_path = log_path
        self.extension = extension
        self.content = {}
        self.name = None
        self.datetime = None

        # Get full path and content raise exception if it's impossible
        if logfile:
            if os.path.isabs(logfile):
                self.abs_log_path = logfile
            else:
                raise ValueError(
                'logfile must be absolute path, but is: {}'.format(logfile)
            )
        elif uuid and validation_id:
            self.abs_log_path = self.get_log_path()
        else:
            raise Exception(
                'When not using logfile argument, the uuid and '
                'validation_id have to be set'
            )

        self.content = self._get_content()
        self.name = self._get_name()
        self.datetime = self._get_time()

        # if we have a log file then extract uuid, validation_id and timestamp
        if logfile:
            try:
                self.uuid, _name = self.name.split('_', 1)
                self.validation_id, self.datetime = _name.rsplit('_', 1)
            except ValueError:
                logging.warning('Wrong log file format, it should be formed '
                                'such as {uuid}_{validation-id}_{timestamp}')

    def _get_content(self):
        try:
            with open(self.abs_log_path, 'r') as log_file:
                return json.load(log_file)
        except IOError:
            msg = "log file: {} not found".format(self.abs_log_path)
            raise IOError(msg)
        except ValueError:
            msg = "bad json format for {}".format(self.abs_log_path)
            raise ValueError(msg)

    def get_log_path(self):
        """Return full path of a validation log"""
        # We return occurence 0, because it should be a uniq file name:
        return glob.glob("{}/{}_{}_*.{}".format(self.abs_log_path,
                                                self.uuid, self.validation_id,
                                                self.extension))[0]

    def _get_name(self):
        """Return name of the log file under the self.full_path

        :rtype: ``string``
        """
        return os.path.splitext(os.path.basename(self.abs_log_path))[0]

    def _get_time(self):
        """Return time component of the log file name

        :rtype: ``string``
        """
        return self.name.rsplit('_', 1)[-1]

    def is_valid_format(self):
        """Return True if the log file is a valid validation format

        The validation log file has to contain three level of data.

        - ``plays`` will contain the Ansible execution logs of the playbooks
        - ``stat`` will contain the statistics for each targeted hosts
        - ``validation_output`` will contain only the warning or failed tasks

        .. code:: bash

            {
              'plays': [],
              'stats': {},
              'validation_output': []
            }

        :return: ``True`` if the log file is valid, ``False`` if not.
        :rtype: ``boolean``
        """
        validation_keys = ['stats', 'validation_output', 'plays']
        return bool(set(validation_keys).intersection(self.content.keys()))

    @property
    def get_logfile_infos(self):
        """Return log file information from the log file basename

        :return: A list with the UUID, the validation name and the
                 datetime of the log file
        :rtype: ``list``

        :Example:

        >>> logfile = '/tmp/123_foo_2020-03-30T13:17:22.447857Z.json'
        >>> val = ValidationLog(logfile=logfile)
        >>> print(val.get_logfile_infos)
        ['123', 'foo', '2020-03-30T13:17:22.447857Z']
        """
        return self.name.replace('.{}'.format(self.extension), '').split('_')

    @property
    def get_logfile_datetime(self):
        """Return log file datetime from a UUID and a validation ID

        :return: The datetime of the log file
        :rtype: ``list``

        :Example:

        >>> logfile = '/tmp/123_foo_2020-03-30T13:17:22.447857Z.json'
        >>> val = ValidationLog(logfile=logfile)
        >>> print(val.get_logfile_datetime)
        ['2020-03-30T13:17:22.447857Z']
        """
        return self.name.replace('.{}'.format(self.extension),
                                 '').split('_')[2]

    @property
    def get_logfile_content(self):
        """Return logfile content

        :rtype: ``dict``
        """
        return self.content

    @property
    def get_uuid(self):
        """Return log uuid

        :rtype: ``string``
        """
        return self.uuid

    @property
    def get_validation_id(self):
        """Return validation id

        :rtype: ``string``
        """
        return self.validation_id

    @property
    def get_status(self):
        """Return validation status

        :return: 'FAILED' if there is failure(s), 'PASSED' if not.
                 If no tasks have been executed, it returns 'NOT_RUN'.
        :rtype: ``string``
        """
        failed = 0
        for h in self.content['stats'].keys():
            if self.content['stats'][h].get('failures'):
                failed += 1
            if self.content['stats'][h].get('unreachable'):
                failed += 1
        return ('FAILED' if failed else 'PASSED')

    @property
    def get_host_group(self):
        """Return host group

        :return: A comma-separated list of host(s)
        :rtype: ``string``
        """
        return ', '.join([play['play'].get('host') for
                          play in self.content['plays']])

    @property
    def get_hosts_status(self):
        """Return status by host(s)

        :return: A comma-separated string of host with its status
        :rtype: ``string``

        :Example:

        >>> logfile = '/tmp/123_foo_2020-03-30T13:17:22.447857Z.json'
        >>> val = ValidationLog(logfile=logfile)
        >>> print(val.get_hosts_status)
        'localhost,PASSED, webserver1,FAILED, webserver2,PASSED'
        """
        hosts = []
        for h in self.content['stats'].keys():
            if self.content['stats'][h].get('failures'):
                hosts.append('{},{}'.format(h, 'FAILED'))
            elif self.content['stats'][h].get('unreachable'):
                hosts.append('{},{}'.format(h, 'UNREACHABLE'))
            else:
                hosts.append('{},{}'.format(h, 'PASSED'))
        return ', '.join(hosts)

    @property
    def get_unreachable_hosts(self):
        """Return unreachable hosts

        :return: A list of unreachable host(s)
        :rtype: ``string``

        :Example:

        - Multiple unreachable hosts

        >>> logfile = '/tmp/123_foo_2020-03-30T13:17:22.447857Z.json'
        >>> val = ValidationLog(logfile=logfile)
        >>> print(val.get_unreachable_hosts)
        'localhost, webserver2'

        - Only one unreachable host

        >>> logfile = '/tmp/123_foo_2020-03-30T13:17:22.447857Z.json'
        >>> val = ValidationLog(logfile=logfile)
        >>> print(val.get_unreachable_hosts)
        'localhost'

        - No unreachable host

        >>> logfile = '/tmp/123_foo_2020-03-30T13:17:22.447857Z.json'
        >>> val = ValidationLog(logfile=logfile)
        >>> print(val.get_unreachable_hosts)
        ''
        """
        return ', '.join(h for h in self.content['stats'].keys()
                         if self.content['stats'][h].get('unreachable'))

    @property
    def get_duration(self):
        """Return duration of Ansible runtime

        :rtype: ``string``
        """
        duration = [play['play']['duration'].get('time_elapsed') for
                    play in self.content['plays']]
        return ', '.join(filter(None, duration))

    @property
    def get_start_time(self):
        """Return Ansible start time

        :rtype: ``string``
        """
        start_time = [play['play']['duration'].get('start') for
                      play in self.content['plays']]
        return ', '.join(filter(None, start_time))

    @property
    def get_plays(self):
        """Return a list of Playbook data"""
        return [play['play'] for play in self.content['plays']]

    @property
    def get_tasks_data(self):
        """Return a list of task from validation output"""
        return [output['task'] for output in self.content['validation_output']]


class ValidationLogs(object):
    """An object for encapsulating the Validation Log files"""

    def __init__(self, logs_path=constants.VALIDATIONS_LOG_BASEDIR):
        self.logs_path = logs_path

    def _get_content(self, file):
        try:
            with open(file, 'r') as log_file:
                return json.load(log_file)
        except IOError:
            msg = "log file: {} not found".format(file)
            raise IOError(msg)

    def get_logfile_by_validation(self, validation_id):
        """Return logfiles by validation_id

        :param validation_id: The ID of the validation
        :type validation_id: ``string``

        :return: The list of the log files for a validation
        :rtype: ``list``
        """
        return glob.glob("{}/*_{}_*".format(self.logs_path, validation_id))

    def get_logfile_content_by_validation(self, validation_id):
        """Return logfiles content by validation_id

        :param validation_id: The ID of the validation
        :type validation_id: ``string``

        :return: The list of the log files contents for a validation
        :rtype: ``list``
        """
        log_files = glob.glob("{}/*_{}_*".format(self.logs_path,
                                                 validation_id))
        LOG.debug(
            "Getting log file for validation {} from {}.".format(
                validation_id,
                log_files)
        )
        return [self._get_content(log) for log in log_files]

    def get_logfile_by_uuid(self, uuid):
        """Return logfiles by uuid

        :param uuid: The UUID of the validation execution
        :type uuid: ``string``

        :return: The list of the log files by UUID
        :rtype: ``list``
        """
        return glob.glob("{}/{}_*".format(self.logs_path, uuid))

    def get_logfile_content_by_uuid(self, uuid):
        """Return logfiles content by uuid

        :param uuid: The UUID of the validation execution
        :type uuid: ``string``

        :return: The list of the log files contents by UUID
        :rtype: ``list``
        """
        log_files = glob.glob("{}/{}_*".format(self.logs_path, uuid))
        return [self._get_content(log) for log in log_files]

    def get_logfile_by_uuid_validation_id(self, uuid, validation_id):
        """Return logfiles by uuid and validation_id

        :param uuid: The UUID of the validation execution
        :type uuid: ``string``
        :param validation_id: The ID of the validation
        :type validation_id: ``string``

        :return: A list of the log files by UUID and validation_id
        :rtype: ``list``
        """
        return glob.glob("{}/{}_{}_*".format(self.logs_path, uuid,
                                             validation_id))

    def get_logfile_content_by_uuid_validation_id(self, uuid, validation_id):
        """Return logfiles content filter by uuid and validation_id

        :param uuid: The UUID of the validation execution
        :type uuid: ``string``
        :param validation_id: The ID of the validation
        :type validation_id: ``string``

        :return: A list of the log files content by UUID and validation_id
        :rtype: ``list``
        """
        log_files = glob.glob("{}/{}_{}_*".format(self.logs_path, uuid,
                                                  validation_id))
        return [self._get_content(log) for log in log_files]

    def get_all_logfiles(self, extension='json'):
        """Return logfiles from logs_path

        :param extension: The extension file (Defaults to 'json')
        :type extension: ``string``

        :return: A list of the absolute path log files
        :rtype: ``list``
        """
        return [join(self.logs_path, f) for f in os.listdir(self.logs_path) if
                os.path.isfile(join(self.logs_path, f)) and extension in
                os.path.splitext(join(self.logs_path, f))[1]]

    def get_all_logfiles_content(self):
        """Return logfiles content

        :return: A list of the contents of every log files available
        :rtype: ``list``
        """
        return [self._get_content(join(self.logs_path, f))
                for f in os.listdir(self.logs_path)
                if os.path.isfile(join(self.logs_path, f))]

    def get_validations_stats(self, logs):
        """Return validations stats from log files

        :param logs: A list of log file contents
        :type logs: ``list``

        :return: Information about validation statistics.
                 ``last execution date`` and ``number of execution``
        :rtype: ``dict``
        """
        if not isinstance(logs, list):
            logs = [logs]

            LOG.debug(
                ("`get_validations_stats` received `logs` argument "
                 "of type {} but it expects a list. "
                 "Attempting to resolve.").format(
                    type(logs))
            )

        # Get validation stats
        total_number = len(logs)
        failed_number = 0
        passed_number = 0
        last_execution = None
        dates = []

        LOG.debug(
            "Retreiving {} validation stats.".format(total_number)
        )

        for log in logs:
            if log.get('validation_output'):
                failed_number += 1
            else:
                passed_number += 1
            date_time = \
                log['plays'][0]['play']['duration'].get('start').split('T')
            date_start = date_time[0]
            time_start = date_time[1].split('Z')[0]
            newdate = \
                time.strptime(date_start + time_start, '%Y-%m-%d%H:%M:%S.%f')
            dates.append(newdate)

        if dates:
            last_execution = time.strftime('%Y-%m-%d %H:%M:%S', max(dates))

        execution_stats = "Total: {}, Passed: {}, Failed: {}".format(
            total_number,
            passed_number,
            failed_number)

        LOG.debug(execution_stats)

        return {"Last execution date": last_execution,
                "Number of execution": execution_stats}

    def get_results(self, uuid, validation_id=None):
        """Return a list of validation results by uuid
        Can be filter by validation_id

        :param uuid: The UUID of the validation execution
        :type uuid: ``string` or ``list``
        :param validation_id: The ID of the validation
        :type validation_id: ``string``

        :return: A list of the log files content by UUID and validation_id
        :rtype: ``list``

        :Example:

        >>> v_logs = ValidationLogs()
        >>> uuid = '78df1c3f-dfc3-4a1f-929e-f51762e67700'
        >>> print(v_logs.get_results(uuid=uuid)
        [{'Duration': '0:00:00.514',
          'Host_Group': 'undercloud,Controller',
          'Status': 'FAILED',
          'Status_by_Host': 'undercloud,FAILED, underclou1d,FAILED',
          'UUID': '78df1c3f-dfc3-4a1f-929e-f51762e67700',
          'Unreachable_Hosts': 'undercloud',
          'Validations': 'check-cpu'}]
        """
        if isinstance(uuid, list):
            results = []
            for identifier in uuid:
                results.extend(self.get_logfile_by_uuid_validation_id(
                    identifier,
                    validation_id)
                               if validation_id else
                               self.get_logfile_by_uuid(identifier))
        elif isinstance(uuid, str):
            results = (self.get_logfile_by_uuid_validation_id(uuid,
                                                              validation_id)
                       if validation_id else self.get_logfile_by_uuid(uuid))
        else:
            raise RuntimeError(
                (
                    "uuid should be either a str or a list"
                    "but is {} instead"
                ).format(type(uuid))
            )

        res = []
        for result in results:
            vlog = ValidationLog(logfile=result)
            data = {}
            data['UUID'] = vlog.get_uuid
            data['Validations'] = vlog.get_validation_id
            data['Status'] = vlog.get_status
            data['Host_Group'] = vlog.get_host_group
            data['Status_by_Host'] = vlog.get_hosts_status
            data['Unreachable_Hosts'] = vlog.get_unreachable_hosts
            data['Duration'] = vlog.get_duration
            res.append(data)
        return res
