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
    """An object for encapsulating a validation

    Each validation is an `Ansible` playbook. Each playbook have some
    ``metadata``. Here is what a minimal validation would look like:

    .. code-block:: yaml

        - hosts: webserver
          vars:
            metadata:
              name: Hello World
              description: This validation prints Hello World!
          roles:
          - hello_world

    As shown here, the validation playbook requires three top-level
    directives:

    ``hosts``, ``vars -> metadata`` and ``roles``

    ``hosts`` specify which nodes to run the validation on.

    The ``vars`` section serves for storing variables that are going to be
    available to the `Ansible` playbook. The validations API uses the
    ``metadata`` section to read validation's name and description. These
    values are then reported by the API.

    The validations can be grouped together by specifying a ``groups``, a
    ``categories`` and a ``products`` metadata. ``groups`` are the deployment
    stage the validations should run on, ``categories`` are the technical
    classification for the validations and ``products`` are the specific
    validations which should be executed against a specific product.

    Groups, Categories and Products function similar to tags and a validation
    can thus be part of many groups and many categories.

    Here is an example:

    .. code-block:: yaml

        - hosts: webserver
          vars:
            metadata:
              name: Hello World
              description: This validation prints Hello World!
              groups:
                - pre-deployment
                - hardware
              categories:
                - os
                - networking
                - storage
                - security
              products:
                - product1
                - product2
          roles:
          - hello_world

    """

    _col_keys = ['ID', 'Name', 'Description',
                 'Groups', 'Categories', 'Products']

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
    def has_vars_dict(self):
        """Check the presence of the vars dictionary

        .. code-block:: yaml

            - hosts: webserver
              vars:                    <====
                metadata:
                  name: hello world
                  description: this validation prints hello world!
                  groups:
                    - pre-deployment
                    - hardware
                  categories:
                    - os
                    - networking
                    - storage
                    - security
                  products:
                    - product1
                    - product2
              roles:
              - hello_world

        :return: `true` if `vars` is found, `false` if not.
        :rtype: `boolean`
        """
        return 'vars' in self.dict.keys()

    @property
    def has_metadata_dict(self):
        """Check the presence of the metadata dictionary

        .. code-block:: yaml

            - hosts: webserver
              vars:
                metadata:             <====
                  name: hello world
                  description: this validation prints hello world!
                  groups:
                    - pre-deployment
                    - hardware
                  categories:
                    - os
                    - networking
                    - storage
                    - security
                  products:
                    - product1
                    - product2
              roles:
              - hello_world

        :return: `true` if `vars` and metadata are found, `false` if not.
        :rtype: `boolean`
        """
        return self.has_vars_dict and 'metadata' in self.dict['vars'].keys()

    @property
    def get_metadata(self):
        """Get the metadata of a validation

        :return: The validation metadata
        :rtype: `dict` or `None` if no metadata has been found
        :raise: A `NameError` exception if no metadata has been found in the
                playbook

        :Example:

        >>> pl = '/foo/bar/val1.yaml'
        >>> val = Validation(pl)
        >>> print(val.get_metadata)
        {'description': 'Val1 desc.',
         'groups': ['group1', 'group2'],
         'categories': ['category1', 'category2'],
         'products': ['product1', 'product2'],
         'id': 'val1',
         'name': 'The validation val1\'s name'}
        """
        if self.has_metadata_dict:
            self.metadata = {'id': self.id}
            self.metadata.update(self.dict['vars'].get('metadata'))
            return self.metadata
        else:
            raise NameError(
                "No metadata found in validation {}".format(self.id)
            )

    @property
    def get_vars(self):
        """Get only the variables of a validation

        :return: All the variables belonging to a validation
        :rtype: `dict` or `None` if no metadata has been found
        :raise: A `NameError` exception if no metadata has been found in the
                playbook

        :Example:

        >>> pl = '/foo/bar/val.yaml'
        >>> val = Validation(pl)
        >>> print(val.get_vars)
        {'var_name1': 'value1',
         'var_name2': 'value2'}
        """
        if self.has_metadata_dict:
            validation_vars = self.dict['vars'].copy()
            validation_vars.pop('metadata')
            return validation_vars
        else:
            raise NameError(
                "No metadata found in validation {}".format(self.id)
            )

    @property
    def get_data(self):
        """Get the full contents of a validation playbook

        :return: The full content of the playbook
        :rtype: `dict`

        :Example:

        >>> pl = '/foo/bar/val.yaml'
        >>> val = Validation(pl)
        >>> print(val.get_data)
        {'gather_facts': True,
         'hosts': 'all',
         'roles': ['val_role'],
         'vars': {'metadata': {'description': 'description of val ',
                               'groups': ['group1', 'group2'],
                               'categories': ['category1', 'category2'],
                               'products': ['product1', 'product2'],
                               'name': 'validation one'},
                               'var_name1': 'value1'}}
        """
        return self.dict

    @property
    def groups(self):
        """Get the validation list of groups

        :return: A list of groups for the validation
        :rtype: `list` or `None` if no metadata has been found
        :raise: A `NameError` exception if no metadata has been found in the
                playbook

        :Example:

        >>> pl = '/foo/bar/val.yaml'
        >>> val = Validation(pl)
        >>> print(val.groups)
        ['group1', 'group2']
        """
        if self.has_metadata_dict:
            return self.dict['vars']['metadata'].get('groups', [])
        else:
            raise NameError(
                "No metadata found in validation {}".format(self.id)
            )

    @property
    def categories(self):
        """Get the validation list of categories

        :return: A list of categories for the validation
        :rtype: `list` or `None` if no metadata has been found
        :raise: A `NameError` exception if no metadata has been found in the
                playbook

        :Example:

        >>> pl = '/foo/bar/val.yaml'
        >>> val = Validation(pl)
        >>> print(val.categories)
        ['category1', 'category2']
        """
        if self.has_metadata_dict:
            return self.dict['vars']['metadata'].get('categories', [])
        else:
            raise NameError(
                "No metadata found in validation {}".format(self.id)
            )

    @property
    def products(self):
        """Get the validation list of products

        :return: A list of products for the validation
        :rtype: `list` or `None` if no metadata has been found
        :raise: A `NameError` exception if no metadata has been found in the
                playbook

        :Example:

        >>> pl = '/foo/bar/val.yaml'
        >>> val = Validation(pl)
        >>> print(val.products)
        ['product1', 'product2']
        """
        if self.has_metadata_dict:
            return self.dict['vars']['metadata'].get('products', [])
        else:
            raise NameError(
                "No metadata found in validation {}".format(self.id)
            )

    @property
    def get_id(self):
        """Get the validation id

        :return: The validation id
        :rtype: `string`

        :Example:

        >>> pl = '/foo/bar/check-cpu.yaml'
        >>> val = Validation(pl)
        >>> print(val.id)
        'check-cpu'
        """
        return self.id

    @property
    def get_ordered_dict(self):
        """Get the full ordered content of a validation

        :return: An `OrderedDict` with the full data of a validation
        :rtype: `OrderedDict`
        """
        data = OrderedDict(self.dict)
        return data

    @property
    def get_formated_data(self):
        """Get basic information from a validation for output display

        :return: Basic information of a validation including the `Description`,
                 the list of 'Categories', the list of `Groups`, the `ID` and
                 the `Name`.
        :rtype: `dict`
        :raise: A `NameError` exception if no metadata has been found in the
                playbook

        :Example:

        >>> pl = '/foo/bar/val.yaml'
        >>> val = Validation(pl)
        >>> print(val.get_formated_data)
        {'Categories': ['category1', 'category2'],
         'Products': ['product1', 'product2'],
         'Description': 'description of val',
         'Groups': ['group1', 'group2'],
         'ID': 'val',
         'Name': 'validation one'}
        """
        data = {}
        metadata = self.get_metadata

        for key in metadata:
            if key == 'id':
                data[key.upper()] = metadata.get(key)
            else:
                data[key.capitalize()] = metadata.get(key)

        return data
