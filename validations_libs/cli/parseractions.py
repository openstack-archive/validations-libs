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

import argparse

from validations_libs import utils

LOG = utils.getLogger(__name__ + '.parseractions')


class CommaListAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values.split(','))


class KeyValueAction(argparse.Action):
    """A custom action to parse arguments as key=value pairs
    Ensures that ``dest`` is a dict and values are strings.
    """

    def __call__(self, parser, namespace, values, option_string=None):
        # Make sure we have an empty dict rather than None
        if getattr(namespace, self.dest, None) is None:
            setattr(namespace, self.dest, {})

        # Add value if an assignment else remove it
        if values.count('=') >= 1:
            for key_value in values.split(','):
                key, value = key_value.split('=', 1)
                if '' == key:
                    msg = (
                        "Property key must be specified: {}"
                    ).format(str(values))

                    raise argparse.ArgumentTypeError(msg)
                elif value.count('=') > 0:
                    msg = (
                        "Only a single '=' sign is allowed: {}"
                    ).format(str(values))

                    raise argparse.ArgumentTypeError(msg)
                else:
                    if key in getattr(namespace, self.dest, {}):
                        LOG.warning((
                                "Duplicate key '%s' provided."
                                "Value '%s' Overriding previous value. '%s'"
                            ) % (
                            key, getattr(namespace, self.dest)[key], value))
                    getattr(namespace, self.dest, {}).update({key: value})
        else:
            msg = (
                "Expected 'key=value' type, but got: {}"
            ).format(str(values))

            raise argparse.ArgumentTypeError(msg)
