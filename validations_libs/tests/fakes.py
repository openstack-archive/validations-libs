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

# @matbu backward compatibility for stable/train
try:
    from pathlib import PosixPath
except ImportError:
    from pathlib2 import PosixPath

from validations_libs import constants

VALIDATIONS_LIST = [{
    'description': 'My Validation One Description',
    'groups': ['prep', 'pre-deployment', 'no-op', 'post'],
    'categories': ['os', 'system', 'ram'],
    'products': ['product1'],
    'id': 'my_val1',
    'name': 'My Validation One Name',
    'parameters': {}
}, {
    'description': 'My Validation Two Description',
    'groups': ['prep', 'pre-introspection', 'post', 'pre'],
    'categories': ['networking'],
    'products': ['product1'],
    'id': 'my_val2',
    'name': 'My Validation Two Name',
    'parameters': {'min_value': 8}
}]

VALIDATIONS_LIST_GROUP = [{
    'description': 'My Validation Two Description',
    'groups': ['prep', 'pre-introspection'],
    'categories': ['networking'],
    'products': ['product1'],
    'id': 'my_val2',
    'name': 'My Validation Two Name',
    'parameters': {'min_value': 8}
}]


VALIDATION_LIST_RESULT = (('ID', 'Name', 'Groups', 'Categories', 'Products'),
                          [('my_val2', 'My Validation Two Name',
                            ['prep', 'pre-introspection'],
                            ['networking'],
                            ['product1'])])

GROUPS_LIST = [
    ('group1', 'Group1 description'),
    ('group2', 'Group2 description'),
    ('group3', 'Group3 description'),
]

BAD_VALIDATIONS_LOGS_CONTENTS_LIST = [{
    'plays': [{
        'play': {
            'duration': {
                'end': '2019-11-25T13:40:17.538611Z',
            },
            'host': 'undercloud',
            'id': '008886df-d297-1eaa-2a74-000000000008',
            'validation_id': '512e',
            'validation_path':
            '/usr/share/openstack-tripleo-validations/playbooks'
            }}],
    'stats': {
        'undercloud': {
            'changed': 0,
            'failures': 0,
            'ignored': 0,
            'ok': 0,
            'rescued': 0,
            'skipped': 0,
            'unreachable': 1
        }
    },
    'validation_output': []
}]

FAILED_VALIDATIONS_LOGS_CONTENTS_LIST = [{
    'plays': [{
        'play': {
            'duration': {
                'end': '2019-11-25T13:40:17.538611Z',
            },
            'host': 'undercloud',
            'id': '008886df-d297-1eaa-2a74-000000000008',
            'validation_id': '512e',
            'validation_path':
            '/usr/share/openstack-tripleo-validations/playbooks'
            }}],
    'stats': {
        'undercloud': {
            'changed': 0,
            'failures': 1,
            'ignored': 0,
            'ok': 0,
            'rescued': 0,
            'skipped': 0,
            'unreachable': 0
        }
    },
    'validation_output': []
}]

VALIDATIONS_LOGS_CONTENTS_LIST = [{
    'plays': [{
        'play': {
            'duration': {
                'end': '2019-11-25T13:40:17.538611Z',
                'start': '2019-11-25T13:40:14.404623Z',
                'time_elapsed': '0:00:03.753'
            },
            'host': 'undercloud',
            'id': '008886df-d297-1eaa-2a74-000000000008',
            'validation_id': '512e',
            'validation_path':
            '/usr/share/openstack-tripleo-validations/playbooks'
        },
        'tasks': [
            {
                'hosts': {
                    'undercloud': {
                        '_ansible_no_log': False,
                        'action': 'command',
                        'changed': False,
                        'cmd': [u'ls', '/sys/class/block/'],
                        'delta': '0:00:00.018913',
                        'end': '2019-11-25 13:40:17.120368',
                        'invocation': {
                            'module_args': {
                                '_raw_params': 'ls /sys/class/block/',
                                '_uses_shell': False,
                                'argv': None,
                                'chdir': None,
                                'creates': None,
                                'executable': None,
                                'removes': None,
                                'stdin': None,
                                'stdin_add_newline': True,
                                'strip_empty_ends': True,
                                'warn': True
                            }
                        },
                        'rc': 0,
                        'start': '2019-11-25 13:40:17.101455',
                        'stderr': '',
                        'stderr_lines': [],
                        'stdout': 'vda',
                        'stdout_lines': [u'vda']
                    }
                },
                'task': {
                    'duration': {
                        'end': '2019-11-25T13:40:17.336687Z',
                        'start': '2019-11-25T13:40:14.529880Z'
                    },
                    'id':
                    '008886df-d297-1eaa-2a74-00000000000d',
                    'name':
                    'advanced-format-512e-support : List the available drives'
                }
            },
            {
                'hosts': {
                    'undercloud': {
                        'action':
                        'advanced_format',
                        'changed': False,
                        'msg':
                        'All items completed',
                        'results': [{
                            '_ansible_item_label': 'vda',
                            '_ansible_no_log': False,
                            'ansible_loop_var': 'item',
                            'changed': False,
                            'item': 'vda',
                            'skip_reason': 'Conditional result was False',
                            'skipped': True
                        }],
                        'skipped': True
                    }
                },
                'task': {
                    'duration': {
                        'end': '2019-11-25T13:40:17.538611Z',
                        'start': '2019-11-25T13:40:17.341704Z'
                    },
                    'id': '008886df-d297-1eaa-2a74-00000000000e',
                    'name':
                    'advanced-format-512e-support: Detect the drive'
                }
            }
        ]
    }],
    'stats': {
        'undercloud': {
            'changed': 0,
            'failures': 0,
            'ignored': 0,
            'ok': 1,
            'rescued': 0,
            'skipped': 1,
            'unreachable': 0
        }
    },
    'validation_output': [{'task': {
                               'hosts': {u'foo': {}},
                               'name': u'Check if iscsi.service is enabled',
                               'status': u'FAILED'}}]
}]

VALIDATIONS_DATA = {'Description': 'My Validation One Description',
                    'Groups': ['prep', 'pre-deployment'],
                    'categories': ['os', 'system', 'ram'],
                    'products': ['product1'],
                    'ID': 'my_val1',
                    'Name': 'My Validation One Name',
                    'parameters': {}}

VALIDATIONS_STATS = {'Last execution date': '2019-11-25 13:40:14',
                     'Number of execution': 'Total: 1, Passed: 0, Failed: 1'}

FAKE_WRONG_PLAYBOOK = [{
    'hosts': 'undercloud',
    'roles': ['advanced_format_512e_support'],
    'vars': {
        'nometadata': {
            'description': 'foo',
            'groups': ['prep', 'pre-deployment'],
            'categories': ['os', 'storage'],
            'products': ['product1'],
            'name': 'Advanced Format 512e Support'
        }
    }
}]

FAKE_PLAYBOOK = [{'hosts': 'undercloud',
                  'roles': ['advanced_format_512e_support'],
                  'vars': {'metadata': {'description': 'foo',
                                        'groups': ['prep', 'pre-deployment'],
                                        'categories': ['os', 'storage'],
                                        'products': ['product1'],
                                        'name':
                                        'Advanced Format 512e Support',
                                        'path': '/tmp'}}}]

FAKE_PLAYBOOK2 = [{'hosts': 'undercloud',
                   'roles': ['advanced_format_512e_support'],
                   'vars': {'metadata': {'description': 'foo',
                                         'groups': ['prep', 'pre-deployment'],
                                         'categories': ['os', 'storage'],
                                         'products': ['product1'],
                                         'name':
                                         'Advanced Format 512e Support'},
                            'foo': 'bar'}}]

FAKE_PLAYBOOK3 = [{'hosts': 'undercloud',
                   'roles': ['advanced_format_512e_support'],
                   'vars': {'metadata': {'description': 'foo',
                                         'name':
                                         'Advanced Format 512e Support'},
                            'foo': 'bar'}}]

FAKE_VARS = {'foo': 'bar'}

FAKE_METADATA = {'id': 'foo',
                 'description': 'foo',
                 'groups': ['prep', 'pre-deployment'],
                 'categories': ['os', 'storage'],
                 'products': ['product1'],
                 'name': 'Advanced Format 512e Support',
                 'path': '/tmp'}

FORMATED_DATA = {'Description': 'foo',
                 'Groups': ['prep', 'pre-deployment'],
                 'Categories': ['os', 'storage'],
                 'Products': ['product1'],
                 'ID': 'foo',
                 'Name': 'Advanced Format 512e Support',
                 'Path': '/tmp'}

GROUP = {'no-op': [{'description': 'noop-foo'}],
         'pre': [{'description': 'pre-foo'}],
         'post': [{'description': 'post-foo'}]}

FAKE_SUCCESS_RUN = [{'Duration': '0:00:01.761',
                     'Host_Group': 'overcloud',
                     'Status': 'PASSED',
                     'Status_by_Host': 'subnode-1,PASSED, subnode-2,PASSED',
                     'UUID': '123',
                     'Unreachable_Hosts': '',
                     'Validations': 'foo'}]

FAKE_FAILED_RUN = [{'Duration': '0:00:01.761',
                    'Host_Group': 'overcloud',
                    'Status': 'FAILED',
                    'Status_by_Host': 'subnode-1,FAILED, subnode-2,PASSED',
                    'UUID': '123',
                    'Unreachable_Hosts': '',
                    'Validations': 'foo'},
                   {'Duration': '0:00:01.761',
                    'Host_Group': 'overcloud',
                    'Status': 'FAILED',
                    'Status_by_Host': 'subnode-1,FAILED, subnode-2,PASSED',
                    'UUID': '123',
                    'Unreachable_Hosts': '',
                    'Validations': 'foo'},
                   {'Duration': '0:00:01.761',
                    'Host_Group': 'overcloud',
                    'Status': 'PASSED',
                    'Status_by_Host': 'subnode-1,PASSED, subnode-2,PASSED',
                    'UUID': '123',
                    'Unreachable_Hosts': '',
                    'Validations': 'foo'}]

FAKE_VALIDATIONS_PATH = '/usr/share/ansible/validation-playbooks'

DEFAULT_CONFIG = {'validation_dir': '/usr/share/ansible/validation-playbooks',
                  'enable_community_validations': True,
                  'ansible_base_dir': '/usr/share/ansible/',
                  'output_log': 'output.log',
                  'history_limit': 15,
                  'fit_width': True}

CONFIG_WITH_COMMUNITY_VAL_DISABLED = {
    'validation_dir': '/usr/share/ansible/validation-playbooks',
    'enable_community_validations': False,
    'ansible_base_dir': '/usr/share/ansible/',
    'output_log': 'output.log',
    'history_limit': 15,
    'fit_width': True}

WRONG_HISTORY_CONFIG = {'default': {'history_limit': 0}}

ANSIBLE_RUNNER_CONFIG = {'verbosity': 5,
                         'fact_cache_type': 'jsonfile',
                         'quiet': True, 'rotate_artifacts': 256}

ANSIBLE_ENVIRONNMENT_CONFIG = {'ANSIBLE_CALLBACK_WHITELIST':
                               'validation_stdout,validation_json,'
                               'profile_tasks',
                               'ANSIBLE_STDOUT_CALLBACK': 'validation_stdout'}

COVAL_SUBDIR = [PosixPath("/foo/bar/community-validations/roles"),
                PosixPath("/foo/bar/community-validations/playbooks"),
                PosixPath("/foo/bar/community-validations/library"),
                PosixPath("/foo/bar/community-validations/lookup_plugins")]

COVAL_MISSING_SUBDIR = [PosixPath("/foo/bar/community-validations/roles"),
                        PosixPath("/foo/bar/community-validations/playbooks")]

FAKE_COVAL_ITERDIR1 = iter(COVAL_SUBDIR)

FAKE_COVAL_MISSING_SUBDIR_ITERDIR1 = iter(COVAL_MISSING_SUBDIR)

FAKE_ROLES_ITERDIR1 = iter([PosixPath("/u/s/a/roles/role_1"),
                            PosixPath("/u/s/a/roles/role_2"),
                            PosixPath("/u/s/a/roles/role_3"),
                            PosixPath("/u/s/a/roles/role_4"),
                            PosixPath("/u/s/a/roles/role_5"),
                            PosixPath("/u/s/a/roles/my_val")])

FAKE_ROLES_ITERDIR2 = iter([PosixPath("/u/s/a/roles/role_1"),
                            PosixPath("/u/s/a/roles/role_2"),
                            PosixPath("/u/s/a/roles/role_3"),
                            PosixPath("/u/s/a/roles/role_4"),
                            PosixPath("/u/s/a/roles/role_5"),
                            PosixPath("/u/s/a/roles/role_6")])

FAKE_PLAYBOOKS_ITERDIR1 = iter([PosixPath("/u/s/a/plays/play_1.yaml"),
                                PosixPath("/u/s/a/plays/play_2.yaml"),
                                PosixPath("/u/s/a/plays/play_3.yaml"),
                                PosixPath("/u/s/a/plays/play_4.yaml"),
                                PosixPath("/u/s/a/plays/play_5.yaml"),
                                PosixPath("/u/s/a/plays/my-val.yaml")])

FAKE_PLAYBOOKS_ITERDIR2 = iter([PosixPath("/u/s/a/plays/play_1.yaml"),
                                PosixPath("/u/s/a/plays/play_2.yaml"),
                                PosixPath("/u/s/a/plays/play_3.yaml"),
                                PosixPath("/u/s/a/plays/play_4.yaml"),
                                PosixPath("/u/s/a/plays/play_5.yaml"),
                                PosixPath("/u/s/a/plays/play_6.yaml")])

FAKE_PLAYBOOK_TEMPLATE = \
"""---
# This playbook has been generated by the `validation init` CLI.
#
# As shown here in this template, the validation playbook requires three
# top-level directive:
#   ``hosts``, ``vars -> metadata`` and ``roles``.
#
# ``hosts``: specifies which nodes to run the validation on. The options can
#            be ``all`` (run on all nodes), or you could use the hosts defined
#            in the inventory.
# ``vars``: this section serves for storing variables that are going to be
#           available to the Ansible playbook. The validations API uses the
#           ``metadata`` section to read each validation's name and description
#           These values are then reported by the API.
#
# The validations can be grouped together by specyfying a ``groups`` metadata.
# Groups function similar to tags and a validation can thus be part of many
# groups. To get a full list of the groups available and their description,
# please run the following command on your Ansible Controller host:
#
#    $ validation show group
#
# The validations can also be categorized by technical domain and acan belong to
# one or multiple ``categories``. For example, if your validation checks some
# networking related configuration, you may want to put ``networking`` as a
# category.  Note that this section is open and you are free to categorize your
# validations as you like.
#
# The ``products`` section refers to the product on which you would like to run
# the validation. It's another way to categorized your community validations.
# Note that, by default, ``community`` is set in the ``products`` section to
# help you list your validations by filtering by products:
#
#    $ validation list --product community
#
- hosts: hostname
  gather_facts: false
  vars:
    metadata:
      name: Brief and general description of the validation
      description: |
        The complete description of this validation should be here
# GROUPS:
# Run ``validation show group`` to get the list of groups
# :type group: `list`
# If you don't want to add groups for your validation, just
# set an empty list to the groups key
      groups: []
# CATEGORIES:
# :type group: `list`
# If you don't want to categorize your validation, just
# set an empty list to the categories key
      categories: []
      products:
        - community
  roles:
    - my_val
"""


def fake_ansible_runner_run_return(status='successful', rc=0):
    return status, rc


def _accept_default_log_path(path, *args):
    if path == constants.VALIDATIONS_LOG_BASEDIR:
        return True
    return False
