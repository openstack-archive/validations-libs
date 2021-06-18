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
"""Default paths for validation playbook directory,
validation groups definitions and validation logs
are defined here.

These paths are used in an absence of user defined overrides,
or as a fallback, when custom locations fail.
"""

import os

DEFAULT_VALIDATIONS_BASEDIR = '/usr/share/ansible'

ANSIBLE_VALIDATION_DIR = os.path.join(
    DEFAULT_VALIDATIONS_BASEDIR,
    'validation-playbooks')

VALIDATION_GROUPS_INFO = os.path.join(
    DEFAULT_VALIDATIONS_BASEDIR,
    'groups.yaml')

# NOTE(fressi) The HOME folder environment variable may be undefined.
VALIDATIONS_LOG_BASEDIR = os.path.expanduser('~/validations')

VALIDATION_ANSIBLE_ARTIFACT_PATH = os.path.join(
    VALIDATIONS_LOG_BASEDIR,
    'artifacts')
