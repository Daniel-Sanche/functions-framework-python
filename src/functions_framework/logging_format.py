# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

def get_format_dict(format_name="plain"):
    """
    Constructs a logging config dictionary to print plain logs
    to standard out
    """
    d = {
        'version': 1,
        'formatters':{
            'plain': {
                'format': '%(message)s'
            },
            'structured': {
                'format': "{\"message\": \"%(message)s\", \"severity\": \"%(levelname)s\"}"
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': format_name
            }
        },
        'root': {
            'level': 'DEBUG',
            'handlers': [
                'console'
            ]
        }
    }
    return d

