#!/usr/bin/env python

#   Copyright 2021 Red Hat, Inc.
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

import json
from prettytable import PrettyTable

from validations_libs import constants
from validations_libs import utils as v_utils

GROUP_FILE = constants.VALIDATION_GROUPS_INFO

# PrettyTable Colors:
RED = "\033[1;31m"
GREEN = "\033[0;32m"
CYAN = "\033[36m"
RESET = "\033[0;0m"
YELLOW = "\033[0;33m"


def print_dict(data):
    """Print table from python dict with PrettyTable"""
    table = PrettyTable(border=True, header=True, padding_width=1)
    # Set Field name by getting the result dict keys
    try:
        table.field_names = data[0].keys()
        table.align = 'l'
    except IndexError:
        raise IndexError()
    for row in data:
        if row.get('Status_by_Host'):
            hosts = []
            for host in row['Status_by_Host'].split(', '):
                try:
                    _name, _status = host.split(',')
                except ValueError:
                    # if ValueError, then host is in unknown state:
                    _name = host
                    _status = 'UNKNOWN'
                color = (GREEN if _status == 'PASSED' else
                         (YELLOW if _status == 'UNREACHABLE' else RED))
                _name = '{}{}{}'.format(color, _name, RESET)
                hosts.append(_name)
            row['Status_by_Host'] = ', '.join(hosts)
        if row.get('Status'):
            status = row.get('Status')
            color = (CYAN if status in ['starting', 'running']
                     else GREEN if status == 'PASSED' else RED)
            row['Status'] = '{}{}{}'.format(color, status, RESET)
        table.add_row(row.values())
    print(table)


def write_output(output_log, results):
    """Write output log file as Json format"""
    with open(output_log, 'w') as output:
        output.write(json.dumps({'results': results}, indent=4,
                                sort_keys=True))
