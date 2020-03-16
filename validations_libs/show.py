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
from validations_libs import utils as v_utils

LOG = logging.getLogger(__name__ + ".show")


class Show(object):

    def __init__(self):
        self.log = logging.getLogger(__name__ + ".Show")

    def show_validations(self, validation):
        """Display detailed information about a Validation"""
        # Get validation data:
        data = v_utils.get_validations_data(
            v_utils.get_validations_details(validation))
        format = v_utils.get_validations_stats(
            v_utils.parse_all_validations_logs_on_disk())
        data.update(format)
        return data
