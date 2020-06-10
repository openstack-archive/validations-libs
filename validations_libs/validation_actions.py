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

from validations_libs.ansible import Ansible as v_ansible
from validations_libs.group import Group
from validations_libs.validation_logs import ValidationLogs, ValidationLog
from validations_libs import constants
from validations_libs import utils as v_utils

LOG = logging.getLogger(__name__ + ".validation_actions")


class ValidationActions(object):

    def __init__(self, validation_path=None, group=None):
        self.log = logging.getLogger(__name__ + ".ValidationActions")
        self.validation_path = (validation_path if validation_path
                                else constants.ANSIBLE_VALIDATION_DIR)
        self.group = group

    def list_validations(self):
        """List the available validations"""
        self.log = logging.getLogger(__name__ + ".list_validations")
        validations = v_utils.parse_all_validations_on_disk(
            self.validation_path, self.group)

        return_values = []
        column_name = ('ID', 'Name', 'Groups')

        for val in validations:
            return_values.append((val.get('id'), val.get('name'),
                                  val.get('groups')))
        return (column_name, return_values)

    def show_validations(self, validation,
                         log_path=constants.VALIDATIONS_LOG_BASEDIR):
        """Display detailed information about a Validation"""
        self.log = logging.getLogger(__name__ + ".show_validations")
        # Get validation data:
        vlog = ValidationLogs(log_path)
        data = v_utils.get_validations_data(validation, self.validation_path)
        logfiles = vlog.get_all_logfiles_content()
        format = vlog.get_validations_stats(logfiles)
        data.update(format)
        return data

    def run_validations(self, playbook=[], inventory='localhost',
                        group=None, extra_vars=None, validations_dir=None,
                        validation_name=None, extra_env_vars=None,
                        ansible_cfg=None, quiet=True, workdir=None,
                        limit_hosts=None, run_async=False,
                        base_dir=constants.DEFAULT_VALIDATIONS_BASEDIR):
        self.log = logging.getLogger(__name__ + ".run_validations")
        playbooks = []
        validations_dir = (validations_dir if validations_dir
                           else self.validation_path)

        if playbook:
            if isinstance(playbook, list):
                playbooks = playbook
            elif isinstance(playbook, str):
                playbooks = [playbook]
            else:
                raise TypeError("Playbooks should be a List or a Str")

        if group:
            self.log.debug('Getting the validations list by group')
            try:
                validations = v_utils.parse_all_validations_on_disk(
                    validations_dir, group)
                for val in validations:
                    playbooks.append(val.get('id') + '.yaml')
            except Exception as e:
                raise(e)
        elif validation_name:
            playbooks = v_utils.get_validations_playbook(validations_dir,
                                                         validation_name,
                                                         group)
            if not playbooks:
                msg = "Validation {} not found in {}.".format(validation_name,
                                                              validations_dir)
                raise RuntimeError(msg)
        else:
            raise RuntimeError("No validations found")

        self.log.debug('Running the validations with Ansible')
        results = []
        for playbook in playbooks:
            validation_uuid, artifacts_dir = v_utils.create_artifacts_dir(
                prefix=os.path.basename(playbook))
            run_ansible = v_ansible(validation_uuid)
            _playbook, _rc, _status = run_ansible.run(
                workdir=artifacts_dir,
                playbook=playbook,
                base_dir=base_dir,
                playbook_dir=validations_dir,
                parallel_run=True,
                inventory=inventory,
                output_callback='validation_json',
                quiet=quiet,
                extra_vars=extra_vars,
                limit_hosts=limit_hosts,
                extra_env_variables=extra_env_vars,
                ansible_cfg=ansible_cfg,
                gathering_policy='explicit',
                ansible_artifact_path=artifacts_dir,
                run_async=run_async)
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
        vlog = ValidationLogs()
        return vlog.get_results(uuid)

    def group_information(self, groups):
        """Get Information about Validation Groups"""
        val_gp = Group(groups)
        group = val_gp.get_formated_group

        group_info = []
        # Get validations number by groups
        for gp in group:
            validations = v_utils.parse_all_validations_on_disk(
                self.validation_path, gp[0])
            group_info.append((gp[0], gp[1], len(validations)))
        column_name = ("Groups", "Description", "Number of Validations")
        return (column_name, group_info)

    def show_validations_parameters(self, validation, group=None,
                                    format='json', download_file=None):
        """Return Validations Parameters"""
        validations = v_utils.get_validations_playbook(
            self.validation_path, validation, group)
        params = v_utils.get_validations_parameters(validations, validation,
                                                    group, format)
        if download_file:
            with open(download_file, 'w') as f:
                f.write(params)
        return params

    def show_history(self, validation_id=None, extension='json'):
        """Return validations history"""
        vlogs = ValidationLogs(self.validation_path)
        logs = (vlogs.get_logfile_by_validation(validation_id)
                if validation_id else vlogs.get_all_logfiles(extension))

        values = []
        column_name = ('UUID', 'Validations',
                       'Status', 'Execution at',
                       'Duration')

        for log in logs:
            vlog = ValidationLog(logfile=log)
            if vlog.is_valid_format():
                values.append((vlog.get_uuid, vlog.validation_id,
                               vlog.get_status, vlog.get_start_time,
                               vlog.get_duration))
        return (column_name, values)
