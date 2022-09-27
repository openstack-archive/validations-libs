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
import logging
import os
from logging.handlers import SysLogHandler


def getLogger(loggerName, stream_lvl=logging.WARN):
    """Create logger instance.

    :param loggerName: name of the new Logger instance
    :type loggerName: `str`
    :param stream_lvl: minimum level at which the messages will be printed to stream
    :type stream_lvl: `int`
    :rtype: `Logger`
    """
    new_logger = logging.getLogger(loggerName)

    formatter = logging.Formatter("%(asctime)s %(module)s %(message)s")

    s_handler = logging.StreamHandler()
    s_handler.setFormatter(formatter)
    s_handler.setLevel(stream_lvl)

    new_logger.addHandler(s_handler)

    if os.path.exists('/dev/log'):
        sys_handler = SysLogHandler(address='/dev/log')
        sys_handler.setFormatter(formatter)

        new_logger.addHandler(sys_handler)
    else:
        new_logger.warning("Journal socket does not exist. Logs will not be processed by syslog.")

    return new_logger
