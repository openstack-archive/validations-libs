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

# PrettyTable Colors:
RED = "\033[1;31m"
GREEN = "\033[0;32m"
CYAN = "\033[36m"
RESET = "\033[0;0m"
YELLOW = "\033[0;33m"

colors = {
    'starting': CYAN,
    'running': CYAN,
    'PASSED': GREEN,
    'UNKNOWN': YELLOW,
    'UNREACHABLE': YELLOW,
    'ERROR': RED,
    'FAILED': RED
}


def color_output(output, status=None):
    """Apply color to output based on colors dict entries.
    Unknown status or no status at all results in aplication
    of YELLOW color.

    .. note::

       Coloring itself is performed using format method of the
       string class. This function is merely a wrapper around it,
       and around ANSI escape sequences as defined by ECMA-48.

    """
    if status:
        color = colors.get(status, YELLOW)
    else:
        color = colors['UNKNOWN']

    output = '{}{}{}'.format(
        color,
        output,
        RESET)

    return output
