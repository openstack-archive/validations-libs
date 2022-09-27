#   Copyright 2022 Red Hat, Inc.
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

import logging

from validations_libs import logger


class TestLogger(TestCase):

    def setUp(self) -> None:
        super().setUp()

    @mock.patch('os.path.exists', reutrn_value=True)
    def test_logger_init(self, mock_exists):
        new_logger = logger.getLogger("fooo")
        mock_exists.assert_called_once_with('/dev/log')
        self.assertEqual(logging.Logger, type(new_logger))

    @mock.patch('logging.Logger.warning')
    @mock.patch('os.path.exists', return_value=False)
    def test_logger_init_no_journal(self, mock_exists, mock_warning):
        new_logger = logger.getLogger("fooo")
        mock_exists.assert_called_once_with('/dev/log')
        mock_warning.assert_called_once()
        self.assertEqual(logging.Logger, type(new_logger))
