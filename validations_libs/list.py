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
import utils as validations_utils

LOG = logging.getLogger(__name__ + ".list")


class List(object):

    def __init__(self, group, validations_dir=None):
        self.log = logging.getLogger(__name__ + ".List")
        self.validations_dir = (validations_dir if validations_dir
                                else constants.ANSIBLE_VALIDATION_DIR)
        self.group = group

    def list_validations(self):
        """List the available validations"""
        validations = validations_utils.parse_all_validations_on_disk(
            self.validations_dir, self.group)

        return_values = []
        column_name = ('ID', 'Name', 'Groups')

        for val in validations:
            return_values.append((val.get('id'), val.get('name'),
                                  val.get('groups')))
        return (column_name, return_values)
