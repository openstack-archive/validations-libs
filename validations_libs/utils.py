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
import datetime
import glob
import json
import logging
import os
import six
import time

from validations_libs import constants
from validations_libs.group import Group
from validations_libs.validation import Validation
from uuid import uuid4

LOG = logging.getLogger(__name__ + ".utils")


def current_time():
    """Return current time"""
    return '%sZ' % datetime.datetime.utcnow().isoformat()


def create_artifacts_dir(dir_path=None, prefix=None):
    """Create Ansible artifacts directory"""
    dir_path = (dir_path if dir_path else
                constants.VALIDATION_ANSIBLE_ARTIFACT_PATH)
    validation_uuid = str(uuid4())
    log_dir = "{}/{}_{}_{}".format(dir_path, validation_uuid,
                                   (prefix if prefix else ''), current_time())
    try:
        os.makedirs(log_dir)
        return validation_uuid, log_dir
    except OSError:
        LOG.exception("Error while creating Ansible artifacts log file."
                      "Please check the access rights for {}").format(log_dir)


def parse_all_validations_on_disk(path, groups=None):
    """
        Return a list of validations metadata
        Can be sorted by Groups
    """
    results = []
    validations_abspath = glob.glob("{path}/*.yaml".format(path=path))
    if isinstance(groups, six.string_types):
        group_list = []
        group_list.append(groups)
        groups = group_list

    for pl in validations_abspath:
        val = Validation(pl)
        if not groups or set(groups).intersection(val.groups):
            results.append(val.get_metadata)
    return results


def get_validation_parameters(validation):
    """Return dictionary of parameters"""
    return Validation(validation).get_vars


def read_validation_groups_file(groups_path=None):
    """Load groups.yaml file and return a dictionary with its contents"""
    gp = Group((groups_path if groups_path else
                constants.VALIDATION_GROUPS_INFO))
    return gp.get_data


def get_validation_group_name_list(groups_path=None):
    """Get the validation group name list only"""
    gp = Group((groups_path if groups_path else
                constants.VALIDATION_GROUPS_INFO))
    return gp.get_groups_keys_list


def get_new_validations_logs_on_disk(validations_logs_dir):
    """Return a list of new log execution filenames """
    files = []

    for root, dirs, filenames in os.walk(validations_logs_dir):
        files = [
            f for f in filenames if not f.startswith('processed')
            and os.path.splitext(f)[1] == '.json'
        ]
    return files


def parse_all_validations_logs_on_disk(uuid_run=None, validation_id=None):
    results = []
    path = constants.VALIDATIONS_LOG_BASEDIR
    logfile = "{}/*.json".format(path)

    if validation_id:
        logfile = "{}/*_{}_*.json".format(path, validation_id)
    if uuid_run:
        logfile = "{}/*_{}_*.json".format(path, uuid_run)

    logfiles_path = glob.glob(logfile)

    for logfile_path in logfiles_path:
        with open(logfile_path, 'r') as log:
            contents = json.load(log)
        results.append(contents)
    return results


def get_validations_details(validation):
    """Return validations information"""
    results = parse_all_validations_on_disk(constants.ANSIBLE_VALIDATION_DIR)
    for r in results:
        if r['id'] == validation:
            return r
    return {}


def get_validations_data(validation):
    """
    Return validations data with format:
    ID, Name, Description, Groups, Other param
    """
    return Validation(validation).get_formated_data


def get_validations_stats(log):
    """Return validations stats from a log file"""
    # Get validation stats
    total_number = len(log)
    failed_number = 0
    passed_number = 0
    last_execution = None
    dates = []

    for l in log:
        if l.get('validation_output'):
            failed_number += 1
        else:
            passed_number += 1

        date_time = \
            l['plays'][0]['play']['duration'].get('start').split('T')
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


def get_validations_parameters(validations_data, validation_name=[],
                               groups=[]):
    params = {}
    for val in validations_data['validations']:
        v = Validation(val)
        if v.id in validation_name or set(groups).intersection(v.groups):
            params[v.id] = {
                'parameters': (val.get('metadata') if val.get('metadata') else
                               val.get('parameters'))
            }
    return params
