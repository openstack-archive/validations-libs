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
import logging
import os
import six
import uuid

from os.path import join
from validations_libs import constants
from validations_libs.group import Group
from validations_libs.validation import Validation

LOG = logging.getLogger(__name__ + ".utils")


def current_time():
    """Return current time"""
    return '%sZ' % datetime.datetime.utcnow().isoformat()


def create_artifacts_dir(dir_path=None, prefix=None):
    """Create Ansible artifacts directory

    :param dir_path: Directory asbolute path
    :type dir_path: `string`
    :param prefix: Playbook name
    :type prefix: `string`
    :return: The UUID of the validation and the absolute Path of the log file
    :rtype: `string`, `string`
    """
    dir_path = (dir_path if dir_path else
                constants.VALIDATION_ANSIBLE_ARTIFACT_PATH)
    validation_uuid = str(uuid.uuid4())
    log_dir = "{}/{}_{}_{}".format(dir_path, validation_uuid,
                                   (prefix if prefix else ''), current_time())
    try:
        os.makedirs(log_dir)
        return validation_uuid, log_dir
    except OSError:
        LOG.exception(
            (
                "Error while creating Ansible artifacts log file."
                "Please check the access rights for {}"
            ).format(log_dir)
        )


def parse_all_validations_on_disk(path, groups=None):
    """Return a list of validations metadata which can be sorted by Groups

    :param path: The absolute path of the validations directory
    :type path: `string`
    :param groups: Groups of validations. Could be a `list` or a
                   comma-separated `string` of groups
    :return: A list of validations metadata.
    :rtype: `list`

    :Example:

    >>> path = '/foo/bar'
    >>> parse_all_validations_on_disk(path)
    [{'description': 'Detect whether the node disks use Advanced Format.',
      'groups': ['prep', 'pre-deployment'],
      'id': '512e',
      'name': 'Advanced Format 512e Support'},
     {'description': 'Make sure that the server has enough CPU cores.',
      'groups': ['prep', 'pre-introspection'],
      'id': 'check-cpu',
      'name': 'Verify if the server fits the CPU core requirements'}]
    """
    results = []
    if not groups:
        groups = []
    else:
        groups = convert_data(groups)

    validations_abspath = glob.glob("{path}/*.yaml".format(path=path))

    for pl in validations_abspath:
        val = Validation(pl)

        if not groups or set(groups).intersection(val.groups):
            results.append(val.get_metadata)
    return results


def get_validations_playbook(path, validation_id=None, groups=None):
    """Get a list of validations playbooks paths either by their names
    or their groups

    :param path: Path of the validations playbooks
    :type path: `string`
    :param validation_id: List of validation name
    :type validation_id: `list` or a `string` of comma-separated validations
    :param groups: List of validation group
    :type groups: `list` or a `string` of comma-separated groups
    :return: A list of absolute validations playbooks path
    :rtype: `list`

    :Example:

    >>> path = '/usr/share/validation-playbooks'
    >>> validation_id = ['512e','check-cpu']
    >>> groups = None
    >>> get_validations_playbook(path, validation_id, groups)
    ['/usr/share/ansible/validation-playbooks/512e.yaml',
     '/usr/share/ansible/validation-playbooks/check-cpu.yaml',]
    """
    if not validation_id:
        validation_id = []
    else:
        validation_id = convert_data(validation_id)

    if not groups:
        groups = []
    else:
        groups = convert_data(groups)

    pl = []
    for f in os.listdir(path):
        pl_path = join(path, f)
        if os.path.isfile(pl_path):
            if validation_id:
                if os.path.splitext(f)[0] in validation_id or \
                        os.path.basename(f) in validation_id:
                    pl.append(pl_path)
            if groups:
                val = Validation(pl_path)
                if set(groups).intersection(val.groups):
                    pl.append(pl_path)
    return pl


def get_validation_parameters(validation):
    """Return dictionary of parameters"""
    return Validation(validation).get_vars


def read_validation_groups_file(groups_path=None):
    """Load groups.yaml file and return a dictionary with its contents

    :params groups_path: The path the groups.yaml file
    :type groups_path: `string`
    :return: The group list with their descriptions
    :rtype: `dict`

    :Example:

    >>> read_validation_groups_file()
    {'group1': [{'description': 'Group1 description.'}],
     'group2': [{'description': 'Group2 description.'}]}
    """
    gp = Group((groups_path if groups_path else
                constants.VALIDATION_GROUPS_INFO))
    return gp.get_data


def get_validation_group_name_list(groups_path=None):
    """Get the validation group name list only

    :params groups_path: The path the groups.yaml file
    :type groups_path: `string`
    :return: The group name list
    :rtype: `list`

    :Example:

    >>> get_validation_group_name_list()
    ['group1',
     'group2',
     'group3',
     'group4']
    """
    gp = Group((groups_path if groups_path else
                constants.VALIDATION_GROUPS_INFO))
    return gp.get_groups_keys_list


def get_validations_details(validation):
    """Return information details for a validation

    :param validation: Name of the validation
    :type validation: `string`
    :return: The information of the validation
    :rtype: `dict`
    :raises: a `TypeError` exception if `validation` is not a string

    :Example:

    >>> validation = "check-something"
    >>> get_validations_details(validation)
    {'description': 'Verify that the server has enough something.',
     'groups': ['group1', 'group2'],
     'id': 'check-something',
     'name': 'Verify the server fits the something requirements'}
    """
    if not isinstance(validation, six.string_types):
        raise TypeError("The input data should be a String")

    results = parse_all_validations_on_disk(constants.ANSIBLE_VALIDATION_DIR)
    for r in results:
        if r['id'] == validation:
            return r
    return {}


def get_validations_data(validation, path=constants.ANSIBLE_VALIDATION_DIR):
    """Return validation data with format:

    ID, Name, Description, Groups, Parameters

    :param validation: Name of the validation without the `yaml` extension.
                       Defaults to `constants.ANSIBLE_VALIDATION_DIR`
    :type validation: `string`
    :param path: The path to the validations directory
    :type path: `string`
    :return: The validation data with the format
             (ID, Name, Description, Groups, Parameters)
    :rtype: `dict`

    :Example:

    >>> validation = 'check-something'
    >>> get_validations_data(validation)
    {'Description': 'Verify that the server has enough something',
     'Groups': ['group1', 'group2'],
     'ID': 'check-something',
     'Name': 'Verify the server fits the something requirements',
     'Parameters': {'param1': 24}}
    """
    if not isinstance(validation, six.string_types):
        raise TypeError("The input data should be a String")

    data = {}
    val_path = "{}/{}.yaml".format(path, validation)
    if os.path.exists(val_path):
        val = Validation(val_path)
        data.update(val.get_formated_data)
        data.update({'Parameters': val.get_vars})
    return data


def get_validations_parameters(validations_data, validation_name=[],
                               groups=[]):
    """Return parameters for a list of validations


    :param validations_data: A list of absolute validations playbooks path
    :type validations_data: `list`
    :param validation_name: A list of validation name
    :type validation_name: `list`
    :param groups: A list of validation groups
    :type groups: `list`
    :return: a dictionary containing the current parameters for
             each `validation_name` or `groups`
    :rtype: `dict`

    :Example:

    >>> validations_data = ['/foo/bar/check-ram.yaml',
                            '/foo/bar/check-cpu.yaml']
    >>> validation_name = ['check-ram', 'check-cpu']
    >>> get_validations_parameters(validations_data, validation_name)
    {'check-cpu': {'parameters': {'minimal_cpu_count': 8}},
     'check-ram': {'parameters': {'minimal_ram_gb': 24}}}
    """
    params = {}
    for val in validations_data:
        v = Validation(val)
        if v.id in validation_name or set(groups).intersection(v.groups):
            params[v.id] = {
                'parameters': v.get_vars
            }

    return params


def convert_data(data=''):
    """Transform a string containing comma-separated validation or group name
    into a list. If `data` is already a list, it will simply return `data`.

    :param data: A string or a list
    :type data: `string` or `list`
    :return: A list of data
    :rtype: `list`
    :raises: a `TypeError` exception if `data` is not a list or a string

    :Example:

    >>> data = "check-cpu,check-ram,check-disk-space"
    >>> convert_data(data)
    ['check-cpu', 'check-ram', 'check-disk-space']
    ...
    >>> data = "check-cpu , check-ram , check-disk-space"
    >>> convert_data(data)
    ['check-cpu', 'check-ram', 'check-disk-space']
    ...
    >>> data = "check-cpu,"
    >>> convert_data(data)
    ['check-cpu']
    ...
    >>> data = ['check-cpu', 'check-ram', 'check-disk-space']
    >>> convert_data(data)
    ['check-cpu', 'check-ram', 'check-disk-space']
    """
    if isinstance(data, six.string_types):
        return [
            conv_data.strip() for conv_data in data.split(',') if conv_data
        ]
    elif not isinstance(data, list):
        raise TypeError("The input data should be either a List or a String")
    else:
        return data
