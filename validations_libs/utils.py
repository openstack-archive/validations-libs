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
import glob
import logging
import os
import yaml

LOG = logging.getLogger(__name__ + ".utils")


def parse_all_validations_on_disk(path, groups=None):
    results = []
    validations_abspath = glob.glob("{path}/*.yaml".format(path=path))

    for pl in validations_abspath:
        validation_id, ext = os.path.splitext(os.path.basename(pl))

        with open(pl, 'r') as val_playbook:
            contents = yaml.safe_load(val_playbook)

        validation_groups = get_validation_metadata(contents, 'groups') or []
        if not groups or set.intersection(set(groups), set(validation_groups)):
            results.append({
                'id': validation_id,
                'name': get_validation_metadata(contents, 'name'),
                'groups': get_validation_metadata(contents, 'groups'),
                'description': get_validation_metadata(contents,
                                                       'description'),
                'parameters': get_validation_parameters(contents)
            })

    return results


def parse_all_validation_groups_on_disk(groups_file_path=None):
    results = []

    if not groups_file_path:
        groups_file_path = constants.VALIDATION_GROUPS_INFO

    if not os.path.exists(groups_file_path):
        return results

    with open(groups_file_path, 'r') as grps:
        contents = yaml.safe_load(grps)

    for grp_name, grp_desc in sorted(contents.items()):
        results.append((grp_name, grp_desc[0].get('description')))

    return results


def get_validation_metadata(validation, key):
    default_metadata = {
        'name': 'Unnamed',
        'description': 'No description',
        'stage': 'No stage',
        'groups': [],
    }

    try:
        return validation[0]['vars']['metadata'].get(key,
                                                     default_metadata[key])
    except KeyError:
        LOG.exception("Key '{key}' not even found in "
                      "default metadata").format(key=key)
    except TypeError:
        LOG.exception("Failed to get validation metadata.")


def get_validation_parameters(validation):
    try:
        return {
            k: v
            for k, v in validation[0]['vars'].items()
            if k != 'metadata'
        }
    except KeyError:
        LOG.debug("No parameters found for this validation")
        return dict()
