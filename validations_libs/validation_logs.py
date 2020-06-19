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

    def __init__(self, uuid=None, validation_id=None, logfile=None,
                 log_path=constants.VALIDATIONS_LOG_BASEDIR,
                 extension='json'):
        # Set properties
        self.uuid = uuid
        self.validation_id = validation_id
        self.log_path = log_path
        self.extension = extension
        # Get full path and content
        if logfile:
            full_path = logfile
        else:
            full_path = self.get_log_path()
        self.content = self._get_content(full_path)
        self.name = os.path.splitext(os.path.basename(full_path))[0]
        # if we have a log file then extract uuid, validation_id and timestamp
        if logfile:
            try:
                self.uuid, _name = self.name.split('_', 1)
                self.validation_id, self.datetime = _name.rsplit('_', 1)
            except ValueError:
                logging.warning('Wrong log file format, it should be formed '
                                'such as {uuid}_{validation-id}_{timestamp}')

    def _get_content(self, file):
        try:
            with open(file, 'r') as log_file:
                return json.load(log_file)
        except IOError:
            msg = "log file: {} not found".format(file)
            raise IOError(msg)
        except ValueError:
            msg = "bad json format for {}".format(file)
            raise ValueError(msg)

    def get_log_path(self):
        """Return full path of a validation log"""
        # We return occurence 0, because it should be a uniq file name:
        return glob.glob("{}/{}_{}_*.{}".format(self.log_path,
                                                self.uuid, self.validation_id,
                                                self.extension))[0]

    def is_valid_format(self):
        """ Return True if the log file is a valid validation format """
        validation_keys = ['stats', 'validation_output', 'plays']
        return bool(set(validation_keys).intersection(self.content.keys()))

    @property
    def get_logfile_infos(self):
        """
            Return log file information:
            uuid,
            validation_id,
            datetime
        """
        return self.name.replace('.{}'.format(self.extension), '').split('_')

    @property
    def get_logfile_datetime(self):
        """Return log file datetime from a UUID and a validation ID"""
        return self.name.replace('.{}'.format(self.extension),
                                 '').split('_')[2]

    @property
    def get_logfile_content(self):
        """Return logfile content as a dict"""
        return self.content

    @property
    def get_uuid(self):
        """Return log uuid"""
        return self.uuid

    @property
    def get_validation_id(self):
        """Return validation id"""
        return self.validation_id

    @property
    def get_status(self):
        """Return validation status"""
        failed = 0
        for h in self.content['stats'].keys():
            if self.content['stats'][h].get('failures'):
                failed += 1
        return ('FAILED' if failed else 'PASSED')

    @property
    def get_host_group(self):
        """Return host group"""
        return ', '.join([play['play'].get('host') for
                          play in self.content['plays']])

    @property
    def get_hosts_status(self):
        """Return hosts status"""
        hosts = []
        for h in self.content['stats'].keys():
            if self.content['stats'][h].get('failures'):
                hosts.append('{},{}'.format(h, 'FAILED'))
            else:
                hosts.append('{},{}'.format(h, 'PASSED'))
        return ', '.join(hosts)

    @property
    def get_unreachable_hosts(self):
        """Return unreachable hosts"""
        return ', '.join(h for h in self.content['stats'].keys()
                         if self.content['stats'][h].get('unreachable'))

    @property
    def get_duration(self):
        """Return duration of Ansible runtime"""
        duration = [play['play']['duration'].get('time_elapsed') for
                    play in self.content['plays']]
        return ', '.join(filter(None, duration))

    @property
    def get_start_time(self):
        """Return Ansible  start time"""
        start_time = [play['play']['duration'].get('start') for
                      play in self.content['plays']]
        return ', '.join(filter(None, start_time))


class ValidationLogs(object):

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
        """Return logfiles by validation_id"""
        return glob.glob("{}/*_{}_*".format(self.logs_path, validation_id))

    def get_logfile_content_by_validation(self, validation_id):
        """Return logfiles content by validation_id"""
        log_files = glob.glob("{}/*_{}_*".format(self.logs_path,
                                                 validation_id))
        return [self._get_content(log) for log in log_files]

    def get_logfile_by_uuid(self, uuid):
        """Return logfiles by uuid"""
        return glob.glob("{}/{}_*".format(self.logs_path, uuid))

    def get_logfile_content_by_uuid(self, uuid):
        """Return logfiles content by uuid"""
        log_files = glob.glob("{}/{}_*".format(self.logs_path, uuid))
        return [self._get_content(log) for log in log_files]

    def get_logfile_by_uuid_validation_id(self, uuid, validation_id):
        """Return logfiles by uuid"""
        return glob.glob("{}/{}_{}_*".format(self.logs_path, uuid,
                                             validation_id))

    def get_logfile_content_by_uuid_validation_id(self, uuid, validation_id):
        """Return logfiles content filter by uuid and content"""
        log_files = glob.glob("{}/{}_{}_*".format(self.logs_path, uuid,
                                                  validation_id))
        return [self._get_content(log) for log in log_files]

    def get_all_logfiles(self, extension='json'):
        """Return logfiles from logs_path"""
        return [join(self.logs_path, f) for f in os.listdir(self.logs_path) if
                os.path.isfile(join(self.logs_path, f)) and
                extension in os.path.splitext(join(self.logs_path, f))[1]]

    def get_all_logfiles_content(self):
        """Return logfiles content filter by uuid and content"""
        return [self._get_content(join(self.logs_path, f))
                for f in os.listdir(self.logs_path)
                if os.path.isfile(join(self.logs_path, f))]

    def get_validations_stats(self, logs):
        """
            Return validations stats from log files
            logs: list of dict
        """
        if not isinstance(logs, list):
            logs = [logs]
        # Get validation stats
        total_number = len(logs)
        failed_number = 0
        passed_number = 0
        last_execution = None
        dates = []
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

        return {"Last execution date": last_execution,
                "Number of execution": "Total: {}, Passed: {}, "
                                       "Failed: {}".format(total_number,
                                                           passed_number,
                                                           failed_number)}

    def get_results(self, uuid, validation_id=None):
        """
            Return a list of validation results by uuid
            Can be filter by validation_id
        """
        if isinstance(uuid, list):
            results = []
            for id in uuid:
                results.extend(self.get_logfile_by_uuid_validation_id(
                    id,
                    validation_id)
                               if validation_id else
                               self.get_logfile_by_uuid(id))
        elif isinstance(uuid, str):
            results = (self.get_logfile_by_uuid_validation_id(uuid,
                                                              validation_id)
                       if validation_id else self.get_logfile_by_uuid(uuid))
        else:
            raise RuntimeError("uuid should be either a str or a list")
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
