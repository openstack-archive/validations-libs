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

import constants
import logging
import os
import six

from validations_libs.ansible import Ansible as v_ansible
from validations_libs import utils as v_utils

LOG = logging.getLogger(__name__ + ".run")


class Run(object):

    def __init__(self):
        self.log = logging.getLogger(__name__ + ".Run")

    def run_validations(self, playbook, inventory,
                        group=None, extra_vars=None, validations_dir=None,
                        validation_name=None, extra_env_var=None,
                        ansible_cfg=None, quiet=True):

        self.log = logging.getLogger(__name__ + ".run_validations")

        playbooks = []
        if group:
            self.log.debug('Getting the validations list by group')
            try:
                validations = v_utils.parse_all_validations_on_disk(
                    (validations_dir if validations_dir
                     else constants.ANSIBLE_VALIDATION_DIR), group)
                for val in validations:
                    playbooks.append(val.get('id') + '.yaml')
            except Exception as e:
                raise(e)

        else:
            for pb in validation_name:
                if pb not in v_utils.get_validation_group_name_list():
                    playbooks.append(pb + '.yaml')
                else:
                    raise("Please, use '--group' argument instead of "
                          "'--validation' to run validation(s) by their "
                          "name(s)."
                         )
        run_ansible = v_ansible()
        self.log.debug('Running the validations with Ansible')
        results = []
        with v_utils.TempDirs(chdir=False) as tmp:
            for playbook in playbooks:
                stdout_file, _playbook, _rc, _status = run_ansible.run(
                    workdir=tmp,
                    playbook=playbook,
                    playbook_dir=(validations_dir if
                                  validations_dir else
                                  constants.ANSIBLE_VALIDATION_DIR),
                    parallel_run=True,
                    inventory=inventory,
                    output_callback='validation_json',
                    quiet=quiet,
                    extra_vars=extra_vars,
                    extra_env_variables=extra_env_var,
                    ansible_cfg=ansible_cfg,
                    gathering_policy='explicit')
            results.append({'validation': {
                                'playbook': _playbook,
                                'rc_code': _rc,
                                'status': _status,
                                'stdout_file': stdout_file
                           }})
        return results
