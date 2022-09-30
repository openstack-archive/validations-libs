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
import logging
import os
import sys
import json
import yaml

from validations_libs.ansible import Ansible as v_ansible
from validations_libs.group import Group
from validations_libs.cli.common import Spinner
from validations_libs.validation_logs import ValidationLogs, ValidationLog
from validations_libs import constants
from validations_libs import utils as v_utils
from validations_libs.exceptions import ValidationRunException, ValidationShowException

LOG = logging.getLogger(__name__ + ".validation_actions")


class ValidationActions:
    """An object for encapsulating the Validation Actions

    This class allows the possibility to execute the following actions:

    - List the available validations
    - Show detailed information about one validation
    - Show the available parameters for one or multiple validations
    - Show the list of the validation groups
    - Run one or multiple validations, by name(s) or by group(s)
    - Show the history of the validations executions

    """

    def __init__(self, validation_path=constants.ANSIBLE_VALIDATION_DIR,
                 groups_path=constants.VALIDATION_GROUPS_INFO,
                 log_path=constants.VALIDATIONS_LOG_BASEDIR):
        """
        :param groups_path: The absolute path to the validation groups
                           definition file.
                           (Defaults to ``constants.VALIDATION_GROUPS_INFO``)
        :type groups_path: ``string``
        :param log_path: The absolute path of the validations logs directory
                           (Defaults to ``constants.VALIDATIONS_LOG_BASEDIR``)
        :type log_path: ``string``
        """
        self.log = logging.getLogger(__name__ + ".ValidationActions")
        self.validation_path = validation_path
        self.log_path = log_path

        self.groups_path = groups_path

    def list_validations(self,
                         groups=None,
                         categories=None,
                         products=None,
                         validation_config=None):
        """Get a list of the validations selected by group membership or by
        category. With their names, group membership information, categories and
        products.

        This is used to print table from python ``Tuple`` with ``PrettyTable``.

        :param groups: List of validation groups.
        :type groups: `list`

        :param categories: List of validation categories.
        :type categories: `list`

        :param products: List of validation products.
        :type products: `list`

        :param validation_config: A dictionary of configuration for Validation
                                  loaded from an validation.cfg file.
        :type validation_config: ``dict``

        :return: Column names and a list of the selected validations
        :rtype: `tuple`

        .. code:: text

            -------+-----------+----------------------+---------------+--------------+
            | ID   | Name      | Groups               | Categories    | Products     |
            +------+-----------+----------------------+---------------+--------------+
            | val1 | val_name1 | ['group1']           | ['category1'] | ['product1'] |
            | val2 | val_name2 | ['group1', 'group2'] | ['category2'] | ['product2'] |
            | val3 | val_name3 | ['group4']           | ['category3'] | ['product3'] |
            +------+-----------+----------------------+---------------+--------------+

        :example:

        >>> path = "/foo/bar"
        >>> groups = ['group1']
        >>> categories = ['category1']
        >>> action = ValidationActions(validation_path=path)
        >>> results = action.list_validations(groups=groups,
                                              categories=categories)
        >>> print(results
        (('ID', 'Name', 'Groups', 'Categories', 'Products'),
         [('val1',
           'val_name1',
           ['group1'],
           ['category1'],
           ['product1']),
          ('val2',
           'val_name2',
           ['group1', 'group2'],
           ['category2'],
           ['product2'])])
        """
        self.log = logging.getLogger(__name__ + ".list_validations")

        validations = v_utils.parse_all_validations_on_disk(
            path=self.validation_path,
            groups=groups,
            categories=categories,
            products=products,
            validation_config=validation_config
        )

        self.log.debug(
            "Parsed {} validations.".format(len(validations))
        )

        return_values = [
            (val.get('id'), val.get('name'),
             val.get('groups'), val.get('categories'),
             val.get('products'))
            for val in validations]

        column_names = ('ID', 'Name', 'Groups', 'Categories', 'Products')

        return (column_names, return_values)

    def show_validations(self, validation,
                         validation_config=None):
        """Display detailed information about a Validation

        :param validation: The name of the validation
        :type validation: `string`
        :param validation_config: A dictionary of configuration for Validation
                                  loaded from an validation.cfg file.
        :type validation_config: ``dict``


        :return: The detailed information for a validation
        :rtype: `dict`

        :raises: ValidationShowException

        :example:

        >>> path = "/foo/bar"
        >>> validation = 'foo'
        >>> action = ValidationActions(validation_path=path)
        >>> results = action.show_validations(validation=validation)
        >>> print(results)
        {
         'Description': 'Description of the foo validation',
         'Categories': ['category1', 'category2'],
         'Groups': ['group1', 'group2'],
         'ID': 'foo',
         'Last execution date': None,
         'Name': 'Name of the validation foo',
         'Number of execution': 'Total: 0, Passed: 0, Failed: 0',
         'Parameters': {'foo1': bar1}
        }
        """
        self.log = logging.getLogger(__name__ + ".show_validations")
        # Get validation data:
        vlog = ValidationLogs(self.log_path)
        data = v_utils.get_validations_data(
                validation,
                self.validation_path,
                validation_config=validation_config)
        if not data:
            extra_msg = ""
            if v_utils.community_validations_on(validation_config):
                extra_msg = " or {}".format(constants.COMMUNITY_LIBRARY_DIR)
            msg = "Validation {} not found in the path: {}{}".format(
                validation,
                self.validation_path,
                extra_msg)
            raise ValidationShowException(msg)

        logfiles = vlog.get_logfile_content_by_validation(validation)
        data_format = vlog.get_validations_stats(logfiles)
        data.update(data_format)
        return data

    def _skip_hosts(self, skip_list, limit_hosts=None):
        """Check Ansible Hosts and return an updated limit_hosts
        :param skip_list: list of hosts to skip with reasons why
        :type skip_list: `dict`
        :param limit_hosts: Limit the execution to the hosts.
        :type limit_hosts: ``string``

        :return the limit hosts according the skip_list or None if the
                validation should be skipped on ALL hosts.
        :example:

        >>> v_actions = ValidationActions()
        >>> limit_hosts = 'cloud1,cloud2'
        >>> skip_list = {
        ... 'xyz': {
        ...     'hosts': 'cloud1',
        ...     'reason': None,
        ...     'lp': None}}
        >>> v_actions._skip_hosts(skip_list, validation, limit_hosts='cloud1,cloud2')
        '!cloud1,cloud2'
        """
        hosts = skip_list.get('hosts', 'all')
        if hosts.lower() == 'all':
            return None
        _hosts = ['!{}'.format(hosts)]
        if limit_hosts:
            # check if skipped hosts is already in limit host
            _hosts.extend([limit for limit in limit_hosts.split(',')
                           if hosts not in limit])
        return ','.join(_hosts)

    def _skip_playbook(self, skip_list, playbook, limit_hosts=None):
        """Check if playbook is in the skiplist
        :param skip_list: Dictionary of validations to skip.
        :type skip_list: `dictionary`
        :param playbook: The name of the playbook
        :type playbook: `string`
        :param limit_hosts: Limit the execution to the hosts.
        :type limit_hosts: `string`

        :return a tuple of playbook and hosts
        :rtype: `tuple`

        :example:

        >>> skip_list = {
        ... 'xyz': {
        ...     'hosts': 'cloud1',
        ...     'reason': None,
        ...     'lp': None}}

        If playbook is not in skip list:
        >>> v_actions = ValidationActions()
        >>> v_actions._skip_playbook(skip_list, 'foo', None)
        ('foo', None)

        If playbook is in the skip list, but with restriction only on
        host cloud1:
        >>> v_actions = ValidationActions()
        >>> v_actions._skip_playbook(skip_list, 'xyz', None)
        ('xyz', '!cloud1')

        If playbook in the skip list, and should be skip on ALL hosts:
        >>> skip_list = {
        ... 'xyz': {
        ...     'hosts': 'ALL',
        ...     'reason': None,
        ...     'lp': None}}
        >>> v_actions = ValidationActions()
        >>> v_actions._skip_playbook(skip_list, 'xyz', None)
        (None, None)
        """
        if skip_list:
            if playbook in skip_list:

                self.log.info((
                    "Validation '{}' skipped on following hosts '{}' "
                    "with reason: '{}'.").format(
                        playbook,
                        skip_list[playbook].get('hosts', 'All'),
                        skip_list[playbook].get('reason', None)))

                _hosts = self._skip_hosts(
                    skip_list[playbook],
                    limit_hosts)
                if _hosts:
                    return playbook, _hosts
                else:
                    return None, _hosts
        return playbook, limit_hosts

    def _retrieve_latest_results(self, logs, history_limit):
        """Retrieve the most recent validation results.
        Previously retrieved logs are sorted in ascending order,
        with the last time the file was modified serving as a key.
        Finally we take the last `n` logs, where `n` == `history_limit`
        and return them while discarding the time information.

        :param logs: List of validation log file paths
        :type logs: `list`
        :param history_limit: number of entries to display
        :type history_limit: `int`

        :return: List of time-modified, path tuples of length =< history_limit
        :rtype: `list`
        """

        history_limit = min(history_limit, len(logs))

        logs = sorted(
                [(os.stat(path).st_mtime, path) for path in logs],
                key=lambda path: path[0])

        return [path[1] for path in logs[-history_limit:]]

    def run_validations(self, validation_name=None, inventory='localhost',
                        group=None, category=None, product=None,
                        extra_vars=None, validations_dir=None,
                        extra_env_vars=None, ansible_cfg=None, quiet=True,
                        limit_hosts=None, run_async=False,
                        base_dir=constants.DEFAULT_VALIDATIONS_BASEDIR,
                        python_interpreter=None, skip_list=None,
                        callback_whitelist=None,
                        output_callback='vf_validation_stdout', ssh_user=None,
                        validation_config=None):
        """Run one or multiple validations by name(s), by group(s) or by
        product(s)

        :param validation_name: A list of validation names.
        :type validation_name: ``list``
        :param inventory: Either proper inventory file, or a comma-separated
                          list. (Defaults to ``localhost``)
        :type inventory: ``string``
        :param group: A list of group names
        :type group: ``list``
        :param category: A list of category names
        :type category: ``list``
        :param product: A list of product names
        :type product: ``list``
        :param extra_vars: Set additional variables as a Dict or the absolute
                           path of a JSON or YAML file type.
        :type extra_vars: Either a Dict or the absolute path of JSON or YAML
        :param validations_dir: The absolute path of the validations playbooks
        :type validations_dir: ``string``
        :param extra_env_vars: Set additional ansible variables using an
                                extravar dictionary.
        :type extra_env_vars: ``dict``
        :param ansible_cfg: Path to an ansible configuration file. One will be
                            generated in the artifact path if this option is
                            None.
        :type ansible_cfg: ``string``
        :param quiet: Disable all output (Defaults to ``True``)
        :type quiet: ``Boolean``
        :param limit_hosts: Limit the execution to the hosts.
        :type limit_hosts: ``string``
        :param run_async: Enable the Ansible asynchronous mode
                          (Defaults to ``False``)
        :type run_async: ``boolean``
        :param base_dir: The absolute path of the validations base directory
                         (Defaults to
                         ``constants.DEFAULT_VALIDATIONS_BASEDIR``)
        :type base_dir: ``string``
        :param python_interpreter: Path to the Python interpreter to be
                                   used for module execution on remote targets,
                                   or an automatic discovery mode (``auto``,
                                   ``auto_silent`` or the default one
                                   ``auto_legacy``)
        :type python_interpreter: ``string``
        :param callback_whitelist: Comma separated list of callback plugins.
                                Custom output_callback is also whitelisted.
                                (Defaults to ``None``)
        :type callback_whitelist: ``list`` or ``string``
        :param output_callback: The Callback plugin to use.
                                (Defaults to 'validation_stdout')
        :type output_callback: ``string``
        :param skip_list: List of validations to skip during the Run form as
                          {'xyz': {'hosts': 'ALL', 'reason': None, 'lp': None}
                          }
                          (Defaults to 'None')
        :type skip_list: ``dict``

        :param ssh_user: Ssh user for Ansible remote connection
        :type ssh_user: ``string``
        :param validation_config: A dictionary of configuration for Validation
                                  loaded from an validation.cfg file.
        :type validation_config: ``dict``
        :return: A list of dictionary containing the informations of the
                 validations executions (Validations, Duration, Host_Group,
                 Status, Status_by_Host, UUID and Unreachable_Hosts)
        :rtype: ``list``

        :raises: ValidationRunException
        :example:

        >>> path = "/u/s/a"
        >>> validation_name = ['foo', 'bar']
        >>> actions = ValidationActions(validation_path=path)
        >>> results = actions.run_validations(inventory='localhost',
                                              validation_name=validation_name,
                                              quiet=True)
        >>> print(results)
        [{'Duration': '0:00:02.285',
          'Host_Group': 'all',
          'Status': 'PASSED',
          'Status_by_Host': 'localhost,PASSED',
          'UUID': '62d4d54c-7cce-4f38-9091-292cf49268d7',
          'Unreachable_Hosts': '',
          'Validations': 'foo'},
         {'Duration': '0:00:02.237',
          'Host_Group': 'all',
          'Status': 'PASSED',
          'Status_by_Host': 'localhost,PASSED',
          'UUID': '04e6165c-7c33-4881-bac7-73ff3f909c24',
          'Unreachable_Hosts': '',
          'Validations': 'bar'}]
        """
        self.log = logging.getLogger(__name__ + ".run_validations")
        playbooks = []
        validations_dir = (validations_dir if validations_dir
                           else self.validation_path)
        if group or category or product:
            self.log.debug(
                "Getting the validations list by:\n"
                "  - groups: {}\n"
                "  - categories: {}\n"
                "  - products: {}".format(group, category, product)
            )
            validations = v_utils.parse_all_validations_on_disk(
                path=validations_dir, groups=group,
                categories=category, products=product,
                validation_config=validation_config
            )
            for val in validations:
                playbooks.append("{path}/{id}.yaml".format(**val))
        elif validation_name:
            self.log.debug(
                "Getting the {} validation.".format(
                    validation_name))

            playbooks = v_utils.get_validations_playbook(
                    validations_dir,
                    validation_name,
                    validation_config=validation_config)

            if not playbooks or len(validation_name) != len(playbooks):
                found_playbooks = []
                for play in playbooks:
                    found_playbooks.append(
                        os.path.basename(os.path.splitext(play)[0]))

                unknown_validations = list(
                    set(validation_name) - set(found_playbooks))

                msg = (
                    "Following validations were not found in '{}': {}"
                    ).format(validations_dir, ', '.join(unknown_validations))

                raise ValidationRunException(msg)
        else:
            raise ValidationRunException("No validations found")

        log_path = v_utils.create_log_dir(self.log_path)

        self.log.debug((
            'Running the validations with Ansible.\n'
            'Gathered playbooks:\n -{}').format(
                '\n -'.join(playbooks)))

        results = []
        for playbook in playbooks:
            # Check if playbook should be skipped and on which hosts
            play_name = os.path.basename(os.path.splitext(playbook)[0])
            _play, _hosts = self._skip_playbook(skip_list,
                                                play_name,
                                                limit_hosts)
            if _play:
                validation_uuid, artifacts_dir = v_utils.create_artifacts_dir(
                    log_path=log_path, prefix=os.path.basename(playbook))
                run_ansible = v_ansible(validation_uuid)
                if sys.__stdin__.isatty() and quiet:
                    with Spinner():
                        _playbook, _rc, _status = run_ansible.run(
                            workdir=artifacts_dir,
                            playbook=playbook,
                            base_dir=base_dir,
                            playbook_dir=os.path.dirname(playbook),
                            parallel_run=True,
                            inventory=inventory,
                            output_callback=output_callback,
                            callback_whitelist=callback_whitelist,
                            quiet=quiet,
                            extra_vars=extra_vars,
                            limit_hosts=_hosts,
                            extra_env_variables=extra_env_vars,
                            ansible_cfg_file=ansible_cfg,
                            gathering_policy='explicit',
                            ansible_artifact_path=artifacts_dir,
                            log_path=log_path,
                            run_async=run_async,
                            python_interpreter=python_interpreter,
                            ssh_user=ssh_user,
                            validation_cfg_file=validation_config)
                else:
                    _playbook, _rc, _status = run_ansible.run(
                        workdir=artifacts_dir,
                        playbook=playbook,
                        base_dir=base_dir,
                        playbook_dir=os.path.dirname(playbook),
                        parallel_run=True,
                        inventory=inventory,
                        output_callback=output_callback,
                        callback_whitelist=callback_whitelist,
                        quiet=quiet,
                        extra_vars=extra_vars,
                        limit_hosts=_hosts,
                        extra_env_variables=extra_env_vars,
                        ansible_cfg_file=ansible_cfg,
                        gathering_policy='explicit',
                        ansible_artifact_path=artifacts_dir,
                        log_path=log_path,
                        run_async=run_async,
                        python_interpreter=python_interpreter,
                        ssh_user=ssh_user,
                        validation_cfg_file=validation_config)
                results.append({'playbook': _playbook,
                                'rc_code': _rc,
                                'status': _status,
                                'validations': _playbook.split('.')[0],
                                'UUID': validation_uuid,
                                })

        if run_async:
            return results
        # Return log results
        uuid = [id['UUID'] for id in results]
        vlog = ValidationLogs(log_path)
        return vlog.get_results(uuid)

    def group_information(self, groups=None, validation_config=None):
        """Get Information about Validation Groups

        This is used to print table from python ``Tuple`` with ``PrettyTable``.

        .. code:: text

            +----------+--------------------------+-----------------------+
            | Groups   | Description              | Number of Validations |
            +----------+--------------------------+-----------------------+
            | group1   | Description of group1    |                     3 |
            | group2   | Description of group2    |                    12 |
            | group3   | Description of group3    |                     1 |
            +----------+--------------------------+-----------------------+

        :param groups: The absolute path of the groups.yaml file.
                       The argument is deprecated and will be removed
                       in the next release.
                       Use the 'groups_path' argument of the init method.
        :type groups: ``string``
        :param validation_config: A dictionary of configuration for Validation
                                  loaded from an validation.cfg file.
        :type validation_config: ``dict``

        :return: The list of the available groups with their description and
                 the numbers of validation belonging to them.
        :rtype: ``tuple``

        :example:

        >>> groups = "/foo/bar/groups.yaml"
        >>> actions = ValidationActions(constants.ANSIBLE_VALIDATION_DIR, groups)
        >>> group_info = actions.group_information()
        >>> print(group_info)
        (('Groups', 'Desciption', 'Number of Validations'),
         [('group1', 'Description of group1', 3),
          ('group2', 'Description of group2', 12),
          ('group3', 'Description of group3', 1)])
        """
        if groups:
            self.log.warning((
                "The 'groups' argument is deprecated and"
                " will be removed in the next release. "
                "Use the 'groups_path' argument of the init method."))
            val_group = Group(groups)
        else:
            val_group = Group(self.groups_path)

        group_definitions = val_group.get_formated_groups

        group_info = []

        validations = v_utils.parse_all_validations_on_disk(
                path=self.validation_path,
                groups=[group[0] for group in group_definitions],
                validation_config=validation_config)

        # Get validations number by group
        for group in group_definitions:
            n_matches = len(
                [val for val in validations if group[0] in val['groups']])
            group_info.append((
                group[0],
                group[1],
                n_matches))

        column_name = ("Groups", "Description", "Number of Validations")
        return (column_name, group_info)

    def show_validations_parameters(self,
                                    validations=None,
                                    groups=None,
                                    categories=None,
                                    products=None,
                                    output_format='json',
                                    download_file=None,
                                    validation_config=None):
        """
        Return Validations Parameters for one or several validations by their
        names, their groups, by their categories or by their products.

        :param validations: List of validation name(s)
        :type validations: `list`

        :param groups: List of validation group(s)
        :type groups: `list`

        :param categories: List of validation category(ies)
        :type categories: `list`

        :param products: List of validation product(s)
        :type products: `list`

        :param output_format: Output format (Supported format are JSON or YAML)
        :type output_format: `string`

        :param download_file: Path of a file in which the parameters will be
                              stored
        :type download_file: `string`
        :param validation_config: A dictionary of configuration for Validation
                                  loaded from an validation.cfg file.
        :type validation_config: ``dict``

        :return: A JSON or a YAML dump (By default, JSON).
                 if `download_file` is used, a file containing only the
                 parameters will be created in the file system.

        :raises: ValidationShowException

        :example:

        >>> validations = ['check-cpu', 'check-ram']
        >>> groups = None
        >>> categories = None
        >>> products = None
        >>> output_format = 'json'
        >>> show_validations_parameters(validations, groups,
                                        categories, products, output_format)
        {
            "check-cpu": {
                "parameters": {
                    "minimal_cpu_count": 8
                }
            },
            "check-ram": {
                "parameters": {
                    "minimal_ram_gb": 24
                }
            }
        }

        """

        supported_format = ['json', 'yaml']

        if output_format not in supported_format:
            raise ValidationShowException("{} output format not supported".format(output_format))

        validation_playbooks = v_utils.get_validations_playbook(
            path=self.validation_path,
            validation_id=validations,
            groups=groups,
            categories=categories,
            products=products,
            validation_config=validation_config
        )

        params = v_utils.get_validations_parameters(
            validations_data=validation_playbooks,
            validation_name=validations,
            groups=groups,
            categories=categories,
            products=products
        )

        if download_file:
            params_only = {}
            try:
                with open(download_file, 'w') as parameters_file:
                    for val_name in params:
                        params_only.update(params[val_name].get('parameters'))

                    if output_format == 'json':
                        parameters_file.write(
                            json.dumps(params_only,
                                       indent=4,
                                       sort_keys=True))
                    else:
                        parameters_file.write(
                            yaml.safe_dump(params_only,
                                           allow_unicode=True,
                                           default_flow_style=False,
                                           indent=2))
                self.log.debug(
                    "Validations parameters file {} saved as {} ".format(
                        download_file,
                        output_format))

            except (PermissionError, OSError) as error:
                self.log.exception(
                    (
                        "Exception {} encountered while tring to write "
                        "a validations parameters file {}"
                    ).format(
                        error,
                        download_file))

        return params

    def show_history(self, validation_ids=None, extension='json',
                     history_limit=None):
        """Return validation executions history

        :param validation_ids: The validation ids
        :type validation_ids: a list of strings
        :param extension: The log file extension (Defaults to ``json``)
        :type extension: ``string``
        :param history_limit: The number of most recent history logs
                              to be displayed.
        :type history_limit: ``int``

        :return: Returns the information about the validation executions
                 history
        :rtype: ``tuple``

        :example:

        >>> actions = ValidationActions(constants.ANSIBLE_VALIDATION_DIR)
        >>> print(actions.show_history())
        (('UUID', 'Validations', 'Status', 'Execution at', 'Duration'),
         [('5afb1597-e2a1-4635-b2df-7afe21d00de6',
         'foo',
         'PASSED',
         '2020-11-13T11:47:04.740442Z',
         '0:00:02.388'),
         ('32a5e217-d7a9-49a5-9838-19e5f9b82a77',
         'foo2',
         'PASSED',
         '2020-11-13T11:47:07.931184Z',
         '0:00:02.455'),
         ('62d4d54c-7cce-4f38-9091-292cf49268d7',
         'foo',
         'PASSED',
         '2020-11-13T11:47:47.188876Z',
         '0:00:02.285'),
         ('04e6165c-7c33-4881-bac7-73ff3f909c24',
         'foo3',
         'PASSED',
         '2020-11-13T11:47:50.279662Z',
         '0:00:02.237')])
        >>> actions = ValidationActions(constants.ANSIBLE_VALIDATION_DIR)
        >>> print(actions.show_history(validation_ids=['foo']))
        (('UUID', 'Validations', 'Status', 'Execution at', 'Duration'),
         [('5afb1597-e2a1-4635-b2df-7afe21d00de6',
         'foo',
         'PASSED',
         '2020-11-13T11:47:04.740442Z',
         '0:00:02.388'),
         ('04e6165c-7c33-4881-bac7-73ff3f909c24',
         'foo',
         'PASSED',
         '2020-11-13T11:47:50.279662Z',
         '0:00:02.237')])

        """
        vlogs = ValidationLogs(self.log_path)

        if validation_ids:
            if not isinstance(validation_ids, list):
                validation_ids = [validation_ids]
            logs = []
            for validation_id in validation_ids:
                logs.extend(
                    vlogs.get_logfile_by_validation(
                        validation_id))
        else:
            logs = vlogs.get_all_logfiles(extension)

        if history_limit and history_limit < len(logs):
            logs = self._retrieve_latest_results(logs, history_limit)

        values = []
        column_name = ('UUID', 'Validations',
                       'Status', 'Execution at',
                       'Duration')
        for log in logs:
            vlog = ValidationLog(logfile=log)
            if vlog.is_valid_format():
                for play in vlog.get_plays:
                    values.append((play['id'], play['validation_id'],
                                   vlog.get_status,
                                   play['duration'].get('start'),
                                   play['duration'].get('time_elapsed')))
        return (column_name, values)

    def get_status(self, validation_id=None, uuid=None, status='FAILED'):
        """Return validations execution details by status

        :param validation_id: The validation id
        :type validation_id: ``string``
        :param uuid: The UUID of the execution
        :type uuid: ``string``
        :param status: The status of the execution (Defaults to FAILED)
        :type status: ``string``

        :return: A list of validations execution with details and by status
        :rtype: ``tuple``

        :example:

        >>> actions = ValidationActions(validation_path='/foo/bar')
        >>> status = actions.get_status(validation_id='foo'))
        >>> print(status)
        (['name', 'host', 'status', 'task_data'],
         [('Check if debug mode is disabled.',
         'localhost',
         'FAILED',
         {'_ansible_no_log': False,
             'action': 'fail',
             'changed': False,
             'failed': True,
             'msg': 'Debug mode is not disabled.'}),
         ('Check if debug mode is disabled.',
         'localhost',
         'FAILED',
         {'_ansible_no_log': False,
             'action': 'fail',
             'changed': False,
             'failed': True,
             'msg': 'Debug mode is not disabled.'}),
         ('Check if debug mode is disabled.',
         'localhost',
         'FAILED',
         {'_ansible_no_log': False,
             'action': 'fail',
             'changed': False,
             'failed': True,
             'msg': 'Debug mode is not disabled.'})])
        """
        vlogs = ValidationLogs(self.log_path)

        if validation_id:
            logs = vlogs.get_logfile_by_validation(validation_id)
        elif uuid:
            logs = vlogs.get_logfile_by_uuid(uuid)
        else:
            raise RuntimeError("You need to provide a validation_id or a uuid")

        values = []
        column_name = ['name', 'host', 'status', 'task_data']
        for log in logs:
            vlog = ValidationLog(logfile=log)
            if vlog.is_valid_format():
                for task in vlog.get_tasks_data:
                    if task['status'] == status:
                        for host in task['hosts']:
                            values.append((task['name'], host, task['status'],
                                           task['hosts'][host]))
        return (column_name, values)
