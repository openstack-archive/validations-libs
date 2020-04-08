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
import yaml

LOG = logging.getLogger(__name__ + ".Group")


class Group(object):

    def __init__(self, groups):
        self.data = self._get_content(groups)

    def _get_content(self, groups):
        try:
            with open(groups, 'r') as gp:
                return yaml.safe_load(gp)
        except IOError:
            raise IOError("Group file not found")

    @property
    def get_data(self):
        return self.data

    @property
    def get_formated_group(self):
        return [(gp_n, gp_d[0].get('description'))
                for (gp_n, gp_d) in sorted(self.data.items())]

    @property
    def get_groups_keys_list(self):
        return [gp for gp in sorted(self.data.keys())]
