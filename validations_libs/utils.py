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
import ast
import configparser
import datetime
import glob
import logging
import os
import site
import six
import subprocess
import uuid

from os.path import join
# @matbu backward compatibility for stable/train
try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path

from validations_libs import constants
from validations_libs.group import Group
from validations_libs.validation import Validation

LOG = logging.getLogger(__name__ + ".utils")


def current_time():
    """Return current time"""
    return '%sZ' % datetime.datetime.utcnow().isoformat()


def community_validations_on(validation_config):
    """Check for flag for community validations to be enabled
    The default value is true

    :param validation_config: A dictionary of configuration for Validation
                              loaded from an validation.cfg file.
    :type validation_config: ``dict``
    :return: A boolean with the status of community validations flag
    :rtype: `bool`
    """
    if not validation_config:
        return True
    return validation_config.get("default", {}).get("enable_community_validations", True)


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
                                  products=None,
                                  validation_config=None):
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

    :param validation_config: A dictionary of configuration for Validation
                              loaded from an validation.cfg file.
    :type validation_config: ``dict``

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
    if community_validations_on(validation_config):
        validations_abspath.extend(glob.glob("{}/*.yaml".format(
            constants.COMMUNITY_PLAYBOOKS_DIR)))

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
                             products=None,
                             validation_config=None):
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

    :param validation_config: A dictionary of configuration for Validation
                              loaded from an validation.cfg file.
    :type validation_config: ``dict``

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
    validations_abspath = glob.glob("{path}/*.yaml".format(path=path))
    if community_validations_on(validation_config):
        validations_abspath.extend(glob.glob("{}/*.yaml".format(
                    constants.COMMUNITY_PLAYBOOKS_DIR)))
    for pl_path in validations_abspath:
        if os.path.isfile(pl_path):
            if validation_id:
                if os.path.splitext(os.path.basename(pl_path))[0] in validation_id or \
                        os.path.basename(pl_path) in validation_id:
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


def get_validations_data(
        validation,
        path=constants.ANSIBLE_VALIDATION_DIR,
        validation_config=None):
    """Return validation data with format:

    ID, Name, Description, Groups, Parameters

    :param validation: Name of the validation without the `yaml` extension.
                       Defaults to `constants.ANSIBLE_VALIDATION_DIR`
    :type validation: `string`
    :param path: The path to the validations directory
    :type path: `string`
    :param validation_config: A dictionary of configuration for Validation
                              loaded from an validation.cfg file.
    :type validation_config: ``dict``
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
    comm_path = ""
    if community_validations_on(validation_config):
        comm_path = "{}/{}.yaml".format(constants.COMMUNITY_PLAYBOOKS_DIR, validation)

    LOG.debug(
        "Obtaining information about validation {} from {}".format(
            validation,
            val_path)
    )

    if os.path.exists(val_path):
        val = Validation(val_path)
        data.update(val.get_formated_data)
        data.update({'Parameters': val.get_vars})
    if not data and comm_path:
        if os.path.exists(comm_path):
            val = Validation(comm_path)
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


def _eval_types(value):
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return ast.literal_eval(value)
    except (SyntaxError, NameError, ValueError):
        pass
    try:
        return str(value)
    except ValueError:
        msg = ("Can not eval or type not supported for value: {},").format(
            value)
        raise ValueError(msg)


def load_config(config):
    """Load Config File from CLI"""
    if not os.path.exists(config):
        msg = ("Config file {} could not be found, ignoring...").format(config)
        LOG.warning(msg)
        return {}
    else:
        msg = "Validation config file found: {}".format(config)
        LOG.info(msg)
    parser = configparser.ConfigParser()
    parser.optionxform = str
    parser.read(config)
    data = {}
    try:
        for section in parser.sections():
            for keys, values in parser.items(section):
                if section not in data:
                    # Init section in dictionary
                    data[section] = {}
                if section == 'ansible_environment':
                    # for Ansible environment variables we dont want to cast
                    # types, each values should a type String.
                    data[section][keys] = values
                elif section == 'ansible_runner' and \
                keys not in constants.ANSIBLE_RUNNER_CONFIG_PARAMETERS:
                    # for Ansible runner parameters, we select only a set
                    # of parameters which will be passed as **kwargs in the
                    # runner, so we have to ignore all the others.
                    msg = ("Incompatible key found for ansible_runner section {}, "
                           "ignoring {} ...").format(section, keys)
                    LOG.warning(msg)
                    continue
                else:
                    data[section][keys] = _eval_types(values)
    except configparser.NoSectionError:
        msg = ("Wrong format for the config file {}, "
               "section {} can not be found, ignoring...").format(config,
                                                                  section)
        LOG.warning(msg)
        return {}
    return data


def find_config_file(config_file_name='validation.cfg'):
    """ Find the config file for Validation in the following order:
        * environment validation VALIDATION_CONFIG
        * current user directory
        * user home directory
        * Python prefix path which has been used for the installation
        * /etc/validation.cfg
    """
    def _check_path(path):
        if os.path.exists(path):
            if os.path.isfile(path) and os.access(path,
                                                  os.R_OK):
                return path
    # Build a list of potential paths with the correct order:
    paths = []
    env_config = os.getenv("VALIDATION_CONFIG", "")
    if _check_path(env_config):
        return env_config
    paths.append(os.getcwd())
    paths.append(os.path.expanduser('~'))
    for prefix in site.PREFIXES:
        paths.append(os.path.join(prefix, 'etc'))
    paths.append('/etc')

    for path in paths:
        current_path = os.path.join(path, config_file_name)
        if _check_path(current_path):
            return current_path
    return current_path


def run_command_and_log(log, cmd, cwd=None,
                        env=None, retcode_only=True):
    """Run command and log output

    :param log: Logger instance for logging
    :type log: `Logger`

    :param cmd: Command to run in list form
    :type cmd: ``List``

    :param cwd: Current working directory for execution
    :type cmd: ``String``

    :param env: Modified environment for command run
    :type env: ``List``

    :param retcode_only: Returns only retcode instead or proc object
    :type retcdode_only: ``Boolean``
    """
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, shell=False,
                            cwd=cwd, env=env)
    if retcode_only:
        while True:
            try:
                line = proc.stdout.readline()
            except StopIteration:
                break
            if line != b'':
                if isinstance(line, bytes):
                    line = line.decode('utf-8')
                log.debug(line.rstrip())
            else:
                break
        proc.stdout.close()
        return proc.wait()
    return proc


def check_community_validations_dir(
        basedir=constants.COMMUNITY_VALIDATIONS_BASEDIR,
        subdirs=constants.COMMUNITY_VALIDATIONS_SUBDIR):
    """Check presence of the community validations directory structure

    The community validations are stored and located in:

    .. code-block:: console

        /home/<username>/community-validations
        ├── library
        ├── lookup_plugins
        ├── playbooks
        └── roles

    This function checks for the presence of the community-validations directory
    in the $HOME of the user running the validation CLI. If the primary
    directory doesn't exist, this function will create it and will check if the
    four subdirectories are present and will create them otherwise.

    :param basedir: Absolute path of the community validations
    :type basedir: ``pathlib.PosixPath``

    :param subdirs: List of Absolute path of the community validations subdirs
    :type subdirs: ``list`` of ``pathlib.PosixPath``

    :rtype: ``NoneType``
    """
    recreated_comval_dir = []

    def create_subdir(subdir):
        for _dir in subdir:
            LOG.debug(
                "Missing {} directory in {}:"
                .format(Path(_dir).name, basedir)
            )
            Path.mkdir(_dir)
            recreated_comval_dir.append(_dir)
            LOG.debug(
                "└── {} directory created successfully..."
                .format(_dir)
            )

    if Path(basedir).exists and Path(basedir).is_dir():
        _subdirectories = [x for x in basedir.iterdir() if x.is_dir()]
        missing_dirs = [
            _dir for _dir in subdirs
            if _dir not in _subdirectories
        ]

        create_subdir(missing_dirs)
    else:
        LOG.debug(
            "The community validations {} directory is not present:"
            .format(basedir)
        )
        Path.mkdir(basedir)
        recreated_comval_dir.append(basedir)
        LOG.debug("└── {} directory created...".format(basedir))
        create_subdir(subdirs)

    LOG.debug(
        (
            "The {} directory and its required subtree are present "
            "and correct:\n"
            "{}/\n"
            "├── library            OK\n"
            "├── lookup_plugins     OK\n"
            "├── playbooks          OK\n"
            "└── roles              OK\n"
            .format(
                basedir,
                basedir)
        )
    )
    return recreated_comval_dir
