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
import yaml

from validations_libs import constants
from uuid import uuid4

LOG = logging.getLogger(__name__ + ".utils")


def current_time():
    return '%sZ' % datetime.datetime.utcnow().isoformat()


def create_artifacts_dir(dir_path=None, prefix=None):
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
    results = []
    validations_abspath = glob.glob("{path}/*.yaml".format(path=path))

    if isinstance(groups, six.string_types):
        group_list = []
        group_list.append(groups)
        groups = group_list

    for pl in validations_abspath:
        validation_id, _ext = os.path.splitext(os.path.basename(pl))

        with open(pl, 'r') as val_playbook:
            contents = yaml.safe_load(val_playbook)

        validation_groups = get_validation_metadata(contents, 'groups') or []
        if not groups or set.intersection(set(groups), set(validation_groups)):
            results.append({
                'id': validation_id,
                'name': get_validation_metadata(contents, 'name'),
                'groups': get_validation_metadata(contents, 'groups'),
                'description': get_validation_metadata(contents,
                                                       'description'),
                'parameters': get_validation_parameters(contents)
            })
    return results


def parse_all_validation_groups_on_disk(groups_file_path=None):
    results = []

    if not groups_file_path:
        groups_file_path = constants.VALIDATION_GROUPS_INFO

    if not os.path.exists(groups_file_path):
        return results

    with open(groups_file_path, 'r') as grps:
        contents = yaml.safe_load(grps)

    for grp_name, grp_desc in sorted(contents.items()):
        results.append((grp_name, grp_desc[0].get('description')))

    return results


def get_validation_metadata(validation, key):
    default_metadata = {
        'name': 'Unnamed',
        'description': 'No description',
        'stage': 'No stage',
        'groups': [],
    }

    try:
        return validation[0]['vars']['metadata'].get(key,
                                                     default_metadata[key])
    except KeyError:
        LOG.exception("Key '{key}' not even found in "
                      "default metadata").format(key=key)
    except TypeError:
        LOG.exception("Failed to get validation metadata.")


def get_validation_parameters(validation):
    try:
        return {
            k: v
            for k, v in validation[0]['vars'].items()
            if k != 'metadata'
        }
    except KeyError:
        LOG.debug("No parameters found for this validation")
        return dict()


def read_validation_groups_file(groups_file_path=None):
    """Load groups.yaml file and return a dictionary with its contents"""
    if not groups_file_path:
        groups_file_path = constants.VALIDATION_GROUPS_INFO

    if not os.path.exists(groups_file_path):
        return []

    with open(groups_file_path, 'r') as grps:
        contents = yaml.safe_load(grps)

    return contents


def get_validation_group_name_list():
    """Get the validation group name list only"""
    results = []

    groups = read_validation_groups_file()

    if groups and isinstance(dict, groups):
        for grp_name in six.viewkeys(groups):
            results.append(grp_name)

    return results


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
    data = {}
    col_keys = ['ID', 'Name', 'Description', 'Groups']
    if isinstance(validation, dict):
        for key in validation.keys():
            if key in map(str.lower, col_keys):
                for k in col_keys:
                    if key == k.lower():
                        output_key = k
                data[output_key] = validation.get(key)
            else:
                # Get all other values:
                data[key] = validation.get(key)
    return data


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
