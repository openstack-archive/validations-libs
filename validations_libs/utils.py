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

import glob
import json
import logging
import os
import six
import shutil
import tempfile
import yaml

from prettytable import PrettyTable
from validations_libs import constants

RED = "\033[1;31m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"

FAILED_VALIDATION = "{}FAILED{}".format(RED, RESET)
PASSED_VALIDATION = "{}PASSED{}".format(GREEN, RESET)

LOG = logging.getLogger(__name__ + ".utils")


class Pushd(object):
    """Simple context manager to change directories and then return."""

    def __init__(self, directory):
        """This context manager will enter and exit directories.

        >>> with Pushd(directory='/tmp'):
        ...     with open('file', 'w') as f:
        ...         f.write('test')

        :param directory: path to change directory to
        :type directory: `string`
        """
        self.dir = directory
        self.pwd = self.cwd = os.getcwd()

    def __enter__(self):
        os.chdir(self.dir)
        self.cwd = os.getcwd()
        return self

    def __exit__(self, *args):
        if self.pwd != self.cwd:
            os.chdir(self.pwd)


class TempDirs(object):
    """Simple context manager to manage temp directories."""

    def __init__(self, dir_path=None, dir_prefix='tripleo', cleanup=True,
                 chdir=True):
        """This context manager will create, push, and cleanup temp directories.

        >>> with TempDirs() as t:
        ...     with open('file', 'w') as f:
        ...         f.write('test')
        ...     print(t)
        ...     os.mkdir('testing')
        ...     with open(os.path.join(t, 'file')) as w:
        ...         print(w.read())
        ...     with open('testing/file', 'w') as f:
        ...         f.write('things')
        ...     with open(os.path.join(t, 'testing/file')) as w:
        ...         print(w.read())

        :param dir_path: path to create the temp directory
        :type dir_path: `string`
        :param dir_prefix: prefix to add to a temp directory
        :type dir_prefix: `string`
        :param cleanup: when enabled the temp directory will be
                         removed on exit.
        :type cleanup: `boolean`
        :param chdir: Change to/from the created temporary dir on enter/exit.
        :type chdir: `boolean`
        """

        # NOTE(cloudnull): kwargs for tempfile.mkdtemp are created
        #                  because args are not processed correctly
        #                  in py2. When we drop py2 support (cent7)
        #                  these args can be removed and used directly
        #                  in the `tempfile.mkdtemp` function.
        tempdir_kwargs = dict()
        if dir_path:
            tempdir_kwargs['dir'] = dir_path

        if dir_prefix:
            tempdir_kwargs['prefix'] = dir_prefix

        self.dir = tempfile.mkdtemp(**tempdir_kwargs)
        self.pushd = Pushd(directory=self.dir)
        self.cleanup = cleanup
        self.chdir = chdir

    def __enter__(self):
        if self.chdir:
            self.pushd.__enter__()
        return self.dir

    def __exit__(self, *args):
        if self.chdir:
            self.pushd.__exit__()
        if self.cleanup:
            self.clean()
        else:
            LOG.warning("Not cleaning temporary directory [ %s ]" % self.dir)

    def clean(self):
        shutil.rmtree(self.dir, ignore_errors=True)
        LOG.info("Temporary directory [ %s ] cleaned up" % self.dir)


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


def read_validation_groups_file(groups_file_path=None):
    """Load groups.yaml file and return a dictionary with its contents"""
    if not groups_file_path:
        groups_file_path = constants.VALIDATION_GROUPS_INFO

    if not os.path.exists(groups_file_path):
        return []

    with open(groups_file_path, 'r') as grps:
        contents = yaml.safe_load(grps)

    return contents


def get_validation_group_name_list():
    """Get the validation group name list only"""
    results = []

    groups = read_validation_groups_file()

    if groups and isinstance(dict, groups):
        for grp_name in six.viewkeys(groups):
            results.append(grp_name)

    return results


def get_new_validations_logs_on_disk():
    """Return a list of new log execution filenames """
    files = []

    for root, dirs, filenames in os.walk(constants.VALIDATIONS_LOG_BASEDIR):
        files = [
            f for f in filenames if not f.startswith('processed')
            and os.path.splitext(f)[1] == '.json'
        ]

    return files


def get_results(results):
    """Get validations results and return as PrettytTable format"""
    new_log_files = get_new_validations_logs_on_disk()

    for i in new_log_files:
        val_id = "{}.yaml".format(i.split('_')[1])
        for res in results:
            if res['validation'].get('validation_id') == val_id:
                res['validation']['logfile'] = \
                    os.path.join(constants.VALIDATIONS_LOG_BASEDIR, i)

    t = PrettyTable(border=True, header=True, padding_width=1)
    t.field_names = [
        "UUID", "Validations", "Status", "Host Group(s)",
        "Status by Host", "Unreachable Host(s)", "Duration"]

    for validation in results:
        r = []
        logfile = validation['validation'].get('logfile', None)
        if logfile and os.path.exists(logfile):
            with open(logfile, 'r') as val:
                contents = json.load(val)

            for i in contents['plays']:
                host = [
                    x.encode('utf-8')
                    for x in i['play'].get('host').split(', ')
                ]
                val_id = i['play'].get('validation_id')
                time_elapsed = \
                    i['play']['duration'].get('time_elapsed', None)

            r.append(contents['plays'][0]['play'].get('id'))
            r.append(val_id)
            if validation['validation'].get('status') == "PASSED":
                r.append(PASSED_VALIDATION)
            else:
                r.append(FAILED_VALIDATION)

            unreachable_hosts = []
            hosts_result = []
            for h in list(contents['stats'].keys()):
                ht = h.encode('utf-8')
                if contents['stats'][ht]['unreachable'] != 0:
                    unreachable_hosts.append(ht)
                elif contents['stats'][ht]['failures'] != 0:
                    hosts_result.append("{}{}{}".format(
                        RED, ht, RESET))
                else:
                    hosts_result.append("{}{}{}".format(
                        GREEN, ht, RESET))

            r.append(", ".join(host))
            r.append(", ".join(hosts_result))
            r.append("{}{}{}".format(RED,
                                     ", ".join(unreachable_hosts),
                                     RESET))
            r.append(time_elapsed)
            t.add_row(r)

    t.sortby = "UUID"
    for field in t.field_names:
        if field == "Status":
            t.align['Status'] = "l"
        else:
            t.align[field] = "l"

    print(t)

    if len(new_log_files) > len(results):
        LOG.warn('Looks like we have more log files than '
                 'executed validations')

    for i in new_log_files:
        os.rename(
            "{}/{}".format(constants.VALIDATIONS_LOG_BASEDIR,
                           i), "{}/processed_{}".format(
                               constants.VALIDATIONS_LOG_BASEDIR, i))
