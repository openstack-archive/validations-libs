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
#
try:
    from unittest import mock
except ImportError:
    import mock
from unittest import TestCase

from validations_libs.cli import colors


class TestColors(TestCase):
    def setUp(self):
        RED = "\033[1;31m"
        GREEN = "\033[0;32m"
        CYAN = "\033[36m"
        YELLOW = "\033[0;33m"
        self.RESET = "\033[0;0m"

        self.status_color = {
            'starting': CYAN,
            'running': CYAN,
            'PASSED': GREEN,
            'UNKNOWN': YELLOW,
            'UNREACHABLE': YELLOW,
            'ERROR': RED,
            'FAILED': RED
        }

        super(TestColors, self).setUp()

    def test_format_known_status(self):
        """Tests formatting, meaning coloring, for every
        status recognized by VF.
        """

        for status in self.status_color:
            color = self.status_color[status]
            colored_output = colors.color_output("fizz", status=status)
            #Checking reset color
            self.assertEqual(colored_output[-6:], self.RESET)
            #Checking output color
            self.assertEqual(colored_output[:len(color)], color)
            #Checking output string
            self.assertEqual(colored_output[len(color):][:4], "fizz")

    def test_format_unknown_status(self):

        color = self.status_color['UNKNOWN']
        colored_output = colors.color_output("buzz")
        #Checking reset color
        self.assertEqual(colored_output[-6:], self.RESET)
        #Checking output color
        self.assertEqual(colored_output[:len(color)], color)
        #Checking output string
        self.assertEqual(colored_output[len(color):][:4], "buzz")
