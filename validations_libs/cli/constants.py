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
"""Constants for the VF CLI.
Constains larger, more frequently used and redundant CLI help strings.
"""

CONF_FILE_DESC = "Config file path for Validation Framework.\n"
LOG_PATH_DESC = "Path where the log files and artifacts are located.\n"
PLAY_PATH_DESC = "Path where validation playbooks are located.\n"
VAL_GROUP_DESC = ("List specific group of validations, "
                  "if more than one group is required "
                  "separate the group names with commas.\n")
VAL_CAT_DESC = ("List specific category of validations, "
                "if more than one category is required "
                "separate the category names with commas.\n")
VAL_PROD_DESC = ("List specific product of validations, "
                 "if more than one product is required "
                 "separate the product names with commas.\n")
