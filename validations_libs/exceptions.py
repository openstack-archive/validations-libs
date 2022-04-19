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

"""This module contains Validation Framework specific exceptions,
to be raised by Validation Framework runtime.

The exceptions are meant to cover the most common of the possible
fail states the framework can encounter, with the rest evoking one
of the built in exceptions, such as 'RuntimeError'.
Use of these exceptions should be limited to cases when cause is known
and within the context of the framework itself.
"""


class ValidationRunException(Exception):
    """ValidationRunException is to be raised when actions
    initiated by the CLI 'run' subcommand or `run_validations` method
    of the `ValidationsActions` class, cause unacceptable behavior
    from which it is impossible to recover.
    """


class ValidationShowException(Exception):
    """ValidationShowException is to be raised when actions
    initiated by the CLI 'show' subcommands or `show_history`,
    `show_validations` or `show_validations_parameters` methods
    of the `ValidationsActions` class, cause unacceptable behavior
    from which it is impossible to recover.
    """
