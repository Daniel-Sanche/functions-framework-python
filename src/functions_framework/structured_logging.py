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

import flask

"""
A Logging formatter string that outputs logs as structured JSON
"""
STRUCTURED_LOG_FORMAT = '{"message": "%(message)s", "severity": "%(levelname)s", "trace", "%(trace)s"}'

class TraceFilter(logging.Filter):
    """
    Logging.Filter subclass class to inject trace data from incoming Flask
    requests into log records. 

    By default, it looks at the X-Cloud-Trace-Context header for trace data.
    If a trace id can't be found, `record.trace` will be an empty string.
    """

    def __init__(self, trace_header='X-Cloud-Trace-Context'):
        self.trace_header = trace_header

    def filter(self, record):
        trace_id = ""
        try:
            if flask and flask.request:
                header = flask.request.headers.get(self.trace_header)
                if header:
                    trace_id = header.split("/", 1)[0]
        except RuntimeError as e:
            # RuntimeError thown when flask session not found
            pass
        record.trace = trace_id
        return True
