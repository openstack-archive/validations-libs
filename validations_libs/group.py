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
    """An object for encapsulating the groups of validation

    The validations can be grouped together by specifying a ``groups``
    metadata. These ``groups`` are referenced in a ``groups.yaml`` file on the
    filesystem.

    .. code-block:: yaml

        group1:
        - description: >-
            Description of the group1
        group2:
        - description: >-
            Description of the group2
        group3:
        - description: >-
            Description of the group3

    """
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
        """Get the full content of the ``groups.yaml`` file

        :return: The content of the ``groups.yaml`` file
        :rtype: `dict`

        :Example:

        >>> groups = "/foo/bar/groups.yaml"
        >>> grp = Group(groups)
        >>> print(grp.get_data)
        {'group1': [{'description': 'Description of the group1'}],
         'group2': [{'description': 'Description of the group2'}],
         'group3': [{'description': 'Description of the group3'}]}
        """
        return self.data

    @property
    def get_formated_group(self):
        """Get a formated content for output display

        :return:
        :rtype: `list` of `tuples`

        :Example:

        >>> groups = "/foo/bar/groups.yaml"
        >>> grp = Group(groups)
        >>> print(grp.get_formated_group)
        [('group1', 'Description of the group1'),
         ('group2', 'Description of the group2'),
         ('group3', 'Description of the group3')]
        """
        return [(gp_n, gp_d[0].get('description'))
                for (gp_n, gp_d) in sorted(self.data.items())]

    @property
    def get_groups_keys_list(self):
        """Get the list of the group name only

        :return: The list of the group name
        :rtype: `list`

        :Example:

        >>> groups = "/foo/bar/groups.yaml"
        >>> grp = Group(groups)
        >>> print(grp.get_groups_keys_list)
        ['group1', 'group2', 'group3']
        """
        return [gp for gp in sorted(self.data.keys())]
