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


def create_log_dir(log_path=constants.VALIDATIONS_LOG_BASEDIR):
    """Check for presence of the selected validations log dir.
    Create the directory if needed, and use fallback if that
    proves too tall an order.

    Log the failure if encountering OSError or PermissionError.

    :param log_path: path of the selected log directory
    :type log_path: `string`
    :return: valid path to the log directory
    :rtype: `string`

    :raises: RuntimeError if even the fallback proves unavailable.
    """
    try:
        if os.path.exists(log_path):
            if os.access(log_path, os.W_OK):
                return os.path.abspath(log_path)
            else:
                LOG.error(
                    (
                        "Selected log directory '{log_path}' is inaccessible. "
                        "Please check the access rights for: '{log_path}'"
                    ).format(
                        log_path=log_path))
                if log_path != constants.VALIDATIONS_LOG_BASEDIR:
                    LOG.warning(
                    (
                        "Resorting to the preset '{default_log_path}'"
                    ).format(
                        default_log_path=constants.VALIDATIONS_LOG_BASEDIR))

                    return create_log_dir()
                else:
                    raise RuntimeError()
        else:
            LOG.warning(
                (
                    "Selected log directory '{log_path}' does not exist. "
                    "Attempting to create it."
                ).format(
                    log_path=log_path))

            os.makedirs(log_path)
            return os.path.abspath(log_path)
    except (OSError, PermissionError) as error:
        LOG.error(
            (
                "Encountered an {error} while creating the log directory. "
                "Please check the access rights for: '{log_path}'"
            ).format(
                error=error,
                log_path=log_path))

        # Fallback in default path if log_path != from constants path
        if log_path != constants.VALIDATIONS_LOG_BASEDIR:
            LOG.debug(
                (
                    "Resorting to the preset '{default_log_path}'."
                ).format(
                    default_log_path=constants.VALIDATIONS_LOG_BASEDIR))

            return create_log_dir()
        raise RuntimeError()


def create_artifacts_dir(log_path=constants.VALIDATIONS_LOG_BASEDIR,
                         prefix=''):
    """Create Ansible artifacts directory for the validation run
    :param log_path: Directory asbolute path
    :type log_path: `string`
    :param prefix: Playbook name
    :type prefix: `string`
    :return: UUID of the validation run, absolute path of the validation artifacts directory
    :rtype: `string`, `string`
    """
    artifact_dir = os.path.join(log_path, 'artifacts')
    validation_uuid = str(uuid.uuid4())
    validation_artifacts_dir = "{}/{}_{}_{}".format(
        artifact_dir,
        validation_uuid,
        prefix,
        current_time())
    try:
        os.makedirs(validation_artifacts_dir)
        return validation_uuid, os.path.abspath(validation_artifacts_dir)
    except (OSError, PermissionError):
        LOG.exception(
            (
                "Error while creating Ansible artifacts log file. "
                "Please check the access rights for '{}'"
            ).format(validation_artifacts_dir))

        raise RuntimeError()


def parse_all_validations_on_disk(path,
                                  groups=None,
                                  categories=None,
                                  products=None):
    """Return a list of validations metadata which can be sorted by Groups, by
    Categories or by Products.

    :param path: The absolute path of the validations directory
    :type path: `string`

    :param groups: Groups of validations
    :type groups: `list`

    :param categories: Categories of validations
    :type categories: `list`

    :param products: Products of validations
    :type products: `list`

    :return: A list of validations metadata.
    :rtype: `list`

    :Example:

    >>> path = '/foo/bar'
    >>> parse_all_validations_on_disk(path)
    [{'categories': ['storage'],
      'products': ['product1'],
      'description': 'Detect whether the node disks use Advanced Format.',
      'groups': ['prep', 'pre-deployment'],
      'id': '512e',
      'name': 'Advanced Format 512e Support'},
     {'categories': ['system'],
      'products': ['product1'],
      'description': 'Make sure that the server has enough CPU cores.',
      'groups': ['prep', 'pre-introspection'],
      'id': 'check-cpu',
      'name': 'Verify if the server fits the CPU core requirements'}]
    """
    if not isinstance(path, six.string_types):
        raise TypeError("The 'path' argument must be a String")

    if not groups:
        groups = []
    elif not isinstance(groups, list):
        raise TypeError("The 'groups' argument must be a List")

    if not categories:
        categories = []
    elif not isinstance(categories, list):
        raise TypeError("The 'categories' argument must be a List")

    if not products:
        products = []
    elif not isinstance(products, list):
        raise TypeError("The 'products' argument must be a List")

    results = []
    validations_abspath = glob.glob("{path}/*.yaml".format(path=path))

    LOG.debug(
        "Attempting to parse validations by:\n"
        "  - groups: {}\n"
        "  - categories: {}\n"
        "  - products: {}\n"
        "from {}".format(groups, categories, products, validations_abspath)
    )

    for playbook in validations_abspath:
        val = Validation(playbook)

        if not groups and not categories and not products:
            results.append(val.get_metadata)
            continue

        if set(groups).intersection(val.groups) or \
           set(categories).intersection(val.categories) or \
           set(products).intersection(val.products):
            results.append(val.get_metadata)

    return results


def get_validations_playbook(path,
                             validation_id=None,
                             groups=None,
                             categories=None,
                             products=None):
    """Get a list of validations playbooks paths either by their names,
    their groups, by their categories or by their products.

    :param path: Path of the validations playbooks
    :type path: `string`

    :param validation_id: List of validation name
    :type validation_id: `list`

    :param groups: List of validation group
    :type groups: `list`

    :param categories: List of validation category
    :type categories: `list`

    :param products: List of validation product
    :type products: `list`

    :return: A list of absolute validations playbooks path
    :rtype: `list`

    :Example:

    >>> path = '/usr/share/validation-playbooks'
    >>> validation_id = ['512e','check-cpu']
    >>> groups = None
    >>> categories = None
    >>> products = None
    >>> get_validations_playbook(path=path,
                                 validation_id=validation_id,
                                 groups=groups,
                                 categories=categories,
                                 products=products)
    ['/usr/share/ansible/validation-playbooks/512e.yaml',
     '/usr/share/ansible/validation-playbooks/check-cpu.yaml',]
    """
    if not isinstance(path, six.string_types):
        raise TypeError("The 'path' argument must be a String")

    if not validation_id:
        validation_id = []
    elif not isinstance(validation_id, list):
        raise TypeError("The 'validation_id' argument must be a List")

    if not groups:
        groups = []
    elif not isinstance(groups, list):
        raise TypeError("The 'groups' argument must be a List")

    if not categories:
        categories = []
    elif not isinstance(categories, list):
        raise TypeError("The 'categories' argument must be a List")

    if not products:
        products = []
    elif not isinstance(products, list):
        raise TypeError("The 'products' argument must be a List")

    pl = []
    for f in os.listdir(path):
        pl_path = join(path, f)
        if os.path.isfile(pl_path):
            if validation_id:
                if os.path.splitext(f)[0] in validation_id or \
                        os.path.basename(f) in validation_id:
                    pl.append(pl_path)

            val = Validation(pl_path)
            if groups:
                if set(groups).intersection(val.groups):
                    pl.append(pl_path)
            if categories:
                if set(categories).intersection(val.categories):
                    pl.append(pl_path)
            if products:
                if set(products).intersection(val.products):
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
     'categories': ['category1', 'category2'],
     'products': ['product1', 'product2'],
     'id': 'check-something',
     'name': 'Verify the server fits the something requirements'}
    """
    if not isinstance(validation, six.string_types):
        raise TypeError("The 'validation' argument must be a String")

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
     'Categories': ['category1', 'category2'],
     'products': ['product1', 'product2'],
     'ID': 'check-something',
     'Name': 'Verify the server fits the something requirements',
     'Parameters': {'param1': 24}}
    """
    if not isinstance(validation, six.string_types):
        raise TypeError("The 'validation' argument must be a String")

    data = {}
    val_path = "{}/{}.yaml".format(path, validation)

    LOG.debug(
        "Obtaining information about validation {} from {}".format(
            validation,
            val_path)
    )

    if os.path.exists(val_path):
        val = Validation(val_path)
        data.update(val.get_formated_data)
        data.update({'Parameters': val.get_vars})
    return data


def get_validations_parameters(validations_data,
                               validation_name=None,
                               groups=None,
                               categories=None,
                               products=None):
    """Return parameters for a list of validations


    :param validations_data: A list of absolute validations playbooks path
    :type validations_data: `list`

    :param validation_name: A list of validation name
    :type validation_name: `list`

    :param groups: A list of validation groups
    :type groups: `list`

    :param categories: A list of validation categories
    :type categories: `list`

    :param products: A list of validation products
    :type products: `list`

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
    if not isinstance(validations_data, list):
        raise TypeError("The 'validations_data' argument must be a List")

    if not validation_name:
        validation_name = []
    elif not isinstance(validation_name, list):
        raise TypeError("The 'validation_name' argument must be a List")

    if not groups:
        groups = []
    elif not isinstance(groups, list):
        raise TypeError("The 'groups' argument must be a List")

    if not categories:
        categories = []
    elif not isinstance(categories, list):
        raise TypeError("The 'categories' argument must be a List")

    if not products:
        products = []
    elif not isinstance(products, list):
        raise TypeError("The 'products' argument must be a List")

    params = {}
    for val in validations_data:
        v = Validation(val)
        if v.id in validation_name or \
           set(groups).intersection(v.groups) or \
           set(categories).intersection(v.categories) or \
           set(products).intersection(v.products):
            params[v.id] = {
                'parameters': v.get_vars
            }

    return params
