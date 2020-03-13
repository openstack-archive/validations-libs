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
DEFAULT_VALIDATIONS_BASEDIR = '/usr/share/validations-common'

ANSIBLE_VALIDATION_DIR = '/usr/share/validations-common/playbooks'

VALIDATION_GROUPS_INFO = '%s/groups.yaml' % DEFAULT_VALIDATIONS_BASEDIR

VALIDATION_GROUPS = ['no-op',
                     'prep',
                     'post']

VALIDATIONS_LOG_BASEDIR = '/var/log/validations/'
VALIDATION_ANSIBLE_ARTIFACT_PATH = '/var/log/validations/artifacts/'
