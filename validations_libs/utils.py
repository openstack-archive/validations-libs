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
import uuid
import yaml

from os.path import join
from validations_libs import constants
from validations_libs.group import Group
from validations_libs.validation import Validation

LOG = logging.getLogger(__name__ + ".utils")


def current_time():
    """Return current time"""
    return '%sZ' % datetime.datetime.utcnow().isoformat()


def create_artifacts_dir(dir_path=None, prefix=None):
    """Create Ansible artifacts directory"""
    dir_path = (dir_path if dir_path else
                constants.VALIDATION_ANSIBLE_ARTIFACT_PATH)
    validation_uuid = str(uuid.uuid4())
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
        groups = [groups]

    for pl in validations_abspath:
        val = Validation(pl)
        if not groups or set(groups).intersection(val.groups):
            results.append(val.get_metadata)
    return results


def get_validations_playbook(path, validation_id, groups=None):
    """
        Return a list of validations playbook
        Can be sorted by Groups
    """
    if isinstance(groups, six.string_types):
        groups = [groups]
    pl = []
    for f in os.listdir(path):
        pl_path = join(path, f)
        if os.path.isfile(pl_path):
            if os.path.splitext(f)[0] in validation_id:
                val = Validation(pl_path)
                if not groups or set(groups).intersection(val.groups):
                    pl.append(pl_path)
    return pl


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


def get_validations_details(validation):
    """Return validations information"""
    results = parse_all_validations_on_disk(constants.ANSIBLE_VALIDATION_DIR)
    for r in results:
        if r['id'] == validation:
            return r
    return {}


def get_validations_data(validation, path=constants.ANSIBLE_VALIDATION_DIR):
    """
    Return validations data with format:
    ID, Name, Description, Groups, Other param
    """
    val_path = "{}/{}.yaml".format(path, validation)
    if os.path.exists(val_path):
        return Validation(val_path).get_formated_data


def get_validations_parameters(validations_data, validation_name=[],
                               groups=[], format='json'):
    """
    Return parameters for a list of validations
    The return format can be in json or yaml
    """
    params = {}
    for val in validations_data:
        v = Validation(val)
        if v.id in validation_name or set(groups).intersection(v.groups):
            params[v.id] = {
                'parameters': v.get_vars
            }
    if format not in ['json', 'yaml']:
        msg = 'Invalid output format, {} is not supported'.format(format)
        raise RuntimeError(msg)
    elif format == 'json':
        return json.dumps(params, indent=4, sort_keys=True)
    else:
        return yaml.safe_dump(params, allow_unicode=True,
                              default_flow_style=False, indent=2)
