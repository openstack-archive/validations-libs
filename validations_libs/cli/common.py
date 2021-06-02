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
import logging
from prettytable import PrettyTable
import re
import yaml

try:
    from junit_xml import TestSuite, TestCase, to_xml_report_string
    JUNIT_XML_FOUND = True
except ImportError:
    JUNIT_XML_FOUND = False

from validations_libs import constants
from validations_libs import utils as v_utils
from validations_libs.cli import colors

GROUP_FILE = constants.VALIDATION_GROUPS_INFO


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
                _name = colors.color_output(_name, status=_status)
                hosts.append(_name)
            row['Status_by_Host'] = ', '.join(hosts)
        if row.get('Status'):
            status = row.get('Status')
            row['Status'] = colors.color_output(status, status=status)
        table.add_row(row.values())
    print(table)


def write_output(output_log, results):
    """Write output log file as Json format"""
    with open(output_log, 'w') as output:
        output.write(json.dumps({'results': results}, indent=4,
                                sort_keys=True))


def write_junitxml(output_junitxml, results):
    """Write output file as JUnitXML format"""
    if not JUNIT_XML_FOUND:
        log = logging.getLogger(__name__ + ".write_junitxml")
        log.warning('junitxml output disabled: the `junit_xml` python module '
                    'is missing.')
        return
    test_cases = []
    duration_re = re.compile('([0-9]+):([0-9]+):([0-9]+).([0-9]+)')
    for vitem in results:
        if vitem.get('Validations'):
            parsed_duration = 0
            test_duration = vitem.get('Duration', '')
            matched_duration = duration_re.match(test_duration)
            if matched_duration:
                parsed_duration = (int(matched_duration[1])*3600
                                   + int(matched_duration[2])*60
                                   + int(matched_duration[3])
                                   + float('0.{}'.format(matched_duration[4])))

            test_stdout = vitem.get('Status_by_Host', '')

            test_case = TestCase('validations', vitem['Validations'],
                                 parsed_duration, test_stdout)
            if vitem['Status'] == 'FAILED':
                test_case.add_failure_info('FAILED')
            test_cases.append(test_case)

    ts = TestSuite("Validations", test_cases)
    with open(output_junitxml, 'w') as output:
        output.write(to_xml_report_string([ts]))


def read_extra_vars_file(extra_vars_file):
    """Read file containing extra variables.
    """
    try:
        with open(extra_vars_file, 'r') as env_file:
            return yaml.safe_load(env_file.read())
    except yaml.YAMLError as error:
        error_msg = (
            "The extra_vars file must be properly formatted YAML/JSON."
            "Details: {}.").format(error)
        raise RuntimeError(error_msg)
