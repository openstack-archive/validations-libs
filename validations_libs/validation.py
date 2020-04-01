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
import yaml
from collections import OrderedDict

LOG = logging.getLogger(__name__ + ".validation")


class Validation(object):

    _col_keys = ['ID', 'Name', 'Description', 'Groups']

    def __init__(self, validation_path):
        self.dict = self._get_content(validation_path)
        self.id = os.path.splitext(os.path.basename(validation_path))[0]

    def _get_content(self, val_path):
        try:
            with open(val_path, 'r') as val_playbook:
                return yaml.safe_load(val_playbook)[0]
        except IOError:
            raise IOError("Validation playbook not found")

    @property
    def get_metadata(self):
        if self.dict['vars'].get('metadata'):
            self.metadata = {'id': self.id}
            self.metadata.update(self.dict['vars'].get('metadata'))
        return self.metadata

    @property
    def get_vars(self):
        vars = self.dict['vars'].copy()
        if vars.get('metadata'):
            vars.pop('metadata')
        return vars

    @property
    def get_data(self):
        return self.dict

    @property
    def groups(self):
        return self.dict['vars']['metadata'].get('groups')

    @property
    def get_id(self):
        return self.id

    @property
    def get_ordered_dict(self):
        data = OrderedDict()
        data.update(self.dict)
        return data

    @property
    def get_formated_data(self):
        data = {}
        for key in self.get_metadata.keys():
            if key in map(str.lower, self._col_keys):
                for k in self._col_keys:
                    if key == k.lower():
                        output_key = k
                data[output_key] = self.get_metadata.get(key)
            else:
                # Get all other values:
                data[key] = self.get_metadata.get(key)
        return data
